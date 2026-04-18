# KALAM — Implementation Plan
### A complete build guide for a vibe-coding agent
> *"Intelligence for the people who need it most"* — Mission 03

---

## 0. READ THIS FIRST — Rules of Engagement (Non-Negotiable)

These rules apply to every file you touch, every prompt you fire, every commit you make. If you break one, roll back and fix it before proceeding.

### 0.1 The Anti-Hallucination Covenant
You are building a system that tells **real people** whether they qualify for **real government money**. A hallucinated eligibility rule is not a bug — it is harm. Therefore:

1. **The LLM never decides eligibility.** The LLM *parses* rules from source documents and *understands* user input. A deterministic Python rule engine — not the LLM — evaluates whether someone qualifies.
2. **Every rule must be traceable to a source.** No rule enters the rule store without `source_url`, `source_section`, `source_text` (the exact snippet), and `fetched_on` date.
3. **"I don't know" is a first-class output.** If data is missing, sources conflict, or language is vague, the engine returns `UNCERTAIN` with a reason. It never guesses.
4. **Never trust your training data for scheme details.** Eligibility criteria change. Always fetch from the official source. If you catch yourself writing "PM-KISAN gives ₹6000" from memory without a citation, stop and fetch the source.
5. **Cross-verify across two sources minimum.** Rule extracted from official PDF must be cross-checked against myScheme.gov.in or a PIB release. Log the diff.

### 0.2 The State File is Sacred
You must maintain `PROJECT_STATE.md` at the repo root. Update it after **every** non-trivial action. Structure below (Section 2). If you start a new session, read it before doing anything else.

### 0.3 The Prompt Log is 25% of the Score
Every LLM call — Sarvam or otherwise — gets logged to `prompt_log/` as described in Section 12. No exceptions. Retroactive logging is not allowed; log as you go.

### 0.4 Test Everything, Twice
- Unit tests for every rule evaluator.
- End-to-end tests with the 10 adversarial profiles.
- Manual sanity check of each scheme's rules against the official source by a human reader before marking it "verified".
- Never mark a scheme or edge-case "done" without a passing test.

### 0.5 Frontend is Out of Scope for This File
All frontend (UI, styling, components, routing) is handled in a separate file: **`frontend.md`**. When you reach Phase 8 (Conversational Interface) and need to build a UI beyond the CLI, read `frontend.md` and follow it. This file covers only the CLI conversational interface and the backend API surface the frontend will consume.

---

## 1. The Mission (Verbatim from Brief)

> Named after APJ Abdul Kalam. You're building an AI document intelligence engine for India's welfare system. Millions of Indians qualify for government schemes but never claim them because the eligibility criteria are buried in bureaucratic language across hundreds of PDFs and the requirements are unclear. Your system changes that.

**Three parts, six mandatory deliverables:**

| # | Deliverable | Where it lives in this plan |
|---|---|---|
| 1 | Structured eligibility rules for 15+ central schemes | Phase 2 & 3 |
| 2 | Ambiguity map (contradictions / overlaps / vague terms) | Phase 4 |
| 3 | Matching engine with explainable confidence scores | Phase 5 & 6 |
| 4 | 10 adversarial edge-case profiles with documented results | Phase 7 |
| 5 | Conversational interface (CLI/UI) with Hinglish support | Phase 8 |
| 6 | Architecture document (system diagram + 3 decisions + 2 gaps) | Phase 9 |

**Plus the prompt log** — 25% of score, see Section 12.

---

## 2. Project State Protocol (MANDATORY)

Create `PROJECT_STATE.md` at the repo root on day one. Keep it current. Format:

```markdown
# KALAM Project State
Last updated: YYYY-MM-DD HH:MM  (update timestamp on every edit)

## Current Phase
Phase X — <name>
Step: <what I'm actively doing right now>

## Schemes Status
| Scheme ID | Name | Rules Extracted | Human-Verified | Tests Passing |
|-----------|------|-----------------|----------------|---------------|
| PM_KISAN | PM Kisan Samman Nidhi | ✅ 12 rules | ✅ | 5/5 |
| MGNREGA  | MGNREGA | ⏳ in progress | ❌ | 0/0 |
| ...

## File Map (update when you add/move files)
- /schemes/*.yaml          → Verified rule files (ground truth)
- /schemes/_raw/*.json     → Raw LLM-extracted rules (pre-verification)
- /engine/                 → Deterministic matching engine
- /ingest/                 → Data fetchers + PDF parsers
- /conv/                   → Conversational interface
- /prompt_log/             → Every LLM call, chronological
- /tests/                  → Unit + integration tests
- /edge_cases/             → 10 adversarial profiles + results
- /docs/architecture.md    → Final architecture deliverable
- /docs/ambiguity_map.md   → Ambiguity deliverable

## Open Questions / Blockers
- [ ] ...

## Completed Milestones
- [x] ...

## Last 5 Actions (most recent first)
1. ...
```

**Rule:** Before asking the user anything, before refactoring, before starting a new file — read `PROJECT_STATE.md`. After any meaningful action — update it.

---

## 3. Tech Stack

### 3.1 Required
- **Language:** Python 3.11+
- **Package manager:** `uv` (or `pip` with `requirements.txt`)
- **Rule store format:** YAML (human-readable, diff-friendly, supports comments)
- **Rule engine:** Pure Python — no LLM in the decision path
- **LLM:** Sarvam AI (see Section 4)
- **PDF parsing:** Sarvam Document Intelligence API (primary) + `pdfplumber` (fallback for simple layouts)
- **HTTP:** `httpx` (async-capable)
- **CLI:** `typer` + `rich` (pretty terminal output)
- **Testing:** `pytest` + `pytest-asyncio`
- **Schema validation:** `pydantic` v2

### 3.2 requirements.txt (starter)
```
httpx>=0.27
pydantic>=2.6
pyyaml>=6.0
typer>=0.12
rich>=13.7
pytest>=8.0
pytest-asyncio>=0.23
pdfplumber>=0.11
python-dotenv>=1.0
sarvamai>=0.1        # official SDK, optional — raw HTTP works too
tenacity>=8.2        # retries with backoff
```

