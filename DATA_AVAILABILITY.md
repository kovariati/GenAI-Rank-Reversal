# Data and artifact availability

This public repository separates project-authored derived research artifacts from third-party source data.

## Included in Git

- public analysis and validation code in `code/`;
- small canonical derived outputs in `results/`;
- manuscript-facing figures in `figures/`;
- ARRP coding tables, construct-commensurability audit, evidence-map metadata and public provenance;
- environment locks, tests and validation tools.

Project-authored assessment-regime coding tables, data dictionaries and derived evidence-map metadata are released under CC BY 4.0 as described in `DATA_LICENSE.md`. Analysis code is MIT licensed under `LICENSE`.

## Third-party source data

Third-party participant-level source files are not redistributed in this repository. Consequently, analyses that require those source files, including the Wong and Qiu 99,999-permutation analysis and the Bastani et al. 9,999-replicate Webb wild-cluster analysis, require retrieval of the original data from their cited sources for a fresh end-to-end raw-source rerun. The released algorithms, canonical derived outputs, provenance records, direct-reversal calculations and computational validators remain publicly auditable without redistributing those source files.

Primary external locations used by the article include:

- Bastani et al. data/code: https://github.com/obastani/GenAICanHarmLearning
- Kestin et al. study data: https://github.com/HarvardAItutor/Study-Data-v4
- Pardos and Bhandari participant data: https://doi.org/10.6084/m9.figshare.23935269
- Bassner et al. pseudonymized data/materials: https://doi.org/10.5281/zenodo.20285307
- Ciçek et al. immediate/delayed clinical-reasoning data: https://doi.org/10.5281/zenodo.13769970
- Wong and Qiu data/code: https://osf.io/t7an8/
- Zhou et al. Study 2 project: https://osf.io/zv8a4/ (the final participant workbook used in the secondary analysis required author-approved contributor access)

Other third-party source materials remain under their original terms. Acquisition notes, expected local filenames and redistribution boundaries are documented in `THIRD_PARTY_DATA_NOTICE.md`.

## Reproduction

The fast public-quality gate requires no third-party raw data:

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
```

Deeper participant-level and public-study regeneration instructions are in `README_RUNNING.md` and `REPRODUCTION_LEVELS.md`.

## Persistent links and release timing

The canonical repository URL is `https://github.com/kovariati/GenAI-Rank-Reversal`. The version-specific release URL, release date, and final article DOI remain intentionally unset until those objects actually exist. After the article has a definitive bibliographic record and the `v1.0.0` release is created, update the canonical metadata, regenerate derived metadata files, and re-run the repository validator.
