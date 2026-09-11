#!/usr/bin/env python3
"""Deterministic ARRP specification audit.

This is a software/specification audit, not human inter-rater validation and not
an NLP benchmark. Structured features are mapped to frozen ARRP values; the
metamorphic tests verify selective sensitivity/invariance of that mapping.
"""
from pathlib import Path
import csv, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / 'results').exists() else HERE.parent
RESULTS = ROOT / 'results'

A_MAP = {'accessible':'available','unavailable':'removed','partial':'restricted','unknown':'unclear'}
O_MAP = {'same':'same','repeated':'repeated','similar':'similar','novel':'novel','unknown':'unclear'}
G_MAP = {'none':'none','near':'near','far':'far','domain_shift':'domain/context shift','unknown':'unclear'}
N_MAP = {'prevented':'prevented','monitored':'monitored','verified':'verified','self_report':'self-report','unknown':'unclear'}

def code(features):
    t=features['timing_feature'].strip()
    if t == 'concurrent': D='concurrent'
    elif t == 'immediate': D='immediate'
    elif t == 'elapsed':
        v=features.get('timing_value','').strip()
        if not v or not re.fullmatch(r'\d+(?:\.\d+)?\s+(?:minute|minutes|hour|hours|day|days|week|weeks|month|months)', v):
            raise AssertionError(f'invalid elapsed timing value: {v!r}')
        D=v
    elif t == 'unknown': D='unclear'
    else: raise AssertionError(f'unknown timing feature: {t!r}')
    return {
        'A': A_MAP[features['ai_access_feature'].strip()],
        'D': D,
        'O': O_MAP[features['overlap_feature'].strip()],
        'G': G_MAP[features['transfer_feature'].strip()],
        'N': N_MAP[features['nonuse_feature'].strip()],
    }

def read_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

checks=[]
def add(name, passed, detail):
    checks.append({'check':name,'status':'PASS' if passed else 'FAIL','detail':detail})
    if not passed: raise AssertionError(f'{name}: {detail}')

# 1. Frozen codebook completeness.
cb=read_csv(RESULTS/'arrp_coding_protocol.csv')
add('codebook_has_five_unique_dimensions', len(cb)==5 and {r['code'] for r in cb}=={'A','D','O','G','N'}, f'{len(cb)} rows; codes={sorted(r["code"] for r in cb)}')
for r in cb:
    vals={x.strip() for x in r['allowed_values'].split('|')}
    add(f'codebook_{r["code"]}_has_unclear', 'unclear' in vals, r['allowed_values'])
    ev = r.get('core_source_evidence', r.get('minimum_source_evidence','')).strip()
    add(f'codebook_{r["code"]}_has_evidence_rule', bool(ev), ev[:120])

# 2. Executable structured feature-to-code tests.
tests=read_csv(RESULTS/'arrp_executable_feature_tests.csv')
for r in tests:
    got=code(r)
    exp={k:r[f'expected_{k}'].strip() for k in 'ADOGN'}
    add(f'executable_{r["case_id"]}', got==exp, f'expected={exp}; got={got}')
add('executable_test_count', len(tests)==20, f'{len(tests)}/20 structured cases')

# 3. Metamorphic selective-sensitivity tests.
metas=read_csv(RESULTS/'arrp_metamorphic_rule_tests.csv')
for r in metas:
    b=code({'ai_access_feature':r['base_ai'],'timing_feature':r['base_timing'],'timing_value':r['base_timing_value'],'overlap_feature':r['base_overlap'],'transfer_feature':r['base_transfer'],'nonuse_feature':r['base_nonuse']})
    v=code({'ai_access_feature':r['variant_ai'],'timing_feature':r['variant_timing'],'timing_value':r['variant_timing_value'],'overlap_feature':r['variant_overlap'],'transfer_feature':r['variant_transfer'],'nonuse_feature':r['variant_nonuse']})
    target=r['target_dimension'].strip()
    changed=[k for k in 'ADOGN' if b[k]!=v[k]]
    add(f'metamorphic_{r["pair_id"]}', changed==[target], f'target={target}; changed={changed}; base={b}; variant={v}')