### 3.3 Repo Layout
```
kalam/
├── PROJECT_STATE.md           # living state file (Section 2)
├── frontend.md                # separate, provided by user
├── README.md
├── requirements.txt
├── .env.example               # SARVAM_API_KEY=sk_...
├── schemes/
│   ├── pm_kisan.yaml          # verified rules
│   ├── mgnrega.yaml
│   ├── ... (15+ files)
│   └── _raw/                  # unverified LLM drafts
├── ingest/
│   ├── sources.yaml           # source URLs per scheme
│   ├── fetcher.py             # download + cache raw docs
│   ├── pdf_parser.py          # Sarvam Doc Intelligence wrapper
│   └── extractor.py           # LLM-based rule extraction
├── engine/
│   ├── models.py              # pydantic: User, Rule, Result, Scheme
│   ├── evaluator.py           # deterministic rule evaluation
│   ├── confidence.py          # confidence score calculation
│   ├── gap_analysis.py        # "almost qualifies" logic
│   └── sequencer.py           # prerequisite detection
├── conv/
│   ├── sarvam_client.py       # Sarvam LLM wrapper
│   ├── nlu.py                 # parse Hinglish user input → structured
│   ├── dialog.py              # follow-up question generator
│   └── cli.py                 # the chat CLI
├── ambiguity/
│   ├── analyzer.py            # finds overlaps, contradictions
│   └── report.py              # renders the map
├── prompt_log/
│   ├── YYYYMMDD/
│   │   ├── 001_extract_pmkisan.md
│   │   ├── 002_nlu_turn.md
│   │   └── ...
│   └── README.md              # log format + index
├── edge_cases/
│   ├── profiles.yaml          # 10 profiles
│   └── results.md             # documented outcomes
├── tests/
│   ├── test_engine.py
│   ├── test_rules_pm_kisan.py
│   ├── test_edge_cases.py
│   └── test_nlu_hinglish.py
└── docs/
    ├── architecture.md        # FINAL deliverable
    ├── ambiguity_map.md       # FINAL deliverable
    └── diagrams/              # system diagram (mermaid or image)
```

---

## 4. Sarvam AI Integration

### 4.1 API Key
```
SARVAM_API_KEY = sk_hm1ed0d0_BHXgdmNOPhc3Qucerutn1q6o
```
Store in `.env` (never commit). Load via `python-dotenv`. Example `.env.example`:
```
SARVAM_API_KEY=sk_hm1ed0d0_BHXgdmNOPhc3Qucerutn1q6o
```

### 4.2 Model Choices — and why

| Task | Model | Why |
|------|-------|-----|
| Rule extraction from scheme text | **`sarvam-m`** (hybrid thinking mode = ON) | 24B, built-in "think" mode gives us reasoning traces for auditability. Strong on code-mixed Indic text (PIB releases often have Hindi terms). |
| Rule extraction — long PDFs (>30k tokens of context) | **`sarvam-30b`** | 64K context window, balanced cost/quality. Use when a full scheme guideline PDF must be reasoned over in one shot. |
| Conversational NLU (Hinglish parsing) | **`sarvam-m`** (non-think mode) | Native Hinglish/code-mixed support, faster, cheaper for high-turn volume. |
| Follow-up question generation | **`sarvam-m`** (non-think) | Same reasoning as above. |
| Edge-case analysis / ambiguity detection | **`sarvam-30b`** (thinking enabled) | Needs multi-step reasoning over many rules at once. |
| PDF → structured text | **Sarvam Document Intelligence** (Sarvam Vision under the hood) | SOTA for Indic-language government docs, table extraction, page-limit 10 per call → chunk larger docs. |
| Optional: translate English scheme text → Hindi for UI | **`mayura`** / **`sarvam-translate`** | Only if you need to show Hindi UI strings beyond what Sarvam-M already outputs in Hinglish. |

**Defaults to use in code:**
```python
PRIMARY_LLM = "sarvam-m"        # everyday calls, Hinglish
REASONING_LLM = "sarvam-30b"    # long-context, rule extraction
# escalate to sarvam-105b only if reasoning quality is visibly failing — it's more expensive
```

### 4.3 Endpoints
- **Chat completion:** `POST https://api.sarvam.ai/v1/chat/completions` (OpenAI-compatible schema)
- **Document Intelligence (digitize):** SDK `client.document_digitization.digitize(file_path=..., language="en-IN", output_format="md")` — returns structured Markdown/HTML
- **Auth header:** `api-subscription-key: sk_...` (preferred) or `Authorization: Bearer sk_...`

### 4.4 Minimal Client Wrapper (`conv/sarvam_client.py`)
```python
import os, json, httpx
from typing import Literal
from tenacity import retry, stop_after_attempt, wait_exponential

BASE = "https://api.sarvam.ai/v1"
KEY = os.environ["SARVAM_API_KEY"]
HEADERS = {"api-subscription-key": KEY, "Content-Type": "application/json"}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def chat(messages, model="sarvam-m", temperature=0.1, think=False, max_tokens=2000):
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if think and model in ("sarvam-m", "sarvam-30b", "sarvam-105b"):
        body["reasoning_effort"] = "medium"   # enables think mode
    r = httpx.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, timeout=120)
    r.raise_for_status()
    return r.json()
```

Critical: **temperature=0.1 by default** for any call whose output feeds the rule store. Creativity is a bug here. Only raise temperature for the conversational surface where naturalness matters — and even there, cap at 0.5.

### 4.5 Thinking Mode — Reasoning Separation
When `think=True`, Sarvam-M returns the reasoning inside `<think>...</think>` tags before the final answer. Split and log the reasoning separately — it is gold for debugging hallucinations.

```python
def split_think(text):
    if "</think>" in text:
        reasoning, answer = text.split("</think>", 1)
        return reasoning.replace("<think>", "").strip(), answer.strip()
    return "", text.strip()
```

---

## 5. The 15+ Schemes — Canonical List

Pick these **18 schemes** (18 gives you safe margin above 15; you can drop the weakest 3 if time is tight). They are deliberately diverse: cross-domain (income, health, housing, pension, insurance, employment, skilling, entrepreneurship, women/child), cross-demographic, and they have well-known overlaps which make the ambiguity map richer.

