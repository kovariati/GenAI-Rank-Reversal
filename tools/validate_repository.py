#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, cwd=ROOT):
    print('+', ' '.join(map(str, cmd)))
    subprocess.run(cmd, cwd=cwd, check=True)


def schema_people(xs):
    return [
        {
            '@type': 'Person',
            'givenName': x['given_names'],
            'familyName': x['family_names'],
            '@id': x['orcid'],
        }
        for x in xs
    ]


def cff_people(xs):
    return [
        {
            'family-names': x['family_names'],
            'given-names': x['given_names'],
            'orcid': x['orcid'],
        }
        for x in xs
    ]


def ris_authors(text: str) -> list[list[str]]:
    records=[]; cur=[]
    for line in text.splitlines():
        if line.startswith('AU  - '): cur.append(line[6:])
        elif line == 'ER  - ':
            records.append(cur); cur=[]
    return records


M = json.loads((ROOT / 'PROJECT_METADATA.json').read_text(encoding='utf-8'))
C = yaml.safe_load((ROOT / 'CITATION.cff').read_text(encoding='utf-8'))
CM = json.loads((ROOT / 'codemeta.json').read_text(encoding='utf-8'))
AM = json.loads((ROOT / 'ARTICLE_METADATA.json').read_text(encoding='utf-8'))
readme = (ROOT / 'README.md').read_text(encoding='utf-8')
bib = (ROOT / 'CITATION.bib').read_text(encoding='utf-8')
ris = (ROOT / 'CITATION.ris').read_text(encoding='utf-8')
llms = (ROOT / 'llms.txt').read_text(encoding='utf-8')

# Identity and abstract.
assert C['title'] == M['article_title'] == CM['name'] == AM['name']
assert C['preferred-citation']['title'] == M['article_title'] == CM['citation']['name']
assert C['preferred-citation']['abstract'] == M['article_abstract'] == CM['citation']['abstract'] == AM['abstract']
assert M['article_title'] in readme
print('metadata_identity: PASS')

# Semantic cross-file consistency, not merely generator byte identity.
assert C['authors'] == cff_people(M['authors'])
assert C['preferred-citation']['authors'] == cff_people(M['authors'])
assert CM['author'] == schema_people(M['authors'])
assert CM['citation']['author'] == schema_people(M['authors'])
assert AM['author'] == schema_people(M['authors'])
assert C['version'] == M['software_version'] == CM['version']
assert C['license'] == M['software_license']
assert CM['license'] == M['software_license_url']
assert CM['runtimePlatform'] == f"Python {M['runtime']['python']}"
assert C['preferred-citation']['year'] == M['article_year']
assert AM['dateCreated'] == str(M['article_year'])
assert C['keywords'] == M['paper_keywords'] == CM['keywords'] == AM['keywords']
assert C['preferred-citation']['keywords'] == M['paper_keywords'] == CM['citation']['keywords']
expected_bib_author = ' and '.join(f"{x['family_names']}, {x['given_names']}" for x in M['authors'])
assert bib.count(f'author = {{{expected_bib_author}}}') == 2
expected_ris_authors = [f"{x['family_names']}, {x['given_names']}" for x in M['authors']]
rr = ris_authors(ris)
assert len(rr) == 2 and all(x == expected_ris_authors for x in rr), rr
assert f'ET  - {M["software_version"]}' in ris
assert M['article_title'] in bib and M['article_title'] in ris and M['article_title'] in llms
for claim in M['canonical_claims']:
    assert claim in llms and claim in readme

# Fail closed on publication identifiers: null is valid; fake values are not.
for k in ('article_doi', 'journal', 'publisher_url', 'repository_url', 'release_url'):
    v = M.get(k)
    assert v is None or (isinstance(v, str) and v.strip()), k