add('metamorphic_test_count', len(metas)==10, f'{len(metas)}/10 single-dimension pairs')

# 4. Legacy scenario-table guardrail checks (retained as descriptive cases).
legacy=read_csv(RESULTS/'arrp_operational_test_cases.csv')
add('legacy_case_count', len(legacy)==12, f'{len(legacy)}/12')
for cid in ('T05','T12'):
    r=next(x for x in legacy if x['case_id']==cid)
    add(f'legacy_{cid}_ambiguity_guardrail', all(r[k].strip()=='unclear' for k in ('A','D','O','G','N')), 'all five dimensions remain unclear')

# 5. Worked-example completeness and traceability (not recoding reliability).
worked=read_csv(RESULTS/'arrp_worked_outcome_examples.csv')
add('worked_example_count', len(worked)==77, f'{len(worked)}/77')
ids=[r['outcome_id'].strip() for r in worked]
add('worked_outcome_ids_unique', len(set(ids))==len(ids), f'{len(set(ids))} unique IDs')
required=['doi','source_url','coding_source','coding_status','ai_availability_at_assessment','assessment_delay','task_item_overlap','transfer_demand','evidence_scope_ai_nonuse','defensible_score_interpretation']
for c in required:
    n=sum(bool(r.get(c,'').strip()) for r in worked)
    add(f'worked_{c}_complete', n==len(worked), f'{n}/{len(worked)} nonblank')
no_claim=sum('no claim' in r['coding_status'].lower() or 'no inter-rater' in r['coding_status'].lower() for r in worked)
add('worked_examples_no_human_reliability_claim', no_claim==len(worked), f'{no_claim}/{len(worked)} explicitly bounded')

# 6. Public-release schema integrity checks replacing development-tree mirror checks.
core=read_csv(RESULTS/'arrp_core_reporting_fields.csv')
add('core_reporting_field_count', len(core)==5, f'{len(core)}/5 proposed core fields')
rat=read_csv(RESULTS/'arrp_dimension_rationale.csv')
add('dimension_rationale_has_five_codes', len(rat)==5 and {r['code'] for r in rat}=={'A','D','O','G','N'}, f'{len(rat)} rows; codes={sorted(r["code"] for r in rat)}')
status=read_csv(RESULTS/'arrp_validation_status.csv')
text=' '.join((r.get('validation_component','')+' '+r.get('inference_boundary','')+' '+r.get('result_or_scope','')) for r in status).lower()
add('validation_status_preserves_boundary', len(status)>0 and 'human inter-rater' in text and ('content validity' in text or 'content-validity' in text) and 'consensus' in text, f'{len(status)} status rows with explicit external-validity boundaries')

out=RESULTS/'arrp_specification_audit.csv'
with out.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['check','status','detail'],lineterminator='\n'); w.writeheader(); w.writerows(checks)
summary={
    'audit_type':'deterministic software/specification audit; not human inter-rater validation',
    'checks_total':len(checks),
    'checks_passed':sum(x['status']=='PASS' for x in checks),
    'checks_failed':sum(x['status']=='FAIL' for x in checks),
    'structured_executable_cases':len(tests),
    'metamorphic_pairs':len(metas),
    'worked_examples_traceability_checked':len(worked),
    'inference_boundary':'Supports frozen-rule completeness, implementation conformance, ambiguity handling, selective sensitivity/invariance, file integrity, and worked-example traceability only. It does not establish human inter-rater reliability, content validity, consensus status, or prevalence.'
}
(RESULTS/'arrp_specification_audit_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"PASS: {summary['checks_passed']}/{summary['checks_total']} deterministic ARRP specification-audit checks passed; 20 executable cases; 10 metamorphic pairs; 77 worked records checked for traceability/completeness.")
