"""Dialog state helpers — map short answers to the currently-pending slot.

The core bug the original NLU couldn't solve: a user saying "haan" or "yes"
has no lexical signal to identify which slot they're answering. The fix is
contextual — the API tells this module what slot was just asked, and we map
the short answer to that slot.
"""
from __future__ import annotations
import re
from typing import Any, Optional


YES_WORDS = {
    "yes", "y", "haan", "ha", "hn", "ji", "ji haan", "bilkul", "sahi",
    "of course", "han", "ok", "okay", "sure", "true", "han ji",
    "haanji", "theek", "thik", "correct",
}
NO_WORDS = {
    "no", "n", "nahi", "nhi", "nahin", "never", "not really", "false",
    "no way", "galat", "bilkul nahi", "kabhi nahi",
}
UNKNOWN_WORDS = {
    "pata nahi", "patanahi", "nahi pata", "idk", "dunno", "don't know",
    "dont know", "malum nahi", "malumm nahi", "maloom nahi", "no idea",
    "shayad", "maybe", "not sure", "skip", "pass",
}

BOOL_SLOTS = {
    "has_aadhaar", "has_bank_account", "has_pan", "ekyc_done",
    "is_pregnant", "has_daughter_under_10", "is_widow", "is_disabled",
    "is_bpl", "income_tax_filed_last_ay", "is_institutional_landholder",
    "land_in_own_name",
}

SEX_MAP = {
    "m": "M", "male": "M", "man": "M", "aadmi": "M", "ladka": "M", "purush": "M",
    "f": "F", "female": "F", "woman": "F", "aurat": "F", "mahila": "F",
    "ladki": "F", "stree": "F", "other": "other",
}

RURAL_URBAN = {
    "rural": "rural", "gaon": "rural", "village": "rural", "gramin": "rural", "dehaat": "rural",
    "urban": "urban", "shahar": "urban", "sheher": "urban", "city": "urban", "nagar": "urban",
}

OCCUPATIONS = {
    "farmer": "farmer", "kisan": "farmer",
    "laborer": "laborer", "labourer": "laborer", "majdoor": "laborer", "mazdoor": "laborer", "worker": "laborer",
    "vendor": "street_vendor", "hawker": "street_vendor", "rehri": "street_vendor", "street_vendor": "street_vendor",
    "artisan": "artisan", "karigar": "artisan", "craftsman": "artisan",
    "doctor": "doctor", "engineer": "engineer", "lawyer": "lawyer", "vakeel": "lawyer",
    "teacher": "teacher", "housewife": "homemaker", "homemaker": "homemaker",
    "student": "student", "retired": "retired",
    "ca": "ca", "architect": "architect",
    "business": "business", "shopkeeper": "business", "dukandar": "business",
    "salaried": "salaried", "employee": "salaried",
    "other": "other",
}

LAND_MAP = {
    "own": "owned_cultivable", "owned": "owned_cultivable", "apni": "owned_cultivable",
    "haan": "owned_cultivable",  # only when slot is land
    "yes": "owned_cultivable",
    "lease": "lease", "theka": "lease", "tenant": "lease", "batai": "lease",
    "sharecrop": "lease", "rent": "lease",
    "no": "none", "nahi": "none", "none": "none", "koi nahi": "none",
    "no land": "none",
}

CASTE_MAP = {
    "sc": "SC", "st": "ST", "obc": "OBC", "general": "General", "gen": "General",
    "ews": "EWS",
}

def _cleanup(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def parse_income(text: str) -> Optional[int]:
    t = text.lower().replace(",", "")
    # Handle "5 lakh", "50k", etc.
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lac|l\b|crore|cr\b|k\b|thousand)", t)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        if unit.startswith(("lakh", "lac", "l")):
            return int(num * 100_000)
        if unit.startswith(("crore", "cr")):
            return int(num * 10_000_000)
        if unit.startswith(("k", "thousand")):
            return int(num * 1_000)
    m = re.search(r"(?:rs\.?|₹|inr|rupees?)?\s*(\d{3,})", t)
    if m:
        return int(m.group(1))
    # bucket phrases
    if "se kam" in t or "less than" in t or "below" in t or "<" in t:
        mnum = re.search(r"(\d+)", t)
        if mnum:
            return max(0, int(mnum.group(1)) - 1)
    return None


