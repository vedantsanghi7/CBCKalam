import re
from typing import Any, Dict, List, Tuple
from engine.models import Scheme, Rule, RuleEvaluation, SchemeResult
from engine.confidence import calculate_confidence
from engine.gap_analysis import run_gap_analysis


# ---------------------------------------------------------------------------
# Safe deterministic predicate evaluator (NO eval / NO exec)
# ---------------------------------------------------------------------------

def _resolve_value(name: str, user_data: Dict[str, Any]) -> Any:
    """Resolve a dotted or plain attribute from user data.
    Supports both `land_ownership.type` and `land_ownership_type` styles.
    """
    # Try exact key first
    if name in user_data:
        return user_data[name]
    # Try dot → underscore conversion  (land_ownership.type → land_ownership_type)
    flat_key = name.replace(".", "_")
    if flat_key in user_data:
        return user_data[flat_key]
    # Try nested dict lookup
    parts = name.split(".")
    obj = user_data
    for p in parts:
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None  # missing
    return obj


def _parse_literal(token: str) -> Any:
    """Parse a literal token into a Python value."""
    token = token.strip()
    if token == "True" or token == "true":
        return True
    if token == "False" or token == "false":
        return False
    if token == "UNKNOWN":
        return "UNKNOWN"
    # Quoted string
    if (token.startswith("'") and token.endswith("'")) or \
       (token.startswith('"') and token.endswith('"')):
        return token[1:-1]
    # Numeric
    try:
        if "." in token:
            return float(token)
        return int(token)
    except ValueError:
        return token  # treat as variable name sentinel


def _parse_list(text: str) -> list:
    """Parse a list literal like ['doctor','lawyer','ca']."""
    inner = text.strip()[1:-1]  # remove [ ]
    items = []
    for item in inner.split(","):
        items.append(_parse_literal(item.strip()))
    return items


def evaluate_predicate(predicate_str: str, user_data: Dict[str, Any]) -> Any:
    """Evaluate a predicate string against user data using safe parsing.
    Returns True, False, or 'UNKNOWN' if data is missing.
    """
    try:
        return _eval_expression(predicate_str.strip(), user_data)
    except KeyError:
        return "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _eval_expression(expr: str, user_data: Dict[str, Any]) -> Any:
    """Recursively evaluate an expression with AND/OR/NOT support."""
    expr = expr.strip()

    # Handle parenthesized groups by finding matching parens
    # Strip outer parens
    if expr.startswith("(") and _find_matching_paren(expr, 0) == len(expr) - 1:
        return _eval_expression(expr[1:-1], user_data)

    # IMPORTANT: Detect BETWEEN...AND before splitting on AND
    # "age BETWEEN 18 AND 50" is a single atomic comparison, not a logical AND
    if re.search(r'\bBETWEEN\b', expr, re.IGNORECASE):
        return _eval_comparison(expr, user_data)

    # Split on OR (lowest precedence) — case insensitive
    parts = _split_respecting_parens(expr, " OR ")
    if len(parts) > 1:
        for part in parts:
            result = _eval_expression(part, user_data)
            if result is True:
                return True
            if result == "UNKNOWN":
                return "UNKNOWN"
        return False

    # Split on AND
    parts = _split_respecting_parens(expr, " AND ")
    if len(parts) > 1:
        has_unknown = False
        for part in parts:
            result = _eval_expression(part, user_data)
            if result is False:
                return False
            if result == "UNKNOWN":
                has_unknown = True
        return "UNKNOWN" if has_unknown else True

    # NOT prefix
    if expr.upper().startswith("NOT "):
        result = _eval_expression(expr[4:], user_data)
        if result == "UNKNOWN":
            return "UNKNOWN"
        return not result

    # Now it's an atomic comparison
    return _eval_comparison(expr, user_data)