| # | Scheme ID | Name | Primary Source URL | Domain |
|---|-----------|------|---------------------|--------|
| 1 | `PM_KISAN` | Pradhan Mantri Kisan Samman Nidhi | https://pmkisan.gov.in + `/Documents/RevisedFAQ.pdf` | Farmer income |
| 2 | `MGNREGA` | Mahatma Gandhi National Rural Employment Guarantee Act | https://nrega.nic.in | Rural employment |
| 3 | `PMJAY` | Ayushman Bharat — PM Jan Arogya Yojana | https://pmjay.gov.in + `/about/PMJAY` | Health insurance |
| 4 | `PMAY_G` | Pradhan Mantri Awas Yojana — Gramin | https://pmayg.nic.in | Rural housing |
| 5 | `PMAY_U` | Pradhan Mantri Awas Yojana — Urban (PMAY 2.0) | https://pmay-urban.gov.in | Urban housing |
| 6 | `PMUY` | Pradhan Mantri Ujjwala Yojana | https://pmuy.gov.in | LPG |
| 7 | `PMJDY` | Pradhan Mantri Jan Dhan Yojana | https://pmjdy.gov.in | Banking inclusion |
| 8 | `PMJJBY` | Pradhan Mantri Jeevan Jyoti Bima Yojana | https://jansuraksha.gov.in | Life insurance |
| 9 | `PMSBY` | Pradhan Mantri Suraksha Bima Yojana | https://jansuraksha.gov.in | Accident insurance |
| 10 | `APY` | Atal Pension Yojana | https://npscra.nsdl.co.in / https://www.pfrda.org.in | Pension (unorganised) |
| 11 | `PMMVY` | Pradhan Mantri Matru Vandana Yojana | https://pmmvy.wcd.gov.in | Maternity benefit |
| 12 | `SSY` | Sukanya Samriddhi Yojana | https://www.nsiindia.gov.in | Girl child savings |
| 13 | `IGNOAPS` | Indira Gandhi National Old Age Pension (NSAP) | https://nsap.nic.in | Old-age pension |
| 14 | `IGNWPS` | Indira Gandhi National Widow Pension (NSAP) | https://nsap.nic.in | Widow pension |
| 15 | `PM_SVANIDHI` | PM Street Vendor's AtmaNirbhar Nidhi | https://pmsvanidhi.mohua.gov.in | Street vendor loan |
| 16 | `STANDUP_INDIA` | Stand-Up India | https://www.standupmitra.in | SC/ST/women entrepreneurship |
| 17 | `PM_VISHWAKARMA` | PM Vishwakarma | https://pmvishwakarma.gov.in | Artisans |
| 18 | `PM_KISAN_MANDHAN` | PM Kisan Maan-Dhan Yojana | https://maandhan.in | Farmer pension |

**Cross-verification secondary source for all 18:** `https://www.myscheme.gov.in` (search by scheme name).
**Tertiary (for policy changes):** PIB releases via `https://pib.gov.in/PressReleasePage.aspx?PRID=<ID>`

**The agent must fetch these live**. Do not use training-data memory for any detail. If a URL is down at fetch time, log it in `PROJECT_STATE.md` and fall back to a Wayback Machine mirror — but flag the rule as `source_stale`.

---

## 6. Data Sources & Fetching Strategy

### 6.1 `ingest/sources.yaml` — Template
```yaml
PM_KISAN:
  name: Pradhan Mantri Kisan Samman Nidhi
  primary:
    - url: https://pmkisan.gov.in/Documents/RevisedFAQ.pdf
      type: pdf
      section: "Full document"
    - url: https://pmkisan.gov.in/
      type: html
      section: "Eligibility tab"
  secondary:
    - url: https://www.myscheme.gov.in/schemes/pm-kisan
      type: html
  pib_latest:
    - url: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146932
      type: html
      date: 2025-02-24
```

### 6.2 Fetching Rules
1. **Cache raw responses** in `ingest/_cache/<scheme_id>/<url_hash>.<ext>` with a sidecar `.meta.json` containing `{url, fetched_on, sha256, http_status}`.
2. **Respect robots.txt** on government sites.
3. **Throttle:** 1 request/sec per domain. Government sites are not robust.
4. **Never re-fetch within 24h** unless explicitly asked — work from cache.
5. **Log every fetch** to `PROJECT_STATE.md`.

### 6.3 PDF Handling via Sarvam Document Intelligence
Sarvam DI has a **10-page limit per call**. Long PDFs (e.g. NREGA operational guidelines, often 80+ pages) must be split.

```python
# Pseudocode
def parse_pdf(path, lang="en-IN"):
    pages = split_pdf_into_chunks(path, chunk_size=10)
    markdown_chunks = []
    for chunk in pages:
        md = sarvam_di_digitize(chunk, output_format="md", language=lang)
        markdown_chunks.append(md)
    return "\n\n---PAGE-BREAK---\n\n".join(markdown_chunks)
```

For Hindi-content PDFs (e.g. some PIB releases), pass `language="hi-IN"`.

---

## 7. System Architecture (High-Level)

```
                        ┌─────────────────────────────────────────────┐
                        │              USER  (CLI / Web)              │
                        │  natural language, Hinglish, incomplete     │
                        └──────────────────┬──────────────────────────┘
                                           │
                        ┌──────────────────▼──────────────────────────┐
                        │        CONVERSATIONAL LAYER  (conv/)        │
                        │  NLU → Slot filling → Dialog policy         │
                        │  LLM: Sarvam-M (Hinglish, non-think)        │
                        │  OUTPUT: structured UserProfile (JSON)      │
                        └──────────────────┬──────────────────────────┘
                                           │  UserProfile
                        ┌──────────────────▼──────────────────────────┐
                        │      DETERMINISTIC MATCHING ENGINE          │
                        │  (engine/)   NO LLM HERE — PURE PYTHON      │
                        │  ┌──────────────────────────────────────┐   │
                        │  │ evaluator.py: for each scheme,       │   │
                        │  │   evaluate each rule; record result, │   │
                        │  │   missing data, ambiguity flags.     │   │
                        │  ├──────────────────────────────────────┤   │
                        │  │ confidence.py: compute score from    │   │
                        │  │   rule completeness + ambiguity      │   │
                        │  ├──────────────────────────────────────┤   │
                        │  │ gap_analysis.py: for near-misses,    │   │
                        │  │   list which rules would need to     │   │
                        │  │   become true.                       │   │
                        │  ├──────────────────────────────────────┤   │
                        │  │ sequencer.py: detect prereqs         │   │
                        │  │   (e.g. PMJDY → PMJJBY → PMSBY)      │   │
                        │  └──────────────────────────────────────┘   │
                        └──────────────────┬──────────────────────────┘
                                           │  Result + trace
                        ┌──────────────────▼──────────────────────────┐
                        │         RULE STORE  (schemes/*.yaml)        │
                        │  Human-verified eligibility rules           │
                        │  + source citations + ambiguity flags       │
                        └──────────────────▲──────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────────────┐
                        │         RULE EXTRACTION PIPELINE            │
                        │  (ingest/)   OFFLINE, RUN ONCE PER UPDATE   │
                        │                                             │
                        │  Raw URL/PDF  →  Sarvam Doc Intelligence    │
                        │       →  Markdown                           │
                        │       →  Sarvam-30B (think mode)            │
                        │       →  Candidate rules (JSON)             │
                        │       →  HUMAN VERIFICATION                 │
                        │       →  Verified YAML  →  Rule Store       │
                        └─────────────────────────────────────────────┘
```

**Why this split matters:** the LLM is in the *ingestion* path (where errors can be caught by humans reviewing YAML diffs) and in the *NLU* path (where errors produce wrong follow-up questions, not wrong eligibility). The **decision** is deterministic. You can audit any result by reading the YAML rules + the evaluator code.

