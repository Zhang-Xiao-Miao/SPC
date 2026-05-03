# Figure 1 Concept

## Caption Draft

**Figure 1: Fair-budget diagnostic audit changes the claim about structural priors.**
Panel A shows the earlier uncontrolled comparison, where structural conditioning and execution-selection opportunity change together and the apparent gain is large (`167/224 -> 184/224`). Panel B shows the fair-budget diagnostic comparison, which matches candidate budget and execution-call accounting while keeping `MBR-exec` fixed across prior conditions; the claim narrows to a modest effect in fixed code-aware `syntax_aware` episodes (`178.67 +/- 0.58 -> 185.00 +/- 1.73`). Panel C shows the information-access boundary: the full `MBPP+224` prompt-only structural rerun is non-positive, and the retrospective prior-quality audit shows that high-fidelity priors are rare in that setting. The takeaway is that evaluation design, information access, and prior quality determine which structural-prior claim is warranted.

## Visual Specification

Panel A:

- label: `Uncontrolled comparison`
- arrows from `no prior / no rerank` to `multi prior / MBR-exec`
- callout: `structural conditioning and execution-selection opportunity change together`
- headline number: `167/224 -> 184/224`

Panel B:

- label: `Fair-budget diagnostic comparison`
- fixed boxes: `candidate budget`, `execution-call accounting`, `MBR-exec`
- vary only prior condition: `no_prior`, `single_prior`, `multi_prior`, `random_prior`, `corrupted_prior`
- headline number: `178.67 +/- 0.58 -> 185.00 +/- 1.73`

Panel C:

- label: `Information-access and prior-quality boundary`
- left mini-table: full prompt-only structural control, `179.33 +/- 2.31 -> 177.67 +/- 1.53`
- right mini-table: prior-quality audit, `multi_prior` medium/high fidelity bins positive in code-aware episodes; high-fidelity cases rare in prompt-only full rerun
- callout: `quality- and information-access-conditioned claim`

Footer takeaway:

- `do not generalize code-aware diagnostic evidence into deployable prompt-only retrieval`
