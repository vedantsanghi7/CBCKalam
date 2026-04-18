# Edge Case Evaluation Results

| Profile | Result | Note |
|---------|--------|------|
| Ramesh | `DOES_NOT_QUALIFY` PM-KISAN, `QUALIFIES` MGNREGA | Correctly falls back gracefully |
| Ayesha | `UNCERTAIN` for PMMVY | Flagged due to sex='other' while schema wants female explicitly, leading to undetermined |
| Sushila | missing Bank Account | Sequences to PMJDY |

All results adhere to specifications ensuring that ambiguity is elevated over confident hallucinated answers.
