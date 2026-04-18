from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Union, Any, Optional


class Rule(BaseModel):
    id: str
    type: str  # inclusion, exclusion, mandatory_doc
    predicate: str
    description: str
    source_text: str = ""
    confidence: str = "high"
    ambiguity_flags: List[str] = Field(default_factory=list)
    ambiguity_notes: Optional[str] = None


class Scheme(BaseModel):
    model_config = ConfigDict(extra="allow")
    scheme_id: str
    name: str
    ministry: str = ""
    launched: str = ""
    category: str = ""                       # e.g. "farmer", "health", "housing"
    description: str = ""                    # human-readable 2-3 sentence description
    short_description: str = ""              # one-liner for catalogue cards
    application_url: str = ""
    benefit: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    inputs_required: List[str] = Field(default_factory=list)
    rules: List[Rule] = Field(default_factory=list)
    prerequisites: List[Dict[str, Any]] = Field(default_factory=list)
    overlaps_with: List[Dict[str, Any]] = Field(default_factory=list)
    documents_checklist: List[str] = Field(default_factory=list)
    verification: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    model_config = ConfigDict(extra="allow")


class RuleEvaluation(BaseModel):
    rule_id: str
    result: Union[bool, str]  # True, False, "UNKNOWN"
    evidence: str


class Benefit(BaseModel):
    amount: int = 0
    frequency: str = ""
    mode: str = ""


class SchemeResult(BaseModel):
    scheme_id: str
    name: str = ""
    status: str  # QUALIFIES, DOES_NOT_QUALIFY, ALMOST_QUALIFIES, UNCERTAIN
    confidence: float
    confidence_breakdown: Dict[str, float]
    rules_evaluated: List[RuleEvaluation]
    missing_inputs: List[str] = Field(default_factory=list)
    gap_analysis: List[str] = Field(default_factory=list)
    ambiguity_notes: List[str] = Field(default_factory=list)
    benefit_if_qualified: Optional[Dict[str, Any]] = None
    documents_checklist: List[str] = Field(default_factory=list)
    application_url: str = ""
    application_order: int = 0


class EngineOutput(BaseModel):
    results: List[SchemeResult]
