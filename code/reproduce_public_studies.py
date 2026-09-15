#!/usr/bin/env python3
"""Reproducible analyses for:
Generative AI, Performance, and Learning: Intervention Rank Reversal Across Assessment Regimes

This script does not redistribute raw participant-level data. It expects the
three user-supplied/public source files at paths given by command line options
or the defaults below.
"""
from __future__ import annotations
import argparse, json, math, os, platform, sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.linear_model import QuantileRegressor

SEED = 20260816
np.random.seed(SEED)


def term_stats(res, term: str):
    # res may be RegressionResultsWrapper or robustcov result with ndarray params
    names = list(res.model.exog_names)
    i = names.index(term)
    b = float(np.asarray(res.params)[i])
    se = float(np.asarray(res.bse)[i])
    p = float(np.asarray(res.pvalues)[i])
    ci = np.asarray(res.conf_int())
    lo, hi = float(ci[i,0]), float(ci[i,1])
    return b, se, p, lo, hi


def linear_contrast_stats(res, weights: dict[str,float]):
    names = list(res.model.exog_names)
    L = np.zeros(len(names))
    for t,w in weights.items():
        L[names.index(t)] = w
    test = res.t_test(L)
    b = float(np.asarray(test.effect).ravel()[0])
    se = float(np.asarray(test.sd).ravel()[0])
    p = float(np.asarray(test.pvalue).ravel()[0])
    ci = np.asarray(test.conf_int())
    lo, hi = float(ci[0,0]), float(ci[0,1])
    return b,se,p,lo,hi


def cluster_fit(formula, data, cluster_col):
    fit = smf.ols(formula, data=data).fit()
    robust = fit.get_robustcov_results(cov_type='cluster', groups=data[cluster_col], use_correction=True, df_correction=True, use_t=True)
    return robust


def hc3_fit(formula, data):
    return smf.ols(formula, data=data).fit(cov_type='HC3', use_t=True)


def holm(pvalues):
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    out = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        val = (m-rank)*p[idx]
        running = max(running, val)
        out[idx] = min(running, 1.0)
    return out


def bootstrap_bastani_profile_contrast(df, formula, B=2000):
    """Fast cluster-pairs bootstrap for the treatment coefficients.

    The design matrix is created once. Classroom clusters are then sampled with
    replacement and OLS coefficients are solved directly by least squares. This
    preserves the entire classroom block and avoids expensive formula parsing in
    each replicate.
    """
    base = smf.ols(formula, data=df).fit()
    X = np.asarray(base.model.exog, dtype=float)
    y = np.asarray(base.model.endog, dtype=float)
    names = list(base.model.exog_names)
    term_idx = {t:names.index(t) for t in ['GPTBase','GPTTutor']}
    clusters = df['Class'].astype(str).to_numpy()
    unique = np.array(sorted(np.unique(clusters)))
    idx_by_cluster = {c:np.flatnonzero(clusters==c) for c in unique}
    vals = {t: np.empty(B, dtype=float) for t in term_idx}
    rng = np.random.default_rng(SEED)
    good=0
    for _ in range(B):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        idx = np.concatenate([idx_by_cluster[c] for c in sampled])
        coef = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
        for t,j in term_idx.items(): vals[t][good]=coef[j]
        good += 1
    rows=[]
    for t,a0 in vals.items():
        a=a0[:good]
        rows.append({'term':t,'bootstrap_reps':int(len(a)),
                     'bootstrap_mean':float(a.mean()),
                     'bootstrap_se':float(a.std(ddof=1)),
                     'bootstrap_ci_low':float(np.quantile(a,.025)),
                     'bootstrap_ci_high':float(np.quantile(a,.975))})
    return pd.DataFrame(rows)




