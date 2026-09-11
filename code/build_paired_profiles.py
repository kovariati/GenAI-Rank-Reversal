#!/usr/bin/env python3
"""Build the single canonical paired-profile dataset used by the manuscript.

Wong & Qiu point estimates and bootstrap intervals come from the public
participant-level OSF workbook via analyze_wong_participant.py. Raw third-party
participant data are not redistributed; the derived non-identifying results are.
"""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
SEED=20260817

def _bassner_point_and_bootstrap(raw_path: Path, reps: int=3999):
    from bassner_source_reproduction import clean_bassner
    b,_,_=clean_bassner(raw_path); b=b.copy()
    b['grp']=pd.Categorical(b.experiment_group,categories=['NOAI','CHATGPT','IRIS'])
    bd=b.groupby('experiment_group').agg(exercise_sd=('exercise_score_artemis','std'),post_knowledge_sd=('post_know_total','std'))
    out=[]
    for grp,label in [('CHATGPT','Unrestricted ChatGPT'),('IRIS','Scaffolded Iris')]:
        m_ex=smf.ols('exercise_score_artemis ~ C(grp)',b).fit(); m_kn=smf.ols('post_know_total ~ C(grp) + pre_know_total',b).fit(); t=f'C(grp)[T.{grp}]'
        out.append((grp,label,float(m_ex.params[t]/bd.loc['NOAI','exercise_sd']),float(m_kn.params[t]/bd.loc['NOAI','post_knowledge_sd'])))
    rng=np.random.default_rng(SEED); ids={g:b.index[b.experiment_group==g].to_numpy() for g in ['NOAI','CHATGPT','IRIS']}; boot={g:[] for g in ['CHATGPT','IRIS']}
    for _ in range(reps):
        z=pd.concat([b.loc[rng.choice(ids[g],size=len(ids[g]),replace=True)].copy() for g in ['NOAI','CHATGPT','IRIS']],ignore_index=True)
        z['grp']=pd.Categorical(z.experiment_group,categories=['NOAI','CHATGPT','IRIS'])
        s_ex=float(z.loc[z.experiment_group=='NOAI','exercise_score_artemis'].std(ddof=1)); s_kn=float(z.loc[z.experiment_group=='NOAI','post_know_total'].std(ddof=1))
        if not np.isfinite(s_ex) or not np.isfinite(s_kn) or s_ex<=0 or s_kn<=0: continue
        me=smf.ols('exercise_score_artemis ~ C(grp)',z).fit(); mk=smf.ols('post_know_total ~ C(grp) + pre_know_total',z).fit()
        for g in ['CHATGPT','IRIS']:
            t=f'C(grp)[T.{g}]'; boot[g].append(float(mk.params[t]/s_kn-me.params[t]/s_ex))
    cis={g:(float(np.quantile(v,.025)),float(np.quantile(v,.975)),len(v)) for g,v in [(g,np.asarray(vals,float)) for g,vals in boot.items()]}
    return out,cis

