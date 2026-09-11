# Computational validation

The computational code audit validates the mathematics, algorithmic identities, manuscript-facing numerical regeneration, repository path handling, result-status logic, and pre-publication release semantics.

## Regression-test layer

The public test suite contains 16 mathematical/algorithmic regression tests. It covers the Wong direct Welch calculations, intersection-union and Holm logic, participant-level randomization-statistic identity, Bassner HC3 and exact Welch contrasts, the Bastani symmetrical preservation rule, rank-weighting/scale robustness algebra, sensitivity identities, paired-evidence regeneration, Bassner source-order preprocessing behavior, corrected repository-root resolution, descriptive bootstrap-field semantics, stale-artifact prevention, and pre-publication release-state behavior.

Run:

```bash
python -m pytest -q
```

The repository-wide gate additionally checks metadata consistency, dependency locking, public-release hygiene, construct/task eligibility, ARRP specification conformance, expected scientific results, and deterministic regeneration of self-contained outputs:

```bash
python tools/validate_repository.py
```

## Raw-source boundary

The public repository does not redistribute every third-party participant-level source file. Therefore, the public validation is not described as a fresh end-to-end raw-source rerun of analyses such as the Wong 99,999-permutation analysis or the Bastani 9,999-replicate Webb wild-cluster analysis. Their algorithms, derived outputs, source logic, and independent invariants are audited. The Wong direct opposite-sign inference is self-contained and regenerates from released sufficient statistics.

## Scientific boundary

These checks establish computational consistency and software regression protection. They do not establish external validity, construct validity, or human reliability of ARRP.
