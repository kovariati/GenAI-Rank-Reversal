# Citation and discovery metadata

`PROJECT_METADATA.json` is the canonical source for identity-bearing metadata. The publication record is synchronized to:

**Kovari, A. (2026). _Generative AI, Performance, and Learning: A Framework for Comparing Interventions Across Assessment Regimes_. Computers, 15(9), 633.** https://doi.org/10.3390/computers15090633

Run `python tools/generate_metadata_files.py` after any intentional identity/metadata update. The generator produces:

- `CITATION.cff`
- `CITATION.bib`
- `CITATION.ris`
- `codemeta.json`
- `ARTICLE_METADATA.json`
- `llms.txt`
- `REPOSITORY_DESCRIPTION.txt`
- `GITHUB_TOPICS.txt`

Then run `python tools/validate_repository.py` to verify semantic and byte-level cross-file consistency.

`llms.txt` is supplementary machine-readable context only. It is not claimed to guarantee search-engine ranking, LLM retrieval, or citations.
