"""Natural-language slot filler.

Strategy (in order):

1. If there is a `pending_slot` (i.e. we just asked a targeted question),
   first try to interpret the user's answer *in that slot's context* via
   `dialog.apply_to_pending_slot`. Short answers like "haan", "yes", "21",
   "Rajasthan" are unambiguous only in context.

2. Then run the local regex extractor across the whole utterance — it often
   extracts multiple slots in one sentence ("main Rajasthan se hoon, kisan
   hoon, 42 saal ka").

3. If online, fire the Sarvam-M LLM slot-filler for any slots still missing
   or ambiguous. The LLM output is merged on top, but NEVER overwrites a
   value we already extracted locally unless the LLM explicitly disagrees
   (and then we log a contradiction).
"""
from __future__ import annotations
import json, re, os
from typing import Any, Dict, List, Optional

from .dialog import apply_to_pending_slot, BOOL_SLOTS
from . import sarvam_client
from .sarvam_client import split_think


# ----- Static maps (shared with dialog.py where applicable) --------------

STATES_MAP = {k: v for k, v in {
    "rajasthan": "Rajasthan", "rj": "Rajasthan",
    "maharashtra": "Maharashtra", "mh": "Maharashtra",
    "up": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh",
    "mp": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh",
    "bihar": "Bihar", "jharkhand": "Jharkhand",
    "karnataka": "Karnataka", "tamil nadu": "Tamil Nadu", "tn": "Tamil Nadu",
    "kerala": "Kerala", "gujarat": "Gujarat", "gj": "Gujarat",
    "punjab": "Punjab", "haryana": "Haryana",
    "west bengal": "West Bengal", "wb": "West Bengal",
    "odisha": "Odisha", "orissa": "Odisha", "delhi": "Delhi", "ncr": "Delhi",
    "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
    "telangana": "Telangana", "assam": "Assam",
    "chhattisgarh": "Chhattisgarh", "goa": "Goa",
    "himachal pradesh": "Himachal Pradesh", "hp": "Himachal Pradesh",
    "jammu and kashmir": "Jammu and Kashmir", "jk": "Jammu and Kashmir",
    "uttarakhand": "Uttarakhand", "uk": "Uttarakhand",
    "tripura": "Tripura", "meghalaya": "Meghalaya",
    "manipur": "Manipur", "mizoram": "Mizoram",
    "nagaland": "Nagaland", "sikkim": "Sikkim",
    "arunachal pradesh": "Arunachal Pradesh", "ladakh": "Ladakh",
    "puducherry": "Puducherry", "chandigarh": "Chandigarh",
}.items()}

OCCUPATION_KEYWORDS = {
    "farmer": "farmer", "kisan": "farmer", "farming": "farmer", "kheti": "farmer",
    "laborer": "laborer", "labourer": "laborer", "majdoor": "laborer",
    "mazdoor": "laborer", "worker": "laborer",
    "vendor": "street_vendor", "hawker": "street_vendor", "rehri": "street_vendor",
    "street vendor": "street_vendor",
    "artisan": "artisan", "karigar": "artisan", "craftsman": "artisan",
    "doctor": "doctor", "engineer": "engineer", "lawyer": "lawyer", "vakeel": "lawyer",
    "teacher": "teacher", "housewife": "homemaker", "ghar": "homemaker",
    "homemaker": "homemaker",
    "student": "student", "retired": "retired",
    "ca": "ca", "chartered accountant": "ca", "architect": "architect",
    "business": "business", "dukandar": "business", "shopkeeper": "business",
    "salaried": "salaried", "employee": "salaried",
}

ALL_SLOTS = [
    "age", "sex", "state", "district_rural_or_urban", "caste_category",
    "annual_income_inr", "land_ownership_type", "land_in_own_name",
    "occupation", "profession", "family_size", "has_aadhaar", "has_bank_account",
    "ekyc_done", "has_pan", "monthly_pension_inr", "govt_employee_status",
    "income_tax_filed_last_ay", "is_pregnant", "has_daughter_under_10",
    "is_widow", "is_disabled", "is_bpl", "is_institutional_landholder",
]

SLOT_PRIORITY = [
    "age", "state", "occupation", "district_rural_or_urban",
    "sex", "has_aadhaar", "has_bank_account", "annual_income_inr",
    "caste_category", "land_ownership_type", "income_tax_filed_last_ay",
    "monthly_pension_inr", "is_bpl", "family_size",
    "has_pan", "ekyc_done", "is_widow", "is_pregnant",
    "has_daughter_under_10", "is_disabled", "govt_employee_status",
]

