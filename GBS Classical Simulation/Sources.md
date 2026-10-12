# Sources

**Reading map for classical GBS algorithm development. Updated October 12, 2026.** Entries identify why a source matters; inclusion does not imply that its implementation was run or its conclusions were reproduced. The comparator status is recorded in [Results](Results.md).

## Background talk

- [Background presentation watched for this project](https://www.youtube.com/watch?v=bHwmuqJxAS8). The Gaussian-state, loss, and classical-approximation background motivated the project. Preserve this user-supplied video link as the original reference.
- [Changhun Oh's Simons Institute slides, May 2024](https://simons.berkeley.edu/sites/default/files/2024-05/QCF24-3%20Slides%20-%20Changhun%20Oh_0.pdf). Companion background on Gaussian covariance, loss, and classical simulation. The discussion of noisy qubit outputs approaching a maximally mixed state is different from the optical loss model; it does not establish that our detector-context assumption holds.

## Main competing approaches

| Source | Mechanism and relevance | Use in this project |
| --- | --- | --- |
| Changhun Oh et al., [Classical algorithm for simulating experimental Gaussian boson sampling](https://arxiv.org/abs/2306.03709) (2023 preprint) | Exploits photon loss through a decomposition into residual quantum resources and classical displacement, with tensor-network simulation | Physical motivation and an important future comparator. Our low-rank source prototype is not a reproduction of their tensor-network sampler |
| Tom Dodd et al., [A fast and frugal Gaussian Boson Sampling emulator](https://arxiv.org/abs/2511.14923) (2025) | Efficient sampling using truncated connected-correlation/cumulant information | Actual pinned author CPU generator at orders 3 and 5 was measured; the strongest implemented dense-circuit accuracy control |
| Ned Goodman et al., [Gaussian boson sampling: Benchmarking quantum advantage](https://arxiv.org/abs/2604.12330) (2026) | Phase-space construction, threshold projection, and moment correction for approximate sampling and experimental comparisons | Transparent Python equation ports were measured, including frozen and batch variants. Production MATLAB performance was not measured |
| Benjamin Villalonga et al., [Efficient approximation of experimental Gaussian boson sampling](https://arxiv.org/abs/2109.11525) (2021; revised 2022) | Efficiently computed small marginals; Boltzmann/mean-field and greedy sampling constructions | Close GBS predecessor. Both their Gibbs and greedy generators should be included in the next comparison; this is not solely an MCMC paper |

## Gaussian physics and exact probabilities

- Craig S. Hamilton et al., [Gaussian Boson Sampling](https://arxiv.org/abs/1612.01199), *Physical Review Letters* 119, 170501 (2017). Foundational squeezed-state GBS formulation and hafnian photon-pattern probabilities. Photon-number outcomes and threshold-click outcomes are different tasks.
- Nicolás Quesada, Juan Miguel Arrazola, and Nathan Killoran, [Gaussian Boson Sampling using threshold detectors](https://arxiv.org/abs/1807.01639), *Physical Review A* 98, 062322 (2018). Torontonian probabilities and exact sampling for threshold detection; essential to the detector model and independent reference.
- Nicolás Quesada and Juan Miguel Arrazola, [Exact simulation of Gaussian boson sampling in polynomial space](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.2.023005), *Physical Review Research* 2, 023005 (2020). Exact sequential sampling and its cost. Chain-rule sampling itself is established.
- R. F. Werner and M. M. Wolf, [Bound entangled Gaussian states](https://arxiv.org/abs/quant-ph/0009118) (2000 preprint; 2001 publication). Covariance-based Gaussian separability. Product quantum cores plus correlated classical displacement are established physics, relevant to the restricted structured-family sampler.

## Graphical models, information, and structural simulation

- Gregory F. Cooper and Edward Herskovits, [A Bayesian Method for the Induction of Probabilistic Networks from Data](https://link.springer.com/content/pdf/10.1023/A:1022649401552.pdf) (1992), especially K2 on p. 322. Ordered bounded-parent Bayesian networks are a generic predecessor; their score and data source differ from our Gaussian oracle.
- Nir Friedman, Iftach Nachman, and Dana Pe'er, [Learning Bayesian Network Structure from Massive Datasets: The “Sparse Candidate” Algorithm](https://arxiv.org/abs/1301.6696), UAI 1999; archived on arXiv in 2013. Candidate-parent restriction and iterative graph learning. The current top-pair-MI rule is simpler than their complete algorithm.
- [Lee et al., Classical simulation of noisy random circuits from exponential decay of correlation](https://arxiv.org/abs/2510.06328) (2025). Relevant local-conditional sampling and output-information framework. Its noisy-qubit circuit assumptions do not certify bounded contexts for arbitrary GBS circuits at 50%–70% total loss.
- [Efficient sampling from shallow Gaussian quantum-optical circuits with local interactions](https://arxiv.org/abs/2009.11824) (2020). Structural tractability of shallow optical circuits; useful when distinguishing a new regime from already easy circuit families.
- [Classical simulation of boson sampling based on graph structure](https://arxiv.org/abs/2110.01564) (2021). Graph structure as a computational resource. An optical interaction graph, a Gaussian matrix graph, and our selected detector-dependence graph need not coincide.

The exact-marginal Chow–Liu maximum-spanning-tree model is a necessary generic control. Our fixed-order one-parent selector is not guaranteed to produce that optimal tree. [Novelty](Novelty.md) records this distinction and the remaining priority uncertainty.

## Experimental claims and eventual target

- Han-Sen Zhong et al., [Quantum computational advantage using photons](https://arxiv.org/abs/2012.01625) (2020). Original Jiuzhang experimental claim; relevant historical context rather than a result of this project.
- [Gaussian boson sampling with 1,024 squeezed states in 8,176 modes](https://www.nature.com/articles/s41586-026-10523-6), *Nature* (2026). Jiuzhang 4.0 is a concrete motivating large-scale claim. Applying our sampler requires the actual circuit/detector model and the experiment's acceptance criteria; the current 6–10 mode synthetic tests do not reproduce this configuration.

## Implementation provenance

| Resource | Pinned revision / status |
| --- | --- |
| [FrugalGBS author repository](https://github.com/tomdodd4598/FrugalGBS) | `fa8b796f2afebd4845a2e335e457735952617ef8`; original CPU generator executed |
| [xqsim](https://github.com/peterddrummond/xqsim) | `32609f3644ae18bff872b53a32a3a7f58f883b3b`; inspected, not executed as the Goodman comparator |
| [Eigen](https://github.com/PX4/eigen) | `e7248b26a1ed53fa030c5c459f7ea095dfd276ac`; benchmark build dependency |
| [xsimd](https://github.com/xtensor-stack/xsimd) | `b8df57b3865cbf38576a9c7099180f9bf1efcf73`; benchmark build dependency |

See [the measured environment](results/smoke_v1/environment.json), [execution notes](results/smoke_v1/execution_notes.json), and [packaging provenance](results/smoke_v1/packaging.json). Vendor source and compiled binaries are outside the vault; our simulation source and bridge are in [src](src/).
