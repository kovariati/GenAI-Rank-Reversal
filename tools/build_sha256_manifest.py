#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
out=Path(sys.argv[2]) if len(sys.argv)>2 else Path('SHA256SUMS.txt')
exclude={out.resolve()}
rows=[]
for p in sorted(x for x in root.rglob('*') if x.is_file()):
    if p.resolve() in exclude: continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    rows.append(f'{h}  {p.relative_to(root).as_posix()}')
out.write_text('\n'.join(rows)+'\n',encoding='utf-8')
print(f'wrote {len(rows)} hashes to {out}')
