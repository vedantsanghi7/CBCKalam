"""FastAPI backend for KALAM.

Routes:
  POST /session                    — start a session
  POST /session/{id}/turn          — conversational turn (slot filler)
  POST /session/{id}/patch         — manual slot edit
  POST /session/{id}/match         — run the eligibility engine
  POST /session/{id}/reset         — clear the session
  GET  /schemes                    — catalogue (with descriptions)
  GET  /schemes/{id}               — full scheme detail
  GET  /ambiguity-map              — rendered markdown
  GET  /languages                  — supported UI languages
  POST /translate                  — body: {text, target, source?}
  POST /translate/batch            — body: {items:[{id,text}], target}
  POST /stt                        — multipart audio → transcript
  POST /tts                        — body: {text, language} → audio bytes (wav/mp3)
"""
import base64
import os
import sys
import uuid
import yaml
import concurrent.futures
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from conv.nlu import (
    extract_slots, get_next_question, get_most_informative_missing,
    SLOT_PRIORITY, SLOT_QUESTIONS, ALL_SLOTS,
)
from conv.dialog import reply_register
from conv import sarvam_client
from engine.evaluator import evaluate_scheme
from engine.models import Scheme, Rule
from engine.sequencer import sequence_schemes

ROOT = Path(__file__).resolve().parent.parent
SCHEMES_DIR = ROOT / "schemes"

