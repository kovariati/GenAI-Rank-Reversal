> **Revision scope (2026-09-14).** Current focal inference is task-specific originality with orientation-plus-Holm p=0.01351; usefulness is secondary. No fresh raw-source participant rerun is claimed. Complete Bassner/Cicek/Zhou raw-to-result pipelines are not supplied. Prior raw-analysis descriptions below document archived provenance, not newly executed validation. See `results/revision_validation_scope.json` and `docs/STATISTICAL_SCOPE.md`.

# Method-to-code map

| Scientific component | Public implementation | Canonical output |
|---|---|---|
| Wong direct opposite-sign inference | `code/analyze_wong_direct_reversal.py` | `results/wong_direct_reversal_inference.csv`, `results/wong_direct_reversal_summary.csv` |
| Wong participant-level differential regime change | `code/analyze_wong_participant.py` | `results/wong_randomization_inference.csv`, `results/wong_interaction_model.csv` |
| Differential regime-shift sensitivity | `code/assessment_regime_rank_sensitivity.py` | `results/wong_rank_reversal_sensitivity.csv` |
| Weight/scale rank robustness | `code/assessment_regime_rank_robustness.py` | `results/wong_rank_robustness_region.csv`, `results/wong_rank_robustness_summary.csv` |
| Paired design profiles | `code/build_paired_profiles.py` | `results/paired_supported_independent_profiles.csv` |
| Pairwise assessment-regime rank status | `code/assessment_regime_rank_order.py` | `results/pairwise_rank_transport_status.csv` |
| Construct-commensurability gate | `code/validate_construct_commensurability.py` | `results/construct_commensurability_audit.csv` |
| ARRP operational rules | `code/validate_arrp_operational_rules.py` | `results/arrp_operational_test_cases.csv` |
| ARRP deterministic specification audit | `code/validate_arrp_specification.py` | `results/arrp_specification_audit.csv` |
| Bastani/Kestin/Pardos public-source reproduction | `code/reproduce_public_studies.py` | derived results in `results/` |
