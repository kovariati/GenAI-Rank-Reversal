# GenAI-Rank-Reversal v1.0.0

Canonical code, results, and reproducibility release for the peer-reviewed article:

**Kovari, A. (2026). _Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes_. Computers, 15(9), 633.** https://doi.org/10.3390/computers15090633

**Publisher article:** https://www.mdpi.com/2073-431X/15/9/633

GenAI-Rank-Reversal is an auditable methodological and computational framework for comparing Generative AI interventions across assessment regimes. It separates assisted from independent performance, makes the construct/task/assessment conditions explicit, and tests whether intervention orderings can be transported across outcome-elicitation contexts.

## Key scientific findings

- **AI-assisted performance does not by itself establish independent human performance.**
- For task-specific expert-rated **originality**, the unrestricted-minus-learner-first contrast changes from **+0.78** points on the stuffed-bunny improvement task to **−0.73** points on the subsequent vocabulary-game task under the no-AI assessment protocol. The orientation-aware reversal analysis with Holm adjustment across originality and usefulness gives **p = 0.01351**.
- **Usefulness** shows a secondary opposite-sign pattern of **+0.66** and **−0.58**; the same two-outcome Holm-adjusted orientation-safe p value is **0.01351**.
- A three-dimension sensitivity analysis does **not** support an elaboration reversal.
- The task-specific reversal is not interpreted as an isolated causal effect of AI removal because task content, sequence, transfer demands, and AI-access policy change together.
- The ARRP and construct-commensurability gate make assessment-regime assumptions explicit before evidence is pooled or generalized.

## What this release contains

The tagged source repository contains the analysis code, ARRP schema and operational rules, construct-commensurability audit, evidence-synthesis schema audit, provenance metadata, canonical derived outputs, analytical figures, citation metadata, regression tests, and repository-validation tools.

The attached **`GenAI_Rank_Reversal_results_v1.0.0.zip`** contains the complete canonical `results/` directory as a convenient downloadable results package.

Raw third-party participant data are not redistributed. Exact public source locations and access boundaries are documented in `DATA_AVAILABILITY.md` and `THIRD_PARTY_DATA_NOTICE.md`.

## Reproduce or validate

Fast repository validation:

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
```

Key self-contained analyses:

```bash
python code/analyze_wong_direct_reversal.py
python code/analyze_wong_direct_reversal.py --outcomes originality usefulness elaboration --output results/wong_three_dimension_inference.csv --summary results/wong_three_dimension_summary.csv
python code/build_paired_profiles.py --results results
python code/build_paired_rank_evidence.py --results results
python code/assessment_regime_rank_robustness.py
python -m pytest -q
```

See `REPRODUCTION_LEVELS.md`, `README_RUNNING.md`, and `docs/REPRODUCIBILITY.md` for the distinction between self-contained reconstruction, software verification, and raw-dependent regeneration.

## Release asset policy

GitHub automatically provides **Source code (zip)** and **Source code (tar.gz)** for the `v1.0.0` tag. The only custom release asset is `GenAI_Rank_Reversal_results_v1.0.0.zip`.

No custom checksum/hash manifest is published for this release, and the release should **not** be made immutable. This keeps later packaging or documentation corrections possible. Scientific changes should be recorded in `CHANGELOG.md` and, when they alter the scientific release state, should use an updated semantic version.

## Citation

If the scientific framework, analyses, or findings contribute to a new work, cite the peer-reviewed article:

**Kovari, A. (2026). _Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes_. Computers, 15(9), 633.** https://doi.org/10.3390/computers15090633

If the software, schema, or code is directly reused or modified, also cite the software release:

**Kovari, A. (2026). _GenAI-Rank-Reversal_ (Version 1.0.0). GitHub.** https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0

**Repository:** https://github.com/kovariati/GenAI-Rank-Reversal  
**Release:** https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0  
**Article DOI:** https://doi.org/10.3390/computers15090633  
**Publisher article:** https://www.mdpi.com/2073-431X/15/9/633  
**Author ORCID:** https://orcid.org/0000-0003-3521-4757

## Scientific identity

This publication-day release synchronizes the public research object with the published version of record in *Computers*. The release metadata update does not alter the canonical numerical result set represented by the repository. It adds the final journal citation, DOI, publisher link, publication date, version-specific release identity, and downloadable results bundle.