assert '<DOI>' not in readme and '10.0000/' not in readme
if M.get('repository_url'):
    assert C.get('repository-code') == M['repository_url']
    assert CM.get('codeRepository') == M['repository_url']
    assert M['repository_url'] in bib and M['repository_url'] in ris and M['repository_url'] in llms
else:
    assert 'repository-code' not in C and 'codeRepository' not in CM
if M.get('article_doi'):
    assert C['preferred-citation'].get('doi') == M['article_doi']
    assert CM['citation'].get('identifier') == 'https://doi.org/' + M['article_doi']
    assert AM.get('identifier') == 'https://doi.org/' + M['article_doi']
else:
    assert 'doi' not in C['preferred-citation'] and 'identifier' not in CM['citation'] and 'identifier' not in AM
if M.get('journal'):
    assert C['preferred-citation'].get('journal') == M['journal']
    assert CM['citation']['isPartOf']['name'] == M['journal']
    assert AM['isPartOf']['name'] == M['journal']
else:
    assert 'journal' not in C['preferred-citation'] and 'isPartOf' not in CM['citation'] and 'isPartOf' not in AM
if M.get('release_url'):
    assert CM.get('downloadUrl') == M['release_url']
    assert M['release_url'] in llms and M['release_url'] in readme
else:
    assert 'downloadUrl' not in CM
if M.get('release_date'):
    assert C.get('date-released') == M['release_date']
    assert CM.get('datePublished') == M['release_date']
    assert CM.get('dateModified') == M['release_date']
if M.get('repository_url'):
    assert M['repository_url'] in readme
print('metadata_semantic_consistency: PASS')

# GitHub discovery surfaces. Current GitHub Create Repository UI permits up to 350 characters.
about = (ROOT / 'REPOSITORY_DESCRIPTION.txt').read_text(encoding='utf-8').strip()
assert about == M['repository_description'].strip()
assert 1 <= len(about) <= 350, len(about)
topics = [x.strip() for x in (ROOT / 'GITHUB_TOPICS.txt').read_text(encoding='utf-8').splitlines() if x.strip()]
assert topics == M['github_topics']
assert 12 <= len(topics) <= 20 and len(topics) == len(set(topics)), topics
assert all(re.fullmatch(r'[a-z0-9-]+', x) for x in topics), topics
assert 'docs/ARRP.md' in readme and 'arrp.schema.json' in readme
print(f'github_discovery_surfaces: PASS (About={len(about)} chars; topics={len(topics)})')

# Release-asset policy: the tagged repository is the canonical source snapshot.
release_notes = (ROOT / 'RELEASE_NOTES_v1.0.0.md').read_text(encoding='utf-8')
release_builder = (ROOT / 'tools/build_release_assets.py').read_text(encoding='utf-8')
for obsolete in ('REPRODUCIBILITY.zip', 'PROVENANCE.zip', 'FINAL_ANALYSIS.zip'):
    assert obsolete not in release_notes, obsolete
    assert obsolete not in release_builder, obsolete
assert 'results-and-artifacts.zip' in release_notes
assert 'results-and-artifacts.zip' in release_builder
assert 'Source code (zip)' in release_notes
assert 'Source code (tar.gz)' in release_notes
if M.get('release_url') is None:
    assert 'DRAFT RELEASE TEMPLATE' in release_notes
    assert 'planned publication-linked v1.0.0 release' in release_notes.lower()
    prov=(ROOT/'docs/RELEASE_PROVENANCE.md').read_text(encoding='utf-8')
    assert 'DRAFT RELEASE TEMPLATE' in prov and 'planned publication-linked v1.0.0 release' in prov.lower()
print('release_asset_policy: PASS')


# Pre-publication release policy: do not claim a live version-specific release or repository DOI before they exist.
if M.get('release_url') is None:
    public_text = '\n'.join((ROOT / name).read_text(encoding='utf-8') for name in [
        'README.md', 'DATA_AVAILABILITY.md', 'RELEASE_NOTES_v1.0.0.md', 'docs/RELEASE_PROVENANCE.md'
    ])
    assert '/releases/tag/v1.0.0' not in public_text
    assert 'repository doi: 10.' not in public_text.lower()
