# Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes

[![DOI](https://img.shields.io/badge/DOI-10.3390%2Fcomputers15090633-blue)](https://doi.org/10.3390/computers15090633)
[![Release](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Official code, results, and reproducibility repository for the peer-reviewed article:

**Kovari, A. (2026). _Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes_. Computers, 15(9), 633.** https://doi.org/10.3390/computers15090633

- **Canonical DOI:** https://doi.org/10.3390/computers15090633
- **Publisher article:** https://www.mdpi.com/2073-431X/15/9/633
- **Canonical repository:** https://github.com/kovariati/GenAI-Rank-Reversal
- **Canonical software release:** https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0
- **Results asset:** https://github.com/kovariati/GenAI-Rank-Reversal/releases/download/v1.0.0/GenAI_Rank_Reversal_results_v1.0.0.zip
- **Author ORCID:** https://orcid.org/0000-0003-3521-4757
- **Published:** 19 September 2026
- **Preferred scholarly citation:** the peer-reviewed journal article above
- **Machine-readable citation:** `CITATION.cff`, `CITATION.bib`, `CITATION.ris`

If the scientific framework, analyses, or findings contribute to a new work, cite the peer-reviewed article. If the software, schema, or code is directly reused or modified, also cite the `v1.0.0` software release and follow the repository license guidance.

## What this project is

This repository accompanies a methodological study of how comparative conclusions about Generative AI interventions can depend on the conditions under which outcomes are elicited. The framework separates the target construct, task/content, assessment conditions, and verification evidence before intervention rankings are compared across regimes.

The contribution is a methodological framework and retrospective secondary analysis, not a new statistical method. The focal empirical reconstruction concerns the Wong–Qiu comparison of unrestricted ChatGPT and learner-first AI across two named creativity tasks. The repository also provides the executable **Assessment-Regime Reporting Profile (ARRP)**, construct-commensurability checks, evidence-synthesis audits, sensitivity analyses, provenance records, and deterministic software-validation tests.

## Article-linked findings represented in this repository

- **AI-assisted performance alone does not establish independent human performance.** Comparative claims depend on the assessment regime in which the outcome is elicited.
- For task-specific expert-rated **originality**, the unrestricted-minus-learner-first contrast is **+0.78** points on the stuffed-bunny improvement task and **−0.73** points on the subsequent vocabulary-game task under the study's no-AI assessment protocol. After accounting for both possible reversal orientations and applying Holm correction across the retained originality/usefulness family, the adjusted **p value is 0.01351**.
- **Usefulness** provides a secondary opposite-sign pattern, with contrasts of **+0.66** and **−0.58**, respectively; the corresponding Holm-adjusted value after accounting for both reversal orientations is also **p = 0.01351**.
- A separate three-dimension sensitivity analysis does **not** support an elaboration reversal. The corresponding **orientation-plus-Holm p value is 0.92891**.
- The task-specific reversal does not identify an isolated causal effect of AI removal because task content, sequence, transfer demands, and AI-access policy change together.
- The construct-commensurability gate prevents shared labels from being treated automatically as evidence of a common construct or common estimand. ARRP provides an executable reporting structure, but it is not presented as an independently validated psychometric instrument or consensus standard.

## Scientific scope and interpretation

The focal endpoint is **expert-rated originality of submitted products** in two named tasks. It is not a measure of general creativity or durable learning. The same 1–7 rating labels and high within-task rater agreement do not establish cross-task measurement invariance. Ratings were relative to each task's product pool, and the intervention packages differ in their AI-access schedules and task sequence.

The source Wong–Qiu experiment already reported an interaction and opposite active-arm task comparisons. This repository does not claim discovery of a new interaction, a new statistical test, or a general creativity/learning effect. It provides an auditable assessment-regime comparison workflow, explicit outcome scope, established inference, and reproducible evidence-synthesis checks.

Canonical methodological boundaries used throughout the repository are:

- The focal Wong–Qiu result concerns task-specific expert-rated originality, not general creativity or durable learning.
- Rank preservation across assessment contexts cannot be inferred from randomization alone.
- Differences in outcome-elicitation context can create estimand heterogeneity before statistical heterogeneity is modeled.

## ARRP and comparison gate

[`docs/ARRP.md`](docs/ARRP.md) and [`arrp.schema.json`](arrp.schema.json) define the Assessment-Regime Reporting Profile. The implementation separates outcome conditions A–D–O–G from evidence of non-use N and applies an explicit construct-commensurability gate before rank labels are assigned.

The validation layer contains **62 deterministic ARRP specification checks**, **20 executable cases**, **10 metamorphic pairs**, and **77 worked records**. These checks establish software/specification conformance, not independent content validity or inter-rater reliability.

## Repository contents

```text
GenAI-Rank-Reversal/
├── README.md                     Scientific landing page and citation funnel
├── PROJECT_METADATA.json         Canonical project/article metadata source
├── CITATION.cff                  GitHub-native citation metadata
├── CITATION.bib                  BibTeX article/software citation export
├── CITATION.ris                  RIS article/software citation export
├── codemeta.json                 CodeMeta 3.1 research-software metadata
├── ARTICLE_METADATA.json         Schema.org article metadata
├── llms.txt                      Supplementary machine-readable project index
├── DATA_AVAILABILITY.md          Public data sources and reuse boundaries
├── THIRD_PARTY_DATA_NOTICE.md    Third-party source and redistribution policy
├── REPRODUCTION_LEVELS.md        Self-contained, software, and raw-dependent levels
├── README_RUNNING.md             Detailed execution instructions
├── CONTRIBUTING.md               Contribution guidance
├── SECURITY.md                   Security reporting policy
├── GITHUB_SETTINGS_CHECKLIST.md  About/Website/Topics/social-preview settings
├── CHANGELOG.md                  Version and release history
├── assets/                       GitHub social-preview assets
├── code/                         Analysis and validation programs
├── results/                      Canonical machine-readable derived results
├── figures/                      Article-linked analytical/conceptual figures
├── docs/                         Methods, provenance, validation, and reuse guides
├── tests/                        Mathematical/algorithmic regression tests
├── tools/                        Metadata, release, and repository validation tools
└── .github/                      Issue templates and repository-quality workflow
```

The public tree intentionally excludes submission-system files, reviewer correspondence, local environments, caches, credentials, and third-party raw participant data.

## Quick start

Validated runtime: **Python 3.13.5**.

```bash
python -m venv .venv
# activate the environment for the local platform
python -m pip install --upgrade pip
pip install -r requirements-lock.txt
python tools/validate_repository.py
```

The full repository gate verifies metadata consistency, dependency closure, ARRP schema/specification conformance, construct-commensurability rules, deterministic regeneration of self-contained results, expected numerical values, and the 56-test mathematical/algorithmic regression suite.

Selected self-contained analyses can also be regenerated directly:

```bash
python code/analyze_wong_direct_reversal.py
python code/analyze_wong_direct_reversal.py --outcomes originality usefulness elaboration --output results/wong_three_dimension_inference.csv --summary results/wong_three_dimension_summary.csv
python code/assessment_regime_rank_robustness.py
python code/assessment_regime_rank_sensitivity.py results/wong_rank_reversal_sensitivity_input.csv results/wong_rank_reversal_sensitivity.csv
python code/build_paired_profiles.py --results results
python code/build_paired_rank_evidence.py --results results
python -m pytest -q
```

## Reproduction levels

- **Level 1 — Self-contained numerical reconstruction:** rebuilds the published-summary Wong contrasts, orientation-aware reversal tests, simultaneous intervals, three-dimension sensitivity, paired evidence, and deterministic weight/scale diagnostics.
- **Level 2 — Software verification:** runs metadata, dependency, schema, ARRP, construct-gate, expected-result, and pytest checks without third-party raw participant data.
- **Level 3 — Raw-dependent regeneration:** requires source files obtained from the original public repositories under their own licenses and access conditions. Several archived participant-level outputs cannot be represented as freshly reproduced in this repository snapshot because the necessary raw inputs or complete raw-to-result pipelines are not supplied.

Details are in [`REPRODUCTION_LEVELS.md`](REPRODUCTION_LEVELS.md), [`README_RUNNING.md`](README_RUNNING.md), and [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Results release asset

The `v1.0.0` release contains **`GenAI_Rank_Reversal_results_v1.0.0.zip`**. The archive contains the repository's `results/` directory as a convenient downloadable research-results object. GitHub also generates `Source code (zip)` and `Source code (tar.gz)` automatically from the tag.

No custom checksum/hash manifest is distributed with this release. The release is intentionally not configured as immutable, consistent with the requested ability to correct files later if necessary. Scientific changes should nevertheless be documented through the changelog and an appropriate version update rather than silently changing the interpretation of the published record.

## Data and artifact availability

Third-party participant-level source files are not redistributed. Public locations include the Bastani et al. GitHub repository, the Harvard AI Tutor data repository, Figshare data for Pardos and Bhandari, Zenodo records for Bassner and Çiçek, and OSF resources for Wong–Qiu and Zhou. Exact source locations, expected filenames, access boundaries, and rerun instructions are documented in [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md) and [`THIRD_PARTY_DATA_NOTICE.md`](THIRD_PARTY_DATA_NOTICE.md).

Project-authored code, ARRP materials, derived result tables, figures, provenance summaries, and validation infrastructure are distributed in this repository. Code is released under the MIT License. Project-authored assessment-regime coding tables and derived evidence-map metadata follow the data-license guidance in [`DATA_LICENSE.md`](DATA_LICENSE.md); third-party rights remain with their original sources.

## Research areas and search terms

**Article keywords:** generative artificial intelligence, large language models, AI in education, human–AI collaboration, assisted performance, learning outcomes, assessment validity, rank reversal, evidence synthesis, reporting framework.

**Related indexing/search terms:** generative AI; GenAI; LLM; human–AI collaboration; AI-assisted task performance; independent human performance; performance–learning gap; retention; learning transfer; assessment regime; outcome elicitation; intervention rank reversal; assessment-regime rank transport; qualitative interaction; crossover interaction; causal transportability; treatment-effect heterogeneity; estimand heterogeneity; meta-analysis; evidence synthesis; cognitive offloading; assessment validity; reproducibility.

## Citation

Peer-reviewed article:

> **Kovari, A. (2026).** _Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes_. **Computers, 15(9), 633.** https://doi.org/10.3390/computers15090633

Software release:

> **Kovari, A. (2026).** _GenAI-Rank-Reversal_ (Version 1.0.0). GitHub. https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0

Use `CITATION.cff`, `CITATION.bib`, or `CITATION.ris` for machine-readable citation export.

## License, contributions, and security

Original source code and documentation are released under the [`MIT License`](LICENSE). Third-party datasets and source materials retain their original licenses and access terms. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`THIRD_PARTY_DATA_NOTICE.md`](THIRD_PARTY_DATA_NOTICE.md).
