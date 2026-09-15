#!/usr/bin/env python3
"""Validate the complete Draft 2020-12 ARRP schema and supplied instance.

Structural conformance does not establish accuracy of source coding, content
validity, inter-rater reliability, or a consensus reporting standard.
"""
from pathlib import Path
import json
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]

def validate_record(record, schema=None):
    schema = schema or json.loads((ROOT/'arrp.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)

if __name__=='__main__':
    schema=json.loads((ROOT/'arrp.schema.json').read_text(encoding='utf-8'))
    example=json.loads((ROOT/'examples/arrp_example_wong_task2.json').read_text(encoding='utf-8'))
    validate_record(example,schema)
    print('arrp_schema: PASS (complete Draft 2020-12 schema and instance validation; not scientific validation)')
