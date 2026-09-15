# Publication-day metadata and release update

During peer review, the canonical live object is the public GitHub repository root. The `v1.0.0` release does **not** yet exist and must not be cited as live. Do not edit CFF, BibTeX, RIS, CodeMeta, JSON-LD, or `llms.txt` independently.

When the journal article gets a definitive bibliographic record:

1. Enter the actual `journal`, `article_doi`, and `publisher_url` in `PROJECT_METADATA.json`.
2. Freeze the audited article-associated source state with a fixed `v1.0.0` Git tag.
3. Create the GitHub Release and upload `GenAI-Rank-Reversal-v1.0.0-results-and-artifacts.zip`.
4. Set the actual `release_url` and `release_date` in `PROJECT_METADATA.json`.
5. Run `python tools/generate_metadata_files.py` and `python tools/validate_repository.py`.
6. Confirm all generated citation/discovery metadata.
7. Set the GitHub Website field to the final DOI or publisher landing page as appropriate.

Never insert placeholder publication identifiers. After release, do not silently replace scientific assets; changes require a new version and an updated change log.
