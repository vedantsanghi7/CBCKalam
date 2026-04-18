# 348 — nlu_occupation
Date/Time: 2026-04-19T03:09:19.928227
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
      "content": "SYSTEM: You are KALAM's slot-filler. Extract explicitly-stated values for Indian welfare-scheme eligibility. Return ONLY JSON with keys {\"extracted\": {...}, \"contradictions\": [...], \"clarifications_needed\": [...]}. Never invent values. Use UNKNOWN only if the user clearly said they don't know. Slot keys: age, sex, state, district_rural_or_urban, caste_category, annual_income_inr, land_ownership_type, land_in_own_name, occupation, profession, family_size, has_aadhaar, has_bank_account, ekyc_done, has_pan, monthly_pension_inr, govt_employee_status, income_tax_filed_last_ay, is_pregnant, has_daughter_under_10, is_widow, is_disabled, is_bpl, is_institutional_landholder.\nIMPORTANT: we just asked the user about the slot `occupation` — map their answer to that slot when it makes sense.\n\nPrevious known values: {\"age\": 25, \"state\": \"Karnataka\"}\nUser message: \"Laborer / Mazdoor\"\n\nOutput JSON only."
    }
  ],
  "temperature": 0.1,
  "max_tokens": 800
}
```

## Response
```
{'id': '20260418_641cf085-b429-4065-9830-0108e14102e0', 'choices': [{'finish_reason': 'stop', 'index': 0, 'logprobs': None, 'message': {'content': '<think>\nOkay, let\'s tackle this. The user provided a response to the \'occupation\' slot as "Laborer / Mazdoor". I need to map this to the correct slot.\n\nFirst, check the slot keys. The available slots include \'occupation\' and \'profession\'. The user\'s answer is about their job, which is typically captured under \'occupation\'. The term "Mazdoor" is a Hindi word for laborer, so the user is indicating their occupation. There\'s no mention of \'profession\' here, so \'occupation\' is the right slot. No contradictions or clarifications needed since the answer directly relates to the asked slot. The previous values are age and state, which don\'t conflict. So, the extracted value for \'occupation\' should be "Laborer / Mazdoor".\n</think>\n\n{"extracted": {"occupation": "Laborer / Mazdoor"}, "contradictions": [], "clarifications_needed": []}', 'refusal': None, 'reasoning_content': None, 'role': 'assistant', 'tool_calls': []}}], 'created': 1776548358, 'model': 'sarvam-m', 'object': 'chat.completion', 'service_tier': None, 'system_fingerprint': None, 'usage': {'completion_tokens': 194, 'prompt_tokens': 285, 'total_tokens': 479, 'completion_tokens_details': None, 'prompt_tokens_details': None}}
```

## Note
live call
