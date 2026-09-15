# Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes

Research software and results for the manuscript by Attila Kovari. The software version `1.0.0` remains a planned publication-linked version; a live release, article DOI, or acceptance is not claimed.

Project repository: https://github.com/kovariati/GenAI-Rank-Reversal

## Manuscript abstract

Generative artificial intelligence (AI) and large language models can improve assisted task performance without establishing learning, retention, or transfer. Evaluating AI in education and human–AI collaboration therefore requires distinguishing assisted from independent human performance. A methodological framework separates target constructs, tasks, assessment conditions, and verification evidence to examine when intervention rankings can be compared across assessment regimes. A retrospective secondary analysis uses established statistical procedures to reassess a previously reported comparison of unrestricted and learner-first ChatGPT use. Published rounded summary statistics indicate a task-specific rank reversal in expert-rated originality: unrestricted-minus-learner-first contrasts are +0.78 points for a stuffed-bunny improvement task and −0.73 for a subsequent vocabulary-game task under a no-AI protocol (two-orientation testing; Holm-adjusted p = 0.01351 across originality and usefulness). Usefulness provides secondary corroboration; reversal is not supported for elaboration. These findings concern task-specific product ratings, not general creativity or durable learning. Task content, sequence, and AI-access policy vary together, precluding attribution to AI removal alone. The Assessment-Regime Reporting Profile supports reporting checks but lacks independent validation. The contribution is an auditable workflow for assessment validity and evidence synthesis: intervention comparisons require explicit outcome definitions and defensible comparability assumptions before findings are pooled or generalized.

## Contribution and endpoint boundary

The contribution is a methodological framework and retrospective secondary analysis, not a new statistical method.

The focal Wong–Qiu result concerns task-specific expert-rated originality, not general creativity or durable learning.

AI-assisted performance alone does not establish independent human performance.

Rank preservation across assessment contexts cannot be inferred from randomization alone.

Differences in outcome-elicitation context can create estimand heterogeneity before statistical heterogeneity is modeled.

The source Wong–Qiu experiment already reported an interaction and opposite active-arm task comparisons. This repository does not claim a newly discovered interaction, a new statistical test, or a general creativity/learning effect. It supplies an auditable workflow for assessment-regime rank transport, explicit outcome scope, established inference, and evidence synthesis. No meta-analysis is generated from incompatible or incomplete inputs.

The focal endpoint is **expert-rated originality of submitted products** in two named tasks: stuffed-bunny improvement and subsequent vocabulary-game invention. The same 1–7 labels and high within-task rater ICCs do not establish cross-task invariance. Ratings were relative to each task's product pool. Access schedules differ by intervention in Task 1, and task content, order and demands change together with access. The contrast is between complete intervention packages, not the isolated causal effect of AI removal.

## Corrected numerical result

Contrasts are unrestricted minus learner-first. Intervals below are marginal Welch–Satterthwaite approximations from published rounded group sizes, means and standard deviations.

| Endpoint | Task 1 contrast, 95% CI | Task 2 contrast, 95% CI | Two-orientation + two-outcome Holm p |
|---|---|---|---:|
| Originality: focal reporting endpoint | +0.78 [0.35, 1.21] | −0.73 [−1.26, −0.20] | 0.01351 |
| Usefulness: secondary, task-goal-relative | +0.66 [0.28, 1.04] | −0.58 [−1.00, −0.16] | 0.01351 |

The old 0.00676 value adjusted a **direction-conditional** IUT across outcomes. Because no prospective direction plan for this retrospective reanalysis is supplied, the main calculation now handles both orientations before applying Holm. The original two-outcome family is retained despite the narrower reporting emphasis; the hierarchy is not presented as preregistered. All four Bonferroni simultaneous intervals also retain the required signs at nominal joint 95% coverage, subject to marginal Welch validity.

A separate three-dimension sensitivity family adds source-reported elaboration: corrected p = 0.02027 for originality/usefulness and 0.92891 for elaboration. There is no supported elaboration reversal. This is an all-rated-dimensions check, not a claim that elaboration is interchangeable with creativity.

