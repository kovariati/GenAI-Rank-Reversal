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
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE/'results').exists() else HERE.parent

def sgn(x: float, tol: float = 1e-12) -> int:
    if not math.isfinite(float(x)) or not math.isfinite(float(tol)) or tol < 0:
        raise ValueError('Finite contrast and nonnegative finite tolerance required')
    if x > tol:
        return 1
    if x < -tol:
        return -1
    return 0

def build(profiles: Path, out: Path, commensurability: Path | None = None):
    df = pd.read_csv(profiles)
    gate_path = commensurability or ROOT/'results/construct_commensurability_audit.csv'
    gates = pd.read_csv(gate_path).set_index('program')
    if not gates.index.is_unique:
        raise ValueError('Duplicate program in commensurability audit')
    required={'program','design','supported_effect_std','independent_effect_std'}
    if not required.issubset(df.columns) or df[list(required)].isna().any().any():
        raise ValueError('Missing profile fields or values')
    if df.duplicated(['program','design']).any():
        raise ValueError('Duplicate intervention profile')
    rows = []
    for program, g in df.groupby('program', sort=False):
        if len(g) != 2:
            raise ValueError(f'{program}: exactly two intervention profiles required')
        a, b = g.iloc[0], g.iloc[1]
        da = float(a['supported_effect_std'] - b['supported_effect_std'])
        di = float(a['independent_effect_std'] - b['independent_effect_std'])
        sa, si = sgn(da), sgn(di)
        eligible = program in gates.index and str(gates.loc[program,'rank_comparison_eligible']) == 'yes' and str(gates.loc[program,'commensurability_status']) in {'directionally_commensurable_with_boundary','construct_linked_directional_only','task_specific_directional_only'}
        scope = str(gates.loc[program,'interpretive_boundary']) if program in gates.index else 'No audited comparison scope supplied'
        if not eligible:
            status = 'not_classified_commensurability_gate'
        elif sa == 0 or si == 0:
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
            'comparison_scope': scope,
            'interpretation': (
                'Comparison not classified because the commensurability gate is missing, unclear or ineligible.'
                if not eligible else
                'At least one observed contrast is tied; neither strict reversal nor strict preservation is assigned.'
                if status == 'tie_in_at_least_one_regime' else
                'Observed signs are opposite within the audited score scope. Population reversal requires direct inferential support for both signs.'
                if status == 'opposite_sign_observed' else
                'Observed signs agree; population preservation requires direct inferential support in both contexts.'
            )
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--profiles', default=str(ROOT/'results'/'paired_supported_independent_profiles.csv'))
    ap.add_argument('--out', default=str(ROOT/'results'/'pairwise_rank_transport_status.csv'))
    ap.add_argument('--commensurability', default=str(ROOT/'results/construct_commensurability_audit.csv'))
    args = ap.parse_args()
    build(Path(args.profiles), Path(args.out), Path(args.commensurability))
    print(Path(args.out).read_text(encoding='utf-8'))
