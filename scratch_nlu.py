def extract_slots_local(utterance: str, current_slots: dict) -> dict:
    """Enhanced regex-based local slot extraction."""
    import re
    text = utterance.lower().strip()
    extracted = {}

    # Age
    for p in [r'(?:i am|main|meri umar|age|umar|umra)\s*(?:is|hai|h|:)?\s*(\d{1,3})', r'(\d{1,3})\s*(?:saal|sal|year|years|yr|yrs)']:
        m = re.search(p, text)
        if m:
            if 0 < int(m.group(1)) < 120:
                extracted["age"] = int(m.group(1))
                break

    # Sex
    if re.search(r'\b(female|woman|aurat|mahila|ladki|stree|f)\b', text):
        extracted["sex"] = "F"
    elif re.search(r'\b(male|man|aadmi|ladka|purush|m)\b', text):
        extracted["sex"] = "M"

    # State mapping (using STATES_MAP from outer scope in nlu.py, but we'll re-declare just for test)
    # Assume it's available
    
    # Rural/Urban
    if re.search(r'\b(rural|gaon|village|gramin|dehaat)\b', text):
        extracted["district_rural_or_urban"] = "rural"
    elif re.search(r'\b(urban|shahar|sheher|city|nagar)\b', text):
        extracted["district_rural_or_urban"] = "urban"

    # Occupation / Profession
    # Will use OCCUPATION_KEYWORDS from outer scope

    # Land ownership
    if re.search(r'\b(own\s+\d+|own land|apni zameen|own farm|owned|owner of)\b', text):
        extracted["land_ownership_type"] = "owned_cultivable"
        extracted["land_in_own_name"] = True
    elif re.search(r'\b(lease|theka|tenant|no land|koi zameen nahi)\b', text):
        extracted["land_ownership_type"] = "none"
        extracted["land_in_own_name"] = False

    # Boolean flags
    flags = {
        "aadhaar": "has_aadhaar", "aadhar": "has_aadhaar",
        "bank account": "has_bank_account", "bank": "has_bank_account", "khata": "has_bank_account",
        "pan": "has_pan",
        "pregnant": "is_pregnant", "garbhvati": "is_pregnant",
        "widow": "is_widow", "vidhwa": "is_widow",
        "disabled": "is_disabled", "divyang": "is_disabled", "viklang": "is_disabled",
        "bpl": "is_bpl", "garib": "is_bpl", "below poverty line": "is_bpl",
        "ekyc": "ekyc_done",
        "daughter": "has_daughter_under_10", "beti": "has_daughter_under_10",
    }
    for kw, slot in flags.items():
        if kw in text:
            neg_pattern = r'(no|nahi|without|don\'t have|dont have|not)\s+(?:\w+\s+){0,3}' + kw
            if re.search(neg_pattern, text):
                extracted[slot] = False
            else:
                extracted[slot] = True

    # Income
    inc_m = re.search(r'(?:making|earn|earning|income|kamai|amdani)\s*(?:is|hai|:)?\s*(?:rs\.?|₹|rupees|inr|of)?\s*(\d[\d,]*)', text)
    if inc_m:
        extracted["annual_income_inr"] = int(inc_m.group(1).replace(",", ""))

    # Pension
    if re.search(r'(?:no|not|nahi|without|don\'t have|dont have|zero|0)\s+(?:\w+\s+){0,2}pension', text):
        extracted["monthly_pension_inr"] = 0
    else:
        pen_m = re.search(r'(?:pension)\s*(?:is|hai|of|:)?\s*(?:rs\.?|₹|rupees|inr)?\s*(\d[\d,]*)', text)
        if pen_m:
            extracted["monthly_pension_inr"] = int(pen_m.group(1).replace(",", ""))

    # Income tax
    if re.search(r'(income tax|itr|tax file|tax paid|tax bhara|filed tax|pay tax|paid tax)', text):
        if re.search(r'(no|nahi|don\'t|dont|never)\s+(?:\w+\s+){0,3}(income tax|itr|tax file|tax paid|tax bhara|filed tax|pay tax|paid tax)', text):
            extracted["income_tax_filed_last_ay"] = False
        else:
            extracted["income_tax_filed_last_ay"] = True

    # Caste
    for cat in ["sc", "st", "obc", "general", "ews"]:
        if re.search(r'\b' + cat + r'\b', text):
            extracted["caste_category"] = cat.upper()
            break

    # Family size
    fam_m = re.search(r'(?:family|parivar)\s*(?:of|mein|me|size|:)?\s*(\d+)', text)
    if fam_m:
        extracted["family_size"] = int(fam_m.group(1))

    # Government employee
    if re.search(r'(govt employee|sarkari naukri|government job|government employee)', text):
        extracted["govt_employee_status"] = "serving"
    elif re.search(r'(retired|sewaniwritt)', text):
        extracted["govt_employee_status"] = "retired"

    return extracted

print(extract_slots_local("I am a 40 year old farmer from up making 30000 rupees a yr and i have pan and aadhaar but no kisan credit card and I own 2 acres of land. I filed tax last year and i have bank account but no pension", {}))

