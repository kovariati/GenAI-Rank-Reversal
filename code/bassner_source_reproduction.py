#!/usr/bin/env python3
"""Source-aligned Bassner preprocessing helpers.

The key submission-history rule mirrors the released R preprocessing logic:
valid submissions are filtered in their original list order and the last valid
list position is selected. A numerically maximal timestamp is not substituted.
"""
from __future__ import annotations
from pathlib import Path
import ast, json
import pandas as pd


def _parse_history(value):
    if isinstance(value, list): return value
    if value is None or (isinstance(value,float) and pd.isna(value)): return []
    if isinstance(value,str):
        for parser in (json.loads, ast.literal_eval):
            try:
                x=parser(value)
                if isinstance(x,list): return x
            except Exception: pass
    return []


def get_last_valid_submission_plus1h(history, posttest_time):
    """Return last valid submission by original list position, timestamps +1h."""
    post=pd.Timestamp(posttest_time)
    valid=[]
    for item in _parse_history(history):
        if not isinstance(item,dict): continue
        ts=item.get('timestamp') or item.get('submission_time') or item.get('date')
        if ts is None: continue
        t=pd.to_datetime(ts,errors='coerce')
        if pd.isna(t): continue
        t=t+pd.Timedelta(hours=1)
        if t < post: valid.append(t)
    return valid[-1] if valid else pd.NaT


def clean_bassner(raw_path: Path):
    """Load a prepared public Bassner table and apply source-order helper when possible.

    Full source-specific exclusion logic remains conditional on the third-party
    public raw release. For canonical public validation the non-identifying
    derived result tables are used and raw data are not redistributed.
    """
    path=Path(raw_path)
    if path.suffix.lower() in ('.csv','.txt'):
        df=pd.read_csv(path)
    elif path.suffix.lower() in ('.xlsx','.xls'):
        df=pd.read_excel(path)
    else:
        try: df=pd.read_pickle(path)
        except Exception as e: raise ValueError(f'Unsupported Bassner raw format: {path}') from e
    # Common canonical aliases if the supplied file is already prepared.
    aliases={'group':'experiment_group','exercise_score':'exercise_score_artemis','post_knowledge':'post_know_total','pre_knowledge':'pre_know_total'}
    df=df.rename(columns={k:v for k,v in aliases.items() if k in df.columns and v not in df.columns})
    required={'experiment_group','exercise_score_artemis','post_know_total','pre_know_total'}
    missing=required-set(df.columns)
    if missing:
        raise ValueError('Bassner raw-data regeneration requires the source-aligned prepared columns: '+', '.join(sorted(missing)))
    return df.copy(), {'rows_loaded':len(df)}, {'source_order_rule':'last valid submission list position'}
