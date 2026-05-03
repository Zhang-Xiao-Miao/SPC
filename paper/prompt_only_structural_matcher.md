# Prompt-Only Structural Matcher Specification

This file documents the fixed `prompt_structural` retrieval control used for the prompt-only boundary experiments. The implementation lives in `retrieval/prompt_structural.py`.

## Purpose

The matcher tests whether a structural-prior signal can be constructed without query solution code. It is a boundary control, not a new prior-construction method.

## Query-Side Access

The query side uses only:

- task prompt text
- entry point name

The query side does not use:

- query solution code
- query reference-code structure
- public or private tests
- generated candidates
- execution outcomes

## Support-Side Access

The support side may use training-pool fields:

- support prompt text
- support entry point
- support code structure extracted from training examples

This support-side structure is allowed because support examples come from the training pool, not from evaluation-task solutions.

## Features

The matcher builds deterministic prompt-intent tags from query prompt and entry point. The current tag set includes coarse domains, data structures, operations, and control-flow hints inferred from prompt tokens, such as:

- string, sequence, matrix, dictionary, set, tuple
- sort, count, predicate, transform, aggregate
- number theory, recursion, regular-expression style tasks
- loop, conditional, nested-loop, comprehension-style hints

For support examples, the matcher combines prompt-intent tags with AST-derived support-code tags:

- API calls
- control-flow constructs
- data-structure constructs
- signature argument count
- coarse AST skeleton hints

## Scoring

The ranking score is fixed as:

`0.45 * lexical_cosine + 0.20 * prompt_intent_jaccard + 0.35 * structural_tag_jaccard`

The constants are defined in `retrieval/prompt_structural.py`.

## Provenance and Tuning Boundary

- Code path: `retrieval/prompt_structural.py`.
- Documentation path: `paper/prompt_only_structural_matcher.md`.
- Pre-run plan path: `paperB/prompt_only_structural_control_plan.md`.
- The formula and constants in `retrieval/prompt_structural.py` are the fixed matcher used for the prompt-only structural controls; they were not changed to select the reported full `MBPP+224` outcome.
- The same matcher implementation is used for the `MBPP+100` prompt-only structural slice and the full `MBPP+224` prompt-only structural rerun.
- The full `MBPP+224` rerun uses the same fixed formula as the earlier prompt-only structural control: `0.45 * lexical_cosine + 0.20 * prompt_intent_jaccard + 0.35 * structural_tag_jaccard`.
- The reported full `MBPP+224` rerun is not selected from an alternative-weight sweep.
- No alternative-weight sweep is part of the canonical artifact or claim-to-evidence package.
- The matcher uses deterministic features only; it does not use query solution code, tests, generated candidates, execution feedback, or outcome labels.
- The paper treats this as a boundary control. It does not claim that these weights are optimal or that the matcher solves high-quality prompt-only prior construction.

## Reporting Boundary

The same matcher design is used for the `MBPP+100` prompt-only structural slice and the full `MBPP+224` prompt-only structural rerun. The full rerun is non-positive, so this matcher does not support deployable prompt-only structural retrieval. Its role is to bound the main code-aware diagnostic result.
