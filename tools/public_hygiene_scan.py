#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
text_ext={'.py','.md','.txt','.json','.csv','.yml','.yaml','.cff','.bib','.ris','.toml'}
# Development-only labels, local paths, review artefacts, and secrets must not leak into the public tree.
patterns={
 'internal_revision_label':re.compile(r'(?i)(?:^|[^a-z0-9])v(?:1[5-9]|2[0-3])(?:[^0-9]|$)|_v(?:1[5-9]|2[0-3])'),
 'local_unix_path':re.compile(r'(?<!https:)(?<!http:)\/(?:mnt\/data|home\/[^\s/]+|Users\/[^\s/]+)\/'),
 'local_windows_path':re.compile(r'(?i)\b[A-Z]:\\\\?(?:Users|Temp|DATA_SSD|AdaptiveLearningSim|Missingness|SmallDataBench|EngTFM)'),
 'review_material':re.compile(r'(?i)reviewer[_ -]?matrix|external_review_round|revision_matrix'),
 'nonfinal_surveillance':re.compile(r'(?i)nonfinalized_surveillance|horizon-surveillance'),
 'secrets':re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{12,}')
}
ignore_dirs={'.git','.venv','venv','__pycache__'}
viol=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in text_ext: continue
    if any(part in ignore_dirs for part in p.parts): continue
    # This scanner contains the patterns by definition; do not scan itself.
    if p.name=='public_hygiene_scan.py': continue
    try: txt=p.read_text(encoding='utf-8-sig')
    except Exception: continue
    for name,pat in patterns.items():
        for m in pat.finditer(txt):
            viol.append((name,p.relative_to(ROOT).as_posix(),txt.count('\n',0,m.start())+1,m.group(0)[:120]))
for item in viol: print('FAIL',*item,sep=' | ')
if viol: sys.exit(f'public hygiene failed: {len(viol)} finding(s)')
print('public_hygiene: PASS')
