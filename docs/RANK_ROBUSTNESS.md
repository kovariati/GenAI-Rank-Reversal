# Rank weighting and scale sensitivity

For fixed D_A>0 and D_I<0, the hypothetical aggregate D(w,lambda)=w*lambda*D_A+(1−w)*D_I changes sign at w*(lambda)=−D_I/(lambda*D_A−D_I). This is elementary algebra, not new statistical methodology or a recommendation to combine different constructs.

The threshold decreases with positive lambda. On a bounded weight/scale rectangle, its corner values determine whether the aggregate is always positive, always negative, or assumption-sensitive/tie-compatible. Input bounds and positive steps are checked; invalid grids cannot silently loop indefinitely.

The curves in `figures/rank_robustness_region.png` use archived participant-derived point means and have **no sampling coverage**. They are not confidence regions. The source-mean threshold near 0.485 differs slightly from the 0.483 value based on published rounded summary means; neither is a portable substantive constant.

The signed diagnostic rho=−(D_I−D_A)/D_A characterizes reversal by rho>1 for D_A nonzero. The absolute ratio alone is insufficient. The sign condition is invariant to separate positive rescalings, not arbitrary nonlinear individual-score transformations.

Implementations: `code/assessment_regime_rank_robustness.py`, `code/assessment_regime_rank_sensitivity.py`. Canonical outputs: `results/wong_rank_robustness_region.csv`, `results/wong_rank_robustness_summary.csv`, `results/wong_rank_reversal_sensitivity.csv`. See `docs/STATISTICAL_SCOPE.md` for the mean-order and scope assumptions.
