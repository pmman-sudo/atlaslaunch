# Recorded evidence — 11 October 2026

Source: the owner's downloaded workbench report, supplied during development. The JSON is retained unchanged at [evidence/2026-10-11-owner-smoke-test.json](evidence/2026-10-11-owner-smoke-test.json). It contains five live rows, no recorded request errors, empty human-score fields, and explicitly labelled preliminary AI review notes. No access key is included.

| Request | Latency |
| --- | ---: |
| English playground | 4,382 ms |
| English suite | 42,013 ms |
| Yoruba suite | 5,562 ms |
| Hausa suite | 5,710 ms |
| Igbo suite | 6,006 ms |

Median across all five rows: **5,710 ms**. All four suite outputs contain two sentences, but several are long or repetitive. Each language has just one suite example about solar panels. The longer English request cannot be conclusively attributed to cold start from this report alone.

The preliminary review notes identify circular/repeated Yoruba wording, repetition in Hausa, a grid-connection generalization in Igbo, and imprecise wording in the English playground output. Fluent-speaker evaluation is pending. The owner entered AI-suggested notes; these are not external developer feedback or human quality scores.

## Supported claims

- The owner demonstrated the hosted workbench and Modal endpoint working together.
- Five recorded requests completed, with timings and raw responses preserved.
- The workflow supports reviewing and exporting model weaknesses.

## Claims not established

- General multilingual accuracy or a validated benchmark score.
- Production uptime, throughput, or a latency guarantee.
- Independently verified model identity.
- External developer adoption or productivity improvement.
- Broad user validation: **zero external tester reports collected so far**.

The repository also includes mock-based software tests. Passing them verifies software behavior, not the quality of model-generated content.