SLOT_QUESTIONS = {
    "age": {"question": "What is your age?", "options": None},
    "state": {"question": "Which state do you live in?", "options": None},
    "occupation": {"question": "What is your occupation?",
                   "options": ["Farmer", "Laborer", "Vendor", "Other"]},
    "district_rural_or_urban": {"question": "Do you live in a rural (village) or urban (city) area?",
                                "options": ["Rural", "Urban"]},
    "sex": {"question": "What is your gender?",
            "options": ["Male", "Female", "Other"]},
    "has_aadhaar": {"question": "Do you have an Aadhaar card?",
                    "options": ["Yes", "No"]},
    "has_bank_account": {"question": "Do you have a bank account?",
                         "options": ["Yes", "No"]},
    "annual_income_inr": {"question": "What is your annual income?",
                          "options": ["Less than ₹50,000", "₹50,000 - ₹2,00,000",
                                      "₹2,00,000 - ₹5,00,000", "₹5,00,000+"]},
    "caste_category": {"question": "What is your caste category?",
                       "options": ["SC", "ST", "OBC", "General", "EWS"]},
    "land_ownership_type": {"question": "Do you own land, lease it, or have no land?",
                            "options": ["Own land", "Leased", "No land"]},
    "income_tax_filed_last_ay": {"question": "Did you file income tax last year?",
                                 "options": ["Yes", "No"]},
    "monthly_pension_inr": {"question": "Do you receive a pension? How much?",
                            "options": ["No pension", "Less than ₹10,000", "₹10,000+"]},
    "is_bpl": {"question": "Do you fall under the BPL (Below Poverty Line) category?",
               "options": ["Yes", "No", "Don't know"]},
    "family_size": {"question": "How many members are in your family?", "options": None},
    "has_pan": {"question": "Do you have a PAN card?",
                "options": ["Yes", "No"]},
    "ekyc_done": {"question": "Is your Aadhaar eKYC completed?",
                  "options": ["Yes", "No", "Don't know"]},
    "is_widow": {"question": "Are you a widow?",
                 "options": ["Yes", "No"]},
    "is_pregnant": {"question": "Are you pregnant or have recently delivered?",
                    "options": ["Yes", "No"]},
    "has_daughter_under_10": {"question": "Do you have a daughter under 10 years old?",
                              "options": ["Yes", "No"]},
    "is_disabled": {"question": "Are you disabled (Divyang)?",
                    "options": ["Yes", "No"]},
    "govt_employee_status": {"question": "Are you a government employee?",
                             "options": ["No", "Serving", "Retired"]},
}


# ----- Local regex extractor ---------------------------------------------

