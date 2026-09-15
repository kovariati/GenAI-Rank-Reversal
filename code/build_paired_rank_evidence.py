#!/usr/bin/env python3
"""Build native-scale paired evidence table used by manuscript/repository."""
from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]

def _welch(n1,m1,s1,n2,m2,s2):
    est=float(m1-m2); se=np.sqrt(s1*s1/n1+s2*s2/n2)
    df=(s1*s1/n1+s2*s2/n2)**2/((s1*s1/n1)**2/(n1-1)+(s2*s2/n2)**2/(n2-1))
    q=stats.t.ppf(.975,df)
    return est,float(est-q*se),float(est+q*se)

def _hc3_two_group(n1,m1,s1,n2,m2,s2):
    est=float(m1-m2)
    # For a saturated two-group model, HC3 variance of the difference.
    se=np.sqrt(s1*s1/(n1-1) + s2*s2/(n2-1))
    q=stats.norm.ppf(.975)
    return est,float(est-q*se),float(est+q*se)

def build(results:Path):
    w=pd.read_csv(results/'wong_direct_reversal_summary.csv')
    gates=pd.read_csv(results/'construct_commensurability_audit.csv').set_index('program')
    if not gates.index.is_unique:
        raise ValueError('Duplicate commensurability program')
    eligible = 'Wong & Qiu' in gates.index and gates.loc['Wong & Qiu','rank_comparison_eligible']=='yes' and gates.loc['Wong & Qiu','commensurability_status'] in {'directionally_commensurable_with_boundary','construct_linked_directional_only','task_specific_directional_only'}
    rows=[]
    for _,r in w.iterrows():
        opposite = r.assisted_estimate*r.independent_estimate < 0
        corrected_p = float(r.holm_adjusted_orientation_reversal_p)
        if not np.isfinite(corrected_p) or not 0 <= corrected_p <= 1:
            raise ValueError('Invalid corrected reversal p value')
        supported = eligible and opposite and corrected_p < .05
        status = ('task-specific reversal supported' if supported else
                  'not classified: commensurability gate' if not eligible else 'reversal not supported')
        rows.append(dict(program='Wong & Qiu',outcome=r.outcome,active_arm_contrast='Unrestricted ChatGPT - learner-first AI',assisted_estimate=r.assisted_estimate,assisted_ci_low=r.assisted_ci_low,assisted_ci_high=r.assisted_ci_high,independent_estimate=r.independent_estimate,independent_ci_low=r.independent_ci_low,independent_ci_high=r.independent_ci_high,observed_sign_pattern='opposite-sign' if opposite else 'not opposite-sign',population_rank_status=status,inference_note=f'Two-orientation Bonferroni plus two-outcome Holm p={corrected_p:.6f}; published rounded statistics; two task-specific rating outcomes, not latent creativity or durable learning.'))
    b=pd.read_csv(results/'bastani_rank_evidence_summary.csv').iloc[0]
    rows.append(dict(program='Bastani',outcome='Mathematics practice / independent exam',active_arm_contrast='Guarded tutor - unrestricted GenAI',assisted_estimate=b.assisted_estimate,assisted_ci_low=b.assisted_ci_low,assisted_ci_high=b.assisted_ci_high,independent_estimate=b.independent_estimate,independent_ci_low=b.independent_ci_low,independent_ci_high=b.independent_ci_high,observed_sign_pattern='same-sign',population_rank_status='preservation not robustly supported',inference_note='Independent CR1 CI excludes zero, but Webb six-point wild-cluster p=0.1238 with 44 clusters; robust population preservation is not claimed.'))
    d=pd.read_csv(results/'bassner_descriptives.csv').set_index('experiment_group'); c=d.loc['CHATGPT']; i=d.loc['IRIS']
    ae,al,ah=_hc3_two_group(int(c.n),c.exercise_mean,c.exercise_sd,int(i.n),i.exercise_mean,i.exercise_sd)
    ie,il,ih=_welch(int(c.n),c.post_knowledge_mean,c.post_knowledge_sd,int(i.n),i.post_knowledge_mean,i.post_knowledge_sd)
    eff=pd.read_csv(results/'bassner_effects.csv')
    adj=float(eff.query("outcome=='post_knowledge_0_6_ancova' and intervention=='CHATGPT'").effect.iloc[0]-eff.query("outcome=='post_knowledge_0_6_ancova' and intervention=='IRIS'").effect.iloc[0])
    rows.append(dict(program='Bassner',outcome='Programming exercise / post-knowledge',active_arm_contrast='ChatGPT - Iris',assisted_estimate=ae,assisted_ci_low=al,assisted_ci_high=ah,independent_estimate=ie,independent_ci_low=il,independent_ci_high=ih,observed_sign_pattern='same-sign',population_rank_status='preservation not supported',inference_note=f'Independent direct estimate/CI is the unadjusted Welch-Satterthwaite approximate contrast. Adjusted ANCOVA active-arm point contrast={adj:.6f}; the direct robust covariance is not present in the distributed aggregate effect output and is not fabricated. The source pairwise post-test comparison was non-significant.'))
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results',default=str(ROOT/'results')); a=ap.parse_args(); r=Path(a.results)
    out=build(r); out.to_csv(r/'paired_rank_evidence_revised.csv',index=False,lineterminator='\n'); print(out.to_string(index=False))
if __name__=='__main__': main()
