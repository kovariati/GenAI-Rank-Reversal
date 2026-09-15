#!/usr/bin/env python3
"""Reusable assessment-regime rank-reversal sensitivity diagnostic.

Input columns: outcome, orientation, D_A, D_I. D_A and D_I are direct
intervention contrasts under two declared assessment regimes on a declared
score scale. The diagnostic is descriptive: it reports the differential
regime shift, the shift required to erase the assisted-regime margin, and the
ratio between the observed and tie-producing shifts. The magnitude ratio is
scale-convention dependent; strict sign reversal is invariant to separate
positive rescaling within regimes.
"""
import argparse, csv, math
from pathlib import Path

SCALE_BOUNDARY = (
    "Magnitude ratio assumes the declared raw-score scale; reversal sign is "
    "invariant to separate positive rescaling within regimes."
)

def diag(outcome, orientation, da, di):
    if not all(math.isfinite(float(v)) for v in (da,di)):
        raise ValueError('Both contrasts must be finite')
    gamma = di - da
    return {
        "outcome": outcome,
        "orientation": orientation,
        "assisted_margin_DA": da,
        "independent_margin_DI": di,
        "differential_regime_shift_Gamma_DI_minus_DA": gamma,
        "shift_to_tie_minus_DA": -da,
        "observed_shift_over_tie_requirement": abs(gamma) / abs(da) if da else math.nan,
        "signed_shift_over_tie_requirement": -gamma / da if da else math.nan,
        "absolute_ratio_is_not_sufficient_for_reversal": True,
        "strict_rank_reversal": "TRUE" if da * di < 0 else "FALSE",
        "scale_boundary": SCALE_BOUNDARY,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    args = ap.parse_args()
    with open(args.input_csv, encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))
    if not src:
        raise ValueError('Input must contain at least one contrast pair')
    out = [
        diag(
            r.get("outcome", r.get("label", str(i))),
            r.get("orientation", "declared intervention contrast"),
            float(r.get("D_A", r.get("assisted_margin_DA"))),
            float(r.get("D_I", r.get("independent_margin_DI"))),
        )
        for i, r in enumerate(src)
    ]
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

if __name__ == "__main__":
    main()
