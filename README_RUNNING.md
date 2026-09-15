# Running the analyses

## Fast public validation (no third-party raw data)

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
```

## Regenerate the direct Wong reversal from published sufficient statistics

```bash
python code/analyze_wong_direct_reversal.py
```

## Regenerate rank-sensitivity and rank-robustness outputs

```bash
python code/assessment_regime_rank_sensitivity.py results/wong_rank_reversal_sensitivity_input.csv results/wong_rank_reversal_sensitivity.csv
python code/assessment_regime_rank_robustness.py
```

## Regenerate paired profiles and pairwise rank status from shipped derived results

```bash
python code/build_paired_profiles.py --results results
python code/assessment_regime_rank_order.py
```

## Validate construct commensurability and ARRP specification

```bash
python code/validate_construct_commensurability.py
python code/validate_arrp_operational_rules.py
python code/validate_arrp_specification.py
```

## Participant-level Wong analysis

Obtain `Supplemental Data.xlsx` from the public Wong & Qiu OSF source listed in `THIRD_PARTY_DATA_NOTICE.md`, then run:

```bash
python code/analyze_wong_participant.py --raw-xlsx data/raw/Supplemental\ Data.xlsx --results results
```

The supplied algorithm requests 99,999 arm-size-preserving permutations. Its sharp-null and constant-standardization assumptions are documented in `docs/STATISTICAL_SCOPE.md`; the archived run was not freshly rerun in this revision.

## Public-study regeneration

Acquire the Bastani, Kestin and Pardos source files listed in `THIRD_PARTY_DATA_NOTICE.md`, place them in `data/raw/` using the documented local filenames, then run:

```bash
python code/reproduce_public_studies.py --outdir .
```

This step is not required for the fast repository-quality gate because third-party raw data are intentionally excluded from Git.

## Dependency-lock and ARRP-schema checks

```bash
python tools/validate_dependency_lock.py
python tools/validate_arrp_schema.py
```

The dependency-lock validator requires the exact versions in `requirements-lock.txt` to be installed and verifies that every runtime transitive dependency is pinned.

## Three-dimension sensitivity and current scope

```bash
python code/analyze_wong_direct_reversal.py --outcomes originality usefulness elaboration --output results/wong_three_dimension_inference.csv --summary results/wong_three_dimension_summary.csv
```

The existing two-outcome family is retained for the focal report. Complete Bassner/Cicek/Zhou raw pipelines are not supplied; raw-source reproduction cannot be obtained merely by running the general public-study script.

## Revised manuscript-facing figures

After the summary-statistic outputs exist, run `python tools/build_revision_figures.py`. It regenerates the two task-specific originality contrasts and the fixed-point weight/scale illustration. An optional `--manuscript-dir PATH` copies the two analytical PNGs into the LaTeX project. No participant input is required.
