#!/usr/bin/env python3
"""Retrospective, task-specific sign inference from published rounded n/mean/SD.

No novel statistical test is proposed. Within each outcome the two orientations
of an opposite-sign alternative are handled by two IUTs and a Bonferroni union
bound. Holm then adjusts over the declared outcome family. The source study
already reported the qualitative interaction. Outcomes are ratings of products
in two named tasks, not a calibrated common latent creativity/learning scale.
"""
from pathlib import Path
import argparse
import math
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
TASKS = [('assisted', 'Task 1 product improvement'),
         ('independent', 'Task 2 product invention')]
GROUPS = {'Human-only', 'Unrestricted ChatGPT', 'Think-first ChatGPT-later'}

def welch(n1, m1, s1, n2, m2, s2):
    """Welch--Satterthwaite approximation; marginal two-sided 95% interval."""
    for n, m, s in [(n1, m1, s1), (n2, m2, s2)]:
        if not all(math.isfinite(float(v)) for v in (n, m, s)):
            raise ValueError('Sample statistics must be finite')
        if n != int(n) or n < 2 or s < 0:
            raise ValueError('n must be an integer >= 2; SD must be nonnegative')
    diff = float(m1 - m2)
    v1, v2 = s1*s1/n1, s2*s2/n2
    if v1 + v2 <= 0:
        raise ValueError('A positive contrast standard error is required')
    se = math.sqrt(v1 + v2)
    df = (v1 + v2)**2 / (v1*v1/(n1-1) + v2*v2/(n2-1))
    t = diff/se
    crit = stats.t.ppf(.975, df)
    return diff, se, df, t, diff-crit*se, diff+crit*se

def holm_adjust(ps):
    ps = [float(p) for p in ps]
    if not all(math.isfinite(p) and 0 <= p <= 1 for p in ps):
        raise ValueError('p values must be finite and lie in [0, 1]')
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0]*len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1., (len(ps)-rank)*ps[i]))
        out[i] = running
    return out

def reversal_pvalues(p_a_greater, p_i_greater):
    """Direction-conditional IUTs and conservative orientation-unselected p.

Marginal p values are Welch approximations. No independence is required between
contexts for the IUT or Bonferroni steps. Independence is required between arms
within each Welch comparison. Reversing the arm coding leaves the final p unchanged.
    """
    for p in (p_a_greater, p_i_greater):
        if not math.isfinite(float(p)) or not 0 <= p <= 1:
            raise ValueError('Invalid marginal p value')
    forward = max(p_a_greater, 1-p_i_greater)
    reverse = max(1-p_a_greater, p_i_greater)
    return forward, reverse, min(1., 2*min(forward, reverse))

