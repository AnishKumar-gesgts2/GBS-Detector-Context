# Classical GBS Algorithm Development

We are developing a classical threshold Gaussian boson sampling (GBS) algorithm that compiles exact small-subset probabilities into a bounded-parent detector model. The goal is to improve the accuracy–cost tradeoff of classical sampling and, eventually, assess a specific experimental quantum-advantage claim under its stated conditions.

The current implementation is a **smoke prototype**. It shows a useful small-system, many-record tradeoff; it has not disproved quantum advantage or established accurate large-system sampling.

| Document | Purpose |
| --- | --- |
| [Project Description](Project%20Description.md) | Objective, mechanism, physical assumptions, and development priorities |
| [Proposal](Proposal.md) | Research proposal, milestones, comparisons, and decision criteria |
| [Code Description](Code%20Description.md) | How the code works, installation, and reproduction instructions |
| [Results](Results.md) | Measured accuracy, runtime, limitations, and experimental relevance |
| [Sources](Sources.md) | Background talk, foundational papers, competing methods, and implementation sources |
| [Novelty](Novelty.md) | Established ingredients and the potentially original GBS contribution |

[Simulation source](src/) and [saved benchmark data](results/smoke_v1/) are included. Start with `src/sample_context.py`; the candidate runs independently of the vendor comparison build. Personal grant-answer drafts are kept locally and excluded from Git.
