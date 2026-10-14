# Final artifact and repository audit

Scientific readiness checks performed October 12, 2026; repository-link and PDF artifact checks updated October 13, 2026. This is a readiness audit of the published proposal, prototype, and saved evidence. It is not a new competitive benchmark or a guarantee of large-system fidelity.

## Corrections

- Removed a vault-index link to an already deleted decoder concept.
- Clarified that the PDF validation record concerns the public artifact; live application status belongs in the ignored local record.
- Corrected the record-generation cost to $O(M(b+1))$, including zero-parent contexts, and corrected “fifth-order Dodd” wording.

## Proposal artifact

The [PDF](GBS_Algorithm_Proposal.pdf) was rebuilt on October 13, 2026 to use the canonical `GBS-Detector-Context` repository URL while retaining the immutable evidence snapshot. It has **four pages including references, 234,913 bytes**. Its SHA-256 is `e0a3a7086fdaa52229d28a7b734dc6b3d7692978852ec25e5c8749b8926f522f`. Extracted text and character positions are unchanged from the October 12 artifact; all four rebuilt pages were rendered and visually inspected. The current source and PDF hashes match [Submission_Validation.json](Submission_Validation.json). All 14 fonts are embedded; the PDF is unencrypted and contains no JavaScript.

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
