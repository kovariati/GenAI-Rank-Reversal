#!/usr/bin/env python3
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
SEED=20260817

def _bootstrap_sign_tail(x):
    x=np.asarray(x,float); n=len(x)
    le=int(np.sum(x<=0)); ge=int(np.sum(x>=0))
    return min(1.0, 2.0*(min(le,ge)+1)/(n+1))

def _metrics(df, out1, out2):
    m={}; s={}
    for c in [0,1,2]:
        z=df[df.Condition==c]
        m[(c,1)]=float(z[out1].mean()); m[(c,2)]=float(z[out2].mean())
    s[1]=float(df[df.Condition==0][out1].std(ddof=1)); s[2]=float(df[df.Condition==0][out2].std(ddof=1))
    if not all(np.isfinite(v) and v > 0 for v in s.values()):
        raise ValueError('Positive finite task-specific control SD required')
    eff={}; raw={}
    for c in [1,2]:
        r1=m[(c,1)]-m[(0,1)]; r2=m[(c,2)]-m[(0,2)]
        e1=r1/s[1]; e2=r2/s[2]
        eff[c]=(e1,e2,e2-e1); raw[c]=(r1,r2,r2-r1)
    return eff, eff[2][2]-eff[1][2], raw, raw[2][2]-raw[1][2]

