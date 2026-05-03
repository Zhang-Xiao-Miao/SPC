# Information Access Card

Use this card to disclose what information each component can see. A structural-prior result has different meaning depending on whether it uses prompt-only information, stored query code, tests, generated outputs, or execution feedback.

| Component | Query prompt | Query solution code | Query tests | Support prompt | Support code | Generated outputs | Execution feedback | Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Main `syntax_aware` retrieval | yes | yes, stored query code fields | no | yes | yes | no | no | code-aware diagnostic retrieval |
| Prompt-only lexical retrieval | yes | no | no | yes | no | no | no | prompt-only boundary |
| Prompt-only structural retrieval | yes, plus entry point | no | no | yes | yes, support-side only | no | no | prompt-only query-side boundary |
| Prior construction: `single_prior` / `multi_prior` | yes | depends on retrieval regime | no | yes | support-side structure when available | no | no | prior construction under disclosed access |
| `random_prior` | no query solution use beyond diagnostic setup | diagnostic stress condition | no | support pool / random prior source | may use support-side structure | no | no | bad-prior control |
| `corrupted_prior` | oracle-derived before corruption | yes, diagnostic/oracle-derived before corruption | no | support-side diagnostic source | yes | no | no | diagnostic stress test, not deployable |
| Generator | prompt text provided by condition | no direct hidden access | no | prompt-provided examples only | prompt-provided summaries only | no | no | candidate generation |
| `MBR-exec` selector | selected candidates | no | yes, packaged task tests | no | no | yes | yes | same-test diagnostic selector, not deployable |
| Solved-count reporting | generated selected output | reference/test oracle for evaluation | yes | no | no | selected output | pass/fail execution | reporting metric |
| `structure_fidelity` audit | reference-code structure | yes, retrospective | no selection use | prior summary | prior summary | no | no | retrospective diagnostic stratifier, not deployable |

## Interpretation

- The main `syntax_aware` result is code-aware diagnostic evidence.
- Prompt-only conditions exclude query solution code on the query side.
- `MBR-exec` is same-test diagnostic selection, not deployable reranking.
- `structure_fidelity` is retrospective/reference-code-based and is not used for generation, selection, or tuning.
- `corrupted_prior` is oracle-derived before corruption and is a diagnostic stress test.
