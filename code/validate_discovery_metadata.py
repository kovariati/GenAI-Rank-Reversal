#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'PROJECT_METADATA.json').read_text(encoding='utf-8'))
readme=(ROOT/'README.md').read_text(encoding='utf-8')
checks=[]
def add(name,ok): checks.append((name,bool(ok)))
add('title_in_readme', meta['article_title'] in readme)
for claim in meta['canonical_claims']: add('claim_'+str(len(checks)+1), claim in readme)
for term in ['generative AI','independent human performance','assessment-regime rank transport','meta-analysis','evidence synthesis']:
    add('term_'+term, term.lower() in readme.lower())
add('no_fake_doi', '<DOI>' not in readme and '10.0000/' not in readme)
for name,ok in checks: print(f'{name}: {"PASS" if ok else "FAIL"}')
if not all(ok for _,ok in checks): sys.exit(1)
print(f'discovery_metadata: {sum(ok for _,ok in checks)}/{len(checks)} PASS')
