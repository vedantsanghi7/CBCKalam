def run_gap_analysis(status, missing_inputs, rules_evaluated, rules) -> list:
    gaps = []
    if status == "DOES_NOT_QUALIFY" or status == "UNCERTAIN":
        # Find which inputs are holding it back
        missing_doc = [r for r in rules if r.type == 'mandatory_doc']
        for md in missing_doc:
            # Check if this rule evaluated to False
            eval_res = next((e for e in rules_evaluated if e["rule_id"] == md.id), None)
            if eval_res and eval_res["result"] == False:
                gaps.append(f"Missing mandatory document/requirement: {md.description}")
        
    for missing in missing_inputs:
        gaps.append(f"Information needed for full evaluation: {missing}")
        
    return gaps
