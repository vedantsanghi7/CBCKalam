import sys
import os
sys.path.append(os.path.abspath('conv'))
from sarvam_client import chat

def extract_slots_llm(user_utterance, current_slots):
    schema = """{
  "age": "int", "sex": "M/F/Other", "state": "string", "district_rural_or_urban": "rural/urban", "caste_category": "SC/ST/OBC/General/EWS",
  "annual_income_inr": "int", "land_ownership_type": "owned_cultivable/none/lease", "land_in_own_name": "bool",
  "occupation": "farmer/laborer/student/street_vendor/artisan/other", "profession": "doctor/lawyer/ca/engineer/architect/other", "family_size": "int", "has_aadhaar": "bool", "has_bank_account": "bool",
  "ekyc_done": "bool", "has_pan": "bool", "monthly_pension_inr": "int", "govt_employee_status": "serving/retired/none",
  "income_tax_filed_last_ay": "bool", "is_pregnant": "bool", "has_daughter_under_10": "bool",
  "is_widow": "bool", "is_disabled": "bool", "is_bpl": "bool", "is_institutional_landholder": "bool"
}"""
    prompt = f"""SYSTEM: You are KALAM's slot-filler. Extract values for the schema below from the user's message.
The user may write in English, Hindi, or Hinglish. Be conservative — only extract what is explicitly stated or strongly implied by context.
If a value is implied but not stated, or if it contradicts current slots, handle it properly.
Return ONLY JSON: {{"extracted": {{...}}, "missing_still": [...], "clarifications_needed": [...]}}.
Never invent values. "UNKNOWN" is a valid extraction for any slot.

Schema: {schema}
Current Slots Context: {current_slots}
User Message: "{user_utterance}"
"""
    messages = [
        {"role": "system", "content": "Return ONLY JSON. Do not include markdown elements or any text outside of the JSON."},
        {"role": "user", "content": prompt}
    ]
    try:
        res = chat(messages, model="sarvam-m", temperature=0.1, think=False, max_tokens=1000)
        return res["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

print("Test 1:", extract_slots_llm("21", {"state": "Jharkhand"}))
print("Test 2:", extract_slots_llm("haan mere paas aadhaar hai", {"age": 21, "state": "Jharkhand"}))
