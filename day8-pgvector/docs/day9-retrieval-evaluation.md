# Day 9 Retrieval Evaluation

## Evaluation summary

- Total questions: 15
- Answerable questions: 12
- Unanswerable questions: 3
- Metric: exact expected-chunk Recall@k

## Recall results

| Metric | Hits | Questions | Recall |
|---|---:|---:|---:|
| Recall@1 | 8 | 12 | 66.67% |
| Recall@3 | 10 | 12 | 83.33% |
| Recall@5 | 11 | 12 | 91.67% |

## Per-question results

| ID | Answerable | Expected chunk | Retrieved chunks | Result |
|---|---|---:|---|---|
| GQ01 | True | [86] | [86, 84, 98, 91, 93] | Hit@5 |
| GQ02 | True | [94] | [94, 84, 98, 91, 86] | Hit@5 |
| GQ03 | True | [101] | [84, 98, 100, 88, 101] | Hit@5 |
| GQ04 | True | [108] | [107, 201, 220, 173, 207] | Miss@5 |
| GQ05 | True | [115] | [115, 117, 103, 113, 220] | Hit@5 |
| GQ06 | True | [122] | [120, 124, 122, 129, 127] | Hit@5 |
| GQ07 | True | [129] | [129, 127, 122, 124, 200] | Hit@5 |
| GQ08 | True | [136] | [136, 134, 157, 152, 151] | Hit@5 |
| GQ09 | True | [144] | [144, 209, 151, 180, 125] | Hit@5 |
| GQ10 | True | [152] | [101, 148, 152, 150, 141] | Hit@5 |
| GQ11 | True | [157] | [157, 158, 155, 185, 138] | Hit@5 |
| GQ12 | True | [165] | [165, 166, 162, 167, 164] | Hit@5 |
| GQ13 | False | [] | [208, 108, 164, 95, 151] | Unanswerable - diagnostic only |
| GQ14 | False | [] | [94, 93, 86, 84, 192] | Unanswerable - diagnostic only |
| GQ15 | False | [] | [124, 120, 125, 122, 94] | Unanswerable - diagnostic only |

## Interpretation

Recall@k measures whether at least one expected chunk appears in the top k results for each answerable question. Unanswerable questions are excluded from the recall denominator. Their nearest distances are recorded separately as a diagnostic; retrieval distance alone does not prove that an answer is safe to provide.

The initial distance threshold used for diagnostic comparison was 0.40. It should be calibrated against the evaluation results rather than treated as a universal cutoff.
