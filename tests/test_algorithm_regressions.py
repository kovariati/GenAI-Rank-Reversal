from pathlib import Path
import json, sys
import numpy as np, pandas as pd, pytest
from scipy import stats
import statsmodels.formula.api as smf
ROOT=Path(__file__).resolve().parents[1]; CODE=ROOT/'code'; RESULTS=ROOT/'results'; sys.path.insert(0,str(CODE))
import analyze_wong_direct_reversal as wdirect
import assessment_regime_rank_robustness as robust
import assessment_regime_rank_sensitivity as sens
import assessment_regime_rank_order as order
import build_paired_profiles as profiles
import build_paired_rank_evidence as evidence
import bassner_source_reproduction as bassner_source

def test_wong_welch_matches_scipy():
 z=pd.read_csv(RESULTS/'wong_published_sufficient_statistics.csv')
 for outcome in ['originality','usefulness']:
  q=z[z.outcome.str.lower()==outcome]
  for task in ['Task 1 product improvement','Task 2 product invention']:
   u=q[(q.group=='Unrestricted ChatGPT')&(q.task==task)].iloc[0]; l=q[(q.group=='Think-first ChatGPT-later')&(q.task==task)].iloc[0]
   d,se,df,tv,lo,hi=wdirect.welch(int(u.n),u['mean'],u.sd,int(l.n),l['mean'],l.sd)
   ref=stats.ttest_ind_from_stats(u['mean'],u.sd,int(u.n),l['mean'],l.sd,int(l.n),equal_var=False)
   assert tv==pytest.approx(ref.statistic,abs=1e-13); assert 2*stats.t.sf(abs(tv),df)==pytest.approx(ref.pvalue,abs=1e-13); assert lo<d<hi

def test_wong_iut_and_holm():
 s=pd.read_csv(RESULTS/'wong_direct_reversal_summary.csv'); p=[]
 for _,r in s.iterrows(): assert r.intersection_union_p==pytest.approx(max(r.assisted_p_one_sided,r.independent_p_one_sided),abs=1e-15); p.append(float(r.intersection_union_p))
 assert wdirect.holm_adjust(p)==pytest.approx(s.holm_adjusted_iut_p_across_outcomes.tolist(),abs=1e-15); assert all(s.assisted_ci_low>0) and all(s.independent_ci_high<0)

def _syn(n,m,sd):
 x=np.arange(n,dtype=float); x=(x-x.mean())/x.std(ddof=1); return m+sd*x

def test_bassner_hc3_closed_form_matches_statsmodels():
 d=pd.read_csv(RESULTS/'bassner_descriptives.csv').set_index('experiment_group'); c,i=d.loc['CHATGPT'],d.loc['IRIS']
 y=np.r_[_syn(int(c.n),c.exercise_mean,c.exercise_sd),_syn(int(i.n),i.exercise_mean,i.exercise_sd)]; g=np.array(['CHATGPT']*int(c.n)+['IRIS']*int(i.n)); df=pd.DataFrame({'y':y,'g':pd.Categorical(g,categories=['IRIS','CHATGPT'])})
 fit=smf.ols('y ~ C(g)',df).fit(cov_type='HC3'); est,lo,hi=evidence._hc3_two_group(int(c.n),c.exercise_mean,c.exercise_sd,int(i.n),i.exercise_mean,i.exercise_sd); term='C(g)[T.CHATGPT]'; ci=fit.conf_int().loc[term]
 assert est==pytest.approx(fit.params[term],abs=1e-12); assert lo==pytest.approx(ci.iloc[0],abs=1e-12); assert hi==pytest.approx(ci.iloc[1],abs=1e-12)

def test_bassner_welch_satterthwaite_ci():
 d=pd.read_csv(RESULTS/'bassner_descriptives.csv').set_index('experiment_group'); c,i=d.loc['CHATGPT'],d.loc['IRIS']; est,lo,hi=evidence._welch(int(c.n),c.post_knowledge_mean,c.post_knowledge_sd,int(i.n),i.post_knowledge_mean,i.post_knowledge_sd)
 assert est==pytest.approx(0.2689810189810191,abs=1e-15); assert lo==pytest.approx(-0.29486047502963264,abs=1e-12); assert hi==pytest.approx(0.8328225129916709,abs=1e-12)

def test_wong_randomization_statistic_equals_ols_interaction():
 rng=np.random.default_rng(42); n_u,n_l=17,15; assisted=np.r_[rng.normal(4,.5,n_u),rng.normal(3.6,.5,n_l)]; independent=np.r_[rng.normal(3,.6,n_u),rng.normal(3.5,.6,n_l)]; lf=np.r_[np.zeros(n_u,dtype=int),np.ones(n_l,dtype=int)]
 observed=(independent-assisted)[lf==1].mean()-(independent-assisted)[lf==0].mean(); long=pd.DataFrame({'lf':np.repeat(lf,2),'independent':np.tile([0,1],n_u+n_l),'y':np.column_stack([assisted,independent]).ravel()}); fit=smf.ols('y ~ lf * independent',long).fit(); assert observed==pytest.approx(fit.params['lf:independent'],abs=1e-12)

