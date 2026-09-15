#!/usr/bin/env python3
"""Rank-robustness region after a two-regime rank reversal.

For D_A > 0 and D_I < 0, define
    D(w, lambda) = w * lambda * D_A + (1-w) * D_I,
where w is the assisted-regime weight and lambda is the positive relative
scale factor c_A/c_I. The tie boundary is
    w*(lambda) = -D_I / (lambda*D_A - D_I).

This script reports the boundary over a declared lambda grid and implements
rectangle classification for bounded assumptions w in [w_L,w_U] and
lambda in [lambda_L,lambda_U]. It is a deterministic sensitivity operation,
not a recommendation to aggregate unlike estimands.
"""
from __future__ import annotations
import argparse, csv, math
from pathlib import Path

def load_defaults():
    import csv
    here = Path(__file__).resolve().parent
    root = here if (here / "results").exists() else here.parent
    candidates = [root / "results/wong_raw_group_means.csv", root / "wong_raw_group_means.csv"]
    src = next((p for p in candidates if p.exists()), None)
    if src is None:
        raise FileNotFoundError("wong_raw_group_means.csv not found")
    rows=list(csv.DictReader(src.open(encoding="utf-8")))
    out={}
    for outcome in ("Originality","Usefulness"):
        rr=[r for r in rows if r["outcome"].lower()==outcome.lower()]
        u=next(r for r in rr if "Unrestricted" in r["design"])
        l=next(r for r in rr if "Learner" in r["design"] or "Think-first" in r["design"])
        out[outcome.lower()] = (float(u["assisted_task_mean"])-float(l["assisted_task_mean"]),
                                float(u["independent_task_mean"])-float(l["independent_task_mean"]))
    return out

def lambda_grid(lo, hi, step):
    if not all(math.isfinite(v) for v in (lo, hi, step)) or not 0 < lo <= hi or step <= 0:
        raise ValueError('Finite 0 < lambda_min <= lambda_max and positive step required')
    n = int(math.floor((hi-lo)/step + 1e-10)) + 1
    if n > 1000000:
        raise ValueError('Grid exceeds one million points')
    return [round(lo + j*step, 10) for j in range(n)]

def w_star(d_a: float, d_i: float, lam: float) -> float:
    if not all(math.isfinite(v) for v in (d_a,d_i,lam)) or not (d_a > 0 and d_i < 0 and lam > 0):
        raise ValueError("Requires D_A>0, D_I<0, lambda>0")
    return (-d_i) / (lam * d_a - d_i)

def classify_rectangle(d_a: float, d_i: float, w_l: float, w_u: float,
                       lam_l: float, lam_u: float) -> str:
    if not all(math.isfinite(v) for v in (w_l,w_u,lam_l,lam_u)) or not (0 <= w_l <= w_u <= 1 and 0 < lam_l <= lam_u):
        raise ValueError("Invalid rectangle bounds")
    high_thr = w_star(d_a, d_i, lam_l)  # largest threshold
    low_thr = w_star(d_a, d_i, lam_u)   # smallest threshold
    eps = 1e-12
    if w_l > high_thr + eps:
        return "positive_for_all_allowed_weight_scale_pairs"
    if w_u < low_thr - eps:
        return "negative_for_all_allowed_weight_scale_pairs"
    return "assumption_sensitive_or_tie_possible"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-out", default="results/wong_rank_robustness_region.csv")
    ap.add_argument("--summary-out", default="results/wong_rank_robustness_summary.csv")
    ap.add_argument("--lambda-min", type=float, default=0.25)
    ap.add_argument("--lambda-max", type=float, default=4.0)
    ap.add_argument("--lambda-step", type=float, default=0.05)
    args = ap.parse_args()

    grid_out = Path(args.grid_out); grid_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out = Path(args.summary_out); summary_out.parent.mkdir(parents=True, exist_ok=True)

    lams = lambda_grid(args.lambda_min,args.lambda_max,args.lambda_step)
    defaults = load_defaults()

    with grid_out.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(["outcome","D_A","D_I","lambda","w_star","interpretation"])
        for outcome, (d_a, d_i) in defaults.items():
            for lam in lams:
                wr.writerow([outcome, f"{d_a:.6f}", f"{d_i:.6f}", f"{lam:.6f}",
                             f"{w_star(d_a,d_i,lam):.9f}",
                             "aggregate tie boundary on declared relative scale"])

    # Three declared rectangles are diagnostics only: unrestricted ignorance,
    # assisted-dominant, and independent-dominant examples.
    rectangles = [
        ("broad_reference", 0.0, 1.0, 0.5, 2.0),
        ("assisted_dominant_example", 0.80, 1.0, 0.5, 2.0),
        ("independent_dominant_example", 0.0, 0.20, 0.5, 2.0),
    ]
    with summary_out.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(["outcome","D_A","D_I","rectangle","w_L","w_U","lambda_L","lambda_U",
                     "w_star_lambda_L","w_star_lambda_U","classification","note"])
        for outcome, (d_a,d_i) in defaults.items():
            for name,w_l,w_u,lam_l,lam_u in rectangles:
                wr.writerow([outcome, f"{d_a:.6f}", f"{d_i:.6f}", name,
                             f"{w_l:.3f}", f"{w_u:.3f}", f"{lam_l:.3f}", f"{lam_u:.3f}",
                             f"{w_star(d_a,d_i,lam_l):.9f}", f"{w_star(d_a,d_i,lam_u):.9f}",
                             classify_rectangle(d_a,d_i,w_l,w_u,lam_l,lam_u),
                             "Point-estimate assumption sensitivity only; not a sampling confidence region or recommended synthesis estimand"])

if __name__ == "__main__":
    main()
