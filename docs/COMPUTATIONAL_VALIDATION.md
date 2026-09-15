# Computational validation

The revised suite contains 56 pytest cases. It checks Welch against SciPy, two-orientation symmetry, retained-family correction, simultaneous intervals, the elaboration family, invalid statistics, actual commensurability gating, ties and nonfinite values, dynamic significance status, the direction-aware shift ratio, monotone-transformation counterexamples, invalid grid termination, complete JSON-Schema validation, and the retained baseline identities.

Run `python -m pytest -q` or the complete gate `python tools/validate_repository.py`. The latter also checks metadata, dependency closure, deterministic numerical regeneration, 62 ARRP specification checks, and expected outputs. Regenerated results and metadata are compared directly using their actual file contents. Structural conformance is not validation of scientific interpretation, human reliability, or population generalization.

No raw-source rerun of archived participant models is claimed. The primary sign audit uses published rounded statistics. The accompanying scope manifest identifies absent raw data and incomplete Bassner/Cicek/Zhou raw-to-result implementations.
