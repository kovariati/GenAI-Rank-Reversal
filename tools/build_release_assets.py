#!/usr/bin/env python3
"""Build the versioned GitHub release results asset.

The Git tag is the canonical source snapshot. GitHub supplies Source code (zip)
and Source code (tar.gz) automatically. This builder creates one convenience
asset containing the repository's canonical results/ directory.

No custom checksum/hash manifest is generated.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / 'PROJECT_METADATA.json').read_text(encoding='utf-8'))
ASSET_NAME = M.get('release_asset') or 'GenAI_Rank_Reversal_results_v1.0.0.zip'
FIXED_DT = (1980, 1, 1, 0, 0, 0)


def write_zip(path: Path) -> None:
    result_files = sorted(
        (p for p in (ROOT / 'results').rglob('*') if p.is_file()),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src in result_files:
            arcname = src.relative_to(ROOT).as_posix()
            zi = zipfile.ZipInfo(arcname, date_time=FIXED_DT)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(zi, src.read_bytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--skip-validation', action='store_true')
    args = ap.parse_args()
    outdir = Path(args.output_dir).resolve()
    if ROOT == outdir or ROOT in outdir.parents:
        raise SystemExit('Output directory must be outside the repository tree.')
    if not args.skip_validation:
        subprocess.run([sys.executable, str(ROOT / 'tools/validate_repository.py')], cwd=ROOT, check=True)
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    archive = outdir / ASSET_NAME
    write_zip(archive)
    print('Built release asset:')
    print(f'  {archive.name}: {archive.stat().st_size} bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
