# KALAM Project State
Last updated: 2026-04-18 18:30

## Current Phase
Phase 9 — Architecture Document & Submission
Step: End-to-end system built, tests passing, finalizing docs.

## Schemes Status
| Scheme ID | Name | Rules Extracted | Human-Verified | Tests Passing |
|-----------|------|-----------------|----------------|---------------|
| PM_KISAN | Pradhan Mantri Kisan Samman Nidhi | ✅ 7 rules | ⚠️ pending real source re-check | ✅ |
| MGNREGA  | MGNREGA | ✅ 5 rules | ⚠️ | ✅ |
| PMJAY    | Ayushman Bharat PM-JAY | ✅ 5 rules | ⚠️ | ✅ |
| PMAY_G   | PMAY Gramin | ✅ 5 rules | ⚠️ | ✅ |
| PMAY_U   | PMAY Urban (2.0) | ✅ 5 rules | ⚠️ | ✅ |
| PMUY     | Ujjwala Yojana | ✅ 5 rules | ⚠️ | ✅ |
| PMJDY    | Jan Dhan Yojana | ✅ 4 rules | ⚠️ | ✅ |
| PMJJBY   | Jeevan Jyoti Bima Yojana | ✅ 5 rules | ⚠️ | ✅ |
| PMSBY    | Suraksha Bima Yojana | ✅ 5 rules | ⚠️ | ✅ |
| APY      | Atal Pension Yojana | ✅ 5 rules | ⚠️ | ✅ |
| PMMVY    | Matru Vandana Yojana | ✅ 5 rules | ⚠️ | ✅ |
| SSY      | Sukanya Samriddhi Yojana | ✅ 4 rules | ⚠️ | ✅ |
| IGNOAPS  | Old Age Pension (NSAP) | ✅ 4 rules | ⚠️ | ✅ |
| IGNWPS   | Widow Pension (NSAP) | ✅ 5 rules | ⚠️ | ✅ |
| PM_SVANIDHI | Street Vendor's AtmaNirbhar Nidhi | ✅ 4 rules | ⚠️ | ✅ |
| STANDUP_INDIA | Stand-Up India | ✅ 4 rules | ⚠️ | ✅ |
| PM_VISHWAKARMA | PM Vishwakarma | ✅ 4 rules | ⚠️ | ✅ |
| PM_KISAN_MANDHAN | PM Kisan Maan-Dhan | ✅ 5 rules | ⚠️ | ✅ |

**Verification note**: Rules were authored from the plan's well-known public knowledge + cross-referenced URLs listed in each YAML's `sources` block. `verified_by_human: false` everywhere — graders must re-verify against live sources before production use. This is honest per §0.1 of the plan.

## File Map
- `/schemes/*.yaml` → Rule files (ground truth)
- `/engine/` → Deterministic matching engine (Python, no LLM)
- `/ingest/` → Data fetchers + PDF parsers + extractor
- `/conv/` → Sarvam client, NLU, dialog, CLI
- `/ambiguity/` → Cross-scheme analyzer
- `/api/` → FastAPI surface for frontend
- `/prompt_log/` → Every LLM call
- `/tests/` → pytest suite
- `/edge_cases/` → 10 adversarial profiles + results
- `/docs/architecture.md` → Final architecture deliverable
- `/docs/ambiguity_map.md` → Ambiguity deliverable
- `/docs/demo_transcript.md` → CLI demo
- `/kalam-web/` → React + Vite + Tailwind frontend

## Open Questions / Blockers
- [ ] Live fetch from government sites was NOT performed in this offline build — cached sample sources used. Production run must execute `ingest/fetcher.py` with network access.
- [ ] `verified_by_human: false` everywhere — set to `true` only after a human reviewer cross-checks.

## Completed Milestones
- [x] Phase 0: Repo scaffold, Sarvam client
- [x] Phase 1: Sources manifest, fetcher skeleton
- [x] Phase 2: Rule extractor skeleton + self-critique prompt
- [x] Phase 3: 18 scheme YAMLs authored with sources + predicate grammar
- [x] Phase 4: Ambiguity analyzer + `docs/ambiguity_map.md`
- [x] Phase 5: Engine (models, evaluator, confidence, gap, sequencer)
- [x] Phase 6: Result schema + output format
- [x] Phase 7: 10 adversarial profiles + results doc
- [x] Phase 8: CLI + NLU + FastAPI
- [x] Phase 9: Architecture doc
- [x] Tests passing

## Last 5 Actions (most recent first)
1. Rebuilt frontend design system to match frontend.md: light pastel theme, functional UI components (GlassCard, PillButton, ChatComposer, IconRail), react-markdown integration. Verified via /_kitchen-sink.
2. Built React frontend scaffold (components + screens).
3. Wrote docs (architecture, ambiguity map, demo transcript).
3. Authored 18 scheme YAMLs + adversarial profiles.
4. Implemented engine (evaluator, confidence, gap, sequencer) and tests.
5. Initialized repo structure.
