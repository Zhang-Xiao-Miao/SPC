# Reviewer Workflow

This guide is organized around the three questions an E&D artifact reviewer is likely to ask.

## 1. What is this project and what is the contribution?

Read:

```bash
cat README.md
cat artifact/PROJECT_GUIDE_FOR_REVIEWERS.md
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

Short answer: SPC-Audit is a diagnostic reporting pattern for structural-prior claims in execution-evaluated code generation. The main claim is quality-conditioned evaluation: a structural prior should not be evaluated only by average prior-vs-no-prior delta; reviewers should also see prior-quality coverage, quality-conditioned net delta, harm rate, information access, selector status, and explicit non-claims.

The expert-edited paper source is:

```text
neurips2026_ed_latex_source_FINAL_v2/paper.tex
```

## 2. Can I quickly verify the paper's numeric claims?

Run:

```bash
bash artifact/reviewer_audit.sh
```

This is the most important reviewer command. It reads packaged raw-result JSONs and checks:

- main fair-budget result: `178.67 -> 185.00`;
- paired query-seed directionality: `30 improved / 11 regressed`;
- task-clustered sensitivity: `14 positive / 5 negative / 205 zero`;
- full prompt-only structural boundary: `179.33` vs `177.67`;
- prior-quality response: medium/high `multi_prior` coverage `0.469`, `23 improved / 6 regressed / net +17`;
- bad-prior harm: random net `-19`, corrupted net `-16`;
- explicit non-claims.

Unlike a plain PASS-only script, this command prints the numbers and their interpretation before asserting them.

## 3. Can I regenerate paper-facing artifacts?

Run:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

`reproduce_main.sh` regenerates derived tables from cached results. `verify_provenance.sh` checks that the prompt-only structural matcher uses only query prompt / entry point on the query side and that the prior-quality audit reads stored `structure_fidelity` fields.

For interpretation of PASS messages and non-claims, read:

```bash
cat artifact/OUTPUT_INTERPRETATION_GUIDE.md
```

## 4. Can I run project code locally?

Optional smoke test:

```bash
bash artifact/run_smoke_test.sh
```

This builds a one-task synthetic fixture and runs the real pipeline twice with the non-LLM `retrieval_edit` backend. It proves the code path executes locally. It is not paper evidence.

## 5. Can I rerun the real experiments?

Read:

```bash
cat artifact/LIVE_RERUN_GUIDE.md
cat artifact/FULL_REPRODUCTION_GUIDE.md
cat artifact/SOURCE_AND_DATA.md
cat artifact/ENVIRONMENT.md
bash artifact/check_live_rerun_prereqs.sh
```

Full live reruns require upstream benchmark assets and matching model endpoints or local models. They are not part of the default quickstart because they call LLMs and execute generated Python code.