## Reproduce the self-contained audit

Use Python 3.13.5 and the provided 32-package direct/transitive lock for the validated environment.

```bash
python -m pip install -r requirements-lock.txt
python tools/validate_repository.py
```

Individual calculations:

```bash
python code/analyze_wong_direct_reversal.py
python code/analyze_wong_direct_reversal.py --outcomes originality usefulness elaboration --output results/wong_three_dimension_inference.csv --summary results/wong_three_dimension_summary.csv
python code/build_paired_profiles.py --results results
python code/assessment_regime_rank_order.py
python code/build_paired_rank_evidence.py --results results
python -m pytest -q
```

The full validation gate checks metadata consistency, dependency closure, structural ARRP conformance, input/gate failures, expected numerical values and deterministic regeneration. The 56 tests establish computational behavior, not scientific validity or population transport.

## Freshly recomputed versus archived

This revision freshly recomputes published-summary Wong contrasts, orientation-aware reversal tests, simultaneous intervals, the elaboration sensitivity family, deterministic profile/evidence derivations, and scale/weight diagnostics. It does **not** freshly rerun participant bootstraps, label permutations, cluster models or every original exclusion pipeline. No raw participant file was supplied or retrieved successfully in this revision.

| Program | Raw-source reproduction status in this snapshot |
|---|---|
| Wong, Bastani, Kestin, Pardos | Raw-dependent programs supplied; raw source inputs absent; participant outputs archived. |
| Bassner | Prepared-column helper supplied, but the complete raw-to-prepared transformation is absent. |
| Cicek and Zhou | Archived derived outputs; complete raw-to-result pipelines absent. Zhou access is author-reported and restricted. |

The archived Wong permutation table now correctly labels constant permutation-SD standardization and the sharp-null scope. Existing marginal permutation p values were Holm-adjusted without regenerating the permutations. The max-statistic column is not represented as a general weak-null or strong marginal-FWER test. See `results/revision_validation_scope.json`, `DATA_AVAILABILITY.md` and `REPRODUCTION_LEVELS.md`.

## ARRP and comparison gate

[ARRP documentation](docs/ARRP.md) and [the complete JSON Schema](arrp.schema.json) separate outcome conditions A–D–O–G from non-use evidence N. The actual rank-classification code now enforces `results/construct_commensurability_audit.csv`; missing, unclear or ineligible scope does not receive a rank label. An eligible task-specific score comparison is not validation of a common construct.

The worked Wong example records source-reported protocol prevention for the study ChatGPT interface, not independently verified non-use; transfer distance is left unclear. Software checks cover structural rules only. The 77 author-coded records are not an independent inter-rater or content-validity study.

## Main outputs and documentation

`results/wong_direct_reversal_inference.csv` and `results/wong_direct_reversal_summary.csv` contain the corrected focal inference. `results/wong_three_dimension_summary.csv` records the sensitivity family. `results/paired_rank_evidence_revised.csv` separates the scoped Wong finding from unestablished preservation in Bastani/Bassner. `docs/STATISTICAL_SCOPE.md` defines the exact testing and transformation assumptions. `docs/RANK_ROBUSTNESS.md` explains why fixed-contrast weight/scale sensitivity is not a sampling confidence region.

The source summary statistics come from Wong and Qiu (2026), *Think First, ChatGPT Later*, DOI: 10.1007/s10648-026-10118-7. All third-party sources and usage boundaries remain in `THIRD_PARTY_DATA_NOTICE.md`. No raw third-party records or access credentials are redistributed.

## Citation and reuse

`PROJECT_METADATA.json` is the identity source for generated CFF, BibTeX, RIS, CodeMeta and article metadata. Publication identifiers remain null until real records exist. Code is MIT-licensed; project-authored coding metadata follow `DATA_LICENSE.md`, with third-party rights retained. See `README_RUNNING.md` for raw-dependent commands and `docs/RELEASE_PROVENANCE.md` for the draft release policy.