print('prepublication_release_policy: PASS')

# ARRP machine-readable values and manuscript-facing reporting surface must stay semantically aligned.
schema = json.loads((ROOT / 'arrp.schema.json').read_text(encoding='utf-8'))
with (ROOT / 'results/arrp_core_reporting_fields.csv').open(encoding='utf-8-sig') as fh:
    core = list(csv.DictReader(fh))
assert len(core) == 5
expected = {
    'AI availability at assessment': schema['properties']['A']['properties']['status']['enum'],
    'Assessment delay': ['concurrent', 'immediate', 'exact elapsed time', 'unclear'],
    'Task or item overlap': schema['properties']['O']['properties']['status']['enum'],
    'Transfer demands': schema['properties']['G']['properties']['status']['enum'],
    'Evidence of AI non-use': ['prevented', 'monitored', 'verified', 'self-report', 'unclear + scope'],
}
for row in core:
    vals = [x.strip() for x in row['proposed_reporting'].split('/')]
    assert vals == expected[row['item']], (row['item'], vals, expected[row['item']])
print('arrp_surface_consistency: PASS')

# Canonical Figure 1 must have synchronized SVG/PDF/PNG assets.
for ext in ('svg','pdf','png'):
    assert (ROOT / f'figures/figure1_structural_rank_transport.{ext}').is_file()
print('figure1_canonical_assets: PASS')

# Canonical metadata generator must reproduce all generated surfaces byte-for-byte.
with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    (t / 'tools').mkdir()
    shutil.copy2(ROOT / 'PROJECT_METADATA.json', t / 'PROJECT_METADATA.json')
    shutil.copy2(ROOT / 'tools/generate_metadata_files.py', t / 'tools/generate_metadata_files.py')
    run([sys.executable, 'tools/generate_metadata_files.py'], cwd=t)
    for name in [
        'CITATION.cff', 'CITATION.bib', 'CITATION.ris', 'codemeta.json',
        'ARTICLE_METADATA.json', 'llms.txt', 'REPOSITORY_DESCRIPTION.txt', 'GITHUB_TOPICS.txt'
    ]:
        assert (t / name).read_bytes() == (ROOT / name).read_bytes(), ('metadata generator drift', name)
print('metadata_generator_idempotence: PASS')

run([sys.executable, 'tools/validate_dependency_lock.py'])
run([sys.executable, 'tools/validate_arrp_schema.py'])
run([sys.executable, 'tools/public_hygiene_scan.py'])
run([sys.executable, 'code/validate_discovery_metadata.py'])
run([sys.executable, 'code/validate_construct_commensurability.py'])
run([sys.executable, 'code/validate_arrp_operational_rules.py'])

# ARRP spec validator rewrites its audit outputs; preserve canonical bytes and require identical result after run.
arrp_files = [ROOT / 'results/arrp_specification_audit.csv', ROOT / 'results/arrp_specification_audit_summary.json']
before = {p.name: p.read_bytes() for p in arrp_files}
run([sys.executable, 'code/validate_arrp_specification.py'])
after = {p.name: p.read_bytes() for p in arrp_files}
assert before == after, ('ARRP regenerated output differs', before, after)
print('arrp_byte_identity: PASS')

