# Repository packaging update — 2026-09-15

Release generation now produces only the results-and-artifacts ZIP. Separate file-identity inventories and auxiliary verification artifacts have been removed. Source provenance retains citations, source locations, filenames where available, sample information and random seeds. The validator compares regenerated results and metadata directly using their actual contents; scientific tests, numerical outputs and figures are retained unchanged. This is a local pre-release packaging update, not a newly published software release.

# Local revision — 2026-09-14

## Final manuscript alignment — 2026-09-14

The final title, 195-word abstract and ten keywords clarify the methodological contribution and retain the restricted Wong–Qiu outcome scope in response to the reviewer. The no-AI wording refers to the assessment protocol rather than independently verified device-wide non-use. Citation metadata, article metadata and the README have been synchronized. Numerical programs, statistical results and figures are unchanged from the corrected revision. Publication identifiers remain unassigned and no live software release is asserted.


Reframed as methodological framework and retrospective secondary analysis, restricted to task-specific originality. Added two-orientation multiplicity handling (Holm p 0.01351), simultaneous four-contrast intervals and the elaboration sensitivity family. Enforced the actual eligibility gate; corrected the signed shift condition, mean-transformation caveat, tie handling, dynamic evidence status, invalid grid/statistics handling and complete JSON-Schema checks. Corrected permutation terminology/null scope without claiming a raw rerun. Expanded 16 original tests to 56 cases. Added explicit raw-data/pipeline limits, revised figures and synchronized metadata. This is a local pre-release revision, not a new published release.

---

# Changelog

## 1.0.0 (planned publication-linked release)

- Audited peer-review repository state; packaging is prepared for the planned publication-linked release after definitive article metadata are available.
- Stable public filenames with development revision labels removed.
- Direct opposite-sign Wong rank-reversal inference and participant-level randomization results.
- Construct-commensurability gate and pairwise preservation/reversal map.
- Rank-sensitivity and bounded weight/scale robustness operations.
- ARRP executable reporting schema with deterministic specification tests.
- Machine-readable `arrp.schema.json`, dedicated `docs/ARRP.md` reuse page and worked JSON example.
- Fully pinned direct+transitive dependency lock with executable closure validation.
- Semantic cross-file metadata validation; author/license/runtime/version/description/topics derive from canonical metadata rather than tool hardcoding.
- Diagnostic synthesis-schema audit and evidence-map provenance.
- Detailed audit and reproducibility ledgers indexed in `docs/REPRODUCIBILITY_ARTIFACTS.md`; software-QC records are kept in the repository rather than expanded in the journal appendix.
- Canonical manuscript visualization set: C/Q/E/V construct-gate diagram and native-scale Wong–Qiu reversal figure; the cross-study effect-profile figure is not shipped as a canonical manuscript figure because it may imply unsupported common-scale comparability.
- Figure 1 synchronized to the final author-supplied SVG with byte-matched PDF/PNG exports; graphical abstract wording narrowed to assisted product improvement versus unassisted product invention.
- ARRP manuscript-facing allowed values synchronized exactly with `arrp.schema.json`.
- Wong–Qiu sample documentation synchronized to 197 randomized / 196 analyzed after one source-author exclusion, with no additional reanalysis exclusions.
- Data-availability language now states the third-party raw-source boundary explicitly for fresh end-to-end reruns.
- Canonical metadata source, CFF/BibTeX/RIS/CodeMeta/JSON-LD exports, social-preview asset and fail-closed public-release validation.
- No third-party raw participant data redistributed.
- Release packaging simplified: the `v1.0.0` Git tag is the canonical source/reproducibility snapshot; no duplicate full-repository or subset-only provenance archive is published.
- One custom `results-and-artifacts.zip` convenience bundle is used for release downloads.
