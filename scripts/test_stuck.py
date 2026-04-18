import requests, json

BASE = "http://127.0.0.1:8000"
SID = "debug_stuck_001"

turns = [
    "mai jharkhand se hu",
    "21",
    "student hu",
    "gaon mein rehta hu",
    "male",
    "haan",       # aadhaar - yes
    "haan",       # should be bank account - but might get stuck here
    "haan",       # another haan
]

for t in turns:
    r = requests.post(f"{BASE}/session/{SID}/turn", json={"utterance": t})
    d = r.json()
    print(f"USER: {t}")
    print(f"  BOT: {d.get('reply')}")
    print(f"  SLOTS: {d.get('slots_known')}")
    print(f"  MISSING: {d.get('slots_missing', [])[:5]}")
    print()
