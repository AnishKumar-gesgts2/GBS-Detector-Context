# Detector-context sampler: novelty audit

**External-review follow-up:** [[GBS External Novelty Review Synthesis]] consolidates two attached and one pasted assessment, verifies the earlier K2 predecessor, corrects citation mismatches, and rejects the unsupported transfer of Lee's correlation-decay guarantee to 50%–70% GBS photon loss. The complete GBS contribution remains potentially original; established ingredients do not disqualify it.

**Checked October 11, 2026. Verdict: established sampling principle; possible GBS-specific adaptation, with novelty unestablished.**

**Clarification after fact-checking:** established ingredients do not exclude a novel GBS algorithm or paper. The audit rules out claiming invention of generic Bayesian-network factorization, MI parent selection, or the local-conditional sampling principle. It does **not** establish that the complete GBS algorithm has already been published. A new GBS formulation, combination, application, or performance result can be a legitimate contribution without inventing a new probability theorem. Whether our present combination is sufficiently distinctive remains unresolved.

## Decision

We should **not describe the present prototype as a fundamentally new algorithm**. It is a bounded-parent Bayesian network supplied with exact Gaussian threshold marginals. Mutual-information parent selection and replacing a full conditioning history with a small selected history have substantial prior work. A close quantum-sampling predecessor explicitly uses local conditional factors and conditional-mutual-information error control.

I did not locate an exact duplicate of the complete GBS implementation: pair-information-ranked earlier detectors, exact threshold conditional tables from a specified lossy covariance, fixed-width compilation, and the particular comparison with Dodd/Goodman ports. This leaves **application-level novelty unresolved**. Absence of search hits does not establish priority.

The speed benefit in [[GBS Mechanism Smoke Benchmark]] remains a measured result of our implementation. A GBS methods contribution could emerge, but the present evidence supports an implementation and feasibility study of established graphical-model ideas.

## Construction audited

For threshold variables $X_1,\ldots,X_M$, the implementation fixes detector order and selects at most $b$ earlier detectors $S_i$ for each $i$. It computes the exact marginal of $S_i\cup\{i\}$ from the Gaussian subcovariance, divides by the parent marginal, and stores a conditional table. Fresh independent random numbers then generate records from

$$
Q(x)=\prod_{i=1}^{M}P(x_i\mid x_{S_i}).
$$

Parents are ranked by pair mutual information $I_P(X_i;X_j)$. The implementation does not optimize the joint information of parent sets, perform global graph search, or provide a scalable GBS error certificate. IID sampling from $Q$ does not imply equality with the target $P$.

For fixed order and parent sets, these exact target conditionals minimize $D_{\rm KL}(P\Vert Q)$ over that directed factorization: minimize each expected negative log conditional separately. This is the usual information projection, not a new GBS theorem. The resulting $Q$ need not preserve all selected joint marginals globally, because its induced parent distributions can differ from those under $P$.

## Closest inspected primary predecessors

