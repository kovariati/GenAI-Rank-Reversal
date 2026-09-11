#!/usr/bin/env python3
"""Build the deterministic custom GitHub release artifact.

After definitive publication metadata are available, the article-associated source/reproducibility snapshot will be the GitHub v1.0.0 tag. GitHub will automatically provide Source code (zip) and Source code (tar.gz). This builder prepares only the deterministic convenience results-and-artifacts ZIP for that future release.

ZIP timestamps are normalized to the ZIP epoch so identical repository content
produces identical artifact bytes. The timestamp is an archive-normalization
choice, not a scientific or publication date.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / 'PROJECT_METADATA.json').read_text(encoding='utf-8'))
PROJECT = M['project_short_name']
VERSION = 'v' + str(M['software_version']).lstrip('v')
ARTICLE_TITLE = M['article_title']
FIXED_DT = (1980, 1, 1, 0, 0, 0)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def manifest(entries: dict[str, bytes]) -> bytes:
    lines = [f"{sha_bytes(entries[name])}  {name}" for name in sorted(entries)]
    return ('\n'.join(lines) + '\n').encode('utf-8')


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    entries = dict(entries)
    entries['MANIFEST_SHA256.txt'] = manifest(entries)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in sorted(entries):
            zi = zipfile.ZipInfo(name, date_time=FIXED_DT)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(zi, entries[name])


def read_entries(relpaths: list[Path]) -> dict[str, bytes]:
    return {rel.as_posix(): (ROOT / rel).read_bytes() for rel in relpaths}


def results_and_artifacts_entries() -> dict[str, bytes]:
    rel: list[Path] = []
    for d in ['results', 'figures']:
        rel += [p.relative_to(ROOT) for p in (ROOT / d).rglob('*') if p.is_file()]
    rel += [Path(x) for x in [
        'PROJECT_METADATA.json',
        'DATA_AVAILABILITY.md',
        'DATA_LICENSE.md',
        'THIRD_PARTY_DATA_NOTICE.md',
        'RUNTIME.txt',
        'arrp.schema.json',
        'examples/arrp_example_wong_task2.json',
        'docs/ARRP.md',
        'docs/METHOD_TO_CODE_MAP.md',
        'docs/REPRODUCIBILITY_ARTIFACTS.md',
        'docs/COMPUTATIONAL_VALIDATION.md',
        'docs/RANK_ROBUSTNESS.md',
        'docs/SYNTHESIS_SCHEMA_AUDIT.md',
        'docs/SOURCE_PROVENANCE.md',
        'docs/PUBLIC_RELEASE_VALIDATION.md',
        'docs/RELEASE_PROVENANCE.md',
        'docs/REPOSITORY_SCORECARD.md',
    ]]
    out = read_entries(sorted(set(rel), key=lambda x: x.as_posix()))
    out['README.md'] = (
        f"# {PROJECT} {VERSION} — results and artifacts\n\n"
        f"Convenience bundle of canonical derived results, reusable ARRP artifacts, public provenance summaries, "
        f"and manuscript-facing figures for _{ARTICLE_TITLE}_.\n\n"
        "When the publication-linked release is created, the canonical article-associated source-code and reproducibility snapshot will be the GitHub `v1.0.0` tag. GitHub automatically "
        "provides Source code (zip) and Source code (tar.gz) for that tag, so this archive intentionally does not "
        "duplicate the full repository.\n\n"
        "Raw third-party participant data are not redistributed. See `DATA_AVAILABILITY.md` and "
        "`THIRD_PARTY_DATA_NOTICE.md`.\n\n"
        "Key machine-readable entry points include `results/wong_direct_reversal_inference.csv`, "
        "`results/pairwise_rank_transport_status.csv`, `results/construct_commensurability_audit.csv`, "
        "`results/arrp_specification_audit_summary.json`, and `arrp.schema.json`.\n"
    ).encode('utf-8')
    return out


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

    filename = f'{PROJECT}-{VERSION}-results-and-artifacts.zip'
    archive = outdir / filename
    write_zip(archive, results_and_artifacts_entries())
    digest = sha_file(archive)
    checksum = outdir / (filename + '.sha256')
    checksum.write_text(f'{digest}  {filename}\n', encoding='utf-8', newline='\n')

    print('Built release artifact:')
    print(f'  {filename}: {archive.stat().st_size} bytes sha256={digest}')
    print(f'  {checksum.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
