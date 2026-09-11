#!/usr/bin/env python3
"""Direct regime-specific sign inference for the Wong-Qiu reversal.

This analysis uses peer-reviewed published group-level sufficient statistics
(n, mean, SD) for unrestricted ChatGPT and learner-first/regulated AI. It is a
self-contained inferential cross-check of the two sign components required for
strict rank reversal. It does not replace the participant-level arm x regime
interaction or conditional randomization inference in analyze_wong_participant.py.

For each creativity outcome and regime, the direct contrast is defined as
unrestricted minus learner-first. Strict reversal requires D_A > 0 and D_I < 0.
The outcome-level reversal p-value uses an intersection-union test (IUT):
max(p_A_one_sided, p_I_one_sided). Holm correction is then applied across the
two co-primary creativity outcomes.
"""
from pathlib import Path
import argparse
import pandas as pd
from scipy import stats
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE/'results').exists() else HERE.parent

def welch(n1,m1,s1,n2,m2,s2):
    diff = m1-m2
    v1=s1*s1/n1; v2=s2*s2/n2
    se=math.sqrt(v1+v2)
    df=(v1+v2)**2/((v1*v1)/(n1-1)+(v2*v2)/(n2-1))
    t=diff/se
    crit=stats.t.ppf(0.975,df)
    return diff,se,df,t,diff-crit*se,diff+crit*se

def holm_adjust(ps):
    n=len(ps)
    order=sorted(range(n), key=lambda i: ps[i])
    out=[None]*n; running=0.0
    for rank,i in enumerate(order):
        adj=min(1.0,(n-rank)*ps[i])
        running=max(running,adj)
        out[i]=running
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', default=str(ROOT/'results'/'wong_published_sufficient_statistics.csv'))
    ap.add_argument('--output', default=str(ROOT/'results'/'wong_direct_reversal_inference.csv'))
    ap.add_argument('--summary', default=str(ROOT/'results'/'wong_direct_reversal_summary.csv'))
    a=ap.parse_args()
    df=pd.read_csv(a.input)
    rows=[]; summary=[]
    for outcome in ['originality','usefulness']:
        z=df[df.outcome.str.lower()==outcome].copy()
        if len(z)!=6:
            raise ValueError(f'Expected 6 sufficient-stat rows for {outcome}, found {len(z)}')
        reg_defs=[('assisted','Task 1 product improvement','greater'),('independent','Task 2 product invention','less')]
        pdir=[]; regrows=[]
        for reg,task,alt in reg_defs:
            u=z[(z.group=='Unrestricted ChatGPT') & (z.task==task)].iloc[0]
            l=z[(z.group=='Think-first ChatGPT-later') & (z.task==task)].iloc[0]
            diff,se,dfree,t,lo,hi=welch(int(u.n),float(u['mean']),float(u.sd),int(l.n),float(l['mean']),float(l.sd))
            if alt=='greater':
                p_one=float(stats.t.sf(t,dfree))
                h0='D_A <= 0'; h1='D_A > 0'
            else:
                p_one=float(stats.t.cdf(t,dfree))
                h0='D_I >= 0'; h1='D_I < 0'
            p_two=float(2*min(stats.t.sf(abs(t),dfree), stats.t.cdf(-abs(t),dfree)))
            row=dict(outcome=outcome.title(),regime=reg,contrast='unrestricted minus learner-first',estimate=diff,se=se,df=dfree,t=t,ci_low=lo,ci_high=hi,one_sided_h0=h0,one_sided_h1=h1,p_one_sided=p_one,p_two_sided=p_two,n_unrestricted=int(u.n),n_learner_first=int(l.n),source='peer-reviewed published n/mean/SD',source_doi=str(u.source_doi))
            rows.append(row); regrows.append(row); pdir.append(p_one)
        iut=max(pdir)
        strict=(regrows[0]['ci_low']>0 and regrows[1]['ci_high']<0)
        summary.append(dict(outcome=outcome.title(),assisted_estimate=regrows[0]['estimate'],assisted_ci_low=regrows[0]['ci_low'],assisted_ci_high=regrows[0]['ci_high'],assisted_p_one_sided=regrows[0]['p_one_sided'],independent_estimate=regrows[1]['estimate'],independent_ci_low=regrows[1]['ci_low'],independent_ci_high=regrows[1]['ci_high'],independent_p_one_sided=regrows[1]['p_one_sided'],intersection_union_p=iut,strict_reversal_supported_by_95ci=strict))
    adj=holm_adjust([r['intersection_union_p'] for r in summary])
    for r,aadj in zip(summary,adj): r['holm_adjusted_iut_p_across_outcomes']=aadj
    pd.DataFrame(rows).to_csv(a.output,index=False)
    pd.DataFrame(summary).to_csv(a.summary,index=False)
    print(pd.DataFrame(summary).to_string(index=False))

if __name__=='__main__':
    main()
