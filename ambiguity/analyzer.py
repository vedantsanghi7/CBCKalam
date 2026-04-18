import os
import yaml

def analyze_schemes(schemes_path="schemes"):
    schemes = []
    for file in os.listdir(schemes_path):
        if file.endswith(".yaml"):
            with open(os.path.join(schemes_path, file), "r") as f:
                schemes.append(yaml.safe_load(f))
                
    overlaps = []
    contradictions = []
    undefined = set()
    
    for s1 in schemes:
        for r1 in s1.get("rules", []):
            for flag in r1.get("ambiguity_flags", []):
                if flag == "UNDEFINED_TERM":
                    undefined.add(f"{s1['scheme_id']} - {r1['id']}: {r1.get('ambiguity_notes', 'Undefined term')}")
        
        for p in s1.get("overlaps_with", []):
            overlaps.append(f"{s1['scheme_id']} overlaps with {p['scheme']} ({p.get('nature', '')})")
            
    print("Overlap Analysis:", overlaps)
    print("Undefined Terms:", list(undefined))

if __name__ == "__main__":
    analyze_schemes()
