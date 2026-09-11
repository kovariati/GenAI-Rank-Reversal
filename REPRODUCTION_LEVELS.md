# Reproduction levels

## Level 1 — Smoke and public-repository quality gate
Runs metadata parsing, public-hygiene scans, construct/ARRP validators, genuine mathematical/algorithmic pytest regression tests and headline-result tests. No third-party raw data required.

## Level 2 — Shipped/prepared-artifact validation
Regenerates self-contained direct-reversal, rank-sensitivity, rank-robustness and manuscript-facing paired-evidence outputs from distributed inputs and compares them with canonical results. Rebuilds paired profiles from distributed derived tables.

## Level 3 — Third-party-data regeneration
Requires source data acquired from the original publications/repositories. Re-runs participant-level/public-study analyses and derived profiles. Redistribution restrictions remain in force.

## Level 4 — Optional extensions
Evidence-map updates or additional sensitivity analyses that are not part of the canonical paper reproduction. These must not silently replace the audited result set or, after publication, the `v1.0.0` scientific result set.

## Mathematical and algorithmic regression tests

Run `python -m pytest -q` after installing `requirements-lock.txt`. The audited suite contains 16 genuine pytest tests. They independently check the direct Welch/IUT/Holm logic, Bassner HC3/Welch calculations and source-order preprocessing rule, Wong randomization-statistic identity, Bastani symmetrical preservation rule, rank-robustness algebra, manuscript-facing paired-evidence regeneration, repository-root resolution, bootstrap sign-tail field semantics, stale artifact-name removal, pre-publication release-state semantics, and the separation of descriptive same-sign patterns from population-preservation claims.

The public repository does not redistribute third-party participant-level raw data. Consequently, a clean public validation is not described as a full raw-source rerun of the Wong 99,999-permutation analysis or the Bastani 9,999-replicate Webb wild-cluster analysis.
