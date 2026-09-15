# ARRP — Assessment-Regime Reporting Profile

**ARRP is an author-proposed, executable outcome-level reporting template derived from the assessment-regime identification problem. It is pending independent human evaluation and is not a validated measurement instrument or consensus reporting standard.**

Use ARRP when a scored outcome in human–AI research may differ in whether AI is available, when it is measured, how much the task overlaps supported work, how much transfer is required, or how non-use of AI is established.

## Five reporting dimensions

| Code | Dimension | Core question | Canonical values |
|---|---|---|---|
| **A** | AI availability at assessment | Could construct-relevant AI contribute to the scored response? | `available`, `removed`, `restricted`, `unclear` |
| **D** | Assessment delay | When was the outcome measured relative to the last relevant assisted exposure? | `concurrent`, `immediate`, exact elapsed time, `unclear` |
| **O** | Task/item overlap | How much did the assessed material overlap supported work? | `same`, `repeated`, `similar`, `novel`, `unclear` |
| **G** | Generalization/transfer demand | How far did the assessment generalize beyond supported work? | `none`, `near`, `far`, `domain-context-shift`, `unclear` |
| **N** | Evidence and scope of AI non-use | How was intended non-use/restriction established and scoped? | `prevented`, `monitored`, `verified`, `self-report`, `unclear` |

Full decision rules and source-evidence requirements are in [`results/arrp_coding_protocol.csv`](../results/arrp_coding_protocol.csv). The machine-readable schema is [`arrp.schema.json`](../arrp.schema.json).

## Construct-commensurability prerequisite

ARRP fields span different structural roles and do **not** constitute a causal treatment vector. AI availability and delay describe elicitation/timing conditions; overlap and transfer demand describe relations between prior supported work and the assessment task; evidence of AI non-use is reporting/verification metadata. Target construct and task/form/content must be recorded separately. ARRP fields do **not** by themselves make two outcomes comparable. A cross-regime rank comparison is substantively interpretable only when the outcomes have a defensible construct link and a common directional interpretation. Otherwise the pair should be classified as non-commensurable or unclear rather than rank-preserved/rank-reversed. See [`results/construct_commensurability_audit.csv`](../results/construct_commensurability_audit.csv).

## Worked example

[`examples/arrp_example_wong_task2.json`](../examples/arrp_example_wong_task2.json) concerns the vocabulary-game product's originality score. It records source-reported Task 2 ChatGPT removal and protocol prevention, not independent verification; exact delay and near/far transfer distance are not manufactured. Task scoring does not establish a common latent creativity construct.

## Use ARRP when…

- designing studies that compare AI-assisted and independent human outcomes;
- extracting outcome-level conditions for systematic review or meta-analysis;
- documenting whether a post-assistance score supports performance, retention, or transfer claims;
- auditing whether apparently similar Generative AI outcomes target the same estimand;
- building machine-readable evidence maps of human–AI assessment conditions.

## Reusable files

- [`arrp.schema.json`](../arrp.schema.json) — JSON Schema for one outcome-level ARRP record;
- [`results/arrp_coding_protocol.csv`](../results/arrp_coding_protocol.csv) — decision rules and source-evidence requirements;
- [`results/arrp_core_reporting_fields.csv`](../results/arrp_core_reporting_fields.csv) — compact five-field reporting profile;
- [`results/arrp_dimension_rationale.csv`](../results/arrp_dimension_rationale.csv) — inferential role and non-redundancy rationale;
- [`results/arrp_worked_outcome_examples.csv`](../results/arrp_worked_outcome_examples.csv) — traceable applicability examples;
- [`code/validate_arrp_specification.py`](../code/validate_arrp_specification.py) — deterministic specification audit;
- [`code/validate_arrp_operational_rules.py`](../code/validate_arrp_operational_rules.py) — executable rule checks.

## Validation boundary

The public package verifies structured feature behavior, metamorphic behavior, traceability, and implementation/specification conformance. It does **not** report human inter-rater reliability, external expert content validity, psychometric validity, or consensus-standard status.

## Validate locally

```bash
python tools/validate_arrp_schema.py
python code/validate_arrp_operational_rules.py
python code/validate_arrp_specification.py
```

## How to cite ARRP

If the ARRP concepts, decision rules, or scientific interpretation contribute to your work, cite the associated manuscript/article using [`CITATION.cff`](../CITATION.cff), [`CITATION.bib`](../CITATION.bib), or [`CITATION.ris`](../CITATION.ris). If you directly reuse or modify the executable schema/code, also cite the software release and follow the code/data license guidance.

Full Draft 2020-12 instance validation now covers required and additional fields, types, nonblank evidence, and conditional exact-delay fields. The actual rank-classification pipeline separately enforces comparison eligibility. These are computational checks, not validation of author coding.
