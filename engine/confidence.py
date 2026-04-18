def calculate_confidence(status, rules, ambiguity_notes, stale_fetched=False):
    # base = 1.0 if all inclusion satisfied else 0.0
    if status == "DOES_NOT_QUALIFY":
        base = 0.0
    else:
        base = 1.0
        
    evals = [r["result"] for r in rules]
    unknowns = evals.count("UNKNOWN")
    completeness = 1.0 - (unknowns / len(rules)) if rules else 1.0
    
    cleanliness = 1.0 - (len(ambiguity_notes) / len(rules)) if rules else 1.0
    freshness = 1.0 if not stale_fetched else 0.8
    
    confidence = base * completeness * cleanliness * freshness
    if base == 0.0:
        confidence = 1.0 # Confident they don't qualify
    elif base == 1.0 and completeness < 1.0:
        confidence = min(confidence, 0.85)

    return {
        "confidence": confidence,
        "breakdown": {
            "base": base,
            "completeness": completeness,
            "cleanliness": cleanliness,
            "freshness": freshness
        }
    }
