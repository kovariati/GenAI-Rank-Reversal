#!/usr/bin/env python3
"""Generate public citation/discovery metadata from PROJECT_METADATA.json.

This file is intentionally deterministic. PROJECT_METADATA.json is the single
authoring source for identity-bearing metadata; generated surfaces should not be
edited by hand.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import unicodedata
import yaml

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / 'PROJECT_METADATA.json').read_text(encoding='utf-8'))

title = M['article_title']
year = int(M['article_year'])
version = str(M['software_version'])
authors = M['authors']
software_license = M['software_license']
software_license_url = M.get('software_license_url') or f"https://spdx.org/licenses/{software_license}.html"
runtime_python = M.get('runtime', {}).get('python', '3.13')


def person_cff(x: dict) -> dict:
    return {
        'family-names': x['family_names'],
        'given-names': x['given_names'],
        'orcid': x['orcid'],
    }


def person_schema(x: dict) -> dict:
    return {
        '@type': 'Person',
        'givenName': x['given_names'],
        'familyName': x['family_names'],
        '@id': x['orcid'],
    }


def bibtex_author(xs: list[dict]) -> str:
    return ' and '.join(f"{x['family_names']}, {x['given_names']}" for x in xs)


def ris_author_lines(xs: list[dict]) -> list[str]:
    return [f"AU  - {x['family_names']}, {x['given_names']}" for x in xs]


def safe_key_part(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9]+', '', s)


first_family = safe_key_part(authors[0]['family_names']) or 'Author'
project_key = safe_key_part(M['project_short_name']) or 'ResearchSoftware'
article_key = f'{first_family}{year}{project_key}'
software_key = f'{article_key}Software'

software_description = (
    f"Code, results, and reproducibility snapshot for the manuscript '{title}'. "
    "Third-party raw participant data are not redistributed."
)

# CFF
cff = {
    'cff-version': '1.2.0',
    'message': (
        'If the scientific method or findings contribute to your work, cite the associated '
        'manuscript/article when appropriate; for direct software reuse, cite this software '
        'release. Publication metadata are added only after they exist.'
    ),
    'title': title,
    'type': 'software',
    'authors': [person_cff(x) for x in authors],
    'version': version,
    'abstract': software_description,
    'keywords': list(M['paper_keywords']),
    'license': software_license,
}
if M.get('release_date'):
    cff['date-released'] = M['release_date']
if M.get('repository_url'):
    cff['repository-code'] = M['repository_url']

preferred = {
    'type': 'article',
    'authors': [person_cff(x) for x in authors],
    'title': title,
    'year': year,
    'abstract': M['article_abstract'],
    'keywords': list(M['paper_keywords']),
}
if M.get('journal'):
    preferred['journal'] = M['journal']
if M.get('article_doi'):
    preferred['doi'] = M['article_doi']
if not M.get('article_doi'):
    preferred['notes'] = 'Manuscript; journal and DOI metadata pending until an actual publication record exists.'
cff['preferred-citation'] = preferred
(ROOT / 'CITATION.cff').write_text(
    yaml.safe_dump(cff, sort_keys=False, allow_unicode=True, width=1000),
    encoding='utf-8',
)

# BibTeX: manuscript/article plus software record. No invented journal/DOI.
author_field = bibtex_author(authors)
if M.get('journal') or M.get('article_doi'):
    fields = [
        f'  author = {{{author_field}}}',
        f'  title = {{{title}}}',
        f'  year = {{{year}}}',
    ]
    if M.get('journal'):
        fields.append(f"  journal = {{{M['journal']}}}")
    if M.get('article_doi'):
        fields.append(f"  doi = {{{M['article_doi']}}}")
    article_record = '@article{' + article_key + ',\n' + ',\n'.join(fields) + '\n}\n'
else:
    article_record = (
        '@unpublished{' + article_key + ',\n'
        f'  author = {{{author_field}}},\n'
        f'  title = {{{title}}},\n'
        f'  year = {{{year}}},\n'
        '  note = {Manuscript; publication metadata pending}\n'
        '}\n'
    )
software_fields = [
    f'  author = {{{author_field}}}',
    f'  title = {{{title}}}',
    f'  version = {{{version}}}',
    f'  year = {{{year}}}',
    '  note = {Code and reproducibility snapshot}',
]
if M.get('repository_url'):
    software_fields.append(f"  url = {{{M['repository_url']}}}")
software_record = '@software{' + software_key + ',\n' + ',\n'.join(software_fields) + '\n}\n'
(ROOT / 'CITATION.bib').write_text(article_record + '\n' + software_record, encoding='utf-8')

# RIS
ris = ['TY  - JOUR' if M.get('journal') else 'TY  - UNPB']
ris += ris_author_lines(authors)
ris += [f'TI  - {title}', f'PY  - {year}']
if M.get('journal'):
    ris.append('JO  - ' + M['journal'])
if M.get('article_doi'):
    ris.append('DO  - ' + M['article_doi'])
else:
    ris.append('N1  - Manuscript; publication metadata pending')
ris += ['ER  - ', '', 'TY  - COMP']
ris += ris_author_lines(authors)
ris += [f'TI  - {title}', f'PY  - {year}', f'ET  - {version}']
if M.get('repository_url'):
    ris.append('UR  - ' + M['repository_url'])
ris += ['N1  - Code and reproducibility snapshot', 'ER  - ', '']
(ROOT / 'CITATION.ris').write_text('\n'.join(ris), encoding='utf-8')

# CodeMeta 3.1
code = {
    '@context': 'https://w3id.org/codemeta/3.1',
    '@type': 'SoftwareSourceCode',
    'name': title,
    'description': software_description,
    'version': version,
    'license': software_license_url,
    'author': [person_schema(x) for x in authors],
    'programmingLanguage': ['Python'],
    'runtimePlatform': f'Python {runtime_python}',
    'keywords': list(M['paper_keywords']),
    'citation': {
        '@type': 'ScholarlyArticle',
        'name': title,
        'abstract': M['article_abstract'],
        'author': [person_schema(x) for x in authors],
        'keywords': list(M['paper_keywords']),
        'description': 'Preferred scientific citation target; manuscript status until final publication metadata exist.',
    },
}
if M.get('repository_url'):
    code['codeRepository'] = M['repository_url']
    code['issueTracker'] = M['repository_url'].rstrip('/') + '/issues'
if M.get('release_url'):
    code['downloadUrl'] = M['release_url']
if M.get('release_date'):
    code['datePublished'] = M['release_date']
    code['dateModified'] = M['release_date']
if M.get('journal'):
    code['citation']['isPartOf'] = {'@type': 'Periodical', 'name': M['journal']}
if M.get('article_doi'):
    code['citation']['identifier'] = 'https://doi.org/' + M['article_doi']
(ROOT / 'codemeta.json').write_text(json.dumps(code, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# Article JSON-LD
article = {
    '@context': 'https://schema.org',
    '@type': 'ScholarlyArticle',
    'name': title,
    'headline': title,
    'abstract': M['article_abstract'],
    'author': [person_schema(x) for x in authors],
    'dateCreated': str(year),
    'creativeWorkStatus': M['article_status'],
    'keywords': list(M['paper_keywords']),
}
if M.get('journal'):
    article['isPartOf'] = {'@type': 'Periodical', 'name': M['journal']}
if M.get('article_doi'):
    article['identifier'] = 'https://doi.org/' + M['article_doi']
if M.get('publisher_url'):
    article['url'] = M['publisher_url']
(ROOT / 'ARTICLE_METADATA.json').write_text(json.dumps(article, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# Supplemental machine-readable project index.
links: list[str] = []
if M.get('repository_url'):
    links.append('- Repository: ' + M['repository_url'])
if M.get('release_url'):
    links.append('- Release: ' + M['release_url'])
if M.get('article_doi'):
    links.append('- Article DOI: https://doi.org/' + M['article_doi'])
llm = (
    f'# {title}\n\n'
    'Public code, results, and reproducibility repository for a manuscript on assessment-regime rank reversal in Generative AI evaluation.\n\n'
    '## Canonical scientific claims\n'
    + ''.join(f'- {x}\n' for x in M['canonical_claims'])
    + '\n## Key concepts\n'
    + ''.join(f'- {x}\n' for x in M['related_search_terms'])
    + '\n## Reusable object\n- ARRP (Assessment-Regime Reporting Profile): docs/ARRP.md and arrp.schema.json\n'
    + '\n## Citation\n'
    'The associated manuscript/article is the scientific citation target for the method and findings. '
    'Publication metadata are intentionally omitted until they exist. Direct software reuse should also '
    f'cite the software release and follow the {software_license} License.\n\n'
    '## Links\n'
    + ('\n'.join(links) if links else '- External canonical links pending actual repository/publication creation.')
    + '\n'
)
(ROOT / 'llms.txt').write_text(llm, encoding='utf-8')

# GitHub discovery surfaces generated from the same canonical source.
(ROOT / 'REPOSITORY_DESCRIPTION.txt').write_text(M['repository_description'].strip() + '\n', encoding='utf-8')
(ROOT / 'GITHUB_TOPICS.txt').write_text('\n'.join(M['github_topics']) + '\n', encoding='utf-8')

print('generated: CITATION.cff, CITATION.bib, CITATION.ris, codemeta.json, ARTICLE_METADATA.json, llms.txt, REPOSITORY_DESCRIPTION.txt, GITHUB_TOPICS.txt')
