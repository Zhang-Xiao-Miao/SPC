# Data Release and Licensing Policy

This note states the artifact release policy for benchmark-derived resources.

## Release Modes

The project distinguishes two release modes:

| Mode | Included | Not Included |
| --- | --- | --- |
| Anonymous review package | Source code, paper-facing tables, raw result JSONs, episode metadata, processed inputs needed for reviewer reproduction, and hash manifests. | No deployment claims and no unrestricted downstream redistribution claim for benchmark-derived assets. |
| Public artifact release | Source code, table-generation scripts, raw outputs when permitted, metadata, hashes, expected directory layout, and preparation scripts. | Upstream benchmark datasets or tests whose redistribution permission is not verified. |

## Conservative Default

For public release, benchmark-derived resources are not redistributed unless upstream terms permit redistribution. When redistribution is not verified or not permitted, the public artifact provides:

- preparation scripts
- provenance notes
- expected directory layout
- file-level hashes when applicable
- metadata needed to regenerate paper-facing tables after the user prepares the upstream data locally

## Current Paper Wording

The manuscript should not say that all benchmark-derived resources are freely redistributable. It should say that the artifact is designed for claim traceability and that public redistribution follows the conservative policy above.

## Public Release Operation

For public release, the maintainer applies the conservative default above: resources without verified redistribution permission are omitted and replaced by scripts, provenance, metadata, expected layout, and hashes. This is a release operation, not a scientific-result dependency.
