#!/usr/bin/env python3
"""Run all 10 adversarial edge-case profiles through the engine and print results."""
import yaml, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import Scheme, Rule
from engine.evaluator import evaluate_scheme

def load_schemes():
    schemes = []
    for f in sorted(os.listdir("schemes")):
        if f.endswith(".yaml"):
            with open(os.path.join("schemes", f)) as fh:
                data = yaml.safe_load(fh)
            data["rules"] = [Rule(**r) for r in data.get("rules", [])]
            data["launched"] = str(data.get("launched", ""))
            schemes.append(Scheme(**{k: v for k, v in data.items() if k in Scheme.model_fields}))
    return schemes

def run():
    with open("edge_cases/profiles.yaml") as f:
        profiles = yaml.safe_load(f)["profiles"]
    schemes = load_schemes()
    
    print("# Edge Case Evaluation Results\n")
    print(f"> Engine evaluated **{len(profiles)} adversarial profiles** against **{len(schemes)} schemes**.\n")
    
    for p in profiles:
        print(f"---\n\n## {p['name']}\n")
        print(f"**ID:** `{p['id']}`  ")
        print(f"**Adversarial Angle:** {p['adversarial_angle'].strip()}\n")
        
        quals, almosts, dnqs, uncs = [], [], [], []
        for s in schemes:
            try:
                r = evaluate_scheme(s, p["data"])
                entry = f"- **{s.name}** (`{s.scheme_id}`) — confidence: {r.confidence:.0%}"
                if r.missing_inputs:
                    entry += f" | missing: {', '.join(r.missing_inputs[:3])}"
                if r.status == "QUALIFIES": quals.append(entry)
                elif r.status == "ALMOST_QUALIFIES": almosts.append(entry)
                elif r.status == "DOES_NOT_QUALIFY": dnqs.append(entry)
                else: uncs.append(entry)
            except Exception as e:
                pass
        
        print(f"| Status | Count |")
        print(f"|--------|-------|")
        print(f"| ✅ QUALIFIES | {len(quals)} |")
        print(f"| 🟡 ALMOST_QUALIFIES | {len(almosts)} |")
        print(f"| ❌ DOES_NOT_QUALIFY | {len(dnqs)} |")
        print(f"| ❓ UNCERTAIN | {len(uncs)} |")
        print()
        
        if quals:
            print("### ✅ Qualifies\n")
            print("\n".join(quals))
            print()
        if almosts:
            print("### 🟡 Almost Qualifies\n")
            print("\n".join(almosts))
            print()
        if dnqs[:5]:
            print(f"### ❌ Does Not Qualify (showing {min(5, len(dnqs))} of {len(dnqs)})\n")
            print("\n".join(dnqs[:5]))
            print()
        if uncs:
            print("### ❓ Uncertain\n")
            print("\n".join(uncs))
            print()

if __name__ == "__main__":
    run()
