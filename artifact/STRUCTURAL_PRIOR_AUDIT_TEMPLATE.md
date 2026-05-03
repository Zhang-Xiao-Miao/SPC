# Structural-Prior Audit Template

Use this template when applying the reporting pattern to a new structural-prior evaluation. It is a template, not a claim that every future study must use this paper's exact benchmark, selector, or fidelity metric.

## 1. Evaluation Target

- Task family:
- Benchmark / split:
- Generator backend:
- Selector:

## 2. Budget Accounting

- Candidate budget:
- Budget split across prior variants:
- Execution calls:
- Prompt tokens matched? yes/no:

## 3. Information Access

| Component | Query-side access | Support-side access | Test access | Diagnostic or deployable? |
| --- | --- | --- | --- | --- |
| Retrieval |  |  |  |  |
| Prompt construction |  |  |  |  |
| Candidate selection |  |  |  |  |
| Solved-count reporting |  |  |  |  |

## 4. Prior Conditions

- `no_prior`:
- intended prior:
- random prior:
- corrupted / misleading prior:
- prompt-only boundary control:

## 5. Results

- Solved tasks:
- Paired improved / regressed / unchanged:
- Task-clustered directionality:

## 6. Replicate Sensitivity, If Making Backend-Level Claims

- Stochastic replicate count:
- Are generation seeds deterministic at the serving backend? yes/no/unknown:
- Candidate-level pass movement:
- Paired changed outcomes:
- Serving format:

## 7. Prior-Quality Response, If Available

- Quality metric:
- Quality coverage:
- Net delta by bin:
- Harm rate:
- Outcome-level fidelity separation:
- Threshold sensitivity:
- All-candidate compile-fail rate:
- Selected-candidate timeout / fail rate:
- Deployable or retrospective?

## 8. Supported Claims

- 

## 9. Unsupported Claims

- 
