# Repository infrastructure scorecard — pre-publication v1.0.0

This is an infrastructure-readiness score, not a scientific-quality score.

| Category | Score | Rationale |
|---|---:|---|
| Scientific identity + README landing page | 15/15 | Full article title, central methodological problem, reusable findings, boundaries and citation guidance are above the fold. |
| Citation metadata + ORCID + cross-links | 13/15 | CFF/BibTeX/RIS/CodeMeta/JSON-LD and ORCID are present; the live repository URL is canonical, while the final article DOI and version-specific release URL do not yet exist and are intentionally omitted. |
| GitHub discoverability | 10/10 | 338-character About text, 20 high-precision curated topics, 1280×640 social preview, natural-language search terms and citation intents. |
| Reproducibility + environment + tests | 20/20 | Canonical runtime, fully pinned direct+transitive dependency lock, reproduction levels, self-contained regeneration, scientific validators and CI quality gate. |
| Release/version/integrity/provenance | 15/15 | Semantic version, deterministic release-asset builder, per-asset SHA-256, internal manifests and release provenance. |
| Data availability + FAIR/archive | 8/10 | Data/source boundaries and persistent third-party identifiers are explicit; the repository is public, while the publication-linked release URL/PID remains pending creation of the finalized release. |
| Community health + support/security | 10/10 | CONTRIBUTING, SECURITY, bug/reproducibility issue forms, pull-request template and security settings guidance. |
| Publication lifecycle + metadata consistency | 5/5 | Single canonical metadata source, semantic cross-file consistency checks, generator idempotence and explicit publication-day update workflow. |
| **Total** | **96/100** | Gold/max-discovery pre-publication infrastructure. Remaining points require real external identifiers, not placeholders. |

The score intentionally does not award points for an article/repository DOI or archive PID that does not yet exist; the canonical GitHub repository URL is already live and recorded in project metadata.
