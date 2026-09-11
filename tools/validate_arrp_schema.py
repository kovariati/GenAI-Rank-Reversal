#!/usr/bin/env python3
"""Lightweight fail-closed structural validation for the public ARRP JSON Schema and worked example."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
S=json.loads((ROOT/'arrp.schema.json').read_text(encoding='utf-8'))
E=json.loads((ROOT/'examples/arrp_example_wong_task2.json').read_text(encoding='utf-8'))
assert S['$schema']=='https://json-schema.org/draft/2020-12/schema'
assert S['required']==['outcome_id','A','D','O','G','N']
assert set(['A','D','O','G','N']).issubset(S['properties'])
for k in ['A','O','G','N']:
    assert E[k]['status'] in S['properties'][k]['properties']['status']['enum'], (k,E[k]['status'])
assert E['D']['category'] in S['properties']['D']['properties']['category']['enum']
assert all(E[k].get('source_evidence','').strip() for k in ['A','D','O','G','N'])
assert E['N'].get('scope','').strip()
assert E['source']['doi'].startswith('10.')
print('arrp_schema: PASS (JSON Schema + worked example structural checks)')
