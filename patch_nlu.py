import re
with open("conv/nlu.py", "r") as f:
    text = f.read()

new_extract = """
import sys
import os
import json
from .sarvam_client import chat, split_think

def extract_slots_llm(user_utterance: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
    schema = '''{
  "age": "int", "sex": "M/F/Other", "state": "string", "district_rural_or_urban": "rural/urban", "caste_category": "SC/ST/OBC/General/EWS",
  "annual_income_inr": "int", "land_ownership_type": "owned_cultivable/none/lease", "land_in_own_name": "bool",
  "occupation": "farmer/laborer/student/street_vendor/artisan/other", "profession": "doctor/lawyer/ca/engineer/architect/other", "family_size": "int", "has_aadhaar": "bool", "has_bank_account": "bool",
  "ekyc_done": "bool", "has_pan": "bool", "monthly_pension_inr": "int", "govt_employee_status": "serving/retired/none",
  "income_tax_filed_last_ay": "bool", "is_pregnant": "bool", "has_daughter_under_10": "bool",
  "is_widow": "bool", "is_disabled": "bool", "is_bpl": "bool", "is_institutional_landholder": "bool"
}'''
    prompt = f'''SYSTEM: You are KALAM's slot-filler. Extract values for the schema below from the user's message.
The user may write in English, Hindi, or Hinglish. Be conservative — only extract what is explicitly stated or strongly implied by context.
If a value is implied but not stated, or if it contradicts current slots, handle it properly.
Return ONLY JSON: {{"extracted": {{...}}, "missing_still": [...], "clarifications_needed": [...]}}.
Never invent values. "UNKNOWN" is a valid extraction for any slot.

Schema: {schema}
Current Slots Context: {current_slots}
User Message: "{user_utterance.strip()}"
'''
    messages = [
        {"role": "system", "content": "Return ONLY valid JSON. Do not include markdown elements or any text outside of the JSON."},
        {"role": "user", "content": prompt}
    ]
    try:
        res = chat(messages, model="sarvam-m", temperature=0.1, think=False, max_tokens=1000)
        content = res["choices"][0]["message"]["content"]
        _, content = split_think(content)
        if content.startswith("<think>"):
            content = re.sub(r'<think>.*?(</think>|$)', '', content, flags=re.DOTALL)
        content = content.replace("```json", "").replace("```", "").strip()
        
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return None

def extract_slots(user_utterance: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Extract slots from user utterance. Uses LLM extraction as primary method, falls back to local.\"\"\"
    
    llm_result = extract_slots_llm(user_utterance, current_slots)
    
    if llm_result and "extracted" in llm_result:
        # LLM succeeded
        return {
            "extracted": llm_result.get("extracted", {}),
            "contradictions": llm_result.get("contradictions", []),
            "clarifications_needed": llm_result.get("clarifications_needed", [])
        }
        
    print("Falling back to regex NLU...")
    extracted = extract_slots_local(user_utterance, current_slots)
    return {"extracted": extracted, "contradictions": [], "clarifications_needed": []}
"""

text = re.sub(r'def extract_slots\(user_utterance: str, current_slots: Dict\[str, Any\]\) -> Dict\[str, Any\]:.*?(?=\n# Priority order)', new_extract, text, flags=re.DOTALL)

with open("conv/nlu.py", "w") as f:
    f.write(text)
