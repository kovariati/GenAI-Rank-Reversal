from pathlib import Path
import copy, json, sys
import numpy as np
import pandas as pd
import pytest
from scipy import stats
from jsonschema import Draft202012Validator, ValidationError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import analyze_wong_direct_reversal as wd
import assessment_regime_rank_order as ro
import assessment_regime_rank_sensitivity as rs
import assessment_regime_rank_robustness as rr
import build_paired_rank_evidence as pe

@pytest.mark.parametrize('args', [(1,0,1,4,0,1),(3.5,0,1,4,0,1),(3,0,-1,4,0,1),(3,float('nan'),1,4,0,1),(3,0,0,4,0,0)])
def test_welch_rejects_invalid_statistics(args):
    with pytest.raises(ValueError): wd.welch(*args)

def test_sufficient_stats_reject_duplicate_and_missing_cells():
    d=pd.read_csv(ROOT/'results/wong_published_sufficient_statistics.csv')
    for z in [pd.concat([d,d.iloc[[0]]]),d.drop(index=0)]:
        with pytest.raises(ValueError): wd.analyze(z)

@pytest.mark.parametrize('pa,pi',[(.001,.99),(.97,.002),(.4,.8),(.2,.3)])
def test_two_orientation_p_is_arm_coding_invariant(pa,pi):
    assert wd.reversal_pvalues(pa,pi)[2]==pytest.approx(wd.reversal_pvalues(1-pa,1-pi)[2])

def test_revised_primary_results_and_simultaneous_intervals():
    det,s=wd.analyze(pd.read_csv(ROOT/'results/wong_published_sufficient_statistics.csv'))
    assert s.holm_adjusted_orientation_reversal_p.tolist()==pytest.approx([.013511339437362484]*2)
    assert (det.query("regime=='assisted'").bonferroni_family_95ci_low>0).all()
    assert (det.query("regime=='independent'").bonferroni_family_95ci_high<0).all()
    for r in det.itertuples():
        assert (r.bonferroni_family_95ci_high-r.estimate)/r.se==pytest.approx(stats.t.ppf(.99375,r.df))

def test_secondary_three_dimension_family_does_not_claim_elaboration_reversal():
    _,s=wd.analyze(pd.read_csv(ROOT/'results/wong_published_sufficient_statistics.csv'),('originality','usefulness','elaboration'))
    assert s.iloc[0].holm_adjusted_orientation_reversal_p==pytest.approx(.020267009156043726)
    assert not bool(s.iloc[2].task_specific_reversal_supported_0_05)

def _profiles(tmp_path,values=(1,1),gate_status='yes'):
    p=tmp_path/'profiles.csv'; g=tmp_path/'gate.csv'; o=tmp_path/'out.csv'
    pd.DataFrame([dict(program='X',design='a',supported_effect_std=values[0],independent_effect_std=values[1]),dict(program='X',design='b',supported_effect_std=0,independent_effect_std=0)]).to_csv(p,index=False)
    pd.DataFrame([dict(program='X',rank_comparison_eligible=gate_status,commensurability_status='task_specific_directional_only',interpretive_boundary='synthetic scope')]).to_csv(g,index=False)
    return p,g,o

def test_gate_blocks_forced_rank_label(tmp_path):
    p,g,o=_profiles(tmp_path,(1,-1),'no'); ro.build(p,o,g)
    assert pd.read_csv(o).iloc[0].pairwise_transport_status=='not_classified_commensurability_gate'

def test_missing_gate_program_blocks_label(tmp_path):
    p,g,o=_profiles(tmp_path); ro.build(p,o) # X is not in real audit
    assert pd.read_csv(o).iloc[0].pairwise_transport_status=='not_classified_commensurability_gate'

def test_tie_not_called_preserved(tmp_path):
    p,g,o=_profiles(tmp_path,(1,0)); ro.build(p,o,g)
    row=pd.read_csv(o).iloc[0]
    assert row.pairwise_transport_status=='tie_in_at_least_one_regime'
    assert 'neither strict reversal nor strict preservation' in row.interpretation

@pytest.mark.parametrize('x',[float('nan'),float('inf'),-float('inf')])
def test_nonfinite_contrast_is_not_tie(x):
    with pytest.raises(ValueError): ro.sgn(x)

def test_large_absolute_shift_does_not_imply_reversal():
    d=rs.diag('counterexample','a-b',1,3)
    assert d['observed_shift_over_tie_requirement']==2
    assert d['signed_shift_over_tie_requirement']==-2
    assert d['strict_rank_reversal']=='FALSE'

@pytest.mark.parametrize('da,di',[(1,-3),(-1,3),(2,4),(-2,-4),(2,0)])
def test_signed_ratio_characterizes_reversal(da,di):
    d=rs.diag('x','a-b',da,di)
    assert (d['signed_shift_over_tie_requirement']>1)==(da*di<0)

@pytest.mark.parametrize('args',[(.25,4,0),(.25,4,-1),(4,.25,.1),(0,4,.1),(.25,float('inf'),.1)])
def test_invalid_grid_fails_not_loops(args):
    with pytest.raises(ValueError): rr.lambda_grid(*args)

def test_grid_endpoints():
    g=rr.lambda_grid(.25,4,.05); assert len(g)==76 and g[0]==.25 and g[-1]==4

def test_arbitrary_monotone_individual_transformation_does_not_preserve_means():
    a=np.array([2.,2.]); b=np.array([0.,3.])
    assert a.mean()>b.mean() and (a*a).mean()<(b*b).mean()

def _schema_example():
    return json.loads((ROOT/'arrp.schema.json').read_text()),json.loads((ROOT/'examples/arrp_example_wong_task2.json').read_text())

@pytest.mark.parametrize('mutation',['missing','extra','whitespace','exact_missing','negative_delay','bad_unit','bad_transfer'])
def test_arrp_full_schema_rejects_invalid_records(mutation):
    s,e=_schema_example()
    if mutation=='missing': del e['N']
    elif mutation=='extra': e['fabricated_field']=True
    elif mutation=='whitespace': e['A']['source_evidence']='  '
    elif mutation=='exact_missing': e['D']['category']='exact'
    elif mutation=='negative_delay': e['D'].update(category='exact',elapsed_value=-1,elapsed_unit='minutes')
    elif mutation=='bad_unit': e['D'].update(category='exact',elapsed_value=1,elapsed_unit='fortnights')
    elif mutation=='bad_transfer': e['G']['status']='domain/context shift'
    with pytest.raises(ValidationError): Draft202012Validator(s).validate(e)

def test_arrp_schema_accepts_exact_delay_and_example():
    s,e=_schema_example(); Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(e)
    for unit in ['seconds','years']:
        e['D'].update(category='exact',elapsed_value=1,elapsed_unit=unit); Draft202012Validator(s).validate(e)

def test_evidence_status_depends_on_corrected_p_not_hardcoded(tmp_path):
    import shutil
    for name in ['wong_direct_reversal_summary.csv','construct_commensurability_audit.csv','bastani_rank_evidence_summary.csv','bassner_descriptives.csv','bassner_effects.csv']:
        shutil.copy2(ROOT/'results'/name,tmp_path/name)
    p=tmp_path/'wong_direct_reversal_summary.csv'; d=pd.read_csv(p); d['holm_adjusted_orientation_reversal_p']=.9; d.to_csv(p,index=False)
    w=pe.build(tmp_path).query("program=='Wong & Qiu'")
    assert set(w.population_rank_status)=={'reversal not supported'}
