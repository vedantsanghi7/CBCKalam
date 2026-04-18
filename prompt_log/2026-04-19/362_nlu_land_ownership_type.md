# 362 — nlu_land_ownership_type
Date/Time: 2026-04-19T03:23:06.549136
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
      "content": "SYSTEM: You are KALAM's slot-filler. Extract explicitly-stated values for Indian welfare-scheme eligibility. Return ONLY JSON with keys {\"extracted\": {...}, \"contradictions\": [...], \"clarifications_needed\": [...]}. Never invent values. Use UNKNOWN only if the user clearly said they don't know. Slot keys: age, sex, state, district_rural_or_urban, caste_category, annual_income_inr, land_ownership_type, land_in_own_name, occupation, profession, family_size, has_aadhaar, has_bank_account, ekyc_done, has_pan, monthly_pension_inr, govt_employee_status, income_tax_filed_last_ay, is_pregnant, has_daughter_under_10, is_widow, is_disabled, is_bpl, is_institutional_landholder.\nIMPORTANT: we just asked the user about the slot `land_ownership_type` — map their answer to that slot when it makes sense.\n\nPrevious known values: {\"age\": 25, \"state\": \"Jharkhand\", \"occupation\": \"farmer\", \"district_rural_or_urban\": \"rural\", \"sex\": \"M\", \"has_aadhaar\": true, \"has_bank_account\": true, \"annual_income_inr\": 50000, \"caste_category\": \"SC\"}\nUser message: \"Haan, apni zameen\"\n\nOutput JSON only."
    }
  ],
  "temperature": 0.1,
  "max_tokens": 800
}
```

## Response
```
{'id': '20260418_c18165cb-0324-4de9-92b6-f980526a8d51', 'choices': [{'finish_reason': 'stop', 'index': 0, 'logprobs': None, 'message': {'content': '<think>\nOkay, let\'s tackle this. The user\'s message is "Haan, apni zameen," which translates to "Yes, my own land." The previous context mentions that the user was asked about \'land_ownership_type\'. The key here is to map their answer to the correct slot.\n\nThe slot in question is \'land_ownership_type\'. The user\'s response indicates that the land is owned by them. So, the value should be "own". I need to check if there are any contradictions or clarifications needed. Since the user clearly states it\'s their own land, there\'s no contradiction. Also, no additional info is needed because the answer is straightforward. The other slots like \'land_in_own_name\' might be relevant, but the user didn\'t mention the name, so it\'s not addressed here. The extracted value is "own" for \'land_ownership_type\'. No contradictions or clarifications needed here.\n</think>\n\n{"extracted": {"land_ownership_type": "own"}, "contradictions": [], "clarifications_needed": []}', 'refusal': None, 'reasoning_content': None, 'role': 'assistant', 'tool_calls': []}}], 'created': 1776549184, 'model': 'sarvam-m', 'object': 'chat.completion', 'service_tier': None, 'system_fingerprint': None, 'usage': {'completion_tokens': 225, 'prompt_tokens': 358, 'total_tokens': 583, 'completion_tokens_details': None, 'prompt_tokens_details': None}}
```

## Note
live call