def wild_cluster_bootstrap_t(data, formula, cluster_col, contrast_weights, null_type, B=9999, seed=SEED+303):
    """Restricted-null Webb wild cluster bootstrap-t, vectorized over replicates.

    The implementation is algebraically equivalent to refitting unrestricted OLS
    for each bootstrap pseudo-outcome, but uses precomputed cluster cross-products
    and contrast-specific cluster scores. This makes 9999 replications practical.
    """
    fit=smf.ols(formula, data=data).fit()
    X=np.asarray(fit.model.exog,dtype=float); y=np.asarray(fit.model.endog,dtype=float)
    names=list(fit.model.exog_names); N,K=X.shape
    clusters=data[cluster_col].astype(str).to_numpy(); uniq=np.array(sorted(np.unique(clusters))); G=len(uniq)
    idx=[np.flatnonzero(clusters==g) for g in uniq]
    XtX=X.T@X; inv=np.linalg.inv(XtX)
    scale=(G/(G-1))*((N-1)/(N-K))
    c=np.zeros(K)
    for term,w in contrast_weights.items(): c[names.index(term)]=w

    def contrast_vcov(beta, yy):
        rr=yy-X@beta; d=inv@c; vv=0.0
        for ii in idx:
            sg=X[ii].T@rr[ii]; vv += float((d@sg)**2)
        return scale*vv

    beta=np.asarray(fit.params,dtype=float)
    effect=float(c@beta); se=float(np.sqrt(contrast_vcov(beta,y))); t_obs=effect/se
    p_cr1=float(2*st.t.sf(abs(t_obs),df=G-1))

    ddata=data.copy()
    if null_type=='GPTBase=0':
        f0=formula.replace('GPTBase + ','')
    elif null_type=='GPTTutor=0':
        f0=formula.replace(' + GPTTutor','')
    elif null_type=='GPTTutor=GPTBase':
        ddata['GPTAny']=ddata['GPTBase']+ddata['GPTTutor']
        lhs=formula.split('~',1)[0].strip()
        rhs='GPTAny + gpa_prev + C(teacher) + C(Session) + C(Grader) + C(Year)'
        f0=f'{lhs} ~ {rhs}'
    else:
        raise ValueError(null_type)
    restricted=smf.ols(f0,data=ddata).fit()
    fit0=np.asarray(restricted.fittedvalues,dtype=float); u0=np.asarray(restricted.resid,dtype=float)

    # Cluster cross-products for vectorized bootstrap.
    Q=np.column_stack([X[ii].T@u0[ii] for ii in idx])              # K x G
    A=[X[ii].T@fit0[ii] for ii in idx]                            # G vectors K
    H=[X[ii].T@X[ii] for ii in idx]                               # G matrices KxK
    Xt_fit0=X.T@fit0
    dvec=inv@c
    rng=np.random.default_rng(seed)
    webb=np.array([-np.sqrt(1.5),-1.0,-np.sqrt(0.5),np.sqrt(0.5),1.0,np.sqrt(1.5)])
    W=rng.choice(webb,size=(G,B))                                 # G x B
    Bstar=inv@(Xt_fit0[:,None] + Q@W)                            # K x B
    effects=c@Bstar                                               # B
    vv=np.zeros(B,dtype=float)
    for g in range(G):
        # d' [Xg'(fit0 + u0*w - Xg*b*)]
        ug=float(dvec@A[g]) + float(dvec@Q[:,g])*W[g,:] - (dvec@H[g])@Bstar
        vv += ug*ug
    sest=np.sqrt(scale*vv)
    tstar=effects/sest
    p_wild=float((np.sum(np.abs(tstar)>=abs(t_obs))+1)/(B+1))
    return {'effect':effect,'se_cr1':se,'t_cr1':float(t_obs),'p_cr1':p_cr1,
            'wild_bootstrap_p':p_wild,'wild_bootstrap_reps':int(B),'clusters':int(G),
            'weights':'Webb six-point','null_hypothesis':null_type}


def leave_one_cluster_out_contrast(data, formula, cluster_col, weights):
    vals=[]
    for g in sorted(data[cluster_col].astype(str).unique()):
        dd=data.loc[data[cluster_col].astype(str)!=g].copy()
        rr=cluster_fit(formula,dd,cluster_col)
        vals.append(linear_contrast_stats(rr,weights)[0])
    a=np.asarray(vals,dtype=float)
    return {'clusters_omitted':int(len(a)),'min_effect':float(a.min()),'max_effect':float(a.max()),
            'mean_effect':float(a.mean()),'all_same_sign':bool(np.all(a>0) or np.all(a<0))}

def quantile_cluster_bootstrap(data, outcome, treatment, covariates, cluster_col, q=0.5, B=1999):
    """Fast participant-cluster bootstrap for median/quantile regression.

    The design matrix is constructed once. Each cluster bootstrap draw is represented
    by integer sample weights and fitted with scikit-learn's HiGHS-backed
    QuantileRegressor. For q=0.5 and alpha=0 this solves the same LAD objective as
    statsmodels QuantReg, while making 1999+ cluster bootstrap replications practical.
    """
    formula = f"{outcome} ~ {treatment}" + (f" + {covariates}" if covariates else "")
    design = smf.ols(formula, data).fit()
    X = np.asarray(design.model.exog, dtype=float)
    y = np.asarray(design.model.endog, dtype=float)
    names = list(design.model.exog_names)
    treatment_idx = names.index(treatment)
    qr0 = QuantileRegressor(quantile=q, alpha=0.0, fit_intercept=False, solver='highs').fit(X, y)
    point = float(qr0.coef_[treatment_idx])
    clusters = np.array(sorted(data[cluster_col].unique()))
    cluster_values = data[cluster_col].to_numpy()
    idx_by_cluster = {c:np.flatnonzero(cluster_values==c) for c in clusters}
    rng = np.random.default_rng(SEED + 101)
    vals = np.empty(B, dtype=float)
    for r in range(B):
        sampled = rng.choice(clusters, size=len(clusters), replace=True)
        unique, counts = np.unique(sampled, return_counts=True)
        weights = np.zeros(len(data), dtype=float)
        for c,n in zip(unique,counts):
            weights[idx_by_cluster[c]] = n
        qr = QuantileRegressor(quantile=q, alpha=0.0, fit_intercept=False, solver='highs').fit(X, y, sample_weight=weights)
        vals[r] = float(qr.coef_[treatment_idx])
    a = vals
    return {
        "effect":point,
        "bootstrap_reps":int(len(a)),
        "bootstrap_se":float(a.std(ddof=1)),
        "ci_low":float(np.quantile(a,.025)),
        "ci_high":float(np.quantile(a,.975)),
        "bootstrap_p":float(min(1.0, 2*min((np.sum(a<=0)+1)/(len(a)+1), (np.sum(a>=0)+1)/(len(a)+1)))),
    }


