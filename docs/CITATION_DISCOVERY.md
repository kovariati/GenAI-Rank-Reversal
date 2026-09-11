# Citation and discovery policy

The repository is designed as a scholarly landing page, citation funnel and reproducibility object. Discovery metadata are redundant across CFF, BibTeX, RIS, CodeMeta, JSON-LD and `llms.txt`, but `PROJECT_METADATA.json` is the single authoring source. The GitHub About description and topic list are generated from the same source and checked semantically across surfaces.

Before publication, machine-readable metadata identify the article as a manuscript and do not invent a journal, DOI or publisher URL. After publication, update `PROJECT_METADATA.json` once and run `python tools/generate_metadata_files.py`; then audit all metadata with `python tools/validate_repository.py`.

`llms.txt` is supplementary machine-readable context only. It is not claimed to guarantee search-engine ranking, LLM retrieval or citations.

ARRP is exposed as a reusable research object through `docs/ARRP.md`, `arrp.schema.json`, a worked machine-readable example and executable validators. This creates a separate reuse path without claiming that ARRP is an externally validated standard.