def build(results: Path, bassner_raw: Path|None=None, reps: int=3999):
    gap=pd.read_csv(results/'bastani_within_study_profile_contrast.csv'); core_desc=pd.read_csv(results/'study_descriptives.csv')
    bc=core_desc[(core_desc.study=='Bastani et al. (2025)') & (core_desc.group=='control')].iloc[0]
    rows=[]; contrasts=[]
    for _,r in gap.iterrows():
        design='Unrestricted GenAI' if 'standard' in str(r.intervention).lower() else 'Pedagogically guarded AI tutor'
        ssd=float(bc.assisted_sd); isd=float(bc.independent_sd)
        supp=float(r.assisted_effect/ssd); indep=float(r.independent_effect/isd)
        rows.append(dict(study='Bastani et al. (2025)',program='Bastani',design=design,paired_role='classroom mathematics practice -> independent exam',
            supported_effect_std=supp,supported_ci_low=float(r.assisted_ci_low/ssd),supported_ci_high=float(r.assisted_ci_high/ssd),
            independent_effect_std=indep,independent_ci_low=float(r.independent_ci_low/isd),independent_ci_high=float(r.independent_ci_high/isd),
            independent_outcome_type='immediate independent near-task exam',effect_scale='control-group SD of each corresponding outcome',
            point_source='participant-level harmonized analysis',ci_source='CR1 model interval; conservative Webb p-values reported separately',source_doi='10.1073/pnas.2422633122'))
        contrasts.append(dict(study='Bastani et al. (2025)',design=design,independent_minus_supported_std=indep-supp,ci_low=np.nan,ci_high=np.nan,
            inference='descriptive standardized profile only; raw-scale study-specific profile analysis and small-cluster sensitivity reported separately'))

    be=pd.read_csv(results/'bassner_effects.csv'); bd=pd.read_csv(results/'bassner_descriptives.csv').set_index('experiment_group'); bassner_ci={}
    # Precomputed derived bootstrap intervals are distributed so the release remains fully inspectable without redistributing third-party raw data.
    bcache=results/'bassner_profile_bootstrap.csv'
    if bcache.exists():
        bz=pd.read_csv(bcache)
        for _,rr in bz.iterrows():
            g='CHATGPT' if 'Unrestricted' in rr['design'] else 'IRIS'
            bassner_ci[g]=(float(rr.ci_low),float(rr.ci_high),3999)
    bassner_pts={}
    if bassner_raw is not None and bassner_raw.exists():
        pts,bassner_ci=_bassner_point_and_bootstrap(bassner_raw,reps); bassner_pts={g:(label,supp,indep) for g,label,supp,indep in pts}
    for grp,label in [('CHATGPT','Unrestricted ChatGPT'),('IRIS','Scaffolded Iris')]:
        ex=be[(be.outcome=='supported_exercise_score_0_100')&(be.intervention==grp)].iloc[0]; kn=be[(be.outcome=='post_knowledge_0_6_ancova')&(be.intervention==grp)].iloc[0]
        ssd=float(bd.loc['NOAI','exercise_sd']); isd=float(bd.loc['NOAI','post_knowledge_sd'])
        supp=float(ex.effect/ssd); indep=float(kn.effect/isd)
        if grp in bassner_pts:
            _,s2,i2=bassner_pts[grp]
            if abs(s2-supp)>1e-10 or abs(i2-indep)>1e-10: raise RuntimeError('Bassner point estimates disagree between canonical result files and raw-data rebuild')
        rows.append(dict(study='Bassner et al. (2026)',program='Bassner',design=label,paired_role='programming exercise -> independent post-knowledge test',
            supported_effect_std=supp,supported_ci_low=float(ex.ci_low/ssd),supported_ci_high=float(ex.ci_high/ssd),
            independent_effect_std=indep,independent_ci_low=float(kn.ci_low/isd),independent_ci_high=float(kn.ci_high/isd),
            independent_outcome_type='immediate independent knowledge assessment',effect_scale='control-group SD of each corresponding outcome',
            point_source='participant-level harmonized analysis',ci_source='study-specific model interval',source_doi='10.1016/j.caeai.2025.100537'))
        ci=bassner_ci.get(grp,(np.nan,np.nan,0)); contrasts.append(dict(study='Bassner et al. (2026)',design=label,independent_minus_supported_std=indep-supp,ci_low=ci[0],ci_high=ci[1],inference=f'participant-stratified bootstrap profile contrast; {ci[2]} valid replicates' if ci[2] else 'bootstrap requires public Bassner raw file'))

    # Wong & Qiu: participant-level public OSF reanalysis, originality is the prespecified main paired outcome.
    wr=pd.read_csv(results/'wong_participant_reanalysis.csv'); wr=wr[wr.outcome=='Originality']
    for design in ['Unrestricted ChatGPT','Think-first, ChatGPT-later']:
        r=wr[wr.design==design].iloc[0]
        rows.append(dict(study='Wong & Qiu (2026)',program='Wong & Qiu',design=design,paired_role='AI-assisted product improvement -> unassisted product invention',
            supported_effect_std=float(r.assisted_effect_std),supported_ci_low=float(r.assisted_ci_low),supported_ci_high=float(r.assisted_ci_high),
            independent_effect_std=float(r.independent_effect_std),independent_ci_low=float(r.independent_ci_low),independent_ci_high=float(r.independent_ci_high),
            independent_outcome_type='immediate independent creative-transfer task',effect_scale='human-only-group SD of each corresponding outcome',
            point_source='participant-level OSF reanalysis',ci_source=f'participant-stratified percentile bootstrap ({int(r.bootstrap_reps)} replicates)',source_doi='10.1007/s10648-026-10118-7'))
        contrasts.append(dict(study='Wong & Qiu (2026)',design=design,independent_minus_supported_std=float(r.independent_minus_assisted_std),
            ci_low=float(r.profile_change_ci_low),ci_high=float(r.profile_change_ci_high),inference=f'participant-stratified bootstrap profile contrast; {int(r.bootstrap_reps)} replicates; not interpreted as causal effect of AI removal'))

    prof=pd.DataFrame(rows); con=pd.DataFrame(contrasts)
    for name in ['paired_supported_independent_profiles.csv','supported_independent_effect_space.csv','extended_supported_independent_profiles.csv']:
        prof.to_csv(results/name,index=False)
    con.to_csv(results/'paired_profile_contrasts.csv',index=False)
    summary={'paired_profiles':int(len(prof)),'independent_research_programs':int(prof.program.nunique()),'supported_min':float(prof.supported_effect_std.min()),'supported_max':float(prof.supported_effect_std.max()),'independent_min':float(prof.independent_effect_std.min()),'independent_max':float(prof.independent_effect_std.max()),'cross_study_pooling':False,'interpretation':'Outcome-specific control-SD profiles. Different assessment regimes target outcome-specific treatment effects; profile differences are not causal effects of removing AI unless the assessment regime is experimentally isolated.'}
    (results/'paired_profile_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return prof,con,summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results',default=str(ROOT/'results')); ap.add_argument('--bassner-raw',default=''); ap.add_argument('--bootstrap-reps',type=int,default=3999)
    a=ap.parse_args(); p=Path(a.bassner_raw) if a.bassner_raw else None; prof,con,s=build(Path(a.results),p,a.bootstrap_reps)
    print(prof.to_string(index=False)); print(con.to_string(index=False)); print(json.dumps(s,indent=2))
if __name__=='__main__': main()
