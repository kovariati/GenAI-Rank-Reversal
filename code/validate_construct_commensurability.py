#!/usr/bin/env python3
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'results'/'construct_commensurability_audit.csv'
required=['program','assisted_outcome','independent_outcome','shared_construct_link','common_directionality','task_identity_changed','transfer_demand_changed','commensurability_status','rank_comparison_eligible','interpretive_boundary','source_basis']
allowed={'directionally_commensurable_with_boundary','construct_linked_directional_only','non_commensurable','unclear'}
rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
checks=[]
checks.append(('three_programs', len(rows)==3))
checks.append(('required_columns', all(c in (rows[0].keys() if rows else []) for c in required)))
checks.append(('unique_programs', len({r['program'] for r in rows})==len(rows)))
checks.append(('allowed_status', all(r['commensurability_status'] in allowed for r in rows)))
checks.append(('binary_change_fields', all(r['task_identity_changed'] in {'yes','no','unclear'} and r['transfer_demand_changed'] in {'yes','no','unclear'} for r in rows)))
checks.append(('rank_eligibility_binary', all(r['rank_comparison_eligible'] in {'yes','no'} for r in rows)))
checks.append(('no_eligible_noncommensurable', all(not (r['rank_comparison_eligible']=='yes' and r['commensurability_status'] in {'non_commensurable','unclear'}) for r in rows)))
checks.append(('source_basis_complete', all(r['source_basis'].strip() for r in rows)))
checks.append(('boundary_complete', all(r['interpretive_boundary'].strip() for r in rows)))
for name, ok in checks:
    print(f'{name}: {"PASS" if ok else "FAIL"}')
if not all(ok for _,ok in checks):
    sys.exit(1)
print(f'construct_commensurability: {sum(ok for _,ok in checks)}/{len(checks)} PASS')