---

## 8. Rule Schema — The Ground Truth Format

Every scheme gets one YAML file. This is the single source of truth the engine reads.

```yaml
# schemes/pm_kisan.yaml
scheme_id: PM_KISAN
name: Pradhan Mantri Kisan Samman Nidhi
ministry: Ministry of Agriculture and Farmers Welfare
launched: 2019-02-24
benefit:
  type: cash_transfer
  amount_inr: 6000
  frequency: yearly
  installments: 3
  mode: DBT_aadhaar_linked_bank

sources:
  - url: https://pmkisan.gov.in/Documents/RevisedFAQ.pdf
    section: "Operational Guidelines — Eligibility"
    fetched_on: 2026-04-18
    sha256: <hash>
  - url: https://www.myscheme.gov.in/schemes/pm-kisan
    fetched_on: 2026-04-18
    sha256: <hash>

inputs_required:
  # what the matching engine needs to know about the user
  - occupation
  - land_ownership.type      # owned_cultivable | leased | none
  - land_ownership.in_own_name
  - income_tax_filed_last_ay
  - monthly_pension_inr
  - govt_employee_status     # none | serving | retired
  - profession               # doctor | lawyer | ca | engineer | architect | other
  - is_institutional_landholder
  - has_aadhaar
  - has_bank_account
  - ekyc_done

rules:
  - id: PMK_R001
    type: inclusion
    predicate: "land_ownership.type == 'owned_cultivable' AND land_ownership.in_own_name == true"
    description: "Must own cultivable land in own name per state land records"
    source_text: "Farmers' families whose names are entered into the land records..."
    confidence: high
    ambiguity_flags: []

  - id: PMK_R002
    type: exclusion
    predicate: "is_institutional_landholder == true"
    description: "Institutional landholders excluded"
    source_text: "Institutional Land holders."
    confidence: medium
    ambiguity_flags: [UNDEFINED_TERM]
    ambiguity_notes: "Guidelines do not define 'institutional landholder' — trust/society/company?"

  - id: PMK_R003
    type: exclusion
    predicate: "income_tax_filed_last_ay == true"
    description: "Filed income tax in previous assessment year"
    source_text: "All Persons who paid Income Tax in last assessment year..."
    confidence: high
    ambiguity_flags: []

  - id: PMK_R004
    type: exclusion
    predicate: "profession IN ['doctor','lawyer','ca','engineer','architect']"
    description: "Specific professionals excluded"
    source_text: "Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects..."
    confidence: high
    ambiguity_flags: []

  - id: PMK_R005
    type: exclusion
    predicate: "monthly_pension_inr >= 10000"
    description: "Pension ≥ ₹10,000/month excluded"
    source_text: "All Superannuated/retired pensioners with monthly pension of Rs. 10,000 or more..."
    confidence: high
    ambiguity_flags: []

  - id: PMK_R006
    type: mandatory_doc
    predicate: "has_aadhaar == true AND ekyc_done == true"
    description: "Aadhaar-based eKYC mandatory"
    source_text: "eKYC is MANDATORY for all PM-KISAN registered farmers."
    confidence: high
    ambiguity_flags: []

  - id: PMK_R007
    type: mandatory_doc
    predicate: "has_bank_account == true"
    description: "Aadhaar-seeded bank account required for DBT"
    source_text: "Amount transferred into Aadhaar seeded bank accounts..."
    confidence: high
    ambiguity_flags: []

prerequisites:
  # Other schemes that must be active first
  - scheme: PMJDY          # needs a bank account — PMJDY is the easy path
    soft: true             # soft = "recommended" not strictly required

overlaps_with:
  - scheme: PM_KISAN_MANDHAN
    nature: "PM Kisan beneficiaries get auto-opt-in for PM-KMY contribution"

documents_checklist:
  - aadhaar_card
  - bank_passbook_with_ifsc
  - land_record_khasra_khatauni
  - mobile_linked_to_aadhaar

verification:
  extracted_by: sarvam-30b
  extracted_on: 2026-04-18
  verified_by_human: true     # MUST be true before engine uses this file
  verifier: <initials>
  verification_notes: "Cross-checked against pmkisan.gov.in FAQ v2025-02 and myScheme entry. All rules match."
```

### 8.1 Predicate Language
Keep it simple. The evaluator parses these with a small, safe expression language — **do not use `eval()`**.

Allowed operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `AND`, `OR`, `NOT`, `IN`, `BETWEEN`
Allowed literals: strings (single-quoted), integers, floats, booleans, lists, the constant `UNKNOWN`

Use a tiny parser (e.g. `lark` or a hand-rolled recursive-descent) — or evaluate a pre-parsed AST stored alongside the predicate. Never `eval()` user-facing strings.

### 8.2 Ambiguity Flag Vocabulary (closed set)
- `UNDEFINED_TERM` — the rule references a term the source doesn't define
- `CONFLICTING_SOURCES` — two official sources disagree
- `STATE_DEPENDENT` — rule varies by state/UT and we don't have all variants
- `OUTDATED_SOURCE` — source URL returned stale content vs PIB latest
- `NEEDS_HUMAN` — LLM extracted this rule but flagged low confidence
- `DISCRETIONARY` — guidelines explicitly give administrative officer discretion

---

## 9. Anti-Hallucination Playbook

Six mechanisms, applied together.

### 9.1 Source Grounding
Every rule MUST have `source_text` that is a substring of the fetched source markdown (within whitespace normalization). Add a validator:

```python
def validate_grounding(rule, source_md):
    if rule.source_text.strip() not in " ".join(source_md.split()):
        raise ValueError(f"Rule {rule.id}: source_text not found in source. HALLUCINATION RISK.")
```

Run this as a pre-commit hook on every `schemes/*.yaml`.

### 9.2 Two-Source Rule
For every rule, the extractor must show that at least two independent sources (official + myScheme, or official + PIB) support it. If only one source mentions a rule, flag it `[NEEDS_HUMAN]` — still include it, but don't auto-use it for eligibility denial.

### 9.3 Structured Output Only
All extractor prompts must demand JSON output matching a Pydantic schema. Parse with `pydantic`. If parsing fails, reject the output and re-prompt — do not salvage.

### 9.4 Self-Critique Pass
After extraction, run a second Sarvam call asking the model to find problems with its own output:
> "Here are the rules you extracted. For each rule, answer: does the source_text actually support this predicate? Is any term undefined in the source? Output JSON: `[{rule_id, supports: bool, undefined_terms: [...], issue: str}]`"

Any rule with `supports: false` is dropped. Any with `undefined_terms` gets `UNDEFINED_TERM` flag.

