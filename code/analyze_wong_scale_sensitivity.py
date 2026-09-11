#!/usr/bin/env python3
"""Reproduce Wong raw-scale composition/scale sensitivity from frozen means.

This analysis is descriptive. It does not recommend pooling the two tasks or
interpret the mixture as a causal estimand.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MEANS = {
    "unrestricted_assisted": 4.082089552238806,
    "learner_assisted": 3.3,
    "unrestricted_independent": 2.6865671641791047,
    "learner_independent": 3.423076923076923,
}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--figures", default="figures")
    args = ap.parse_args()
    results = Path(args.results); figures = Path(args.figures)
    results.mkdir(parents=True, exist_ok=True); figures.mkdir(parents=True, exist_ok=True)

    da = MEANS["unrestricted_assisted"] - MEANS["learner_assisted"]
    di = MEANS["unrestricted_independent"] - MEANS["learner_independent"]
    lam = np.geomspace(0.25, 4.0, 241)
    w = (-di) / (lam * da - di)
    pd.DataFrame({
        "scale_ratio_lambda_cA_over_cI": lam,
        "assisted_raw_contrast_DA": da,
        "independent_raw_contrast_DI": di,
        "composition_threshold_w_star": w,
    }).to_csv(results / "wong_scale_composition_sensitivity.csv", index=False)

    key = np.array([0.25, 0.5, 1.0, 2.0, 4.0])
    keyw = (-di) / (key * da - di)
    pd.DataFrame({"lambda_cA_over_cI": key, "w_star": keyw}).to_csv(
        results / "wong_scale_composition_sensitivity_keypoints.csv", index=False
    )

    fig, ax = plt.subplots(figsize=(7.8, 4.9))
    ax.plot(lam, w, linewidth=2)
    ax.scatter([1.0], [(-di)/(da-di)], zorder=3)
    ax.axvline(1.0, linestyle="--", linewidth=1)
    ax.set_xscale("log", base=2)
    ax.set_xticks([0.25, 0.5, 1, 2, 4])
    ax.set_xticklabels(["0.25", "0.5", "1", "2", "4"])
    ax.set_ylim(0, 1)
    ax.set_xlabel(r"Relative scale factor, $\lambda=c_A/c_I$")
    ax.set_ylabel(r"Composition sensitivity threshold, $w^*(\lambda)$")
    ax.set_title("Wong originality: composition threshold is scale-sensitive")
    ax.grid(alpha=0.2)
    ax.text(1.0, (-di)/(da-di)+0.055, r"$w^*(1)=0.485$", ha="center")
    fig.tight_layout()
    fig.savefig(figures / "figure4_regime_mixture.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures / "figure4_regime_mixture.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"D_A={da:.12f}; D_I={di:.12f}; w*(1)={(-di)/(da-di):.12f}")

if __name__ == "__main__":
    main()
