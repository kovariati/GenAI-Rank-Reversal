# DRAFT RELEASE TEMPLATE — provenance

No `v1.0.0` release is live yet. This document describes the **planned publication-linked v1.0.0 release** associated with the manuscript identity in `PROJECT_METADATA.json`.

The public tree was rebuilt from the finalized analysis state rather than copied wholesale from the development workspace. Development/review history, internal revision labels, local paths, caches, non-finalized surveillance notes, submission-system artifacts, and third-party raw data were excluded.

Once created after final publication metadata are available, the **Git tag `v1.0.0` will be the canonical article-associated source-code and reproducibility snapshot**. GitHub automatically provides `Source code (zip)` and `Source code (tar.gz)` for that tag. A separate full-repository reproducibility archive is intentionally not published because it would duplicate the tagged repository.

The only custom scientific bundle is:

- `GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip`
- `GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip.sha256`

The bundle contains canonical derived results, manuscript-facing figures, ARRP schema/example, public provenance summaries, and release-validation material. It does not contain third-party raw participant data.

Scientific headline values are retained and checked by the standalone expected-results validator, the full repository validator, and a genuine pytest mathematical/algorithmic regression suite.

Canonical repository:
https://github.com/kovariati/GenAI-Rank-Reversal

Planned release URL (not live until the release is created):
[release URL to be added only after the final v1.0.0 release is published]

Journal, DOI, and publisher metadata remain intentionally absent until those objects actually exist.