### 9.5 Confidence Floor
The engine NEVER returns `qualifies=true` with confidence > 0.9 unless:
- all rules evaluate with full data (no UNKNOWN values),
- no rule has any ambiguity flag except empty list,
- both sources were fetched within the last 90 days.

Otherwise cap at 0.85 and include reasons.

### 9.6 Fail Clearly, Not Silently
If any of the following happens during evaluation, the engine returns `status: UNCERTAIN` with a `reasons: []` list — it does **not** return `qualifies: false`:
- A required user input is missing.
- A rule has `UNDEFINED_TERM` and the user's value falls in the gray zone.
- A source is stale (>365 days).
- The scheme's guidelines have been updated since the YAML was verified (detected via PIB feed).

The UI must show UNCERTAIN results distinctly from NO results. "Not sure" and "No" are different answers.

---

## 10. Phase-by-Phase Build Plan

### Phase 0 — Repo Setup (½ day)
- [ ] Init repo, create directory structure from Section 3.3.
- [ ] Create `PROJECT_STATE.md` (Section 2).
- [ ] Create `.env` with Sarvam key.
- [ ] Smoke-test Sarvam API: one chat call to `sarvam-m`, log it to `prompt_log/`.
- [ ] Write `conv/sarvam_client.py` (Section 4.4).
- [ ] Commit. Tag `v0.0-setup`.

### Phase 1 — Data Ingestion (1–1.5 days)
- [ ] Write `ingest/sources.yaml` covering all 18 schemes (Section 5).
- [ ] Write `ingest/fetcher.py` — downloads + caches. Throttled.
- [ ] Write `ingest/pdf_parser.py` — wraps Sarvam Document Intelligence with 10-page chunking.
- [ ] Fetch + parse all sources. Cache results.
- [ ] Update `PROJECT_STATE.md` with fetch status per scheme.
- [ ] Commit. Tag `v0.1-ingested`.

### Phase 2 — Rule Extraction (2 days)
- [ ] Write `ingest/extractor.py` — per-scheme extraction prompt (Section 11.1).
- [ ] Run extractor on each scheme → write to `schemes/_raw/<scheme>.json`.
- [ ] Run self-critique pass (Section 9.4) → filter results.
- [ ] Log every prompt + response to `prompt_log/`.
- [ ] Update `PROJECT_STATE.md`.
- [ ] Commit. Tag `v0.2-extracted`.

### Phase 3 — Human Verification & Rule Store (1 day)
- [ ] For each `schemes/_raw/*.json`, manually review against the primary source. Move verified rules into `schemes/<scheme>.yaml` using the Section 8 schema.
- [ ] Set `verified_by_human: true` only after actually comparing to source.
- [ ] Run the grounding validator (Section 9.1) in CI.
- [ ] **Deliverable 1 complete:** 15+ verified scheme rule files.
- [ ] Commit. Tag `v0.3-verified`.

### Phase 4 — Ambiguity Map (1 day)
- [ ] Write `ambiguity/analyzer.py`. For each pair of schemes, find:
  - **Overlaps:** rules with same `type: exclusion` targeting same attribute (e.g. both PMKISAN and PMAY-G exclude income-tax payers with different thresholds).
  - **Contradictions:** e.g. PMJJBY has upper age 50, PMSBY has upper age 70, PMUY has no age cap — document what that means if a user is 55.
  - **Prerequisite chains:** PMJDY → PMJJBY → PMSBY (bank account → life → accident).
  - **Undefined terms** across schemes: "BPL", "farmer", "small farmer", "institutional", "urban poor" — map each definition and highlight mismatches.
- [ ] Render `docs/ambiguity_map.md` with sections: Contradictions, Overlaps, Undefined Terms, State-Dependent Rules, Discretionary Zones.
- [ ] **Deliverable 2 complete.**
- [ ] Commit. Tag `v0.4-ambiguity`.

### Phase 5 — Matching Engine (2 days)
- [ ] Write `engine/models.py` — Pydantic models for `User`, `Rule`, `SchemeResult`, `EngineOutput`.
- [ ] Write `engine/evaluator.py` — loads YAML files, evaluates predicates safely (no `eval()`). Supports `UNKNOWN` as a third truth value.
- [ ] Write `engine/confidence.py` — confidence formula below.
- [ ] Write `engine/gap_analysis.py` — for failed rules, list exactly which inputs would need to change.
- [ ] Write `engine/sequencer.py` — topological sort over scheme prerequisites; output suggested application order.
- [ ] Unit tests for every rule in every scheme: `tests/test_rules_<scheme>.py`.
- [ ] Commit. Tag `v0.5-engine`.

**Confidence Formula (deterministic):**
```
base         = 1.0 if all inclusion rules satisfied else 0.0
completeness = 1 - (# rules with UNKNOWN inputs / total rules)
cleanliness  = 1 - (# rules with ambiguity_flags / total rules)
freshness    = 1 if sources fetched < 90 days ago
               else 0.8 if < 180
               else 0.6 if < 365
               else 0.4

confidence   = base * completeness * cleanliness * freshness
```

If `base == 0` (some hard exclusion triggered) — return `qualifies=false, confidence=1.0` (we're confident they DON'T qualify). If `base == 1` but `completeness < 1` — cap confidence at 0.85 and mark `status=UNCERTAIN`.

**Every confidence score must be accompanied by the breakdown** — this is what "explainable" means. Show the user: "Base: 1.0 × Completeness: 0.87 × Cleanliness: 1.0 × Freshness: 1.0 = 0.87".

### Phase 6 — Scheme Result Output Format
```json
{
  "scheme_id": "PM_KISAN",
  "status": "QUALIFIES" | "DOES_NOT_QUALIFY" | "ALMOST_QUALIFIES" | "UNCERTAIN",
  "confidence": 0.87,
  "confidence_breakdown": {
      "base": 1.0, "completeness": 0.87, "cleanliness": 1.0, "freshness": 1.0
  },
  "rules_evaluated": [
    {"rule_id": "PMK_R001", "result": true,  "evidence": "user reported owned_cultivable in own name"},
    {"rule_id": "PMK_R002", "result": false, "evidence": "user is individual, not institutional"},
    {"rule_id": "PMK_R003", "result": "UNKNOWN", "evidence": "user did not provide ITR status"},
    ...
  ],
  "missing_inputs": ["income_tax_filed_last_ay"],
  "gap_analysis": [],              // only populated for ALMOST_QUALIFIES
  "ambiguity_notes": ["Rule PMK_R002: 'institutional' undefined in source"],
  "benefit_if_qualified": {"amount": 6000, "frequency": "year", "mode": "DBT"},
  "documents_checklist": [...],
  "application_url": "https://pmkisan.gov.in/RegistrationFormupdated.aspx",
  "application_order": 2           // from sequencer (PMJDY first, then this)
}
```

