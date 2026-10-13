# Final artifact and repository audit

Checked October 12, 2026. This is a readiness audit of the published proposal, prototype, and saved evidence. It is not a new competitive benchmark or a guarantee of large-system fidelity.

## Corrections

- Removed a vault-index link to an already deleted decoder concept.
- Clarified that the PDF validation record concerns the public artifact; live application status belongs in the ignored local record.
- Corrected the record-generation cost to $O(M(b+1))$, including zero-parent contexts, and corrected “fifth-order Dodd” wording.

## Proposal artifact

The [PDF](GBS_Algorithm_Proposal.pdf) remains the previously rendered and visually inspected artifact: **four pages including references, 234,909 bytes**. Its SHA-256 is `a9e9d348b937d929fd257d1bcfb9bf515a47ebeadc1b30df945b1313354457dc`. The current source and PDF hashes match [Submission_Validation.json](Submission_Validation.json). All 14 fonts are embedded; the PDF is unencrypted and contains no JavaScript.

The live optional upload section specifies one PDF, at most four pages and 10 MB. The artifact satisfies those limits. Publishing a PDF or this audit does not submit an application.

## Repeated correctness checks

| Check | Result |
| --- | --- |
| Recompute six-parent induced-law TVD on all 39 saved fixtures | Maximum difference from recorded values: **0** |
| Ten-mode full-history control | TVD **$1.0721\times10^{-16}$** against the exact reference |
| Vacuum control | All 10,000 records contain no clicks |
| Zero-parent control | Nonnegative normalized induced distribution |
| Portable CLI in the minimal dependency environment | 10,000 valid records; saved bits and packed records agree; TVD matches the saved fixture |
| Recompute aggregate analysis from a separate copy of saved data | Identical summary JSON |
| Existing physics and original-author Dodd sampler checks | Passed, including independent probability/cumulant and sampling controls |
| Saved main comparison | All **429 completed rows / 39 circuits** retained |
| Public local links and snapshot hashes | Passed after corrections |
| Private grant answers and temporary files | Ignored and absent from the tracked tree |

No algorithm source or benchmark measurements were changed by this audit. Fresh QA outputs, application answers, and screenshots remain in ignored local storage.

## Evidence limits

The scientific qualifications in [Results](../Results.md), [Code Description](../Code%20Description.md), and [Novelty](../Novelty.md) still apply. These checks establish artifact integrity and reproducibility of existing small-system controls. They do not establish novelty, accurate fixed-width sampling at large mode counts, superiority to every published implementation, or a quantum-advantage disproof.
