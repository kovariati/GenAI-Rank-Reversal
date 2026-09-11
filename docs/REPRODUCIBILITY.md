# Reproducibility design

The repository separates source acquisition, code, canonical derived results and integrity validation. Third-party raw participant data are never treated as Git artifacts.

The fast quality gate is intentionally fail-closed: missing required public-tree files, changed headline results, invalid metadata, internal-version leakage, local paths, secrets or unsupported claims cause a nonzero exit.

Canonical numerical environment and seeds are recorded in `RUNTIME.txt`; `requirements-lock.txt` contains the complete 23-package direct+transitive runtime dependency closure for the canonical Python 3.13.5 environment. `tools/validate_dependency_lock.py` verifies exact installed versions, dependency-specifier compatibility and closure completeness.