app = FastAPI(title="KALAM — Welfare Eligibility Engine", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

sessions: Dict[str, Dict[str, Any]] = {}


# ----- Helpers ------------------------------------------------------------

_schemes_cache: List[Scheme] = []
_schemes_cache_ts: float = 0

def _load_all_schemes() -> List[Scheme]:
    global _schemes_cache, _schemes_cache_ts
    import time
    now = time.time()
    if _schemes_cache and (now - _schemes_cache_ts) < 60:
        return _schemes_cache
    schemes: List[Scheme] = []
    if not SCHEMES_DIR.exists():
        return schemes
    for p in sorted(SCHEMES_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text()) or {}
            if "scheme_id" not in data:
                continue
            data["rules"] = [Rule(**r) for r in data.get("rules", [])]
            data["launched"] = str(data.get("launched") or "")
            schemes.append(Scheme(**{k: v for k, v in data.items() if k in Scheme.model_fields}))
        except Exception as e:
            print(f"[api] failed to load {p.name}: {e}")
    _schemes_cache = schemes
    _schemes_cache_ts = now
    return schemes


def _scheme_summary(s: Scheme) -> dict:
    benefit = s.benefit or {}
    amount = benefit.get("amount_inr")
    freq = benefit.get("frequency")
    mode = benefit.get("mode")
    btype = benefit.get("type")
    if isinstance(amount, (int, float)) and amount:
        benefit_line = f"₹{int(amount):,}/{freq or 'year'}"
    elif btype == "insurance":
        benefit_line = f"Insurance cover: {benefit.get('notes', '')}" or "Insurance benefit"
    elif btype:
        benefit_line = btype.replace("_", " ").title()
    else:
        benefit_line = "Welfare benefit"
    extra: dict = {}
    for k in ("description", "category", "application_url", "short_description"):
        v = getattr(s, k, None) if hasattr(s, k) else None
        if not v:
            # pydantic-allow-extra: fall back to dict attrs on sneak-through
            v = s.model_extra.get(k) if getattr(s, "model_extra", None) else None
        if v:
            extra[k] = v
    return {
        "id": s.scheme_id,
        "name": s.name,
        "ministry": s.ministry,
        "launched": s.launched,
        "benefit": s.benefit,
        "benefit_line": benefit_line,
        "documents_checklist": s.documents_checklist,
        "rules_count": len(s.rules),
        **extra,
    }


def _get_pending_slot(session: Dict[str, Any]) -> Optional[str]:
    return session.get("pending_slot")


# ----- Models -------------------------------------------------------------

class TurnRequest(BaseModel):
    utterance: str
    language: Optional[str] = None


class PatchRequest(BaseModel):
    slot: str
    value: Any


class TranslateRequest(BaseModel):
    text: str
    target: str
    source: Optional[str] = "auto"


class TranslateBatchItem(BaseModel):
    id: str
    text: str


class TranslateBatchRequest(BaseModel):
    items: List[TranslateBatchItem]
    target: str
    source: Optional[str] = "auto"


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "hi-IN"
    speaker: Optional[str] = "anushka"


# ----- Session / turn -----------------------------------------------------

@app.post("/session")
def create_session():
    sid = str(uuid.uuid4())
    sessions[sid] = {"slots": {}, "turn_count": 0, "pending_slot": None, "history": []}
    return {"session_id": sid, "greeting":
            "Namaste 🙏 I am KALAM. I check your eligibility for government schemes. Shall we begin?",
            "supported_slots": ALL_SLOTS}


MIN_SLOTS_FOR_MATCH = 5


@app.post("/session/{sid}/turn")
def handle_turn(sid: str, payload: TurnRequest):
    session = sessions.setdefault(sid, {"slots": {}, "turn_count": 0,
                                        "pending_slot": None, "history": []})
    session["turn_count"] += 1
    pending = session.get("pending_slot")
    utt = payload.utterance.strip()
    session["history"].append({"role": "user", "text": utt})

    # ---- Extract (with pending-slot context & history) ----
    result = extract_slots(utt, session["slots"], history=session["history"], pending_slot=pending, language=payload.language)
    newly = (result or {}).get("extracted", {}) or {}

    contradictions = []
    for k, v in list(newly.items()):
        if v in (None, "", "UNKNOWN"):
            continue
        if k in session["slots"] and session["slots"][k] != v:
            contradictions.append({"slot": k, "old_value": session["slots"][k], "new_value": v})
        session["slots"][k] = v

    # ---- Choose next question ----
    
    # Auto-resolve irrelevant slots based on known values
    occupation = session["slots"].get("occupation")
    sex = session["slots"].get("sex")
    
    if occupation and occupation not in ("farmer", "UNKNOWN"):
        session["slots"]["land_in_own_name"] = False
        session["slots"]["land_ownership_type"] = "none"
        
    if sex == "M" or sex == "male":
        session["slots"]["is_pregnant"] = False
        session["slots"]["is_widow"] = False

    known = set(session["slots"].keys())
    missing = [s for s in SLOT_PRIORITY if s not in known]
    known_count = len([k for k in session["slots"]
                       if session["slots"][k] not in (None, "", "UNKNOWN")])
                       
    qualifies_count = 0
    almost_count = 0
    schemes = _load_all_schemes()
    for s in schemes:
        try:
            res = evaluate_scheme(s, session["slots"])
            if res.status == "QUALIFIES":
                qualifies_count += 1
            elif res.status == "ALMOST_QUALIFIES":
                almost_count += 1
        except Exception:
            pass

    eligible_count = qualifies_count + almost_count

    # Ready logic:
    # - If we have QUALIFIES schemes and enough data → ready (but keep asking if slots remain)
    # - If all slots exhausted → ready regardless
    # - If only ALMOST or 0 and slots remain → keep asking
    all_slots_done = not missing
    has_qualifiers = qualifies_count > 0
    enough_data = known_count >= MIN_SLOTS_FOR_MATCH
    
    ready = all_slots_done or (has_qualifiers and enough_data)

    llm_reply = result.get("next_message") if result else None

    if llm_reply:
        reply = llm_reply
        # Use the LLM's asking_slot to determine which options to show
        asking_slot = (result.get("asking_slot") or "").strip() if result else None
        if asking_slot and asking_slot != "null" and asking_slot in SLOT_QUESTIONS:
            q = get_next_question(asking_slot)
            options = q.get("options")
            session["pending_slot"] = asking_slot
        elif missing:
            # Fallback: use first missing slot
            q = get_next_question(missing[0])
            options = q.get("options")
            session["pending_slot"] = missing[0]
        else:
            options = None
            session["pending_slot"] = None
        if ready and not missing:
             session["pending_slot"] = None
    else:
        if missing:
            next_slot = missing[0]
            q = get_next_question(next_slot)
            session["pending_slot"] = next_slot
            if has_qualifiers and enough_data:
                reply = (f"Got it. So far {qualifies_count} schemes look promising. "
                         f"Let me ask a few more to refine: {q['question']}")
            elif known_count == 0:
                reply = q["question"]
            else:
                accepted = next(iter(newly.keys()), None)
                prefix = ("Got it. " if accepted and pending and accepted == pending
                          else "Okay. ")
                # Don't set ready if we only have almost-qualifies
                if almost_count > 0 and qualifies_count == 0:
                    prefix += f"({almost_count} schemes are close but need more info.) "
                reply = prefix + q["question"]
            options = q.get("options")
            # Don't signal ready if there are still questions and 0 qualifiers
            if not has_qualifiers:
                ready = False
        else:
            # All questions exhausted
            if qualifies_count > 0:
                reply = f"Got all the details! I found {qualifies_count} schemes you are eligible for. Evaluating now…"
            elif almost_count > 0:
                reply = f"Got all the details. {almost_count} schemes are close — let me show you the full analysis…"
            else:
                reply = "I have gathered all your details. Let me check the full results for your profile…"
            ready = True
            options = None
            session["pending_slot"] = None

    session["history"].append({"role": "assistant", "text": reply,
                               "pending": session.get("pending_slot")})

    # Translate reply if user selected a non-Hinglish/non-English language.
    # The LLM doesn't reliably generate in the target language, so we
    # translate server-side as a safety net. The frontend will NOT re-translate
    # because the message is tagged with the current language.
    target_lang = (payload.language or "hinglish").strip()
    if target_lang and target_lang not in ("hinglish", "en", ""):
        try:
            reply = sarvam_client.translate(reply, target=target_lang, source="en")
        except Exception:
            pass  # Fall back to original if translation fails
        # Also translate quick-reply options
        if options:
            try:
                translated_opts = []
                for opt in options:
                    translated_opts.append(sarvam_client.translate(opt, target=target_lang, source="en"))
                options = translated_opts
            except Exception:
                pass

    return {
        "reply": reply,
        "options": options,
        "pending_slot": session.get("pending_slot"),
        "slots_known": session["slots"],
        "slots_missing": missing[:5],
        "ready_to_match": ready,
        "eligible_count": eligible_count,
        "qualifies_count": qualifies_count,
        "almost_count": almost_count,
        "total_slots_known": known_count,
        "total_slots_possible": len(SLOT_PRIORITY),
        "contradictions": contradictions,
        "register": reply_register(utt),
    }


@app.post("/session/{sid}/patch")
def patch_slot(sid: str, payload: PatchRequest):
    if sid not in sessions:
        raise HTTPException(404, "Session not found")
    sessions[sid]["slots"][payload.slot] = payload.value
    return {"ok": True, "slots_known": sessions[sid]["slots"]}


@app.post("/session/{sid}/reset")
def reset_session(sid: str):
    sessions[sid] = {"slots": {}, "turn_count": 0, "pending_slot": None, "history": []}
    return {"ok": True}


@app.post("/session/{sid}/match")
def match_session(sid: str):
    user_data = sessions.get(sid, {}).get("slots", {})
    schemes = _load_all_schemes()
    order_map = sequence_schemes(schemes)
    results = []
    for scheme in schemes:
        try:
            res = evaluate_scheme(scheme, user_data)
            res.application_order = order_map.get(scheme.scheme_id, 99)
            results.append(res.model_dump())
        except Exception as e:
            print(f"[engine] {scheme.scheme_id}: {e}")
    status_rank = {"QUALIFIES": 0, "ALMOST_QUALIFIES": 1, "UNCERTAIN": 2, "DOES_NOT_QUALIFY": 3}
    results.sort(key=lambda x: (status_rank.get(x["status"], 4), -x["confidence"]))
    return results


# ----- Catalogue ----------------------------------------------------------

@app.get("/schemes")
def list_schemes():
    return {"schemes": [_scheme_summary(s) for s in _load_all_schemes()]}


@app.get("/schemes/{scheme_id}")
def get_scheme(scheme_id: str):
    for s in _load_all_schemes():
        if s.scheme_id.lower() == scheme_id.lower():
            return s.model_dump()
    raise HTTPException(404, "Scheme not found")


@app.get("/ambiguity-map")
def get_ambiguity_map():
    path = ROOT / "docs" / "ambiguity_map.md"
    if path.exists():
        return {"markdown": path.read_text()}
    return {"markdown": "# Ambiguity Map\n\nNot yet generated."}


# ----- Languages + translation -------------------------------------------

LANGUAGES = [
    {"code": "hinglish", "name": "Hinglish", "local_name": "Hinglish"},
    {"code": "en", "name": "English", "local_name": "English"},
    {"code": "hi", "name": "Hindi", "local_name": "हिन्दी"},
    {"code": "bn", "name": "Bengali", "local_name": "বাংলা"},
    {"code": "gu", "name": "Gujarati", "local_name": "ગુજરાતી"},
    {"code": "kn", "name": "Kannada", "local_name": "ಕನ್ನಡ"},
    {"code": "ml", "name": "Malayalam", "local_name": "മലയാളം"},
    {"code": "mr", "name": "Marathi", "local_name": "मराठी"},
    {"code": "or", "name": "Odia", "local_name": "ଓଡ଼ିଆ"},
    {"code": "pa", "name": "Punjabi", "local_name": "ਪੰਜਾਬੀ"},
    {"code": "ta", "name": "Tamil", "local_name": "தமிழ்"},
    {"code": "te", "name": "Telugu", "local_name": "తెలుగు"},
    {"code": "ur", "name": "Urdu", "local_name": "اردو"},
]


@app.get("/languages")
def get_languages():
    return {"languages": LANGUAGES}


@app.post("/translate")
def translate_one(req: TranslateRequest):
    out = sarvam_client.translate(req.text, target=req.target, source=req.source or "auto")
    return {"translated_text": out, "target": req.target}


@app.post("/translate/batch")
def translate_batch(req: TranslateBatchRequest):
    def _do_trans(item):
        t = sarvam_client.translate(item.text, target=req.target, source=req.source or "auto")
        return {"id": item.id, "translated_text": t}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        out = list(executor.map(_do_trans, req.items))
    return {"items": out, "target": req.target}


# ----- Voice --------------------------------------------------------------

@app.post("/stt")
async def stt(file: UploadFile = File(...), language: str = Form("hi-IN")):
    data = await file.read()
    text = sarvam_client.transcribe(data, language=language)
    return {"transcript": text, "language": language}


@app.post("/tts")
def tts(req: TTSRequest):
    audio = sarvam_client.synthesize(req.text, language=req.language or "hi-IN",
                                     speaker=req.speaker or "anushka")
    return Response(content=audio, media_type="audio/wav")


# ----- Health -------------------------------------------------------------

@app.get("/healthz")
def health():
    n = len(_load_all_schemes())
    return {"ok": True, "schemes_loaded": n, "offline": sarvam_client.OFFLINE}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
