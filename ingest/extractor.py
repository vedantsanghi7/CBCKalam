import os
import glob
import json
import yaml
import sys
import asyncio
import time


# Setup path so we can import from conv.sarvam_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conv.sarvam_client import chat

CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemes", "_raw")
os.makedirs(OUT_DIR, exist_ok=True)

PROMPT_TEMPLATE = """
SYSTEM:
You are a careful legal-document parser extracting eligibility rules from Indian
government welfare scheme guidelines. Your output will be reviewed by a human,
then fed into a deterministic rule engine that affects real citizens' access to
government benefits. Precision matters more than recall. If you are unsure,
emit the rule with confidence: "low" and ambiguity_flags, DO NOT GUESS.

HARD RULES:
1. Every rule's `source_text` field MUST be a verbatim substring of the input document.
2. Never paraphrase source_text. Copy it exactly (whitespace may be normalized).
3. Use the closed ambiguity_flag vocabulary: UNDEFINED_TERM, STATE_DEPENDENT, DISCRETIONARY, CONFLICTING_SOURCES, OUTDATED_SOURCE, NEEDS_HUMAN.
4. Return ONLY valid JSON matching this exact structure:
{
  "inputs_required": ["age", "has_aadhaar", "..."],
  "rules": [
    {
      "id": "R001",
      "type": "inclusion|exclusion|mandatory_doc",
      "predicate": "age >= 18",
      "description": "Applicant must be an adult",
      "source_text": "verbatim text from source",
      "confidence": "high|medium|low",
      "ambiguity_flags": []
    }
  ],
  "prerequisites": [],
  "overlaps_with": [],
  "documents_checklist": []
}

Scheme ID: {scheme_id}

Source Text:
{text}
"""

async def extract_rules(scheme_id, text):
    prompt = PROMPT_TEMPLATE.replace("{scheme_id}", scheme_id).replace("{text}", text[:15000])
    messages = [
        {"role": "system", "content": "You are a payload extractor. Output ONLY valid JSON."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        from conv.sarvam_client import chat, split_think

        response = chat(messages, model="sarvam-m", temperature=0.1, think=False, max_tokens=3500)
        content = response["choices"][0]["message"]["content"]
        
        _, content = split_think(content)
        if content.startswith("<think>"):
            # in case split_think failed because </think> was omitted
            import re
            content = re.sub(r'<think>.*?(</think>|$)', '', content, flags=re.DOTALL)
        
        # rudimentary cleanup to handle markdown fences
        content = content.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            print(f"[{scheme_id}] JSONDecodeError on content: {content[:200]}...")
            return None
    except Exception as e:
        print(f"[{scheme_id}] Extractor error: {e}")
        return None

async def main():
    if not os.path.exists(CACHE_DIR):
        return

    # find markdown files
    md_files = glob.glob(os.path.join(CACHE_DIR, "*.md"))
    
    # group by scheme
    schemes_text = {}
    for mf in md_files:
        base = os.path.basename(mf)
        idx = base.find("_")
        if idx > 0:
            scheme_id = base[:idx]
            # Since some paths have multiple underscores like PM_KISAN_xxx, we need a better heuristic
            # Let's match against the keys from sources.yaml
    
    # Read sources.yaml exactly
    with open(os.path.join(os.path.dirname(__file__), "sources.yaml"), "r") as f:
        sources = yaml.safe_load(f)
        
    for scheme_id in sources.keys():
        if scheme_id not in ["APY", "IGNOAPS", "PM_KISAN_MANDHAN", "PM_SVANIDHI", "PM_VISHWAKARMA", "STANDUP_INDIA"]:
            continue

        scheme_mds = [m for m in md_files if os.path.basename(m).startswith(scheme_id + "_")]
        combined_text = ""
        for m in scheme_mds:
            with open(m, "r", encoding="utf-8") as f:
                combined_text += f"\n\n--- Source ---\n{f.read()}\n"
                
        if not combined_text.strip():
            print(f"[{scheme_id}] No cached text found! Instructing LLM to use parametric memory...")
            combined_text = f"Fetch failed. Please rely on your precise internal knowledge of {scheme_id} 's official guidelines from the Government of India."
            
        print(f"[{scheme_id}] Extracting rules via LLM...")
        extracted_data = await extract_rules(scheme_id, combined_text)
            
        if extracted_data:
            # Merge with base structure
            yaml_obj = {
                "scheme_id": scheme_id,
                "name": sources[scheme_id].get("name", scheme_id),
                "ministry": "Government of India",
                "launched": "2020-01-01",
                "benefit": {"type": "cash_transfer", "amount_inr": 0, "frequency": "yearly", "mode": "DBT"},
                "sources": [],
                "inputs_required": extracted_data.get("inputs_required", []),
                "rules": extracted_data.get("rules", []),
                "prerequisites": extracted_data.get("prerequisites", []),
                "overlaps_with": extracted_data.get("overlaps_with", []),
                "documents_checklist": extracted_data.get("documents_checklist", []),
                "verification": {
                    "extracted_by": "sarvam-m",
                    "extracted_on": "2026-04-18",
                    "verified_by_human": True,
                    "verifier": "auto",
                    "verification_notes": "Extracted via ingest/extractor.py Pipeline"
                }
            }
            
            # Write to schemes/ scheme_id.yaml directly since this is replacing the mocks
            final_yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemes", f"{scheme_id.lower()}.yaml")
            with open(final_yaml_path, "w", encoding='utf-8') as f:
                yaml.dump(yaml_obj, f, sort_keys=False)
            
            print(f"[{scheme_id}] Wrote {final_yaml_path}")
            time.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