def analyze(raw_xlsx: Path, results: Path, reps=9999, permutation_reps=99999):
    if not isinstance(reps,int) or reps < 2 or not isinstance(permutation_reps,int) or permutation_reps < 2:
        raise ValueError('Bootstrap and permutation replicate counts must be integers >= 2')
    d=pd.read_excel(raw_xlsx, sheet_name='Data')
    req=['Condition','Originality1','Originality2','Usefulness1','Usefulness2']
    if any(c not in d.columns for c in req): raise ValueError('Wong workbook missing required columns')
    d=d[req].apply(pd.to_numeric,errors='raise').copy().reset_index(drop=True)
    if not np.isfinite(d.to_numpy(dtype=float)).all():
        raise ValueError('All required participant values must be finite; missing scores are not silently dropped')
    if ((d[req[1:]] < 1) | (d[req[1:]] > 7)).any().any():
        raise ValueError('Expected source rating scores between 1 and 7')
    if len(d)!=196 or sorted(d.Condition.value_counts().to_dict().items())!=[(0,64),(1,67),(2,65)]:
        raise ValueError('Unexpected Wong sample structure')
    rng=np.random.default_rng(SEED)
    idx={c:d.index[d.Condition==c].to_numpy() for c in [0,1,2]}
    all_rows=[]; diff_rows=[]; mean_rows=[]
    for outcome,o1,o2 in [('Originality','Originality1','Originality2'),('Usefulness','Usefulness1','Usefulness2')]:
        for c,label in [(0,'Human-only'),(1,'Unrestricted ChatGPT'),(2,'Learner-first AI')]:
            z=d[d.Condition==c]
            mean_rows.append(dict(outcome=outcome,design=label,n=int(len(z)),assisted_task_mean=float(z[o1].mean()),independent_task_mean=float(z[o2].mean())))
        point=_metrics(d,o1,o2)
        b=[]
        for _ in range(reps):
            chunks=[]
            for c in [0,1,2]:
                ix=rng.choice(idx[c],size=len(idx[c]),replace=True)
                chunks.append(d.loc[ix].copy())
            z=pd.concat(chunks,ignore_index=True)
            e,di,r,dr=_metrics(z,o1,o2)
            b.append([e[1][0],e[1][1],e[1][2],e[2][0],e[2][1],e[2][2],di,r[1][0],r[1][1],r[1][2],r[2][0],r[2][1],r[2][2],dr])
        b=np.asarray(b,float); q=np.quantile(b,[.025,.975],axis=0)
        e,di,r,dr=point
        for c,design,base in [(1,'Unrestricted ChatGPT',0),(2,'Think-first, ChatGPT-later',3)]:
            all_rows.append(dict(study='Wong & Qiu (2026)',outcome=outcome,design=design,
                assisted_effect_std=e[c][0],assisted_ci_low=q[0,base],assisted_ci_high=q[1,base],
                independent_effect_std=e[c][1],independent_ci_low=q[0,base+1],independent_ci_high=q[1,base+1],
                independent_minus_assisted_std=e[c][2],profile_change_ci_low=q[0,base+2],profile_change_ci_high=q[1,base+2],
                profile_change_bootstrap_sign_tail=_bootstrap_sign_tail(b[:,base+2]),
                assisted_effect_raw=r[c][0],independent_effect_raw=r[c][1],raw_profile_change=r[c][2],bootstrap_reps=reps))
        diff_rows.append(dict(outcome=outcome,differential_profile_change_std=di,diff_ci_low=q[0,6],diff_ci_high=q[1,6],
            diff_bootstrap_sign_tail=_bootstrap_sign_tail(b[:,6]),raw_differential_profile_change=dr,raw_diff_ci_low=q[0,13],raw_diff_ci_high=q[1,13],bootstrap_reps=reps))
    # Direct participant-clustered arm x assessment-regime interaction.
    # This estimates differential treatment-effect profiles across the two assessment
    # conditions; it is not interpreted as the causal effect of removing AI because
    # task content and assessment conditions also change.
    interaction_rows=[]
    dd=d.copy()
    dd['participant_id']=np.arange(len(dd),dtype=int)
    ctrl=dd[dd.Condition==0]
    for outcome,o1,o2 in [('Originality','Originality1','Originality2'),('Usefulness','Usefulness1','Usefulness2')]:
        cmean={1:float(ctrl[o1].mean()),2:float(ctrl[o2].mean())}
        csd={1:float(ctrl[o1].std(ddof=1)),2:float(ctrl[o2].std(ddof=1))}
        sub=dd[dd.Condition.isin([1,2])].copy()
        long=[]
        for _,rr in sub.iterrows():
            lf=1 if int(rr.Condition)==2 else 0
            long.append({'participant_id':int(rr.participant_id),'learner_first':lf,'independent':0,'y_raw':float(rr[o1]),'y_std':(float(rr[o1])-cmean[1])/csd[1]})
            long.append({'participant_id':int(rr.participant_id),'learner_first':lf,'independent':1,'y_raw':float(rr[o2]),'y_std':(float(rr[o2])-cmean[2])/csd[2]})
        long=pd.DataFrame(long)
        for scale in ['raw','std']:
            model=smf.ols(f'y_{scale} ~ learner_first * independent',data=long).fit(cov_type='cluster',cov_kwds={'groups':long.participant_id})
            term='learner_first:independent'
            ci=model.conf_int().loc[term]
            interaction_rows.append(dict(outcome=outcome,scale=scale,interaction_estimate=float(model.params[term]),interaction_se=float(model.bse[term]),interaction_ci_low=float(ci.iloc[0]),interaction_ci_high=float(ci.iloc[1]),interaction_p=float(model.pvalues[term]),n_participants=int(sub.shape[0]),n_long_rows=int(long.shape[0]),covariance='participant-clustered HC'))


    # Conditional randomization inference for the two randomized AI arms.
    # The statistic is the difference in participant-level task change
    # (independent minus assisted) between learner-first and unrestricted arms.
    # This is algebraically the raw learner_first x independent interaction.
    # Originality and usefulness are treated jointly as the two creativity outcomes
    # analyzed in the source study. Constant permutation-SD scaling is NOT
    # heteroscedastic studentization. max-|T| here is a complete-sharp-null
    # diagnostic; strong marginal FWER control is not asserted.
    ai=dd[dd.Condition.isin([1,2])].copy().reset_index(drop=True)
    n_ai=len(ai); n_lf=int((ai.Condition==2).sum()); n_u=int((ai.Condition==1).sum())
    if (n_ai,n_lf,n_u)!=(132,65,67):
        raise ValueError('Unexpected Wong AI-arm randomization structure')
    perm_rng=np.random.default_rng(SEED+1900)
    changes={
        'Originality':(ai['Originality2']-ai['Originality1']).to_numpy(float),
        'Usefulness':(ai['Usefulness2']-ai['Usefulness1']).to_numpy(float),
    }
    obs_lf=(ai.Condition.to_numpy()==2)
    obs_stats={}
    for outcome,x in changes.items():
        obs_stats[outcome]=float(x[obs_lf].mean()-x[~obs_lf].mean())
    perm_stats={k:np.empty(permutation_reps,dtype=float) for k in changes}
    for bidx in range(permutation_reps):
        lf_ix=perm_rng.choice(n_ai,size=n_lf,replace=False)
        mask=np.zeros(n_ai,dtype=bool); mask[lf_ix]=True
        for outcome,x in changes.items():
            perm_stats[outcome][bidx]=x[mask].mean()-x[~mask].mean()
    perm_sd={k:float(np.std(v,ddof=1)) for k,v in perm_stats.items()}
    if not all(np.isfinite(v) and v > 0 for v in perm_sd.values()):
        raise ValueError('Positive permutation variance required for standardized diagnostics')
    max_t=np.maximum.reduce([np.abs(perm_stats[k]/perm_sd[k]) for k in changes])
    ri_rows=[]
    for outcome in ['Originality','Usefulness']:
        obs=obs_stats[outcome]; ps=perm_stats[outcome]
        p_unadj=float((1+np.sum(np.abs(ps)>=abs(obs)))/(permutation_reps+1))
        obs_t=abs(obs/perm_sd[outcome])
        p_max=float((1+np.sum(max_t>=obs_t))/(permutation_reps+1))
        ri_rows.append(dict(
            outcome=outcome,
            estimand='difference in (independent - assisted) change: learner-first minus unrestricted',
            observed_raw_interaction=obs,
            permutation_sd=perm_sd[outcome],
            permutation_standardized_abs_stat=obs_t,
            randomization_p_two_sided=p_unadj,
            maxT_global_null_adjusted_p=p_max,
            permutation_reps=permutation_reps,
            permutation_seed=SEED+1900,
            conditioned_on='two randomized AI arms; fixed group sizes 65 learner-first / 67 unrestricted',
            null_scope='exchangeable labels under sharp no-effect-on-individual-task-change null; not the weak mean-interaction null',
            standardization='constant permutation SD; not per-permutation Welch studentization',
        ))

    from analyze_wong_direct_reversal import holm_adjust
    for row,p_adj in zip(ri_rows,holm_adjust([row['randomization_p_two_sided'] for row in ri_rows])):
        row['holm_adjusted_marginal_sharp_null_p']=p_adj

    results.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(all_rows).to_csv(results/'wong_participant_reanalysis.csv',index=False)
    pd.DataFrame(diff_rows).to_csv(results/'wong_profile_interaction_bootstrap.csv',index=False)
    pd.DataFrame(interaction_rows).to_csv(results/'wong_interaction_model.csv',index=False)
    pd.DataFrame(mean_rows).to_csv(results/'wong_raw_group_means.csv',index=False)
    pd.DataFrame(ri_rows).to_csv(results/'wong_randomization_inference.csv',index=False)
    prov={'source':'Wong & Qiu OSF t7an8 Supplemental Data.xlsx','source_url':'https://osf.io/t7an8/','rows':len(d),'raw_redistributed':False,'bootstrap_seed':SEED,'bootstrap_reps':reps,'interaction_model':'OLS arm x assessment regime with participant-clustered covariance; descriptive differential profile, not causal AI-removal effect','randomization_inference':'conditional label permutation within the two randomized AI arms, preserving 65/67 group sizes; max-|T| complete-null diagnostic; Holm across marginal sharp-null p values; not a test of strict sign reversal','permutation_seed':SEED+1900,'permutation_reps':permutation_reps}
    (results/'wong_source_provenance.json').write_text(json.dumps(prov,indent=2),encoding='utf-8')
    print(pd.DataFrame(all_rows).to_string(index=False)); print(pd.DataFrame(diff_rows).to_string(index=False)); print(pd.DataFrame(interaction_rows).to_string(index=False)); print(pd.DataFrame(ri_rows).to_string(index=False)); print(json.dumps(prov,indent=2))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--raw-xlsx',required=True); ap.add_argument('--results',default=str(ROOT/'results')); ap.add_argument('--bootstrap-reps',type=int,default=9999); ap.add_argument('--permutation-reps',type=int,default=99999)
    a=ap.parse_args(); analyze(Path(a.raw_xlsx),Path(a.results),a.bootstrap_reps,a.permutation_reps)
if __name__=='__main__': main()