def test_bastani_symmetrical_preservation_rule():
 r=pd.read_csv(RESULTS/'paired_rank_evidence_revised.csv').query("program=='Bastani'").iloc[0]; assert r.assisted_ci_low>0 and r.independent_ci_low>0; assert '0.1238' in r.inference_note; assert r.population_rank_status=='preservation not robustly supported'

def test_rank_robustness_formula_and_rectangle_classification():
 da,di=.78,-.73
 for lam in [.25,.5,1,2,4]:
  ws=robust.w_star(da,di,lam); assert 0<ws<1; assert ws*lam*da+(1-ws)*di==pytest.approx(0,abs=1e-14)

def test_gamma_sensitivity_identity():
 r=sens.diag('x','a-b',.78,-.73); assert r['differential_regime_shift_Gamma_DI_minus_DA']==pytest.approx(-1.51); assert r['shift_to_tie_minus_DA']==pytest.approx(-.78); assert r['observed_shift_over_tie_requirement']==pytest.approx(1.51/.78); assert r['strict_rank_reversal']=='TRUE'

def test_manuscript_facing_paired_evidence_regenerates():
 got=evidence.build(RESULTS); can=pd.read_csv(RESULTS/'paired_rank_evidence_revised.csv'); pd.testing.assert_frame_equal(got.reset_index(drop=True),can,check_exact=False,rtol=1e-13,atol=1e-13)

def test_bassner_source_order_preprocessing():
 hist='[{"timestamp":"2025-01-23 09:00:00"},{"timestamp":"2025-01-23 08:00:00"}]'; got=bassner_source.get_last_valid_submission_plus1h(hist,pd.Timestamp('2025-01-23 10:30:00')); assert got==pd.Timestamp('2025-01-23 09:00:00')

def test_wong_scale_sensitivity_links_to_canonical_means():
 means=pd.read_csv(RESULTS/'wong_raw_group_means.csv'); inp=pd.read_csv(RESULTS/'wong_rank_reversal_sensitivity_input.csv')
 for _,r in inp.iterrows():
  z=means[means.outcome==r.outcome].set_index('design'); assert r.D_A==pytest.approx(z.loc['Unrestricted ChatGPT','assisted_task_mean']-z.loc['Learner-first AI','assisted_task_mean']); assert r.D_I==pytest.approx(z.loc['Unrestricted ChatGPT','independent_task_mean']-z.loc['Learner-first AI','independent_task_mean'])

def test_same_sign_never_auto_becomes_population_preservation(tmp_path):
 p=pd.DataFrame([{'program':'X','design':'A','supported_effect_std':1,'independent_effect_std':1},{'program':'X','design':'B','supported_effect_std':0,'independent_effect_std':0}]); src=tmp_path/'p.csv'; out=tmp_path/'o.csv'; p.to_csv(src,index=False); gate=tmp_path/'gate.csv'; pd.DataFrame([{'program':'X','rank_comparison_eligible':'yes','commensurability_status':'task_specific_directional_only','interpretive_boundary':'synthetic test scope'}]).to_csv(gate,index=False); order.build(src,out,gate); row=pd.read_csv(out).iloc[0]; assert row.pairwise_transport_status=='same_sign_observed'; assert 'population preservation requires direct inferential support' in row.interpretation

def test_build_paired_profiles_root_is_repository_root(): assert profiles.ROOT==ROOT

def test_wong_bootstrap_fields_are_sign_tail_not_p_values():
 a=pd.read_csv(RESULTS/'wong_participant_reanalysis.csv'); b=pd.read_csv(RESULTS/'wong_profile_interaction_bootstrap.csv'); assert 'profile_change_bootstrap_sign_tail' in a.columns and 'profile_change_bootstrap_p' not in a.columns; assert 'diff_bootstrap_sign_tail' in b.columns and 'diff_bootstrap_p' not in b.columns

def test_no_stale_figure4_bastani_artifact_name():
 text=(CODE/'reproduce_public_studies.py').read_text(); assert 'figure4_bastani_design_profile' not in text; assert 'bastani_design_profile_diagnostic' in text

def test_publication_release_metadata_is_live_and_consistent():
 m=json.loads((ROOT/'PROJECT_METADATA.json').read_text()); assert m.get('release_url')=='https://github.com/kovariati/GenAI-Rank-Reversal/releases/tag/v1.0.0'; assert m.get('release_date')=='2026-09-19'; assert m.get('article_doi')=='10.3390/computers15090633'; notes=(ROOT/'RELEASE_NOTES_v1.0.0.md').read_text(); prov=(ROOT/'docs/RELEASE_PROVENANCE.md').read_text(); assert 'DRAFT RELEASE TEMPLATE' not in notes and 'DRAFT RELEASE TEMPLATE' not in prov; assert m['release_url'] in notes and m['release_url'] in prov
