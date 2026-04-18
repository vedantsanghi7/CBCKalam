import pytest
from engine.evaluator import evaluate_predicate, run_evaluation, evaluate_scheme
from engine.models import Scheme, Rule
from engine.confidence import calculate_confidence


def test_predicate_basic():
    user = {"age": 42, "is_willing": True, "income": 50000}
    assert evaluate_predicate("age > 18", user) is True
    assert evaluate_predicate("age < 18", user) is False
    assert evaluate_predicate("is_willing == True AND income < 100000", user) is True
    # unknown
    assert evaluate_predicate("profession == 'doctor'", user) == "UNKNOWN"


def test_predicate_in_operator():
    user = {"profession": "doctor"}
    assert evaluate_predicate("profession IN ['doctor','lawyer','ca']", user) is True
    user2 = {"profession": "farmer"}
    assert evaluate_predicate("profession IN ['doctor','lawyer','ca']", user2) is False


def test_predicate_comparison():
    user = {"monthly_pension_inr": 15000}
    assert evaluate_predicate("monthly_pension_inr >= 10000", user) is True
    user2 = {"monthly_pension_inr": 5000}
    assert evaluate_predicate("monthly_pension_inr >= 10000", user2) is False


def test_predicate_and_or():
    user = {"age": 25, "has_aadhaar": True}
    assert evaluate_predicate("age >= 18 AND has_aadhaar == True", user) is True
    assert evaluate_predicate("age >= 60 OR has_aadhaar == True", user) is True
    assert evaluate_predicate("age >= 60 AND has_aadhaar == False", user) is False


def test_engine_flow():
    scheme = Scheme(
        scheme_id="T01",
        name="Test",
        inputs_required=["age"],
        rules=[
            Rule(id="T_001", type="inclusion", predicate="age >= 18",
                 description="Adult", source_text="x", confidence="high",
                 ambiguity_flags=[])
        ],
    )

    # 1. Successful pass
    user_pass = {"age": 20}
    res, missing, ambig, status = run_evaluation(scheme, user_pass)
    assert status == "QUALIFIES"
    conf = calculate_confidence(status, res, ambig)["confidence"]
    assert conf == 1.0

    # 2. Unknown Status
    user_unk = {}
    res, missing, ambig, status = run_evaluation(scheme, user_unk)
    assert status == "UNCERTAIN"
    assert "age" in missing

    # 3. Fail Status
    user_fail = {"age": 15}
    res, missing, ambig, status = run_evaluation(scheme, user_fail)
    assert status == "DOES_NOT_QUALIFY"
    conf = calculate_confidence(status, res, ambig)["confidence"]
    assert conf == 1.0  # 100% confident they don't qualify


def test_evaluate_scheme_returns_result():
    scheme = Scheme(
        scheme_id="T02",
        name="Test Scheme 2",
        inputs_required=["age"],
        rules=[
            Rule(id="T2_001", type="inclusion", predicate="age >= 18",
                 description="Adult", source_text="x", confidence="high",
                 ambiguity_flags=[])
        ],
    )
    result = evaluate_scheme(scheme, {"age": 25})
    assert result.status == "QUALIFIES"
    assert result.confidence > 0
    assert result.scheme_id == "T02"
    assert result.name == "Test Scheme 2"
    assert len(result.rules_evaluated) == 1


def test_ambiguity_detection():
    scheme = Scheme(
        scheme_id="T03",
        name="Test",
        inputs_required=[],
        rules=[
            Rule(id="T3_001", type="exclusion", predicate="is_institutional == True",
                 description="Institutional excluded", source_text="x",
                 confidence="medium", ambiguity_flags=["UNDEFINED_TERM"],
                 ambiguity_notes="'institutional' not defined")
        ],
    )
    result = evaluate_scheme(scheme, {"is_institutional": False})
    assert len(result.ambiguity_notes) > 0
    assert result.confidence < 1.0