def validate_statistics(df, outcomes):
    required = {'outcome','task','group','n','mean','sd','source_doi'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing required columns: {sorted(required-set(df.columns))}')
    z = df.copy()
    if z[list(required)].isna().any().any():
        raise ValueError('Missing sufficient-statistics values')
    z['outcome'] = z.outcome.str.lower()
    if z.duplicated(['outcome','task','group']).any():
        raise ValueError('Duplicate outcome/task/group row')
    for outcome in outcomes:
        q = z[z.outcome == outcome]
        expected = {(task, group) for _, task in TASKS for group in GROUPS}
        if set(zip(q.task,q.group)) != expected:
            raise ValueError(f'Incomplete or unexpected task/group cells for {outcome}')
    for row in z.itertuples():
        if not all(math.isfinite(float(v)) for v in (row.n,row.mean,row.sd)):
            raise ValueError('Non-finite sample statistics')
        if row.n != int(row.n) or row.n < 2 or row.sd < 0:
            raise ValueError('Invalid n or SD')
    return z

def analyze(df, outcomes=('originality','usefulness')):
    """The two-outcome family is retained from the submitted analysis.

Originality is now the focal presentation, usefulness secondary corroboration;
this retrospective narrowing is NOT represented as preregistered selection.
    """
    outcomes = tuple(str(x).lower() for x in outcomes)
    if not outcomes or len(set(outcomes)) != len(outcomes):
        raise ValueError('Specify a nonempty family of distinct outcomes')
    df = validate_statistics(df, outcomes)
    rows, summary = [], []
    for outcome in outcomes:
        z = df[df.outcome == outcome]
        regrows, pg = [], []
        for reg, task in TASKS:
            u = z[(z.group == 'Unrestricted ChatGPT') & (z.task == task)].iloc[0]
            l = z[(z.group == 'Think-first ChatGPT-later') & (z.task == task)].iloc[0]
            diff,se,dfree,t,lo,hi = welch(u.n,u['mean'],u.sd,l.n,l['mean'],l.sd)
            pgreater, pless = float(stats.t.sf(t,dfree)), float(stats.t.cdf(t,dfree))
            row = dict(outcome=outcome.title(),regime=reg,task=task,
                       contrast='unrestricted minus learner-first',estimate=diff,se=se,df=dfree,t=t,
                       ci_low=lo,ci_high=hi,p_greater=pgreater,p_less=pless,
                       p_one_sided=pgreater if reg=='assisted' else pless,
                       p_two_sided=float(2*stats.t.sf(abs(t),dfree)),
                       n_unrestricted=int(u.n),n_learner_first=int(l.n),
                       source='published rounded n/mean/SD; Welch approximation',source_doi=u.source_doi)
            rows.append(row); regrows.append(row); pg.append(pgreater)
        # Direct tails avoid cancellation when the first IUT is very small.
        forward = max(regrows[0]['p_greater'],regrows[1]['p_less'])
        reverse = max(regrows[0]['p_less'],regrows[1]['p_greater'])
        unoriented = min(1., 2*min(forward,reverse))
        a, i = regrows
        opposite = a['estimate']*i['estimate'] < 0
        summary.append(dict(outcome=outcome.title(),
            assisted_estimate=a['estimate'],assisted_ci_low=a['ci_low'],assisted_ci_high=a['ci_high'],
            assisted_p_one_sided=a['p_one_sided'],
            independent_estimate=i['estimate'],independent_ci_low=i['ci_low'],independent_ci_high=i['ci_high'],
            independent_p_one_sided=i['p_one_sided'],
            intersection_union_p=forward,reverse_orientation_iut_p=reverse,
            orientation_adjusted_reversal_p=unoriented,
            opposite_signs_observed=opposite,
            strict_reversal_supported_by_95ci=(a['ci_low']>0 and i['ci_high']<0) or (a['ci_high']<0 and i['ci_low']>0),
            endpoint_scope='expert-rated '+outcome+' of products in these two tasks only',
            inference_status='retrospective; approximate marginal tests; not a new statistical method'))
    joint_critical_probability = 1 - .05/(2*len(rows))
    for row in rows:
        crit = stats.t.ppf(joint_critical_probability,row['df'])
        row['bonferroni_family_95ci_low'] = row['estimate']-crit*row['se']
        row['bonferroni_family_95ci_high'] = row['estimate']+crit*row['se']
        row['simultaneous_contrast_family_size'] = len(rows)
        row['simultaneous_coverage_note'] = 'Bonferroni joint 95% nominal; subject to marginal Welch approximation'
    legacy = holm_adjust([r['intersection_union_p'] for r in summary])
    corrected = holm_adjust([r['orientation_adjusted_reversal_p'] for r in summary])
    for r, pold, pnew in zip(summary,legacy,corrected):
        r['holm_adjusted_iut_p_across_outcomes'] = pold  # retained, explicitly conditional diagnostic
        r['holm_adjusted_orientation_reversal_p'] = pnew
        r['multiplicity_family_size'] = len(outcomes)
        r['task_specific_reversal_supported_0_05'] = r['opposite_signs_observed'] and pnew < .05
    return pd.DataFrame(rows), pd.DataFrame(summary)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=str(ROOT/'results/wong_published_sufficient_statistics.csv'))
    ap.add_argument('--output', default=str(ROOT/'results/wong_direct_reversal_inference.csv'))
    ap.add_argument('--summary', default=str(ROOT/'results/wong_direct_reversal_summary.csv'))
    ap.add_argument('--outcomes', nargs='+', default=['originality','usefulness'])
    a = ap.parse_args()
    detail, summary = analyze(pd.read_csv(a.input), a.outcomes)
    for frame, name in [(detail,a.output),(summary,a.summary)]:
        p=Path(name); p.parent.mkdir(parents=True,exist_ok=True); frame.to_csv(p,index=False)
    print(summary.to_string(index=False))

if __name__ == '__main__':
    main()
