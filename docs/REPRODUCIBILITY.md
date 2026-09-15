> **Revision scope (2026-09-14).** Current focal inference is task-specific originality with orientation-plus-Holm p=0.01351; usefulness is secondary. No fresh raw-source participant rerun is claimed. Complete Bassner/Cicek/Zhou raw-to-result pipelines are not supplied. Prior raw-analysis descriptions below document archived provenance, not newly executed validation. See `results/revision_validation_scope.json` and `docs/STATISTICAL_SCOPE.md`.

# Reproducibility design

The repository separates source acquisition, code, canonical derived results and scientific/software validation. Regenerated numerical outputs and generated metadata are compared directly with the supplied file contents. Third-party raw participant data are never treated as Git artifacts.

The fast quality gate is intentionally fail-closed: missing required public-tree files, changed headline results, invalid metadata, internal-version leakage, local paths, secrets or unsupported claims cause a nonzero exit.

Canonical numerical environment and seeds are recorded in `RUNTIME.txt`; `requirements-lock.txt` contains the complete 32-package direct+transitive runtime dependency closure for the canonical Python 3.13.5 environment. `tools/validate_dependency_lock.py` verifies exact installed versions, dependency-specifier compatibility and closure completeness.
