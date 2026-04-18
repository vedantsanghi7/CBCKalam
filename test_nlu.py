from conv.nlu import extract_slots

existing_slots = {"state": "Jharkhand"}
result = extract_slots("21", existing_slots)
print("Result of extract_slots:", result)