def apply_to_pending_slot(utterance: str, pending_slot: Optional[str]) -> dict[str, Any]:
    """Interpret a short answer in the context of the slot that was just asked."""
    if not pending_slot:
        return {}
    t = _cleanup(utterance)
    out: dict[str, Any] = {}

    # Yes/No answers
    if t in YES_WORDS:
        if pending_slot in BOOL_SLOTS:
            out[pending_slot] = True
            if pending_slot == "land_in_own_name":
                out.setdefault("land_ownership_type", "owned_cultivable")
        elif pending_slot == "land_ownership_type":
            out["land_ownership_type"] = "owned_cultivable"
            out["land_in_own_name"] = True
        elif pending_slot == "govt_employee_status":
            out["govt_employee_status"] = "serving"
        return out
    if t in NO_WORDS:
        if pending_slot in BOOL_SLOTS:
            out[pending_slot] = False
            if pending_slot in ("is_pregnant", "has_daughter_under_10", "is_widow"):
                # ensure none triggers gender auto-infer later
                pass
        elif pending_slot == "land_ownership_type":
            out["land_ownership_type"] = "none"
            out["land_in_own_name"] = False
        elif pending_slot == "monthly_pension_inr":
            out["monthly_pension_inr"] = 0
        elif pending_slot == "govt_employee_status":
            out["govt_employee_status"] = "none"
        return out
    if t in UNKNOWN_WORDS or t.startswith("pata nahi") or t.startswith("don't know"):
        out[pending_slot] = "UNKNOWN"
        return out

    # Slot-specific parsing
    if pending_slot == "age":
        m = re.search(r"\d{1,3}", t)
        if m:
            v = int(m.group())
            if 0 < v < 120:
                out["age"] = v
        return out

    if pending_slot == "sex":
        for k, v in SEX_MAP.items():
            if re.search(rf"\b{k}\b", t):
                out["sex"] = v
                return out

    if pending_slot == "state":
        # Return raw-ish state name; extractor also has a map, but we let NLU decide.
        out["state"] = utterance.strip().title()
        return out

    if pending_slot == "district_rural_or_urban":
        for k, v in RURAL_URBAN.items():
            if k in t:
                out["district_rural_or_urban"] = v
                return out

    if pending_slot == "occupation":
        for k, v in OCCUPATIONS.items():
            if re.search(rf"\b{k}\b", t):
                out["occupation"] = v
                if v in ("doctor", "engineer", "lawyer", "ca", "architect"):
                    out["profession"] = v
                return out
        # Numeric option ("1", "2", "3", "4")
        num_map = {"1": "farmer", "2": "laborer", "3": "street_vendor", "4": "other"}
        if t in num_map:
            out["occupation"] = num_map[t]
            return out

    if pending_slot == "caste_category":
        for k, v in CASTE_MAP.items():
            if re.search(rf"\b{k}\b", t):
                out["caste_category"] = v
                return out

    if pending_slot == "annual_income_inr":
        v = parse_income(t)
        if v is not None:
            out["annual_income_inr"] = v
            return out

    if pending_slot == "monthly_pension_inr":
        if "no" in t or "nahi" in t or "koi nahi" in t or "zero" in t or t == "0":
            out["monthly_pension_inr"] = 0
            return out
        v = parse_income(t)
        if v is not None:
            out["monthly_pension_inr"] = v
            return out

    if pending_slot == "family_size":
        m = re.search(r"\d+", t)
        if m:
            out["family_size"] = int(m.group())
        return out

    if pending_slot == "land_ownership_type":
        for k, v in LAND_MAP.items():
            if k in t:
                out["land_ownership_type"] = v
                out["land_in_own_name"] = (v == "owned_cultivable")
                return out

    if pending_slot == "govt_employee_status":
        if "retired" in t or "sewaniwritt" in t:
            out["govt_employee_status"] = "retired"
        elif "serving" in t or "karyarat" in t or "current" in t:
            out["govt_employee_status"] = "serving"
        elif "not" in t or "nahi" in t or "none" in t:
            out["govt_employee_status"] = "none"
        return out

    return out


def reply_register(utterance: str) -> str:
    """Very rough detection: Hinglish if we see both scripts/hints, Hindi if mostly Hindi."""
    t = utterance.lower()
    hindi_hints = any(w in t for w in ["haan", "nahi", "aap", "mera", "kya", "kaun", "kahaan",
                                        "saal", "zameen", "khata", "aadhar"])
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in utterance)
    if has_devanagari:
        return "hi"
    if hindi_hints:
        return "hinglish"
    return "en"