# Regenerate self-contained outputs in an isolated temp tree and compare their contents directly.
with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    (t / 'results').mkdir(); (t / 'code').mkdir()
    for name in ['wong_published_sufficient_statistics.csv', 'wong_raw_group_means.csv', 'wong_rank_reversal_sensitivity_input.csv']:
        shutil.copy2(ROOT / 'results' / name, t / 'results' / name)
    for name in ['analyze_wong_direct_reversal.py', 'assessment_regime_rank_robustness.py', 'assessment_regime_rank_sensitivity.py']:
        shutil.copy2(ROOT / 'code' / name, t / 'code' / name)
    run([sys.executable, 'code/analyze_wong_direct_reversal.py'], cwd=t)
    run([sys.executable, 'code/analyze_wong_direct_reversal.py', '--outcomes', 'originality', 'usefulness', 'elaboration', '--output', 'results/wong_three_dimension_inference.csv', '--summary', 'results/wong_three_dimension_summary.csv'], cwd=t)
    run([sys.executable, 'code/assessment_regime_rank_robustness.py'], cwd=t)
    run([sys.executable, 'code/assessment_regime_rank_sensitivity.py', 'results/wong_rank_reversal_sensitivity_input.csv', 'results/wong_rank_reversal_sensitivity.csv'], cwd=t)
    for name in ['wong_direct_reversal_inference.csv', 'wong_direct_reversal_summary.csv', 'wong_three_dimension_inference.csv', 'wong_three_dimension_summary.csv', 'wong_rank_robustness_region.csv', 'wong_rank_robustness_summary.csv', 'wong_rank_reversal_sensitivity.csv']:
        assert (t / 'results' / name).read_bytes() == (ROOT / 'results' / name).read_bytes(), name
print('self_contained_regeneration: PASS')

# Rebuild paired profiles and pairwise rank status from shipped derived results in a temp tree.
with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    (t / 'results').mkdir(); (t / 'code').mkdir()
    deps = ['construct_commensurability_audit.csv', 'bastani_within_study_profile_contrast.csv', 'study_descriptives.csv', 'bassner_effects.csv', 'bassner_descriptives.csv', 'bassner_profile_bootstrap.csv', 'wong_participant_reanalysis.csv']
    for name in deps:
        shutil.copy2(ROOT / 'results' / name, t / 'results' / name)
    for name in ['build_paired_profiles.py', 'assessment_regime_rank_order.py']:
        shutil.copy2(ROOT / 'code' / name, t / 'code' / name)
    run([sys.executable, 'code/build_paired_profiles.py', '--results', 'results'], cwd=t)
    run([sys.executable, 'code/assessment_regime_rank_order.py'], cwd=t)
    for name in ['paired_supported_independent_profiles.csv', 'paired_profile_contrasts.csv', 'paired_profile_summary.json', 'pairwise_rank_transport_status.csv']:
        if name != 'pairwise_rank_transport_status.csv':
            assert (t / 'results' / name).read_bytes() == (ROOT / 'results' / name).read_bytes(), name

    def rr(p):
        return {r['program']: r['pairwise_transport_status'] for r in csv.DictReader(Path(p).open(encoding='utf-8-sig'))}

    assert rr(t / 'results/pairwise_rank_transport_status.csv') == rr(ROOT / 'results/pairwise_rank_transport_status.csv')
print('paired_profile_regeneration: PASS')

with tempfile.TemporaryDirectory() as td:
    t=Path(td); (t/'results').mkdir(); (t/'code').mkdir()
    deps=['construct_commensurability_audit.csv','wong_direct_reversal_summary.csv','bastani_rank_evidence_summary.csv','bassner_descriptives.csv','bassner_effects.csv']
    for name in deps: shutil.copy2(ROOT/'results'/name,t/'results'/name)
    shutil.copy2(ROOT/'code/build_paired_rank_evidence.py',t/'code/build_paired_rank_evidence.py')
    run([sys.executable,'code/build_paired_rank_evidence.py','--results','results'],cwd=t)
    assert (t/'results/paired_rank_evidence_revised.csv').read_bytes() == (ROOT/'results/paired_rank_evidence_revised.csv').read_bytes()
print('manuscript_facing_evidence_regeneration: PASS')

run([sys.executable, 'tests/test_expected_results.py'])
run([sys.executable, '-m', 'pytest', '-q'])
print('mathematical_algorithm_pytest: PASS')
print('repository_validation: PASS')
