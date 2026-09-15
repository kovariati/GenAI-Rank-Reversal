> **Revision scope (2026-09-14).** Current focal inference is task-specific originality with orientation-plus-Holm p=0.01351; usefulness is secondary. No fresh raw-source participant rerun is claimed. Complete Bassner/Cicek/Zhou raw-to-result pipelines are not supplied. Prior raw-analysis descriptions below document archived provenance, not newly executed validation. See `results/revision_validation_scope.json` and `docs/STATISTICAL_SCOPE.md`.

# Reproducibility and audit artifacts

This page indexes the detailed reproducibility records that support the associated manuscript. Machine-readable ledgers, software-conformance evidence, provenance, and extended computational outputs are maintained in the public research repository rather than expanded in the journal article. The article itself retains the scientific definitions, analysis specifications, direct estimates, uncertainty intervals, inferential boundaries, and, in Appendix A only, the composition/scale sensitivity formalism for regime-agnostic ordering under explicit weighting and scale conventions.

## Evidence and reproducibility map

| Evidence object | Canonical repository artifact | Scope |
|---|---|---|
| Construct/task commensurability audit | `results/construct_commensurability_audit.csv` | Three directly paired programs; directional bridge and claim boundary |
| Paired dataset model/sample/exclusion audit | `results/paired_dataset_model_audit.csv` | Analysis samples, exclusions, models, uncertainty logic |
| Paired native-scale inferential evidence | `results/paired_rank_evidence_revised.csv` | Direct contrasts, confidence intervals, sign pattern, population-rank interpretation |
| Seven-synthesis selection rule | `results/meta_analysis_selection_rule.csv` | Frozen reproducible comparator-set inclusion rule |
| Full synthesis-by-ARRP field ledger | `results/meta_analysis_schema_field_audit.csv` | 35 synthesis-by-dimension checks |
| ARRP specification audit | `results/arrp_specification_audit.csv` and `results/arrp_specification_audit_summary.json` | 62 software/specification checks; not human validation |
| ARRP executable feature cases | `results/arrp_executable_feature_tests.csv` | 20 structured cases |
| ARRP metamorphic rule cases | `results/arrp_metamorphic_rule_tests.csv` | 10 controlled-change pairs |
| ARRP worked-outcome traceability | `results/arrp_worked_outcome_examples.csv` | 77 outcome records |
| Master source provenance | `results/source_provenance_master.csv` | 106 provenance objects and redistribution boundaries |
| Rank weighting/scale sensitivity | `docs/RANK_ROBUSTNESS.md`, `code/assessment_regime_rank_robustness.py`, `results/wong_rank_robustness_region.csv` | Machine-readable implementation and extended outputs supporting Appendix A |
| Computational validation | `docs/COMPUTATIONAL_VALIDATION.md`, `tests/test_algorithm_regressions.py`, `tests/test_expected_results.py`, `tools/validate_repository.py` | Mathematical, algorithmic and repository regression checks |
| Public release validation | `docs/PUBLIC_RELEASE_VALIDATION.md` | Consolidated pre-publication validation status and raw-source boundary |
| Conceptual/reusable figures | `tools/build_conceptual_figures.py`, `figures/figure1_structural_rank_transport.*`, `figures/figure2_symmetrical_evidence_rule.*` | The C/Q/E/V structural gate is maintained as a canonical SVG with synchronized PDF/PNG exports; the build tool copies those canonical assets without redrawing them. The symmetrical evidential-rule visualization is generated separately; only the structural gate is used in the revised article |

## Interpretation boundary

The existence of these artifacts does not turn software checks into scientific validation. In particular, ARRP has not undergone independent human inter-rater testing, expert content-validation, psychometric validation, or a consensus process. The synthesis-schema audit is illustrative and does not establish that any meta-analysis pooled incompatible estimands or is biased or invalid.

## Reproduce

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
```

Third-party participant-level data are not redistributed. Full raw-source reruns that require those files must obtain them from the original sources under their original terms.