### Phase 7 — Adversarial Edge Cases (1 day)
Write these 10 profiles in `edge_cases/profiles.yaml`. Then run the engine on each, document results in `edge_cases/results.md` including: what the engine said, what the "right" answer is, and whether it flagged uncertainty correctly.

1. **Widow Who Recently Remarried (Leela, 38)** — applies for IGNWPS. Remarriage disqualifies in most states but some are silent. Should trigger `UNCERTAIN` for IGNWPS with `STATE_DEPENDENT` flag.
2. **Farmer Who Leases Land (Ramesh, 42)** — no land in own name, cultivates as tenant. Should return `DOES_NOT_QUALIFY` for PM-KISAN (high confidence), `QUALIFIES` for MGNREGA.
3. **Aadhaar-Yes, Bank-No (Sushila, 28)** — has Aadhaar but no bank account. Should return `ALMOST_QUALIFIES` for multiple schemes with `gap_analysis: open PMJDY account first`, and `application_order` pointing to PMJDY.
4. **Transgender Applicant (Ayesha, 35)** — scheme PMMVY says "pregnant woman / lactating mother". Should return `UNCERTAIN` for PMMVY with note about gender-definition ambiguity.
5. **Interstate Migrant (Mohan, 34)** — Bihar native working in Maharashtra, has Aadhaar with Bihar address. For PMAY-U in Mumbai — `UNCERTAIN` (domicile rules vary).
6. **Joint Family, Multiple Adult Sons (Rajesh + 2 sons, land in father's name)** — only father qualifies for PM-KISAN per current definition of "farmer's family". Must explain to sons why NOT (common misconception).
7. **Divorced Father Raising Daughter (Arjun, 44, daughter 6)** — wants Sukanya Samriddhi. Guardian rules allow, but often require documentation of sole custody. `QUALIFIES` with `ambiguity_notes` about documentation friction.
8. **Organic Farmer, No PAN (Kamla, 52)** — owns land, no PAN. No ITR filed because income below threshold. Qualifies PM-KISAN. But PMJDY bank opening often smoother with PAN → flag soft friction.
9. **Husband Missing 7+ Years (Meena, 45)** — not legally widowed, not divorced. Applies for IGNWPS. Hard ambiguity — return `UNCERTAIN` with note about "deemed widow" state variations.
10. **Orphan Minor Applying Through NGO (Karan, 16)** — wants scholarship. Guardian must be legal. NGO guardianship varies by state. `UNCERTAIN`.

**The graders will feed these profiles in. The system MUST flag uncertainty where uncertainty exists. Returning a confident wrong answer on any of these is an auto-fail on that case.**

Commit. Tag `v0.7-edgecases`.

### Phase 8 — Conversational Interface (2 days)
This is where Hinglish lives. Backend only — UI lives in `frontend.md`.

**Dialog state machine:**
```
GREETING → ELICIT_SLOTS → CONFIRM → MATCH → EXPLAIN → FOLLOWUP → END
            ↑                                           │
            └───────────── (missing slots) ─────────────┘
```

**Slots to fill** (same as `inputs_required` across all schemes, unioned + deduped):
`age, sex, state, district_rural_or_urban, caste_category, annual_income_inr, land_ownership_type, land_in_own_name, occupation, profession, family_size, has_aadhaar, has_bank_account, ekyc_done, has_pan, pension_inr, govt_employee_status, income_tax_filed_last_ay, is_pregnant, has_daughter_under_10, is_widow, is_disabled, is_bpl, ...`

**Hinglish handling:**
- System prompt to Sarvam-M includes Hinglish vocabulary hints: `khet = field, zameen = land, maalik = owner, theka/batai = lease/sharecropping, pati = husband, vidhwa = widow, BPL = garib, aadhar = Aadhaar, khata = account, pension = pension`.
- Accept Roman-Hindi, Devanagari, English, and code-mixed input.
- Use `temperature=0.3` for NLU so the LLM doesn't invent values.
- Always respond in the **same register** the user used. If they wrote in Hinglish, respond in Hinglish.

**NLU prompt (skeleton — see Section 11.3 for full):**
```
System: You are KALAM's slot-filler. Extract values for the schema below from the user's message.
The user may write in English, Hindi, or Hinglish. Be conservative — only extract what is explicitly stated.
Return ONLY JSON: {extracted: {...}, missing_still: [...], clarifications_needed: [...]}.
If a value is implied but not stated, put it in clarifications_needed, not extracted.
Never invent values. "UNKNOWN" is a valid extraction for any slot.

Schema: <paste slot names + types>
User message: "<user turn>"
```

**Follow-up question generation:**
- Pick the **single most informative missing slot** (information-gain heuristic: which slot, if known, would let us classify the most schemes?).
- Ask one question, short, friendly, in user's register.
- Offer 2–4 discrete answer options when applicable (the frontend can render as buttons; CLI uses numbers).

**Contradiction handling:** If user says "I don't own land" in turn 3, then "I have 2 acres" in turn 5, the dialog must detect conflict and ask for clarification — it must NOT silently overwrite.

**"I don't know" handling:** If user says "pata nahi" / "don't know" for a slot, record `UNKNOWN` and move on. Don't push. The engine will return `UNCERTAIN` for schemes depending on that slot, and the user can be told exactly why.

**CLI deliverable** in `conv/cli.py`:
```
$ python -m conv.cli

KALAM 👋  Namaste! Main aapki sarkari yojanaon ke liye eligibility check karne wala hoon.
KALAM 🗨️  Aapki umar kya hai?
You > main 34 saal ka hoon
KALAM 🗨️  Theek hai. Aap kis state mein rehte hain?
You > Rajasthan
...
KALAM ✅  Aap 4 yojanaon ke liye eligible hain:
     1. PM Kisan Samman Nidhi — confidence 0.91
     2. ...
     Aur 2 yojanaon ke liye almost-eligible. Main detail dikhau? (y/n)
```

**Deliverable 5 complete.** Commit. Tag `v0.8-conv`.

### Phase 9 — Architecture Document (½ day)
Write `docs/architecture.md` containing:

1. **System diagram** — use Mermaid (preferred, renders in GitHub) or an SVG. Show the layers from Section 7 plus data flow arrows.

2. **Three key technical decisions with rejected alternatives:**

   **Decision 1: Rule store as YAML vs a database vs pure LLM-in-the-loop.**
   - Chose: YAML.
   - Rejected: (a) SQLite — overhead for 18 files, loses diff-ability. (b) Let the LLM re-read the source on every query — non-deterministic, slow, expensive, unauditable.

   **Decision 2: LLM role — parser-only vs decision-maker.**
   - Chose: parser-only. Deterministic engine for decisions.
   - Rejected: (a) Ask LLM "is this user eligible?" — un-auditable, hallucination-prone, non-reproducible. (b) Fine-tuned classifier — needs labeled data we don't have.

   **Decision 3: Uncertainty as first-class output vs binary yes/no.**
   - Chose: 4-state status (`QUALIFIES / DOES_NOT_QUALIFY / ALMOST_QUALIFIES / UNCERTAIN`) + confidence breakdown.
   - Rejected: binary — loses critical information, creates false confidence that harms users.

3. **Two most critical production-readiness gaps:**

   **Gap 1: Rule freshness.** We fetch once; government rules change via notification/PIB release. In production we'd need a scheduled re-fetcher + diff detector + human review loop. Proposed: weekly CRON → if source_text for any rule changes, flag the scheme as `stale` and require re-verification before use.

   **Gap 2: State-level variation.** Central schemes have state-specific implementation differences (land-record systems, domicile proofs, BPL lists). We model 18 central schemes at the national level only. Production needs per-state overrides layered on top. Proposed: `schemes/<id>/<state>.yaml` override files merged at eval time.

**Deliverable 6 complete.** Commit. Tag `v1.0-submission`.

---

## 11. Prompt Engineering Patterns

Every prompt must follow these principles. Store each prompt template as a file in `conv/prompts/` so you can iterate without hunting through code.

### 11.1 Rule Extraction Prompt (Sarvam-30B, think mode)
```
SYSTEM:
You are a careful legal-document parser extracting eligibility rules from Indian
government welfare scheme guidelines. Your output will be reviewed by a human,
then fed into a deterministic rule engine that affects real citizens' access to
government benefits. Precision matters more than recall. If you are unsure,
emit the rule with confidence: "low" and ambiguity_flags, DO NOT GUESS.

HARD RULES:
1. Every rule's `source_text` field MUST be a verbatim substring of the input document.
2. Never paraphrase source_text. Copy it exactly (whitespace may be normalized).
3. Use the closed ambiguity_flag vocabulary: UNDEFINED_TERM, STATE_DEPENDENT,
   DISCRETIONARY, CONFLICTING_SOURCES, OUTDATED_SOURCE, NEEDS_HUMAN.
4. If a criterion is expressed vaguely ("suitable", "appropriate", "as may be
   prescribed"), emit it with confidence: "low" and flag DISCRETIONARY.
5. Return ONLY valid JSON matching the schema below. No prose before/after.

SCHEMA:
{ "scheme_id": str, "rules": [{
    "id": str, "type": "inclusion"|"exclusion"|"mandatory_doc",
    "predicate": str, "description": str, "source_text": str,
    "confidence": "high"|"medium"|"low", "ambiguity_flags": [str],
    "ambiguity_notes": str|null }] }

PREDICATE LANGUAGE:
  Operators: == != < <= > >= AND OR NOT IN BETWEEN
  Variables: use snake_case. Prefer canonical names from this list: <paste list>

USER:
Scheme: {scheme_name}
Source document (markdown):
<<<
{source_markdown}
>>>

Extract all eligibility rules. Remember: source_text must be a verbatim substring.
```

### 11.2 Self-Critique Prompt (same model, think mode)
```
SYSTEM:
You extracted these rules from a scheme document. Audit your own output.
For each rule, verify: (1) does source_text actually appear verbatim in the
source? (2) does the predicate logically encode the source_text? (3) is any
term in the predicate undefined in the source?

Return JSON: [{rule_id, grounded: bool, logically_correct: bool,
               undefined_terms: [str], issue: str|null}]

USER:
Source:
<<< {source_markdown} >>>

Rules:
{extracted_rules_json}
```

### 11.3 NLU Slot-Filler (Sarvam-M, non-think, temperature=0.3)
```
SYSTEM:
You are KALAM's slot-filler for government scheme eligibility. Extract ONLY
explicitly stated values from the user's message. The user may write in English,
Hindi, Hinglish, or code-mixed text.

HARD RULES:
1. Do NOT invent values. If not explicitly stated, it is UNKNOWN.
2. Do NOT infer from stereotypes (don't assume male farmer if "kisan").
3. Output JSON only. No prose.
4. If user expresses uncertainty ("shayad", "maybe", "pata nahi"), set UNKNOWN
   and add a clarifications_needed entry.
5. If user contradicts a previously-known value, flag it in contradictions.

Slot schema:
{ age: int?, sex: "M"|"F"|"other"|null, state: str?, ... (full list) }

Previous known values: {current_slots_json}

USER:
{user_utterance}

Output:
{"extracted": {...}, "contradictions": [...], "clarifications_needed": [...]}
```

### 11.4 Follow-up Question Generator (Sarvam-M, temperature=0.4)
```
SYSTEM:
You are KALAM. Ask ONE short follow-up question to fill the most informative
missing slot. Match the user's language register (Hinglish if they wrote Hinglish).
Offer 2-4 answer options if the slot is categorical.

HARD RULES:
- Max 25 words in the question.
- No scheme names yet (we're still eliciting).
- No medical/financial advice.

Missing slot: {slot_name}
User's register (detected): {register}

Output JSON: {"question": str, "options": [str] | null}
```

### 11.5 Explanation Generator (Sarvam-M, temperature=0.3)
Given an `EngineOutput`, produce a natural-language explanation for the user. **Must cite rule IDs in parentheses so anyone can audit against the YAML.** Never summarize in a way that hides uncertainty — if status is UNCERTAIN, say so plainly.

### 11.6 General Prompt Hygiene
- Always lead with `SYSTEM:` role establishing the job, the stakes, and the output contract.
- Hard rules in numbered list, negative framing ("do NOT").
- End with `Output:` showing the exact JSON shape expected.
- For structured output, include 1 example in the system prompt if the schema is non-trivial.
- Use `temperature=0.1` for anything feeding the rule store; `0.3` for NLU; `0.4–0.5` for user-facing natural language.
- Never put user data in the system prompt; it goes in the user turn.

---

## 12. Prompt Log Format (25% of score)

Directory: `prompt_log/YYYY-MM-DD/NNN_<short_name>.md`. One file per LLM call. Index in `prompt_log/README.md`.

**Each file:**
```markdown
# 042 — Extract rules for PMAY-G
Date/Time (IST): 2026-04-18 14:32
Model: sarvam-30b
Temperature: 0.1
Thinking mode: on

## Purpose
Extract eligibility rules from the PMAY-G operational guidelines PDF.

## Prompt
<full system prompt + user prompt, verbatim>

## Output (raw)
<full model response, verbatim>

## Reasoning (from think block if present)
<verbatim>

## Outcome
[kept | modified | discarded]

## Why
- Kept rules PMAYG_R001..R006 — source_text verified, passed self-critique.
- Modified R007 — predicate `num_rooms < 2` was too strict; source says "kutcha
  house" which is a structural not a count criterion. Changed to `house_type == 'kutcha'`.
- Discarded R009 — model hallucinated a rule about "beneficiary must be BPL" that
  does NOT appear in the source text. Flagged as hallucination.

## Diff from previous attempt (if any)
<only if this is a retry>
```

**Index file** (`prompt_log/README.md`) — auto-generate from the individual logs:
| # | Date | Model | Purpose | Outcome | File |
|---|------|-------|---------|---------|------|
| 001 | 2026-04-17 | sarvam-m | Smoke test | kept | [link] |
| 002 | 2026-04-17 | sarvam-30b | Extract PM-KISAN | kept (partial) | [link] |
| ... |

**Non-negotiable:** log discarded prompts and outputs too. If the grader cannot see what you threw away, you lose the grade.

---

## 13. Testing Requirements

### 13.1 Unit Tests
- **One test file per scheme** (`tests/test_rules_<scheme>.py`) with at least 5 cases: 1 clean pass, 1 clean fail (each type of exclusion), 1 boundary case, 1 with UNKNOWN input, 1 with ambiguous input.
- **Engine core tests** (`tests/test_engine.py`): predicate parser correctness, three-valued logic (`true/false/UNKNOWN`), confidence formula exact arithmetic.
- **Grounding validator test** (`tests/test_grounding.py`): every `source_text` in every YAML file is a substring of its cached source.

### 13.2 Integration Tests
- **10 adversarial profiles** (`tests/test_edge_cases.py`) — each profile, each expected outcome. If any profile changes behaviour, you must investigate whether the rules were wrong or the test was wrong; never "fix" the test without understanding.

### 13.3 NLU Tests
- **Hinglish test set** (`tests/test_nlu_hinglish.py`): at least 30 hand-written utterances in mixed Hindi-English covering every slot. Assert the NLU extracts the expected structured values.
- These are LLM-backed so allow some drift — assert the core slot is correct, not the exact JSON.

### 13.4 Manual QA (before submission)
- Walk through a full CLI session end-to-end in Hinglish. Record the transcript. Attach to submission.
- Verify every scheme YAML has `verified_by_human: true` and the verifier's notes are real.

### 13.5 CI Gate
A single `make test` or `pytest` run must:
- Execute all unit + integration tests.
- Run the grounding validator across every YAML.
- Fail loudly if any YAML has `verified_by_human: false`.

**No submission with failing tests.**

---

## 14. Frontend

**Frontend work is scoped to a separate file: `frontend.md`.**

When you finish the CLI in Phase 8 and are ready to build a web UI, read `frontend.md` and follow it. This file only specifies the API the frontend will consume.

**Backend API surface for the frontend** (FastAPI — minimal):
```
POST /session          → start new session, returns session_id
POST /session/{id}/turn
  body: { "utterance": "main kisan hoon, rajasthan se" }
  → { "reply": "...", "options": [...]|null, "slots_known": {...},
      "slots_missing": [...], "ready_to_match": bool }
POST /session/{id}/match
  → EngineOutput (see Phase 6 schema)
GET  /schemes          → list of 18 schemes with summary + application URLs
GET  /schemes/{id}     → full scheme YAML as JSON
GET  /ambiguity-map    → ambiguity map as structured JSON
```

Keep the backend FastAPI server in `api/server.py`. CORS enabled for local dev.

---

## 15. Final Deliverables Checklist (Submission Gate)

Cross-reference to the brief's checklist:

- [ ] **Structured eligibility rules for 15+ central schemes** → `schemes/*.yaml`, all with `verified_by_human: true`.
- [ ] **Ambiguity map** → `docs/ambiguity_map.md` with Contradictions, Overlaps, Undefined Terms, State-Dependent Rules sections.
- [ ] **Working matching engine with explainable confidence scores** → `engine/` module, every output includes `confidence_breakdown` and rule-level `rules_evaluated` trace.
- [ ] **Ten adversarial edge-case profiles with documented results** → `edge_cases/profiles.yaml` + `edge_cases/results.md`.
- [ ] **Conversational interface supporting Hinglish natural language input** → `conv/cli.py` (mandatory) + optional web UI per `frontend.md`.
- [ ] **Architecture document with system diagram and technical decisions** → `docs/architecture.md` with mermaid diagram + 3 decisions (with rejected alternatives) + 2 production gaps.
- [ ] **Prompt log** → `prompt_log/` directory + index README, every single LLM call, kept/modified/discarded with reasons.
- [ ] **`PROJECT_STATE.md`** — current, with all schemes verified and tests passing.
- [ ] **All tests passing** — `pytest` green.
- [ ] **CLI transcript** of an end-to-end Hinglish session attached as `docs/demo_transcript.md`.

**One last paranoid check before you submit:** pick 3 random rules from 3 random scheme YAMLs and manually verify the `source_text` against the live official source. If any has drifted, fix and re-verify everything. Government data is genuinely messy — rules you extracted on day 1 may have changed by day 5.

---

## 16. Appendix — Starter Prompts to Fire Today

### A. First Sarvam smoke test
```python
from conv.sarvam_client import chat
r = chat([{"role": "user", "content": "Namaste! Ek line mein apna parichay do."}],
         model="sarvam-m", temperature=0.3)
print(r["choices"][0]["message"]["content"])
```
Log this as `prompt_log/2026-04-18/001_smoke.md`.

### B. First scheme extraction (PM-KISAN)
1. Fetch `https://pmkisan.gov.in/Documents/RevisedFAQ.pdf` → cache.
2. Split into 10-page chunks, send to Sarvam Document Intelligence → `md`.
3. Concatenate markdown.
4. Fire Section 11.1 prompt with `scheme_name = "PM-KISAN"` and the markdown.
5. Save raw output to `schemes/_raw/pm_kisan.json`.
6. Fire Section 11.2 self-critique prompt.
7. Drop rules flagged `grounded: false`.
8. Manually review and promote to `schemes/pm_kisan.yaml`.
9. Log every call with outcomes.
10. Update `PROJECT_STATE.md`.

### C. Rubber-duck before you build
Before writing any code, open `PROJECT_STATE.md` and write — in one paragraph — what "done" looks like for this phase. If you can't define done, you're not ready to start.

---

## 17. The Evaluator Will...

...feed your engine profiles it designed to break you. They will specifically test whether your system **flags ambiguity instead of fabricating a confident answer**. Re-read Section 9 before submission. A system that says "I don't know, and here's exactly why" on a genuinely ambiguous case scores higher than one that confidently returns the wrong answer. Design for that graders's eye.

Good luck. Build carefully. Citizens are counting on this being right.

— End of plan —
