# Statistical scope and numerical changes

## Fixed task-score contrasts, not a new statistical method

For each outcome define D_A = unrestricted minus learner-first on Task 1, and D_I on Task 2. These are the means of ratings of two different products under the source's scoring reference. Ratings are not a common calibrated creativity or durable-learning scale. The packages also use different access schedules in Task 1.

The source study already reported the interaction. This retrospective reanalysis uses established Welch, intersection–union, Bonferroni and Holm methods; it makes no statistical priority claim.

## Direction selection and multiplicity

Let p_A+ and p_A− test a positive/negative Task 1 contrast, and p_I+, p_I− the corresponding Task 2 contrast. Define p_+− = max(p_A+,p_I−) and p_−+ = max(p_A−,p_I+). With no prospectively fixed direction, use p_rev = min(1, 2 min(p_+−,p_−+)), followed by Holm across originality and usefulness. These are conservative union-bound steps, conditional on valid marginal p values. The within-task Welch comparisons assume independent arms; repeated task dependence requires no additional independence assumption for these multiplicity operations.

The old `intersection_union_p` and `holm_adjusted_iut_p_across_outcomes` columns remain for compatibility and are explicitly **direction-conditional diagnostics only**. The current primary column is `holm_adjusted_orientation_reversal_p`: 0.013511339437362484 for both outcomes. The reporting focus on originality is retrospective, and usefulness remains in the family.

Four direct contrasts use Bonferroni two-sided 98.75% marginal intervals (critical quantile 0.99375). Their joint coverage is nominally at least 95% subject to the Welch–Satterthwaite approximation. They are not exact distribution-free confidence intervals. Originality intervals: [0.223751,1.336249] and [−1.409056,−0.050944]. Usefulness: [0.171633,1.148367] and [−1.113685,−0.046315].

The separate all-rated-dimensions family includes elaboration and returns Holm p = 0.020267 for originality/usefulness, 0.928908 for elaboration. The original source treated elaboration as a secondary diagnostic, not an interchangeable creativity component.

## Interaction orientation and archived permutations

The original participant model codes learner-first minus unrestricted, so its Task 2–Task 1 interaction is −Gamma when Gamma = D_I − D_A under the direct-test orientation. The numerical interaction is not a learning-loss estimate across calibrated tasks.

The archived label-permutation algorithm divides each outcome's statistics by one constant permutation SD. It is not per-permutation Welch studentization. Conditional exchangeability under the sharp no-effect-on-individual-change null is required; no generally valid weak mean-interaction test is claimed. The max-statistic values are complete-null diagnostics, not asserted strong marginal-FWER control. Existing marginal permutation p values have a separate Holm adjustment (0.00004 each). These annotations and adjustments do not constitute a raw-data rerun.

## Mean ordering and score transformations

A common increasing transformation of intervention means preserves their ordering. A common monotone transformation of individual scores need not preserve means: A is constantly 2 and B is 0 or 3 with equal probabilities; their means are 2 and 1.5, but squaring yields means 4 and 4.5. Common positive-affine individual transformations do preserve mean order. The formal partial-order result assumes a jointly eligible intervention set and a common score functional within each context. Arbitrary pair-specific deletions or significance decisions need not remain transitive.

For D_A nonzero, rho = −(D_I−D_A)/D_A = 1−D_I/D_A exceeds 1 exactly when D_A*D_I < 0. The absolute ratio alone is insufficient: D_A=1,D_I=3 gives 2 without reversal. Fixed-estimate weight/scale boundaries have no sampling coverage claim.

## Reproduction scope

Fresh calculations use published rounded n/mean/SD and supplied summary outputs. They do not reconstruct individual records or within-person covariances. `results/revision_validation_scope.json` is the machine-readable statement of raw-source and pipeline limits.
