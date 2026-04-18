# 🗺️ Ambiguity Map — Cross-Scheme Contradictions & Overlaps

> **Scope**: 30 central government welfare schemes  
> **Last Updated**: April 2026  
> **Engine**: KALAM Welfare Eligibility Intelligence  

---

## 📊 Summary at a Glance

| Category | Count | Details |
|:---------|:-----:|:--------|
| 🔗 Scheme Overlaps | **2** | PM-KISAN ↔ PM-KISAN Mandhan auto-opt |
| ⚠️ Ambiguity Flags | **12** | 9 STATE_DEPENDENT · 2 UNDEFINED_TERM · 1 DISCRETIONARY |
| 🔄 Prerequisite Chains | **3** | PM-KISAN, PMJJBY, PMSBY → all soft-require PMJDY |
| ❌ Contradictions | **0** | No direct logical contradictions detected |

---

## 1. 🔗 Scheme Overlaps

### PM-KISAN ↔ PM-KISAN Mandhan (PM-KMY)

```
PM-KISAN (₹6,000/yr income support)
       │
       └──── auto-opt ────▶ PM-KISAN Mandhan (₹3,000/mo pension at 60)
```

- **Nature**: PM-KISAN beneficiaries are automatically enrolled in PM-KMY pension contributions.  
- **Impact**: A farmer qualifying for PM-KISAN also gets a pension plan — both are returned independently by the engine.  
- **Resolution**: The `prerequisites` field in YAML links these schemes. The engine surfaces both in results.

---

## 2. 🔄 Prerequisite Chains

Several schemes require a basic **bank account** (PMJDY), creating a natural sequencing dependency:

```
                    ┌──────────────────────┐
                    │      PM J D Y        │
                    │  (Bank Account)      │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     ┌────────────────┐ ┌───────────────┐ ┌───────────────┐
     │   PM-KISAN     │ │    PMJJBY     │ │    PMSBY      │
     │ ₹6,000/yr      │ │ Life ₹2L      │ │ Accident ₹2L  │
     └────────────────┘ └───────────────┘ └───────────────┘
```

> All three prerequisites are `soft: true` — they don't block evaluation but are surfaced as recommendations when `has_bank_account == false`.

---

## 3. ⚠️ Ambiguity Flags

### 3.1 `STATE_DEPENDENT` — 9 Flags

Rules where eligibility criteria **vary by state**. The engine evaluates central rules only and flags these for the user.

| # | Scheme | Rule ID | What Varies |
|:-:|:-------|:--------|:------------|
| 1 | DDU-GKY | `DGKY_R003` | Training availability and beneficiary limits |
| 2 | IGNDPS | `DPS_R001` | Disability pension amount (₹300 – ₹1,500) |
| 3 | IGNOAPS | `IGNOAPS_R002` | Old-age pension eligibility thresholds |
| 4 | IGNWPS | `IGNWPS_R001` | Definition of "widow" (remarriage, missing-husband) |
| 5 | KCC | `KCC_R002` | Tenancy documentation — informal tenants often rejected |
| 6 | NRLM | `NRLM_R003` | SHG formation rules and support structures |
| 7 | PMAY-G | `PMAYG_R002` | Housing allotment lists are state-managed |
| 8 | PMJAY | `PMJAY_R001` | Kerala, Delhi etc. extend coverage via state schemes |
| 9 | PMUY | `PMUY_R002` | LPG cylinder subsidy has state-level variations |

> **Future extension**: Load state-specific rule overrides from `state/*.yaml` files.

---

### 3.2 `UNDEFINED_TERM` — 2 Flags

Terms used in official scheme documents that **lack a formal definition**, preventing deterministic evaluation.

| # | Scheme | Rule ID | Undefined Term | Impact |
|:-:|:-------|:--------|:---------------|:-------|
| 1 | PM-KISAN | `PMK_R002` | *"Institutional landholder"* | Source excludes "institutional landholders" but never defines the term. Engine cannot verify. |
| 2 | PMMVY | `PMMVY_R001` | *Gender definition* | Transgender applicants (`sex='other'`) face ambiguity — scheme requires `sex='F'` but does not address transgender individuals. |

> **Engine handling**: Predicates that reference undefined terms return `UNKNOWN`, which reduces the confidence score via the completeness factor.

---

### 3.3 `DISCRETIONARY` — 1 Flag

Rules where eligibility depends on **officer/branch discretion** beyond what the policy text specifies.

| # | Scheme | Rule ID | Discretion Area |
|:-:|:-------|:--------|:----------------|
| 1 | SSY | `SSY_R001` | Single-father or non-natural-guardian cases may require additional documentation at the bank level. |

> **Engine handling**: The engine qualifies legal guardians but surfaces the discretionary flag so the user is aware extra steps may be needed.

---

## 4. ❌ Cross-Scheme Contradiction Analysis

**No contradictions detected** across all 30 schemes.

- ✅ No two schemes have mutually exclusive eligibility criteria that logically conflict  
- ✅ The only overlap (PM-KISAN ↔ PM-KMY) is intentionally complementary  
- ✅ Age ranges are disjoint or overlapping **by design** — see coverage chart below

### Age Coverage Across Schemes

```
Scheme          |10  15  18  20  30  40  50  60  65  70+
PM YASASVI      |████████████████░░░░░░░░░░░░░░░░░░░░░░░  13-22
DDU-GKY         |░░░████████████████████░░░░░░░░░░░░░░░░░  15-35
APY             |░░░░░░████████████████████████░░░░░░░░░░░  18-40
PM-SYM          |░░░░░░████████████████████████░░░░░░░░░░░  18-40
PMJJBY          |░░░░░░████████████████████████████░░░░░░░  18-50
MGNREGA         |░░░░░░████████████████████████████████████  18+
IGNWPS          |░░░░░░░░░░░░░░░░░░░░░░░░░░████████████████  40+
IGNOAPS         |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████  60+
ANNAPURNA       |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████  65+
```

> **No gaps or contradictions** — the portfolio covers ages 13 through 70+ with appropriate overlap in the working-age range (18–60).

---

## 5. 🔬 Methodology

| Step | Method | Tool |
|:-----|:-------|:-----|
| **1. Automated scan** | Parse all 30 YAMLs for `ambiguity_flags`, `overlaps_with`, `prerequisites` | `ambiguity/analyzer.py` |
| **2. Predicate conflict detection** | Compare rule predicates across schemes for logical contradictions | Custom analysis |
| **3. Edge case stress test** | Run 10 adversarial profiles through the engine | `edge_cases/run_tests.py` |
| **4. Human review** | Verify each flag against source documents cited in YAML `sources` field | Manual audit |

---

*Generated from 30 scheme YAML files in `schemes/`. Run `python ambiguity/analyzer.py` to regenerate.*
