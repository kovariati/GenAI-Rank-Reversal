#!/usr/bin/env python3
import csv
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / 'results').exists() else HERE.parent
p = ROOT / 'results' / 'arrp_operational_test_cases.csv'
allowed = {
    'A': {'available','removed','restricted','unclear'},
    'O': {'same','repeated','similar','novel','unclear'},
    'G': {'none','near','far','domain-context-shift','unclear'},
    'N': {'prevented','monitored','verified','self-report','unclear'},
}
rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
assert len(rows)==12, f'expected 12 cases, got {len(rows)}'
for r in rows:
    for k, vals in allowed.items():
        assert r[k] in vals, (r['case_id'], k, r[k])
    assert r['D'].strip(), (r['case_id'],'D blank')
# Cases explicitly described as under-reported must remain unresolved rather than imputed.
for cid in ('T05','T12'):
    r=next(x for x in rows if x['case_id']==cid)
    assert r['A']=='unclear' and r['N']=='unclear'
print(f'PASS: {len(rows)}/12 ARRP operational rule cases satisfy the frozen value and ambiguity rules.')
