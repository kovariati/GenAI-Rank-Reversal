#!/usr/bin/env python3
"""Compute pairwise rank-transport status across assessment regimes.

The operation is deliberately scale-light: within each regime it uses only the
sign of direct pairwise differences. A pair is regime-invariant only when all
non-tied regime-specific signs agree. If any two regimes imply opposite signs,
the pair is conflicting and cannot belong to a regime-invariant complete
ranking without an additional aggregation/weighting rule.
"""
from pathlib import Path
import argparse
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE/'results').exists() else HERE.parent

def sgn(x: float, tol: float = 1e-12) -> int:
    if x > tol:
        return 1
    if x < -tol:
        return -1
    return 0

def build(profiles: Path, out: Path):
    df = pd.read_csv(profiles)
    rows = []
    for program, g in df.groupby('program', sort=False):
        if len(g) != 2:
            continue
        a, b = g.iloc[0], g.iloc[1]
        da = float(a['supported_effect_std'] - b['supported_effect_std'])
        di = float(a['independent_effect_std'] - b['independent_effect_std'])
        sa, si = sgn(da), sgn(di)
        if sa == 0 or si == 0:
            status = 'tie_in_at_least_one_regime'
        elif sa == si:
            status = 'same_sign_observed'
        else:
            status = 'opposite_sign_observed'
        rows.append({
            'program': program,
            'intervention_a': a['design'],
            'intervention_b': b['design'],
            'assisted_difference_a_minus_b_std': da,
            'independent_difference_a_minus_b_std': di,
            'assisted_sign': sa,
            'independent_sign': si,
            'pairwise_transport_status': status,
            'sample_pairwise_order_agrees_across_regimes': status == 'same_sign_observed',
            'interpretation': ('Observed regime-specific signs are opposite. Population reversal is claimed only where direct inferential support for both signs is available.'
                               if status == 'opposite_sign_observed' else
                               'Observed pairwise signs agree across the two coded regimes. This is a descriptive sign pattern only; population preservation requires direct inferential support in both regimes.')
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--profiles', default=str(ROOT/'results'/'paired_supported_independent_profiles.csv'))
    ap.add_argument('--out', default=str(ROOT/'results'/'pairwise_rank_transport_status.csv'))
    args = ap.parse_args()
    build(Path(args.profiles), Path(args.out))
    print(Path(args.out).read_text(encoding='utf-8'))
