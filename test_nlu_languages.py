from conv.nlu import extract_slots

current_slots = {"age": 21, "state": "Jharkhand", "occupation": "student"}

prompts = [
    "i am an artisan",
    "kheti karta hu",
    "meri umar byaais hai",  # '22' in hindi
    "divyang hu",
    "female from odisha, age is 45 and I make 3000 a month",
    "nothing else"
]

for p in prompts:
    print(f"User: {p}")
    parsed = extract_slots(p, current_slots)
    print(f"Extracted: {parsed['extracted']}")
    print("-" * 50)