def _eval_comparison(expr: str, user_data: Dict[str, Any]) -> Any:
    """Evaluate a single comparison like `age >= 18` or `profession IN [...]`."""
    expr = expr.strip()

    # Handle IN operator: `field IN ['a','b','c']`
    in_match = re.match(r'^(.+?)\s+IN\s+(\[.+?\])$', expr, re.IGNORECASE)
    if in_match:
        var_name = in_match.group(1).strip()
        list_str = in_match.group(2)
        val = _resolve_value(var_name, user_data)
        if val is None:
            raise KeyError(var_name)
        lst = _parse_list(list_str)
        return val in lst

    # Handle NOT IN
    not_in_match = re.match(r'^(.+?)\s+NOT\s+IN\s+(\[.+?\])$', expr, re.IGNORECASE)
    if not_in_match:
        var_name = not_in_match.group(1).strip()
        list_str = not_in_match.group(2)
        val = _resolve_value(var_name, user_data)
        if val is None:
            raise KeyError(var_name)
        lst = _parse_list(list_str)
        return val not in lst

    # Handle BETWEEN: `age BETWEEN 18 AND 60`
    between_match = re.match(r'^(.+?)\s+BETWEEN\s+(.+?)\s+AND\s+(.+?)$', expr, re.IGNORECASE)
    if between_match:
        var_name = between_match.group(1).strip()
        low = _parse_literal(between_match.group(2))
        high = _parse_literal(between_match.group(3))
        val = _resolve_value(var_name, user_data)
        if val is None:
            raise KeyError(var_name)
        # Type coercion: convert string to number if bounds are numeric
        if isinstance(val, str) and isinstance(low, (int, float)):
            try:
                val = float(val) if '.' in val else int(val)
            except (ValueError, TypeError):
                pass
        return low <= val <= high

    # Standard comparisons: ==, !=, >=, <=, >, <
    for op_str, op_fn in [
        (">=", lambda a, b: a >= b),
        ("<=", lambda a, b: a <= b),
        ("!=", lambda a, b: a != b),
        ("==", lambda a, b: a == b),
        (">", lambda a, b: a > b),
        ("<", lambda a, b: a < b),
    ]:
        idx = expr.find(op_str)
        if idx != -1:
            left_str = expr[:idx].strip()
            right_str = expr[idx + len(op_str):].strip()

            # Left side is always a variable
            left_val = _resolve_value(left_str, user_data)
            if left_val is None:
                raise KeyError(left_str)

            # Right side is a literal
            right_val = _parse_literal(right_str)

            # Type coercion for comparisons
            if isinstance(left_val, str) and isinstance(right_val, (int, float)):
                try:
                    left_val = type(right_val)(left_val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(right_val, str) and isinstance(left_val, (int, float)):
                try:
                    right_val = type(left_val)(right_val)
                except (ValueError, TypeError):
                    pass

            return op_fn(left_val, right_val)

    # If nothing matched, try resolving as a boolean variable
    val = _resolve_value(expr, user_data)
    if val is None:
        raise KeyError(expr)
    return bool(val)


def _find_matching_paren(s: str, start: int) -> int:
    """Find the index of the matching closing parenthesis."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_respecting_parens(s: str, delimiter: str) -> List[str]:
    """Split string by delimiter, but not inside parentheses or brackets."""
    parts = []
    depth = 0
    bracket_depth = 0
    current = []
    i = 0
    delim_upper = delimiter.upper()

    while i < len(s):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
        elif s[i] == '[':
            bracket_depth += 1
        elif s[i] == ']':
            bracket_depth -= 1

        if depth == 0 and bracket_depth == 0:
            # Check if delimiter matches at this position
            chunk = s[i:i + len(delimiter)]
            if chunk.upper() == delim_upper:
                parts.append("".join(current))
                current = []
                i += len(delimiter)
                continue

        current.append(s[i])
        i += 1

    parts.append("".join(current))
    return parts


# ---------------------------------------------------------------------------
# Rule evaluation logic
# ---------------------------------------------------------------------------

def run_evaluation(scheme: Scheme, user_data: Dict[str, Any]):
    """Evaluate all rules for a scheme against user data.
    Returns (rule_evaluations, missing_inputs, ambiguity_notes, status).
    """
    # Normalize user data - convert string booleans and numeric strings
    normalized = {}
    for k, v in user_data.items():
        if isinstance(v, str):
            vl = v.lower().strip()
            if vl in ("true", "yes", "haan", "ha"):
                normalized[k] = True
            elif vl in ("false", "no", "nahi", "naa"):
                normalized[k] = False
            else:
                # Try to convert numeric strings to numbers
                try:
                    normalized[k] = int(v)
                except ValueError:
                    try:
                        normalized[k] = float(v)
                    except ValueError:
                        normalized[k] = v
        else:
            normalized[k] = v

    results = []
    missing_inputs = []
    ambiguity_notes = []
    base_fail = False
    has_unknown = False
    all_known_pass = True  # Track if all evaluated (non-unknown) rules pass

    for req in scheme.inputs_required:
        flat_req = req.replace(".", "_")
        if normalized.get(req) is None and normalized.get(flat_req) is None:
            missing_inputs.append(req)

    failed_rules = []
    for rule in scheme.rules:
        try:
            val = evaluate_predicate(rule.predicate, normalized)
        except Exception:
            val = "UNKNOWN"

        result_status: Any = True
        if val == "UNKNOWN":
            result_status = "UNKNOWN"
            has_unknown = True
        else:
            if rule.type == "inclusion" and val is False:
                result_status = False
                base_fail = True
                all_known_pass = False
                failed_rules.append(rule)
            elif rule.type == "exclusion" and val is True:
                result_status = False
                base_fail = True
                all_known_pass = False
                failed_rules.append(rule)
            elif rule.type == "mandatory_doc" and val is False:
                result_status = False
                base_fail = True
                all_known_pass = False
                failed_rules.append(rule)

        results.append({
            "rule_id": rule.id,
            "result": result_status,
            "evidence": f"Predicate `{rule.predicate}` evaluated to {val}"
        })

        if rule.ambiguity_flags:
            for flag in rule.ambiguity_flags:
                ambiguity_notes.append(f"Rule {rule.id}: {flag} — {rule.ambiguity_notes or rule.description}")

    # Determine status
    if base_fail:
        unchangeable_vars = ["age", "sex", "caste_category", "is_widow", "is_disabled", "is_pregnant", "occupation", "profession"]
        has_unchangeable = False
        for r in failed_rules:
            if any(uv in r.predicate for uv in unchangeable_vars):
                has_unchangeable = True
                break
        status = "DOES_NOT_QUALIFY" if has_unchangeable else "ALMOST_QUALIFIES"
    elif has_unknown:
        # Some rules couldn't be evaluated because data is missing
        status = "UNCERTAIN"
    else:
        # All rules evaluated and all passed
        status = "QUALIFIES"

    return results, missing_inputs, ambiguity_notes, status


def evaluate_scheme(scheme: Scheme, user_data: Dict[str, Any]) -> SchemeResult:
    """Full evaluation pipeline: rules → confidence → gap analysis → SchemeResult."""
    rules_evaluated, missing_inputs, ambiguity_notes, status = run_evaluation(scheme, user_data)

    conf_result = calculate_confidence(status, rules_evaluated, ambiguity_notes)
    confidence = conf_result["confidence"]
    breakdown = conf_result["breakdown"]

    gaps = run_gap_analysis(status, missing_inputs, rules_evaluated, scheme.rules)

    # Build benefit info
    benefit_info = None
    if scheme.benefit:
        benefit_info = {
            "amount": scheme.benefit.get("amount_inr", 0),
            "frequency": scheme.benefit.get("frequency", ""),
            "mode": scheme.benefit.get("mode", ""),
            "type": scheme.benefit.get("type", ""),
        }

    return SchemeResult(
        scheme_id=scheme.scheme_id,
        name=scheme.name,
        status=status,
        confidence=round(confidence, 4),
        confidence_breakdown=breakdown,
        rules_evaluated=[
            RuleEvaluation(
                rule_id=r["rule_id"],
                result=r["result"],
                evidence=r["evidence"]
            ) for r in rules_evaluated
        ],
        missing_inputs=missing_inputs,
        gap_analysis=gaps,
        ambiguity_notes=ambiguity_notes,
        benefit_if_qualified=benefit_info,
        documents_checklist=scheme.documents_checklist,
        application_url="",
        application_order=0,
    )
