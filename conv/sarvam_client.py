"""Thin wrapper around Sarvam APIs:

- `chat(messages, ...)` — chat completions (Sarvam-M / Sarvam-30B)
- `translate(text, source, target)` — Sarvam Translate
- `transcribe(audio_path, language)` — Sarvam Saaras (STT)
- `synthesize(text, language)` — Sarvam Bulbul (TTS), returns audio bytes

All calls honour `KALAM_OFFLINE=1`: they return deterministic mock data
instead of hitting the network, so tests, the CLI, and the engine run
without a key.

Every call is also written to `prompt_log/YYYY-MM-DD/NNN_<purpose>.md`
per the implementation plan's § 12 contract.
"""
from __future__ import annotations
import os, json, base64, re
from datetime import datetime
from pathlib import Path
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

import dotenv
dotenv.load_dotenv()

BASE = "https://api.sarvam.ai"
KEY = os.environ.get("SARVAM_API_KEY", "")
OFFLINE = os.environ.get("KALAM_OFFLINE", "").lower() in ("1", "true", "yes") or not KEY or KEY.startswith("sk_replace") or KEY == "dummy"

HEADERS = {"api-subscription-key": KEY, "Content-Type": "application/json"}

LOG_ROOT = Path(__file__).resolve().parent.parent / "prompt_log"


# ----- Prompt logging -----------------------------------------------------

def _log_call(purpose: str, payload: dict, response: Any, *, model: str = "", note: str = "") -> None:
    day = datetime.now().strftime("%Y-%m-%d")
    day_dir = LOG_ROOT / day
    day_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(day_dir.glob("*.md"))) + 1
    short = re.sub(r"[^A-Za-z0-9_]+", "_", purpose)[:40] or "call"
    path = day_dir / f"{n:03d}_{short}.md"
    path.write_text(
        f"# {n:03d} — {purpose}\n"
        f"Date/Time: {datetime.now().isoformat()}\n"
        f"Model: {model}\n"
        f"Offline: {OFFLINE}\n\n"
        f"## Payload\n```json\n{json.dumps(payload, indent=2, ensure_ascii=False)[:4000]}\n```\n\n"
        f"## Response\n```\n{str(response)[:4000]}\n```\n\n"
        f"## Note\n{note}\n"
    )


def split_think(text: str) -> tuple[str, str]:
    if "</think>" in text:
        reasoning, answer = text.split("</think>", 1)
        return reasoning.replace("<think>", "").strip(), answer.strip()
    return "", text.strip()


# ----- Chat ---------------------------------------------------------------

def _offline_chat_reply(messages: list[dict], **_) -> dict:
    """Deterministic stub. Returns an empty-JSON extraction by default."""
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if "Slot-filler" in last_user or "extracted" in last_user or "Schema" in last_user:
        stub = {"extracted": {}, "missing_still": [], "clarifications_needed": []}
    elif "audit" in last_user.lower():
        stub = []
    else:
        stub = {"reply": "offline-stub"}
    return {"choices": [{"message": {"content": json.dumps(stub)}}]}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=6))
def _chat_http(body: dict) -> dict:
    r = httpx.post(f"{BASE}/v1/chat/completions", headers=HEADERS, json=body, timeout=120)
    r.raise_for_status()
    return r.json()


def chat(messages, model: str = "sarvam-m", temperature: float = 0.1,
         think: bool = False, max_tokens: int = 2000,
         purpose: str = "chat") -> dict:
    body = {"model": model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens}
    if think and model in ("sarvam-m", "sarvam-30b", "sarvam-105b"):
        body["reasoning_effort"] = "medium"

    if OFFLINE:
        resp = _offline_chat_reply(messages, **body)
        _log_call(purpose, body, resp, model=model, note="offline stub")
        return resp

    try:
        resp = _chat_http(body)
        _log_call(purpose, body, resp, model=model, note="live call")
        return resp
    except Exception as e:
        _log_call(purpose, body, f"ERROR {e}", model=model, note="network fail — falling back to offline stub")
        return _offline_chat_reply(messages, **body)


# ----- Translate ----------------------------------------------------------

