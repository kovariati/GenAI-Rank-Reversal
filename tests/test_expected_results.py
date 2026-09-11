#!/usr/bin/env python3
from pathlib import Path
import csv, math, sys
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'
fail=[]
def check(name,cond,detail=''):
    print(f'{name}: {"PASS" if cond else "FAIL"} {detail}')
    if not cond: fail.append(name)

def rows(name): return list(csv.DictReader((R/name).open(encoding='utf-8-sig')))
# Direct reversal
s=rows('wong_direct_reversal_summary.csv')
check('two_wong_outcomes',len(s)==2)
for r in s:
    check(r['outcome']+'_assisted_positive',float(r['assisted_estimate'])>0)
    check(r['outcome']+'_independent_negative',float(r['independent_estimate'])<0)
    check(r['outcome']+'_holm',abs(float(r['holm_adjusted_iut_p_across_outcomes'])-0.006755669718681242)<1e-12)
# Exact Bassner manuscript-facing direct Welch interval
e=rows('paired_rank_evidence_revised.csv')
br=next(r for r in e if r['program']=='Bassner')
check('Bassner_exact_Welch_low',abs(float(br['independent_ci_low'])-(-0.29486047502963264))<1e-12)
check('Bassner_exact_Welch_high',abs(float(br['independent_ci_high'])-0.8328225129916709)<1e-12)
wp=rows('wong_participant_reanalysis.csv'); wb=rows('wong_profile_interaction_bootstrap.csv')
check('Wong_bootstrap_sign_tail_name','profile_change_bootstrap_sign_tail' in wp[0] and 'profile_change_bootstrap_p' not in wp[0])
check('Wong_diff_sign_tail_name','diff_bootstrap_sign_tail' in wb[0] and 'diff_bootstrap_p' not in wb[0])

# Pairwise transport status
p={r['program']:r for r in rows('pairwise_rank_transport_status.csv')}
check('Bastani_same_sign_observed',p['Bastani']['pairwise_transport_status']=='same_sign_observed')
check('Bassner_same_sign_observed',p['Bassner']['pairwise_transport_status']=='same_sign_observed')
check('Wong_opposite_sign_observed',p['Wong & Qiu']['pairwise_transport_status']=='opposite_sign_observed')
# ARRP audit
q=rows('arrp_specification_audit.csv')
check('ARRP_all_pass',len(q)>0 and all(r['status']=='PASS' for r in q),f'n={len(q)}')
# Construct gate
c=rows('construct_commensurability_audit.csv')
check('construct_three_programs',len(c)==3)
check('construct_no_ineligible_forced_rank',all(not (r['rank_comparison_eligible']=='yes' and r['commensurability_status'] in {'non_commensurable','unclear'}) for r in c))
if fail: sys.exit('FAILED: '+', '.join(fail))
print('expected_results: PASS')
