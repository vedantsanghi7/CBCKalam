# 021 — nlu_caste_category
Date/Time: 2026-04-18T23:09:48.140705
Model: sarvam-m
Offline: False

## Payload
```json
{
  "model": "sarvam-m",
  "messages": [
    {
      "role": "system",
      "content": "Return ONLY valid JSON, no markdown."
    },
    {
      "role": "user",
      "content": "SYSTEM: You are KALAM's slot-filler. Extract explicitly-stated values for Indian welfare-scheme eligibility. Return ONLY JSON with keys {\"extracted\": {...}, \"contradictions\": [...], \"clarifications_needed\": [...]}. Never invent values. Use UNKNOWN only if the user clearly said they don't know. Slot keys: age, sex, state, district_rural_or_urban, caste_category, annual_income_inr, land_ownership_type, land_in_own_name, occupation, profession, family_size, has_aadhaar, has_bank_account, ekyc_done, has_pan, monthly_pension_inr, govt_employee_status, income_tax_filed_last_ay, is_pregnant, has_daughter_under_10, is_widow, is_disabled, is_bpl, is_institutional_landholder.\nIMPORTANT: we just asked the user about the slot `caste_category` — map their answer to that slot when it makes sense.\n\nPrevious known values: {\"age\": 25, \"state\": \"Jharkhand\", \"occupation\": \"laborer\", \"district_rural_or_urban\": \"rural\", \"sex\": \"M\", \"has_aadhaar\": true, \"has_bank_account\": false, \"annual_income_inr\": 50000}\nUser message: \"ST\"\n\nOutput JSON only."
    }
  ],
  "temperature": 0.1,
  "max_tokens": 800
}
```

## Response
```
{'id': '20260418_666bd72b-1b86-4272-a34f-9ffe60c672a9', 'choices': [{'finish_reason': 'stop', 'index': 0, 'logprobs': None, 'message': {'content': '<think>\nOkay, let\'s tackle this. The user provided the answer "ST" when asked about caste_category. The task is to map this to the appropriate slot.\n\nFirst, I need to check if "ST" corresponds to any known caste category in Indian welfare schemes. ST typically stands for Scheduled Tribe, which is a recognized category. So, the caste_category should be "ST".\n\nLooking at the previous values, there\'s no mention of caste before, so this is new information. The user didn\'t mention any contradictions or uncertainties here. The answer is straightforward. No need for clarifications because "ST" is a clear indicator of Scheduled Tribe. So, the extracted value is "ST", and there are no contradictions or clarifications needed.\n</think>\n\n{"extracted": {"caste_category": "ST"}, "contradictions": [], "clarifications_needed": []}', 'refusal': None, 'reasoning_content': None, 'role': 'assistant', 'tool_calls': []}}], 'created': 1776533986, 'model': 'sarvam-m', 'object': 'chat.completion', 'service_tier': None, 'system_fingerprint': None, 'usage': {'completion_tokens': 180, 'prompt_tokens': 341, 'total_tokens': 521, 'completion_tokens_details': None, 'prompt_tokens_details': None}}
```

## Note
live call