def extract_slots_local(utterance: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
    text = utterance.lower().strip()
    extracted: Dict[str, Any] = {}

    # Age: standalone number, "X saal", "age X"
    for p in [r"(?:i am|main|meri umar|umar|umra|age)\s*(?:is|hai|h|:)?\s*(\d{1,3})",
              r"(\d{1,3})\s*(?:saal|sal|year|years|yr|yrs)"]:
        m = re.search(p, text)
        if m and 0 < int(m.group(1)) < 120:
            extracted["age"] = int(m.group(1))
            break
    if "age" not in extracted and text.isdigit():
        v = int(text)
        if 0 < v < 120:
            extracted["age"] = v

    # Sex
    if re.search(r"\b(female|woman|aurat|mahila|ladki|stree)\b", text):
        extracted["sex"] = "F"
    elif re.search(r"\b(male|man|aadmi|ladka|purush)\b", text):
        extracted["sex"] = "M"

    # State
    for key, st in STATES_MAP.items():
        if re.search(r"\b" + re.escape(key) + r"\b", text):
            extracted["state"] = st
            break

    # Rural/urban
    if re.search(r"\b(rural|gaon|village|gramin|dehaat)\b", text):
        extracted["district_rural_or_urban"] = "rural"
    elif re.search(r"\b(urban|shahar|sheher|city|nagar)\b", text):
        extracted["district_rural_or_urban"] = "urban"

    # Occupation
    for kw, occ in OCCUPATION_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            extracted["occupation"] = occ
            if occ in ("doctor", "engineer", "lawyer", "ca", "architect"):
                extracted["profession"] = occ
            break

    # Land
    if re.search(r"\b(own land|apni zameen|owned land|own farm|owner of)\b", text):
        extracted["land_ownership_type"] = "owned_cultivable"
        extracted["land_in_own_name"] = True
    elif re.search(r"\b(lease|theka|theke|tenant|sharecrop|batai|rent)\b", text):
        extracted["land_ownership_type"] = "lease"
        extracted["land_in_own_name"] = False
    elif re.search(r"\b(no land|koi zameen nahi|zameen nahi hai|landless)\b", text):
        extracted["land_ownership_type"] = "none"
        extracted["land_in_own_name"] = False

    # Boolean flags with negation awareness
    bool_flags = {
        "aadhaar": "has_aadhaar", "aadhar": "has_aadhaar",
        "bank account": "has_bank_account", "khata": "has_bank_account",
        "pan": "has_pan", "pan card": "has_pan",
        "pregnant": "is_pregnant", "garbhvati": "is_pregnant",
        "widow": "is_widow", "vidhwa": "is_widow",
        "disabled": "is_disabled", "divyang": "is_disabled", "viklang": "is_disabled",
        "bpl": "is_bpl", "below poverty line": "is_bpl",
        "ekyc": "ekyc_done",
        "daughter": "has_daughter_under_10", "beti": "has_daughter_under_10",
    }
    for kw, slot in bool_flags.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            neg = re.search(r"(no|nahi|without|don't have|dont have|never|not)\s+(?:\w+\s+){0,3}"
                            + re.escape(kw), text)
            extracted[slot] = not bool(neg)

    # Income
    im = re.search(r"(?:earn|earning|income|kamai|amdani|salary)\s*(?:is|hai|of|:)?\s*"
                   r"(?:rs\.?|₹|rupees|inr)?\s*(\d[\d,]*)\s*(lakh|lac|k|crore)?", text)
    if im:
        num = int(im.group(1).replace(",", ""))
        unit = (im.group(2) or "").strip()
        if unit.startswith("lakh") or unit.startswith("lac"):
            num *= 100_000
        elif unit == "k":
            num *= 1_000
        elif unit.startswith("crore"):
            num *= 10_000_000
        extracted["annual_income_inr"] = num

    # Pension
    if re.search(r"(no|nahi|without|don't have|dont have|zero|koi\s+nahi|0)\s+(?:\w+\s+){0,3}pension", text):
        extracted["monthly_pension_inr"] = 0
    elif re.search(r"pension\s+nahi|koi\s+pension\s+nahi", text):
        extracted["monthly_pension_inr"] = 0

    # Income tax
    if re.search(r"(income tax|itr|tax file|tax paid|tax bhara|filed tax|pay tax|paid tax)", text):
        neg = re.search(r"(no|nahi|don't|dont|never|not)\s+(?:\w+\s+){0,3}"
                        r"(income tax|itr|tax file|tax paid|tax bhara|filed tax|pay tax|paid tax)", text)
        extracted["income_tax_filed_last_ay"] = not bool(neg)

    # Caste
    for cat in ["sc", "st", "obc", "general", "ews"]:
        if re.search(r"\b" + cat + r"\b", text):
            extracted["caste_category"] = cat.upper() if cat != "general" else "General"
            break

    # Family
    fm = re.search(r"(?:family|parivar)\s*(?:of|mein|me|size|:)?\s*(\d+)", text)
    if fm:
        extracted["family_size"] = int(fm.group(1))

    # Govt employee
    if re.search(r"(govt employee|sarkari naukri|government job|government employee|sarkari employee)", text):
        extracted["govt_employee_status"] = "serving"
    elif re.search(r"(retired|sewaniwritt|pensioner)", text):
        extracted["govt_employee_status"] = "retired"

    return extracted


# ----- LLM slot filler ---------------------------------------------------

def extract_slots_llm(utterance: str, current_slots: Dict[str, Any],
                      history: List[Dict[str, str]] = None,
                      pending_slot: Optional[str] = None,
                      language: Optional[str] = None) -> Optional[Dict[str, Any]]:
    schema_doc = ", ".join(ALL_SLOTS)
    hist_list = []
    if history:
        for msg in history[-10:]:
            if msg.get("role") != "user" or msg.get("text") != utterance.strip():
                hist_list.append(f"{msg['role'].upper()}: {msg['text']}")
    hist_str = "\n".join(hist_list)
    lang_instruction = "Reply natively in the same language/script as the user's last message."
    if language:
        if language.lower() == "hinglish":
            lang_instruction = "Reply in Hinglish (Hindi written in the Roman/English alphabet). NEVER use Devanagari script."
        else:
            lang_instruction = f"Reply in the '{language}' language."

    prompt = (
        "SYSTEM: You are KALAM, a conversational AI collecting eligibility data for Indian welfare schemes. "
        "Extract explicitly-stated values into a JSON object AND formulate a natural language response to the user. "
        "Never invent values. Use UNKNOWN only if the user clearly said they don't know.\n\n"
        f"Available slots: {schema_doc}\n"
        f"Previously extracted slots: {json.dumps(current_slots, ensure_ascii=False)}\n\n"
        f"Recent conversation:\n{hist_str}\n"
        f"USER: \"{utterance.strip()}\"\n\n"
        "Return ONLY JSON in this format:\n"
        "{\n"
        "  \"extracted\": { \"slot_name\": \"new or updated value\" },\n"
        f"  \"next_message\": \"Friendly response confirming info and asking for important missing slots. {lang_instruction} If you have enough info, say you are checking schemes.\"\n"
        "}"
    )
    msgs = [
        {"role": "system", "content": "Return ONLY valid JSON, no markdown."},
        {"role": "user", "content": prompt},
    ]
    try:
        r = sarvam_client.chat(msgs, model="sarvam-m", temperature=0.1,
                               think=False, max_tokens=800,
                               purpose=f"nlu_{pending_slot or 'open'}")
        content = r["choices"][0]["message"]["content"]
        _, content = split_think(content)
        content = re.sub(r"```json|```", "", content).strip()
        return json.loads(content)
    except Exception as e:
        print(f"[nlu] LLM extraction error: {e}")
        return None


def extract_slots(utterance: str, current_slots: Dict[str, Any],
                  history: List[Dict[str, Any]] = None,
                  pending_slot: Optional[str] = None,
                  language: Optional[str] = None) -> Dict[str, Any]:
    """Main entry. Merges pending-slot → local regex → LLM (online only)."""
    merged: Dict[str, Any] = {}

    # 1. Pending-slot context (wins for short answers)
    if pending_slot:
        merged.update(apply_to_pending_slot(utterance, pending_slot))

    # 2. Local regex over the full utterance
    local = extract_slots_local(utterance, current_slots)
    for k, v in local.items():
        merged.setdefault(k, v)

    # 3. LLM — only if online AND we still have room to discover more.
    if not sarvam_client.OFFLINE:
        llm = extract_slots_llm(utterance, current_slots, history, pending_slot, language)
        if llm and isinstance(llm, dict):
            for k, v in (llm.get("extracted") or {}).items():
                if v in (None, "", "UNKNOWN"):
                    continue
                merged.setdefault(k, v)

            # Post-process: coerce booleans
            for k in list(merged.keys()):
                if k in BOOL_SLOTS and isinstance(merged[k], str):
                    v = merged[k].lower()
                    if v in ("true", "yes", "haan"):
                        merged[k] = True
                    elif v in ("false", "no", "nahi"):
                        merged[k] = False
            
            if "land_ownership_type" in merged and "land_in_own_name" not in merged:
                merged["land_in_own_name"] = (merged["land_ownership_type"] == "owned_cultivable")

            if "next_message" in llm:
                return {"extracted": merged, "next_message": llm["next_message"], "contradictions": [], "clarifications_needed": []}

    # Post-process: coerce booleans
    for k in list(merged.keys()):
        if k in BOOL_SLOTS and isinstance(merged[k], str):
            v = merged[k].lower()
            if v in ("true", "yes", "haan"):
                merged[k] = True
            elif v in ("false", "no", "nahi"):
                merged[k] = False

    # If we inferred land_ownership_type and user hasn't given land_in_own_name, sync it
    if "land_ownership_type" in merged and "land_in_own_name" not in merged:
        merged["land_in_own_name"] = (merged["land_ownership_type"] == "owned_cultivable")

    return {"extracted": merged, "contradictions": [], "clarifications_needed": []}


def get_next_question(missing_slot: str) -> Dict[str, Any]:
    if missing_slot in SLOT_QUESTIONS:
        return SLOT_QUESTIONS[missing_slot]
    return {"question": f"Aapki {missing_slot.replace('_', ' ')} kya hai?", "options": None}


def get_most_informative_missing(current_slots: Dict[str, Any]) -> Optional[str]:
    for slot in SLOT_PRIORITY:
        if slot not in current_slots or current_slots.get(slot) == "UNKNOWN":
            return slot
    return None