# Sarvam supports: en-IN, hi-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, or-IN, pa-IN,
# ta-IN, te-IN, ur-IN (and auto-detect via "auto")
SUPPORTED_LANGS = {
    "en": "en-IN", "hi": "hi-IN", "bn": "bn-IN", "gu": "gu-IN",
    "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "or": "or-IN",
    "pa": "pa-IN", "ta": "ta-IN", "te": "te-IN", "ur": "ur-IN",
    # "hinglish" is treated as a local-only register — never send to translate
}


def _offline_translate(text: str, target: str) -> str:
    prefix = {
        "hi": "[हिंदी] ", "bn": "[বাংলা] ", "gu": "[ગુજરાતી] ", "kn": "[ಕನ್ನಡ] ",
        "ml": "[മലയാളം] ", "mr": "[मराठी] ", "or": "[ଓଡ଼ିଆ] ", "pa": "[ਪੰਜਾਬੀ] ",
        "ta": "[தமிழ்] ", "te": "[తెలుగు] ", "ur": "[اردو] ", "en": "[EN] ",
    }.get(target.split("-")[0], f"[{target}] ")
    return prefix + text


def translate(text: str, target: str, source: str = "auto", purpose: str = "translate") -> str:
    if not text.strip():
        return text
    if target == "hinglish":
        # Hinglish is rendered client-side already as native text
        return text
    lang_key = target.split("-")[0]
    target_code = SUPPORTED_LANGS.get(lang_key, target)
    source_code = "auto" if source == "auto" else SUPPORTED_LANGS.get(source.split("-")[0], source)

    if OFFLINE:
        out = _offline_translate(text, target_code)
        _log_call(purpose, {"input": text, "source": source_code, "target": target_code}, out, model="translate", note="offline stub")
        return out

    body = {"input": text, "source_language_code": source_code,
            "target_language_code": target_code, "mode": "formal"}
    try:
        r = httpx.post(f"{BASE}/translate", headers=HEADERS, json=body, timeout=30)
        r.raise_for_status()
        out = r.json().get("translated_text", text)
        _log_call(purpose, body, out, model="translate", note="live call")
        return out
    except Exception as e:
        _log_call(purpose, body, f"ERROR {e}", model="translate", note="network fail")
        return _offline_translate(text, target_code)


# ----- Speech-to-Text (Sarvam Saaras) ------------------------------------

def transcribe(audio_bytes: bytes, language: str = "hi-IN", purpose: str = "stt") -> str:
    if OFFLINE:
        out = "[offline-stt] namaste main ek kisan hoon"
        _log_call(purpose, {"language": language, "audio_bytes": f"{len(audio_bytes)} bytes"}, out, model="saaras", note="offline stub")
        return out
    files = {"file": ("audio.webm", audio_bytes, "audio/webm")}
    data = {"language_code": language, "model": "saaras:v2"}
    try:
        r = httpx.post(f"{BASE}/speech-to-text",
                       headers={"api-subscription-key": KEY}, files=files,
                       data=data, timeout=60)
        r.raise_for_status()
        out = r.json().get("transcript", "")
        _log_call(purpose, data, out, model="saaras", note="live call")
        return out
    except Exception as e:
        _log_call(purpose, data, f"ERROR {e}", model="saaras", note="network fail")
        return ""


# ----- Text-to-Speech (Sarvam Bulbul) ------------------------------------

def synthesize(text: str, language: str = "hi-IN", speaker: str = "anushka",
               purpose: str = "tts") -> bytes:
    if OFFLINE:
        _log_call(purpose, {"text": text[:200], "language": language}, "offline bytes", model="bulbul", note="offline stub")
        # return 1 sec of silence as WAV placeholder (44-byte header + zeros)
        return b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    body = {"inputs": [text], "target_language_code": language, "speaker": speaker}
    try:
        r = httpx.post(f"{BASE}/text-to-speech", headers=HEADERS, json=body, timeout=60)
        r.raise_for_status()
        audios = r.json().get("audios", [])
        if audios:
            _log_call(purpose, body, f"{len(audios[0])} b64 chars", model="bulbul", note="live")
            return base64.b64decode(audios[0])
    except Exception as e:
        _log_call(purpose, body, f"ERROR {e}", model="bulbul", note="network fail")
    return b""


# ----- Language detect ----------------------------------------------------

def detect_language(text: str) -> str:
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "hi"
    return "en"