| Predecessor | Verified overlap | Difference from this prototype |
| --- | --- | --- |
| [Friedman, Nachman, Pe'er, UAI 1999](https://arxiv.org/pdf/1301.6696), Sections 1 and 4, pp. 207 and 209–210 | Discusses greedy pair-MI parent selection, bounded candidate sets, redundancy failures, and conditional-MI refinement | Learns generic Bayesian networks from data rather than a GBS probability oracle |
| [Chow–Liu construction, checked in Bhattacharyya et al.](https://arxiv.org/html/2011.04144), Introduction/preliminaries | Mutual-information-weighted tree selection and conditional factorization are established | Our multiple-parent fixed-order heuristic is not the globally optimal one-parent Chow–Liu tree |
| [Lee et al.](https://arxiv.org/html/2510.06328), Section II, Proposition 1, Eq. 7 | Replaces full history by earlier neighboring regions in a product of target conditionals, with classical CMI error control | Geometric qubit circuits and correlation-decay assumptions; our contexts are information-ranked optical detectors |
| [Napp et al.](https://arxiv.org/html/2001.00021), Section 2.4 | Earlier CMI-based patching of small-region quantum-output distributions | Shallow local qudit circuits and recovery maps rather than our detector table chain |
| [Villalonga et al.](https://arxiv.org/html/2109.11525), Sections II.1–II.2, Appendix A | Uses tractable low-order GBS marginals to build approximate sampling models | Boltzmann/Gibbs or batch empirical greedy generation rather than fixed selected-parent conditionals |
| [Dodd et al.](https://arxiv.org/html/2511.14923), Section I.2, Appendices B–C | Precomputed correlations and approximate sequential marginal updates | Cumulant truncation over the history rather than limiting the conditioning parents |
| [Quesada, Arrazola, Killoran](https://arxiv.org/html/1807.01639), Eqs. 25–26 | Gaussian threshold probabilities through determinant sums | Supplies established probability machinery, not our approximate parent selection |
| [Quesada and Arrazola](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.2.023005), sampling algorithm | Exact marginal-based chain-rule GBS sampling | Conditions on the full past to retain exact sampling |
| [Kolarovszki et al.](https://arxiv.org/html/2603.11195), Section 4.1.3 | An empirical Chow–Liu Bayesian network is already used in GBS generative-model research | Fits external datasets, not exact marginals of a specified optical device |
| [Qi et al.](https://arxiv.org/html/2009.11824); [Oh et al.](https://arxiv.org/html/2110.01564) | Efficient optical sampling exploits bounded structural complexity | Banded matrices/treewidth, not an approximate detector-DAG factorization |

Friedman's original conference paper is **1999**; its arXiv upload is **2013**. The original [Chow and Liu paper](https://doi.org/10.1109/TIT.1968.1054142) dates to **1968**. Its publisher full text was inaccessible here; the construction and historical attribution were checked in the primary Bhattacharyya et al. paper. Lee's accessible preprint was initially posted in **2025** and its rendering carries an August 2026 manuscript date. All precede this prototype.

## Consequences for the novelty claim

**The strongest generic overlap is parent selection.** Friedman explicitly describes picking parents with high pair mutual information and explains why redundant variables can displace informative parents. Switching to conditional-MI selection would use an established refinement. Neither strategy is our generic invention.

**The strongest quantum overlap is the sampling factorization.** Lee's Proposition 1 already approximates a global output distribution by a product of local target conditionals. The exact mathematical form is close to ours. Their efficient-simulation conditions have not been established for dense complex-Haar GBS with fixed total photon loss. This leaves room for a GBS extension but prevents claiming invention of the local-conditional/CMI principle.

**The closest GBS approximations are materially different implementations.** Villalonga's generators try to reproduce low-order marginals; Dodd truncates cumulants. Our model restricts history while calculating the retained conditionals exactly. That distinction can produce a useful accuracy–cost tradeoff. It does not clear novelty merely because the methods are unequal.

Kolarovszki's Chow–Liu baseline is a related application, not evidence of an identical simulator. Likewise, optical bandwidth/treewidth methods exploit different structure. These distinctions should be preserved rather than declaring every related paper an exact duplicate.

## Which contributions could still be original?

| Claim | Current verdict | Evidence required |
| --- | --- | --- |
| New general bounded-context sampling principle | Established prior construction | Do not make this claim |
| First use of graphical models or MI with GBS | Broad claim unsafe | Existing GBS graphical-model work must be credited |
| This specific exact-marginal detector-DAG adaptation | Possibly original; unresolved | Wider implementation/prior-work checks and an explicit difference from standard DAG baselines |
| New GBS-specific parent selector | Not implemented | A distinctive selector with better measured error per total cost than pair-MI, conditional-MI, and ordering baselines |
| New physical accuracy guarantee | Not established | An affordable bound on omitted classical detector information, with a defined circuit family and precision regime |
| New context-width scaling result | Not established | Accuracy-controlled evidence or proof as modes, source count, brightness, and loss vary |
| Useful comparative implementation/result | Our measurements exist | Broader accuracy-controlled comparison and stronger vendor builds; usefulness does not itself establish methodological novelty |

Adaptive parent growth, selecting an order, caching tables, batching, and rewriting in C++ are insufficient standalone generic novelty claims. A specific GBS construction or result involving them could still justify a paper.

For our fixed-DAG construction,

$$
D_{\rm KL}(P\Vert Q)=\sum_i I_P\!\left(X_i;X_{<i}\setminus S_i\mid X_{S_i}\right).
$$

This is an entropy-chain-rule consequence, not a new theorem. The difficult opportunity is bounding or estimating these omitted terms cheaply for a physically meaningful GBS family. Low pair information alone does not bound higher-order synergy. The qubit-circuit CMI assumptions cannot simply be imported as a proven property of our optical model.

## Other smoke-benchmark mechanisms

[Werner and Wolf](https://arxiv.org/html/quant-ph/0009118), Proposition 1 and its proof, already characterize Gaussian separability through a covariance dominating a product covariance and construct a positive Gaussian mixture of displaced product states. Our exact real-interferometer product-core construction is a specialization of this established mechanism.

[Oh et al.](https://arxiv.org/html/2306.03709), Section III.1, already separate lossy GBS into a reduced pure quantum covariance and classical displacement noise. Retaining strong residual sources needs a distinctive representation, bound, or sampling implementation to support a new-method claim. Exact implementation duplicates for these two secondary mechanisms were not searched exhaustively in this detector-context-focused audit.

## Search scope and decision

### Fact-check: which papers originated which claims?

- **Friedman et al., UAI 1999:** a concrete sparse-candidate Bayesian-network learning algorithm and efficiency study, not merely a statement that the computation is possible. It neither addresses GBS nor determines originality of the entire optical sampler. [Original paper, Section 7](https://arxiv.org/pdf/1301.6696).
- **Lee et al., initially 2025:** classical simulation of noisy random **qubit** circuits under approximate-Markov/CMI conditions. Proposition 1 supplies a close local-conditional construction; it does not originate the GBS framework or its experimental quantum-advantage claim. [Paper, Sections II–III](https://arxiv.org/html/2510.06328).
- **Villalonga et al., 2021:** approximate classical GBS generators evaluated against existing experiments. It is a challenge to earlier experimental claims, not their origin. [Paper, Introduction and Section II](https://arxiv.org/html/2109.11525).
- **Historical distinction:** the boson-sampling complexity proposal is associated with [Aaronson and Arkhipov, STOC 2011](https://dspace.mit.edu/entities/publication/d7c8ab3d-9bb1-4ab5-9b48-e84494b52f9f); the Gaussian squeezed-input framework is developed in [Hamilton et al., 2016 preprint / 2017 publication](https://arxiv.org/abs/1612.01199); the original Jiuzhang experimental claim appears in [Zhong et al., 2020](https://arxiv.org/abs/2012.01625). A theoretical hardness argument, an experimental advantage claim, and a subsequent classical challenge are different contributions.

**Revised interpretation:** assess originality of the complete GBS construction and result. Existing statistical tools set the attribution and comparison requirements; they do not automatically disqualify the method. The search establishes close predecessors but does not establish an exact previously published GBS implementation. Novelty remains possible and unresolved.

Targeted searches combined GBS/boson sampling with Bayesian networks, Chow–Liu, graphical models, autoregressive sampling, local marginals, selected subsets, conditional independence, finite memory, limited history, conditional tables, conditional mutual information, Markov approximation, and truncated conditioning. Accessible 2026 primary work was included. Secondary summaries helped locate papers; conclusions rely on the inspected primary texts and current local code.

The original Chow–Liu publisher page and an old arXiv HTML rendering were inaccessible; alternate primary papers/PDFs supplied the needed construction evidence. This is an academic prior-work audit, not exhaustive coverage of every code repository, thesis, patent, or unpublished project. No researcher was contacted. No numerical probability of novelty is assigned.

**Defensible description now:** an exact-marginal bounded-parent graphical surrogate for lossy threshold GBS, with measured small-system accuracy–cost tradeoffs.

**Development decision:** retain the functional prototype, but make a distinctive GBS selector, physical guarantee, or broader performance result the contribution target. Do not premise the grant or paper on having already invented a new general sampling principle.
