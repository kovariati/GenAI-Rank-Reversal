# DRAFT RELEASE TEMPLATE — GenAI Rank Reversal v1.0.0

This file is a **DRAFT RELEASE TEMPLATE** for the planned publication-linked v1.0.0 release of code, results, and reproducibility materials associated with the manuscript:

> **Generative AI, Performance, and Learning: Intervention Rank Reversal Across Assessment Regimes**

## Preferred citation

**Kovari, A. (2026). _Generative AI, Performance, and Learning: Intervention Rank Reversal Across Assessment Regimes_. Manuscript.**

The final journal citation, DOI, and publisher link will be added only after a final publication record exists. No provisional or fabricated DOI is used. The version-specific `v1.0.0` release is finalized only after those definitive article metadata exist, so the repository citation files and release metadata can be synchronized before the release is frozen.

If the assessment-regime rank-transport framework, ARRP reporting schema, statistical methods, numerical results, or released reproducibility artefacts contribute to scientific work, please cite the associated article once its final bibliographic record is available. For direct software or schema reuse, also follow `CITATION.cff`, `LICENSE`, and `DATA_LICENSE.md`.

## About this project

Generative AI and large language models can improve task performance while assistance is available without implying equivalent gains in independent human performance, learning, retention, or transfer.

This project addresses a stronger methodological question:

> **The intervention that performs best with AI need not be the intervention that performs best without AI.**

The central problem is **assessment-regime rank transport**. An intervention ranking identified under one assessment regime does not automatically identify the ranking under another assessment regime.

Three reusable methodological conclusions organize the project:

> **AI-assisted performance alone does not establish independent human performance.**

> **Rank preservation across assessment contexts cannot be inferred from randomization alone.**

> **Differences in outcome-elicitation context can create estimand heterogeneity before statistical heterogeneity is modeled.**

These issues are relevant to human–AI collaboration, AI-assisted assessment, learning and transfer, causal inference, meta-analysis, evidence synthesis, and other settings where assisted output is interpreted as evidence about later independent human capability.

## Included in v1.0.0

- assessment-regime rank-transport framework
- direct opposite-sign inference for intervention rank reversal
- intersection–union reversal testing with multiplicity control
- participant-level conditional randomization inference
- rank-sensitivity and bounded weight/scale robustness analysis
- construct-commensurability gate for cross-regime comparison
- paired rank-preservation and rank-reversal evidence profiles
- **Assessment-Regime Reporting Profile (ARRP)**
- machine-readable ARRP JSON Schema and worked example
- executable ARRP feature and metamorphic tests
- deterministic ARRP specification and traceability validation
- diagnostic meta-analysis coding-schema audit
- canonical derived numerical results and manuscript-facing figures
- conceptual figures for the C/Q/E/V construct gate and manuscript-facing rank-transport evidence
- source and data provenance documentation
- frozen direct and transitive Python dependency environment
- machine-readable citation and article metadata
- fail-closed public-release and reproducibility validation
- audit/reproducibility artifact index (`docs/REPRODUCIBILITY_ARTIFACTS.md`) covering synthesis, ARRP, provenance, paired-dataset, rank-robustness, and computational-validation records

Internal working material, development-version history, local paths, caches, debug/progress files, credentials, and non-redistributable participant-level data are intentionally excluded.

## Assessment-Regime Reporting Profile (ARRP)

ARRP is an executable outcome-level reporting schema for five conditions that can affect the interpretation of AI-related performance estimates:

- **A — AI availability:** whether AI assistance is available during the scored outcome
- **D — Delay:** temporal distance between intervention or exposure and assessment
- **O — Overlap:** task or item overlap between assisted activity and assessment
- **G — Generalization:** transfer or generalization demand
- **N — Non-use evidence:** evidence supporting AI non-use during independent assessment

ARRP is derived from the identification problem addressed in the manuscript. It is **not presented as a validated psychometric instrument or consensus reporting standard**.

See `docs/ARRP.md`, `arrp.schema.json`, and the machine-readable worked example in `examples/`.

## Key scientific result

