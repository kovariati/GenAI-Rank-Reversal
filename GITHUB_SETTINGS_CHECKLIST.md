# GitHub settings checklist

## Repository identity

- **Suggested repository name:** `GenAI-Rank-Reversal`
- **About description (338 characters; GitHub currently allows up to 350):**
  `Generative AI and large language models: intervention rank reversal across AI-assisted and independent assessment regimes. Code, results, and reproducibility for human–AI collaboration, independent human performance, learning transfer, assessment validity, causal inference, qualitative interaction, meta-analysis, and evidence synthesis.`
- **Website:** leave blank until a real canonical article DOI/publisher page exists; after publication, prefer the canonical DOI URL.
- **Repository:** https://github.com/kovariati/GenAI-Rank-Reversal
- **Planned publication-linked release (not live during peer review):** https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0
- **Default branch:** `main`

## Topics (20)

`generative-ai`, `large-language-models`, `human-ai-collaboration`, `ai-assisted-performance`, `independent-human-performance`, `learning-transfer`, `assessment-validity`, `causal-inference`, `causal-transportability`, `treatment-effect-heterogeneity`, `qualitative-interaction`, `rank-reversal`, `assessment-regimes`, `meta-analysis`, `evidence-synthesis`, `human-computer-interaction`, `ai-education`, `research-methods`, `reproducible-research`, `research-software`

The GitHub topics intentionally favor high precision. Broader cross-domain terms such as software engineering, workplace productivity and clinical decision support remain in README/search metadata rather than being asserted as primary repository topics.

## Social preview

Upload `.github/assets/social-preview.png` in GitHub → Settings → General → Social preview. The asset is 1280×640 and contains no invented DOI/journal metadata.

## CI / trust signal

After the first `repository-quality` workflow has passed on the live repository, add the live GitHub Actions status badge to the README badge row. Do not show a passing badge before a real workflow run exists.

## Recommended repository settings

- Enable Issues if reproducibility support will be provided.
- Enable secret scanning / push protection where available.
- Enable dependency security alerts where available.
- Keep Actions enabled for `.github/workflows/repository-quality.yml`.
- After the article has a definitive bibliographic record, create the `v1.0.0` release; upload only `GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip` and its `.sha256` companion. The `v1.0.0` Git tag is the canonical source/reproducibility snapshot; do not upload duplicate full-repository or provenance ZIPs that merely repeat files already versioned in Git.
- If immutable releases are available, enable immutability only after the draft release has passed final asset QA.
- Do not enable Zenodo integration for this project unless a later explicit archival decision is made.

## Publication-day update

After a real journal record exists, edit only `PROJECT_METADATA.json` (`journal`, `article_doi`, `publisher_url`), run `python tools/generate_metadata_files.py`, then `python tools/validate_repository.py`. After creating the live release, add the actual `release_url` and `release_date` to `PROJECT_METADATA.json`, regenerate metadata, and rerun the validator.