def main():
    ap=argparse.ArgumentParser()
    package_root = Path(__file__).resolve().parents[1]
    ap.add_argument('--bastani', default=str(package_root/'data'/'raw'/'bastani_final_data.csv'))
    ap.add_argument('--kestin', default=str(package_root/'data'/'raw'/'Harvard_AI_Tutor_Study_Data.dta'))
    ap.add_argument('--pardos', default=str(package_root/'data'/'raw'/'Participants.csv'))
    ap.add_argument('--outdir', default=str(package_root))
    ap.add_argument('--bootstrap', type=int, default=500)
    ap.add_argument('--wild-bootstrap', type=int, default=9999)
    ap.add_argument('--quantile-bootstrap', type=int, default=1999)
    args=ap.parse_args()
    out=Path(args.outdir); resdir=out/'results'; figdir=out/'figures'
    resdir.mkdir(parents=True, exist_ok=True); figdir.mkdir(parents=True, exist_ok=True)

    paths={k:Path(v) for k,v in [('Bastani',args.bastani),('Kestin',args.kestin),('Pardos',args.pardos)]}
    provenance=[]
    for k,p in paths.items():
        provenance.append({'study':k,'source_file':p.name,'bytes':p.stat().st_size})
    pd.DataFrame(provenance).to_csv(resdir/'source_provenance.csv',index=False)

    # ---------------- Bastani et al. ----------------
    b=pd.read_csv(paths['Bastani'])
    b0=b.copy()
    b_nonhonors=b[b['Honors']==0].copy()
    # Statsmodels C() factor terms mirror R factors. OLS drops missing rows automatically;
    # force one complete common analysis sample for supported and independent outcomes.
    vars_b=['Part2Tot','Part3Tot','GPTBase','GPTTutor','gpa_prev','teacher','Session','Grader','Year','Class','Student ID','Treatment arm']
    b=b_nonhonors.dropna(subset=vars_b).copy()

    # Analysis-sample / missingness audit. This reports only what can be established
    # from the released files; it does not reconstruct unreleased enrollment records.
    sample_audit=[]
    for arm in ['control','vanilla','augmented']:
        raw_arm=b_nonhonors[b_nonhonors['Treatment arm']==arm].copy()
        ana_arm=raw_arm.dropna(subset=vars_b).copy()
        sample_audit.append({
            'study':'Bastani et al. (2025)','group':arm,'released_rows':len(raw_arm),
            'released_participants':raw_arm['Student ID'].nunique(),
            'analysis_rows':len(ana_arm),'analysis_participants':ana_arm['Student ID'].nunique(),
            'rows_excluded_core_complete_case':len(raw_arm)-len(ana_arm),
            'missing_supported_outcome':int(raw_arm['Part2Tot'].isna().sum()),
            'missing_independent_outcome':int(raw_arm['Part3Tot'].isna().sum()),
            'missing_baseline':int(raw_arm['gpa_prev'].isna().sum()),
            'other_core_missing':int((raw_arm[vars_b].isna().any(axis=1) & ~raw_arm['gpa_prev'].isna()).sum()),
            'audit_scope':'Released non-honors rows; honors excluded by primary source-aligned specification'
        })
    f2='Part2Tot ~ GPTBase + GPTTutor + gpa_prev + C(teacher) + C(Session) + C(Grader) + C(Year)'
    f3='Part3Tot ~ GPTBase + GPTTutor + gpa_prev + C(teacher) + C(Session) + C(Grader) + C(Year)'
    b['profile_contrast_outcome']=b['Part2Tot']-b['Part3Tot']
    fg='profile_contrast_outcome ~ GPTBase + GPTTutor + gpa_prev + C(teacher) + C(Session) + C(Grader) + C(Year)'
    r2=cluster_fit(f2,b,'Class'); r3=cluster_fit(f3,b,'Class'); rg=cluster_fit(fg,b,'Class')

    bdesc=[]
    for arm in ['control','vanilla','augmented']:
        d=b[b['Treatment arm']==arm]
        bdesc.append({'study':'Bastani et al. (2025)','group':arm,'n_observations':len(d),'n_participants':d['Student ID'].nunique(),
                      'assisted_mean':d['Part2Tot'].mean(),'assisted_sd':d['Part2Tot'].std(ddof=1),
                      'independent_mean':d['Part3Tot'].mean(),'independent_sd':d['Part3Tot'].std(ddof=1)})
    bdesc=pd.DataFrame(bdesc)
    b_control_sd=float(bdesc.loc[bdesc.group=='control','independent_sd'].iloc[0])

    primary=[]
    for term,label in [('GPTBase','Standard generative AI vs no-AI control'),('GPTTutor','Pedagogically guarded AI tutor vs no-AI control')]:
        bb,se,p,lo,hi=term_stats(r3,term)
        primary.append({'study':'Bastani et al. (2025)','intervention':label,'comparator':'No-AI business-as-usual','outcome':'Unassisted exam score (0–1)',
                        'effect_raw':bb,'se_raw':se,'ci_low_raw':lo,'ci_high_raw':hi,'p_value':p,
                        'control_sd':b_control_sd,'effect_std':bb/b_control_sd,'se_std':se/b_control_sd,
                        'ci_low_std':lo/b_control_sd,'ci_high_std':hi/b_control_sd,
                        'analysis':'ITT OLS with prior GPA and teacher/session/grader/year fixed effects; class-cluster robust SE'})

    gap=[]
    for term,label in [('GPTBase','Standard generative AI'),('GPTTutor','Pedagogically guarded AI tutor')]:
        b2,se2,p2,l2,h2=term_stats(r2,term); b3,se3,p3,l3,h3=term_stats(r3,term); bg,seg,pg,lg,hg=term_stats(rg,term)
        gap.append({'intervention':label,'assisted_effect':b2,'assisted_se':se2,'assisted_ci_low':l2,'assisted_ci_high':h2,'assisted_p':p2,
                    'independent_effect':b3,'independent_se':se3,'independent_ci_low':l3,'independent_ci_high':h3,'independent_p':p3,
                    'within_study_profile_contrast':bg,'contrast_se':seg,'contrast_ci_low':lg,'contrast_ci_high':hg,'contrast_p':pg})
    gap=pd.DataFrame(gap)
    bootcontrast=bootstrap_bastani_profile_contrast(b,fg,B=args.bootstrap)
    gap['bootstrap_reps']=gap['intervention'].map({'Standard generative AI':'GPTBase','Pedagogically guarded AI tutor':'GPTTutor'}).map(dict(zip(bootcontrast.term,bootcontrast.bootstrap_reps)))
    gap['bootstrap_ci_low']=gap['intervention'].map({'Standard generative AI':'GPTBase','Pedagogically guarded AI tutor':'GPTTutor'}).map(dict(zip(bootcontrast.term,bootcontrast.bootstrap_ci_low)))
    gap['bootstrap_ci_high']=gap['intervention'].map({'Standard generative AI':'GPTBase','Pedagogically guarded AI tutor':'GPTTutor'}).map(dict(zip(bootcontrast.term,bootcontrast.bootstrap_ci_high)))

    # Direct Tutor vs Base contrast
    contrasts=[]
    for result,outcome in [(r2,'Assisted practice'),(r3,'Independent exam'),(rg,'Within-study supported-to-independent profile contrast')]:
        x=linear_contrast_stats(result,{'GPTTutor':1,'GPTBase':-1})
        contrasts.append({'contrast':'Pedagogically guarded AI tutor minus standard generative AI','outcome':outcome,
                          'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    pd.DataFrame(contrasts).to_csv(resdir/'bastani_direct_contrasts.csv',index=False)

    # Small-cluster inference for the flagship independent-exam contrasts.
    # The source-aligned CR1 estimates use 44 classroom clusters. Webb wild-cluster
    # bootstrap-t inference is reported because conventional cluster-robust p-values
    # can be optimistic with a modest number of clusters.
    small_cluster=[]
    tests=[
        ('Standard GenAI vs no-AI','GPTBase=0',{'GPTBase':1.0},SEED+401),
        ('Guarded tutor vs no-AI','GPTTutor=0',{'GPTTutor':1.0},SEED+402),
        ('Guarded tutor minus standard GenAI','GPTTutor=GPTBase',{'GPTTutor':1.0,'GPTBase':-1.0},SEED+403),
    ]
    for label,null,w,seed in tests:
        z=wild_cluster_bootstrap_t(b,f3,'Class',w,null,B=args.wild_bootstrap,seed=seed); z['contrast']=label
        small_cluster.append(z)
    loo=leave_one_cluster_out_contrast(b,f3,'Class',{'GPTTutor':1.0,'GPTBase':-1.0})
    for z in small_cluster:
        if z['contrast']=='Guarded tutor minus standard GenAI':
            z.update({f'loo_{k}':v for k,v in loo.items()})
    small_cluster=pd.DataFrame(small_cluster)
    small_cluster.to_csv(resdir/'bastani_small_cluster_inference.csv',index=False)

    # Bastani robustness: drop five noncomplier class-sessions, include honors, add survey covariates
    sens=[]
    noncomp=((b['Class'].astype(str)=='11S')&(b['Session']==2))|((b['Class'].astype(str)=='11S')&(b['Session']==4))|((b['Class'].astype(str)=='10A')&(b['Session']==2))|((b['Class'].astype(str)=='9J')&(b['Session']==1))|((b['Class'].astype(str)=='10B')&(b['Session']==3))
    bnc=b.loc[~noncomp].copy()
    for name,dd in [('Primary non-honors ITT',b),('Drop reported noncomplier class-sessions',bnc)]:
        rr=cluster_fit(f3,dd,'Class')
        for term in ['GPTBase','GPTTutor']:
            x=term_stats(rr,term)
            sens.append({'study':'Bastani','analysis':name,'term':term,'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    # honors sensitivity on common complete vars
    ball=b0.dropna(subset=vars_b).copy()
    rr=cluster_fit(f3,ball,'Class')
    for term in ['GPTBase','GPTTutor']:
        x=term_stats(rr,term); sens.append({'study':'Bastani','analysis':'Include honors classes','term':term,'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})

    # ---------------- Kestin et al. ----------------
    k_raw=pd.read_stata(paths['Kestin'])
    for ai,label in [(0.0,'In-class active learning'),(1.0,'AI tutor')]:
        raw_arm=k_raw[k_raw['lect_AI']==ai].copy()
        ana_arm=raw_arm.dropna(subset=['rid','lect_AI','post_score','pre_score']).copy()
        sample_audit.append({
            'study':'Kestin et al. (2025)','group':label,'released_rows':len(raw_arm),
            'released_participants':raw_arm['rid'].nunique(),
            'analysis_rows':len(ana_arm),'analysis_participants':ana_arm['rid'].nunique(),
            'rows_excluded_core_complete_case':len(raw_arm)-len(ana_arm),
            'missing_supported_outcome':'not applicable','missing_independent_outcome':int(raw_arm['post_score'].isna().sum()),
            'missing_baseline':int(raw_arm['pre_score'].isna().sum()),'other_core_missing':int(raw_arm[['rid','lect_AI']].isna().any(axis=1).sum()),
            'audit_scope':'Released analysis file only; source-paper enrolled/excluded cases are not represented in this public file'
        })
    k=k_raw.dropna(subset=['rid','lect_AI','post_score','pre_score']).copy()
    k['rid_str']=k['rid'].astype(str)
    kdesc=[]
    for ai,label in [(0,'In-class active learning'),(1,'AI tutor')]:
        d=k[k['lect_AI']==ai]
        kdesc.append({'study':'Kestin et al. (2025)','group':label,'n_observations':len(d),'n_participants':d.rid.nunique(),
                      'pre_mean':d.pre_score.mean(),'pre_sd':d.pre_score.std(ddof=1),'post_mean':d.post_score.mean(),'post_sd':d.post_score.std(ddof=1)})
    kdesc=pd.DataFrame(kdesc)
    k_control_sd=float(kdesc.loc[kdesc.group=='In-class active learning','post_sd'].iloc[0])
    # Primary: crossover-aligned participant FE ANCOVA. Clustered by participant.
    kfe=cluster_fit('post_score ~ lect_AI + pre_score + C(rid_str)',k,'rid_str')
    kb,se,p,lo,hi=term_stats(kfe,'lect_AI')
    primary.append({'study':'Kestin et al. (2025)','intervention':'Pedagogically designed AI tutor','comparator':'In-class active learning','outcome':'Independent post-test score (0–6)',
                    'effect_raw':kb,'se_raw':se,'ci_low_raw':lo,'ci_high_raw':hi,'p_value':p,'control_sd':k_control_sd,
                    'effect_std':kb/k_control_sd,'se_std':se/k_control_sd,'ci_low_std':lo/k_control_sd,'ci_high_std':hi/k_control_sd,
                    'analysis':'Participant fixed-effects ANCOVA with pre-test adjustment; participant-cluster robust SE'})
    # Sensitivity: all-observed ANCOVA and complete-pair gain comparison
    ka=cluster_fit('post_score ~ lect_AI + pre_score',k,'rid_str')
    x=term_stats(ka,'lect_AI'); sens.append({'study':'Kestin','analysis':'All-observed ANCOVA; participant-cluster SE','term':'AI tutor','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    x=term_stats(kfe,'lect_AI'); sens.append({'study':'Kestin','analysis':'Participant fixed-effects ANCOVA (primary; released observations)','term':'AI tutor','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    counts=k.groupby('rid').size(); pairids=counts[counts==2].index
    kp=k[k.rid.isin(pairids)].copy(); kp['gain']=kp.post_score-kp.pre_score; kp['rid_str']=kp['rid'].astype(str)
    kfe_pair=cluster_fit('post_score ~ lect_AI + pre_score + C(rid_str)',kp,'rid_str')
    x=term_stats(kfe_pair,'lect_AI'); sens.append({'study':'Kestin','analysis':f'Complete-pair participant fixed-effects ANCOVA (n={len(pairids)} participants)','term':'AI tutor','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    wide=kp.pivot(index='rid',columns='lect_AI',values='gain').dropna()
    dif=wide[1]-wide[0]
    t=st.ttest_1samp(dif,0)
    mean=float(dif.mean()); se=float(dif.std(ddof=1)/math.sqrt(len(dif))); lo=mean-st.t.ppf(.975,len(dif)-1)*se; hi=mean+st.t.ppf(.975,len(dif)-1)*se
    sens.append({'study':'Kestin','analysis':f'Complete-pair raw gain difference (n={len(dif)})','term':'AI tutor','effect':mean,'se':se,'p_value':float(t.pvalue),'ci_low':lo,'ci_high':hi})

    # Ceiling-sensitive sensitivity analysis: median quantile ANCOVA with participant-cluster bootstrap.
    qmed=quantile_cluster_bootstrap(k,'post_score','lect_AI','pre_score','rid',q=.5,B=args.quantile_bootstrap)
    sens.append({'study':'Kestin','analysis':f'Median quantile ANCOVA with participant-cluster bootstrap (B={qmed["bootstrap_reps"]})',
                 'term':'AI tutor','effect':qmed['effect'],'se':qmed['bootstrap_se'],'p_value':qmed['bootstrap_p'],
                 'ci_low':qmed['ci_low'],'ci_high':qmed['ci_high']})
    ceiling=k.assign(at_ceiling=(k.post_score>=k.post_score.max()).astype(int)).groupby('lect_AI').at_ceiling.agg(['sum','count','mean']).reset_index()
    ceiling['condition']=ceiling['lect_AI'].map({0.0:'In-class active learning',1.0:'AI tutor'})
    ceiling[['condition','sum','count','mean']].rename(columns={'sum':'n_at_max','count':'n','mean':'fraction_at_max'}).to_csv(resdir/'kestin_ceiling_diagnostic.csv',index=False)

    # ---------------- Pardos & Bhandari ----------------
    p_raw=pd.read_csv(paths['Pardos'])
    for group in ['No-hint control','Human tutor','ChatGPT']:
        raw_arm=p_raw[p_raw['condition']==group].copy()
        ana_arm=raw_arm.dropna(subset=['condition','preTest','postTest','lesson']).copy()
        sample_audit.append({
            'study':'Pardos & Bhandari (2024)','group':group,'released_rows':len(raw_arm),
            'released_participants':raw_arm['anonUserID'].nunique(),
            'analysis_rows':len(ana_arm),'analysis_participants':ana_arm['anonUserID'].nunique(),
            'rows_excluded_core_complete_case':len(raw_arm)-len(ana_arm),
            'missing_supported_outcome':'not applicable','missing_independent_outcome':int(raw_arm['postTest'].isna().sum()),
            'missing_baseline':int(raw_arm['preTest'].isna().sum()),'other_core_missing':int(raw_arm[['condition','lesson']].isna().any(axis=1).sum()),
            'audit_scope':'Released participant file only; publication reports upstream recruitment exclusions separately'
        })
    pdat=p_raw.dropna(subset=['condition','preTest','postTest','lesson']).copy()
    # explicit treatment coding with No-hint as reference
    pdat['condition']=pd.Categorical(pdat['condition'],categories=['No-hint control','Human tutor','ChatGPT'])
    pdesc=[]
    for group in ['No-hint control','Human tutor','ChatGPT']:
        d=pdat[pdat.condition==group]
        pdesc.append({'study':'Pardos & Bhandari (2024)','group':group,'n_observations':len(d),'n_participants':d.anonUserID.nunique(),
                      'pre_mean':d.preTest.mean(),'pre_sd':d.preTest.std(ddof=1),'post_mean':d.postTest.mean(),'post_sd':d.postTest.std(ddof=1),
                      'gain_mean':d.learningGain.mean(),'gain_sd':d.learningGain.std(ddof=1)})
    pdesc=pd.DataFrame(pdesc)
    p_control_sd=float(pdesc.loc[pdesc.group=='No-hint control','post_sd'].iloc[0])
    pr=hc3_fit('postTest ~ C(condition, Treatment(reference="No-hint control")) + preTest + C(lesson)',pdat)
    term_chat='C(condition, Treatment(reference="No-hint control"))[T.ChatGPT]'
    term_hum='C(condition, Treatment(reference="No-hint control"))[T.Human tutor]'
    pb,se,pv,lo,hi=term_stats(pr,term_chat)
    primary.append({'study':'Pardos & Bhandari (2024)','intervention':'ChatGPT-generated worked-solution hints','comparator':'No-hint control','outcome':'Independent repeated post-test score (0–1)',
                    'effect_raw':pb,'se_raw':se,'ci_low_raw':lo,'ci_high_raw':hi,'p_value':pv,'control_sd':p_control_sd,
                    'effect_std':pb/p_control_sd,'se_std':se/p_control_sd,'ci_low_std':lo/p_control_sd,'ci_high_std':hi/p_control_sd,
                    'analysis':'ANCOVA with pre-test and mathematics-subject fixed effects; HC3 robust SE'})
    x=term_stats(pr,term_hum); sens.append({'study':'Pardos','analysis':'ANCOVA post-test; HC3 SE','term':'Human tutor vs no-hint','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    x=term_stats(pr,term_chat); sens.append({'study':'Pardos','analysis':'ANCOVA post-test (primary); HC3 SE','term':'ChatGPT vs no-hint','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    x=linear_contrast_stats(pr,{term_chat:1,term_hum:-1}); sens.append({'study':'Pardos','analysis':'ANCOVA direct contrast; HC3 SE','term':'ChatGPT vs human tutor','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    pgain=hc3_fit('learningGain ~ C(condition, Treatment(reference="No-hint control")) + C(lesson)',pdat)
    for tterm,ll in [(term_chat,'ChatGPT vs no-hint'),(term_hum,'Human tutor vs no-hint')]:
        x=term_stats(pgain,tterm); sens.append({'study':'Pardos','analysis':'Gain-score model with subject FE; HC3 SE','term':ll,'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})

    # Discrete-score sensitivity: the post-test represents 0--3 correct items.
    # Fit a grouped-binomial GLM using the exact integer success count reconstructed
    # from the released aggregate score; this does not fabricate item-level responses.
    pdat['post_successes']=np.rint(pdat['postTest']*3).astype(int)
    pdat['post_prop_exact']=pdat['post_successes']/3.0
    pglm=smf.glm('post_prop_exact ~ C(condition, Treatment(reference="No-hint control")) + preTest + C(lesson)',
                 data=pdat, family=sm.families.Binomial(), freq_weights=np.repeat(3,len(pdat))).fit(cov_type='HC3')
    x=term_stats(pglm,term_chat); sens.append({'study':'Pardos','analysis':'Grouped-binomial GLM for 0--3 post-test count; HC3 SE (log-odds scale)','term':'ChatGPT vs no-hint','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    x=term_stats(pglm,term_hum); sens.append({'study':'Pardos','analysis':'Grouped-binomial GLM for 0--3 post-test count; HC3 SE (log-odds scale)','term':'Human tutor vs no-hint','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})

    pd.DataFrame(sample_audit).to_csv(resdir/'analysis_sample_audit.csv',index=False)

    # ---------------- Moderation by baseline achievement ----------------
    mods=[]
    # Bastani: z previous GPA, interactions simultaneously
    bm=b.copy(); bm['zbaseline']=(bm.gpa_prev-bm.gpa_prev.mean())/bm.gpa_prev.std(ddof=1)
    br=cluster_fit('Part3Tot ~ GPTBase*zbaseline + GPTTutor*zbaseline + gpa_prev + C(teacher)+C(Session)+C(Grader)+C(Year)',bm,'Class')
    for term,label in [('GPTBase:zbaseline','GPT Base × baseline'),('GPTTutor:zbaseline','GPT Tutor × baseline')]:
        x=term_stats(br,term); mods.append({'study':'Bastani','term':label,'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    km=k.copy(); km['zbaseline']=(km.pre_score-km.pre_score.mean())/km.pre_score.std(ddof=1)
    kr=cluster_fit('post_score ~ lect_AI*zbaseline + pre_score + C(rid_str)',km,'rid_str')
    x=term_stats(kr,'lect_AI:zbaseline'); mods.append({'study':'Kestin','term':'AI tutor × baseline','effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    pm=pdat.copy(); pm['zbaseline']=(pm.preTest-pm.preTest.mean())/pm.preTest.std(ddof=1)
    rr=hc3_fit('postTest ~ C(condition, Treatment(reference="No-hint control"))*zbaseline + preTest + C(lesson)',pm)
    for term,label in [(term_chat+':zbaseline','ChatGPT × baseline'),(term_hum+':zbaseline','Human tutor × baseline')]:
        x=term_stats(rr,term); mods.append({'study':'Pardos','term':label,'effect':x[0],'se':x[1],'p_value':x[2],'ci_low':x[3],'ci_high':x[4]})
    mods=pd.DataFrame(mods); mods['p_holm']=holm(mods.p_value.values)

    # Descriptives and primary output
    desc=pd.concat([bdesc,kdesc,pdesc],ignore_index=True,sort=False)
    primary=pd.DataFrame(primary)
    sens=pd.DataFrame(sens)
    desc.to_csv(resdir/'study_descriptives.csv',index=False)
    primary.to_csv(resdir/'primary_effects.csv',index=False)
    gap.to_csv(resdir/'bastani_within_study_profile_contrast.csv',index=False)
    mods.to_csv(resdir/'baseline_moderation.csv',index=False)
    sens.to_csv(resdir/'sensitivity_analyses.csv',index=False)

    # ---------------- Paired-profile visualization ----------------
    # The canonical paired-profile dataset and Figures 1--3 are built by
    # build_paired_profiles.py and render_extended_figures.py. Keeping this
    # core script free of a second effect-space implementation prevents stale
    # or manually entered profile values from becoming a competing source of truth.

    # Fig. 4: within-experiment Bastani design contrast.
    fig,ax=plt.subplots(figsize=(8,5.2))
    xpos=np.array([0,1]); width=.32
    assisted=gap.assisted_effect.values; independent=gap.independent_effect.values
    aerr=np.vstack([assisted-gap.assisted_ci_low.values,gap.assisted_ci_high.values-assisted])
    ierr=np.vstack([independent-gap.independent_ci_low.values,gap.independent_ci_high.values-independent])
    ax.bar(xpos-width/2,assisted,width,label='AI-supported practice effect',yerr=aerr,capsize=4)
    ax.bar(xpos+width/2,independent,width,label='Independent exam effect',yerr=ierr,capsize=4)
    ax.axhline(0,lw=1)
    ax.set_xticks(xpos,['Standard generative AI','Pedagogically guarded AI tutor'])
    ax.set_ylabel('Adjusted randomized treatment effect (score scale 0–1)')
    ax.set_title('Changing pedagogical architecture changes the supported-to-assistance-removed profile')
    wild_guard=float(small_cluster.loc[small_cluster['contrast']=='Guarded tutor minus standard GenAI','wild_bootstrap_p'].iloc[0])
    ax.text(.02,.03,f'Independent guarded-minus-standard contrast: CR1 p=0.038; Webb wild-cluster p={wild_guard:.3f}.',transform=ax.transAxes,fontsize=7.7,style='italic')
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figdir/'bastani_design_profile_diagnostic.png',dpi=180,bbox_inches='tight')
    fig.savefig(figdir/'bastani_design_profile_diagnostic.pdf',bbox_inches='tight')
    plt.close(fig)

    # ---------------- machine-readable summary ----------------
    summary={
        'seed':SEED,
        'analytic_counts':{
            'Bastani':{'observations':int(len(b)),'participants':int(b['Student ID'].nunique()),'clusters':int(b.Class.nunique())},
            'Kestin':{'observations':int(len(k)),'participants':int(k.rid.nunique()),'complete_crossover_participants':int(len(pairids))},
            'Pardos':{'observations':int(len(pdat)),'participants':int(pdat.anonUserID.nunique())},
            'analysis_sample_audit_rows':int(len(sample_audit)),
            'total_unique_participants_across_studies':int(b['Student ID'].nunique()+k.rid.nunique()+pdat.anonUserID.nunique()),
            'total_analysis_rows':int(len(b)+len(k)+len(pdat))},
        'primary_effects':primary.to_dict(orient='records'),
        'bastani_within_study_profile_contrast':gap.to_dict(orient='records'),
        'bastani_small_cluster_inference':small_cluster.to_dict(orient='records'),
        'moderation':mods.to_dict(orient='records'),
        'software':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':__import__('scipy').__version__,'statsmodels':__import__('statsmodels').__version__}
    }
    (resdir/'results_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (resdir/'analysis_session.txt').write_text('\n'.join([f'{k}: {v}' for k,v in summary['software'].items()])+f'\nseed: {SEED}\n',encoding='utf-8')

    # verification checks with nonzero exit on mismatch
    checks=[]
    # published Bastani coefficients, tolerances to allow package covariance implementation differences only in SE
    expected={'GPTBase_P2':0.137,'GPTTutor_P2':0.361,'GPTBase_P3':-0.054,'GPTTutor_P3':-0.004}
    observed={'GPTBase_P2':term_stats(r2,'GPTBase')[0],'GPTTutor_P2':term_stats(r2,'GPTTutor')[0],
              'GPTBase_P3':term_stats(r3,'GPTBase')[0],'GPTTutor_P3':term_stats(r3,'GPTTutor')[0]}
    for key,e in expected.items(): checks.append({'check':key,'observed':observed[key],'target_rounded':e,'pass':abs(observed[key]-e)<.0015})
    checks.append({'check':'Kestin public-data median AI post','observed':float(k[k.lect_AI==1].post_score.median()),'target_rounded':4.5,'pass':float(k[k.lect_AI==1].post_score.median())==4.5})
    checks.append({'check':'Kestin public-data median control post','observed':float(k[k.lect_AI==0].post_score.median()),'target_rounded':3.5,'pass':float(k[k.lect_AI==0].post_score.median())==3.5})
    checks.append({'check':'Pardos N','observed':int(len(pdat)),'target_rounded':274,'pass':len(pdat)==274})
    pd.DataFrame(checks).to_csv(resdir/'verification_checks.csv',index=False)
    if not all(c['pass'] for c in checks):
        raise RuntimeError('Verification check failed; inspect verification_checks.csv')

if __name__=='__main__':
    main()