The Wong–Qiu data provide the focal constructive counterexample. For unrestricted ChatGPT versus a learner-first design, the intervention ordering changes between AI-assisted assessment and subsequent unassisted creative transfer. Direct regime-specific inference supports opposite-signed contrasts for both originality and usefulness.

The result establishes a **non-guarantee, not a prevalence estimate**:

> **One verified reversal is sufficient to show that rank preservation across assessment regimes does not follow automatically from randomization.**

The framework does **not** predict that rankings must reverse. Rank preservation is also a possible and informative empirical result.

Cross-regime rank comparison is interpreted only when the compared outcomes have a defensible construct link and common directional interpretation. Otherwise the outcomes should be treated as non-commensurable rather than classified as rank-preserved or rank-reversed.

## Implications for meta-analysis and evidence synthesis

Assessment regime can create **estimand heterogeneity before statistical heterogeneity**.

> **Standardization resolves units, not estimand identity.**

The included seven-synthesis audit is a diagnostic of **coding-schema vulnerability and readiness**. It does not claim that the examined meta-analyses are invalid or that incompatible estimands were necessarily pooled.

## Source code and reproducibility

The complete versioned source code, validation tools, reporting schemas, environment specification, documentation, and small canonical outputs are contained directly in the **`v1.0.0` Git tag**.

GitHub automatically provides downloadable archives under **Source code (zip)** and **Source code (tar.gz)**. A separate full-repository reproducibility archive is intentionally not attached because it would duplicate the tagged source tree.

To validate the release:

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
python -m pytest -q
```

See `README_RUNNING.md`, `REPRODUCTION_LEVELS.md`, and `docs/REPRODUCIBILITY.md` for the available validation and regeneration workflows.

The public validation does not require redistribution of third-party participant-level datasets.

## Release artifact

### `GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip`

Convenience bundle containing canonical derived numerical results, result tables, manuscript-facing figures, ARRP schema/example, public provenance summaries, and release-validation material.

**SHA-256**

`8229fca4c5f4815ddb34cd0e813f8fe4deb3fb83079591aa503afea4ad8c0c74`

Companion checksum file:

`GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip.sha256`

The archive also contains its own file-level `MANIFEST_SHA256.txt`.

Large or non-redistributable third-party participant-level data are intentionally not included.

## When to cite or reuse this project

This repository may be useful when research:

- distinguishes AI-assisted task performance from independent human performance or learning
- compares assisted and unassisted outcomes
- evaluates whether intervention rankings transport across assessment regimes
- studies learning transfer, retention, or post-assistance capability
- synthesizes heterogeneous Generative AI outcomes
- evaluates human–AI collaboration or AI-assisted assessment
- reports AI availability, delay, task overlap, transfer demand, or evidence of AI non-use
- implements direct rank-reversal inference
- conducts weighting/scaling sensitivity analyses for regime-dependent rankings
- applies the ARRP outcome-reporting schema

## Research and indexing terms

Generative AI; large language models; human–AI collaboration; AI-assisted performance; independent human performance; performance–learning gap; learning outcomes; learning transfer; retention; assessment validity; assessment regimes; intervention rank reversal; qualitative interaction; causal inference; causal transportability; treatment-effect heterogeneity; estimand heterogeneity; meta-analysis; evidence synthesis; reproducible research.

## Citation metadata

Machine-readable citation and discovery metadata are provided in:

- `CITATION.cff`
- `CITATION.bib`
- `CITATION.ris`
- `codemeta.json`
- `ARTICLE_METADATA.json`
- `llms.txt`

These metadata are generated from the canonical `PROJECT_METADATA.json` source and validated for cross-file consistency.

## Canonical links

**Repository:** https://github.com/kovariati/GenAI-Rank-Reversal  
**Release:** [release URL to be added only after the final v1.0.0 release is published]  
**Article DOI:** to be added after publication  
**Publisher article:** to be added after publication

## Integrity and versioning

When created after definitive publication metadata are available, the planned publication-linked `v1.0.0` tag will identify the canonical article-associated scientific state of the code, derived results, ARRP reporting template, and reproducibility infrastructure. Until then, the public repository remains the reviewable pre-release state.

Scientific release artifacts should not be silently replaced. Any later scientific or packaging change that alters a released artifact should use a new semantic version and new checksum.
