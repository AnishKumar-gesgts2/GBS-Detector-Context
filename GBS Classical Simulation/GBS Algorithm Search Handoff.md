# GBS algorithm search: handoff for independent evaluation

**Prepared:** October 11, 2026. **Purpose:** ask another researcher or assistant to critically evaluate our current algorithm ideas, give feedback, and then propose additional approaches to classical Gaussian boson sampling (GBS). This document is a research brief, not a claim that a new competitive sampler exists.

**Follow-up:** Four supplied responses are consolidated and evaluated in [[GBS Algorithm Review Synthesis]], including a new conditional-cumulant diagnostic and revised development priorities.

## Assignment for the recipient

We are searching for a physically motivated computational mechanism that could produce a genuinely useful classical GBS sampling algorithm. First evaluate the existing ideas below, including reasons to reject them. Then conduct your own literature search and propose alternatives. You may overturn our rankings or recommend abandoning every current candidate. Prioritize a plausible mechanism for reducing computation at a specified accuracy over a broad list of fashionable methods.

We want an original contribution with a concrete niche: a circuit family, source spectrum, loss/brightness regime, detector task, or conditional sampling problem where the mechanism offers a meaningful benefit. General simulation of arbitrary dense optical circuits would have broad impact, but a narrower, well-supported advance is preferable to an unsupported universal claim.

The user wants algorithm development to be the immediate intellectual focus. Independent reproduction and stress testing of published methods remain in the grant proposal and provide the evaluation framework. Do not equate a classical improvement with disproving quantum advantage: that requires a comparison against a particular experimental claim, target distribution, accuracy requirement, and resource budget.

## Target and practical constraints

- **Primary output:** complete threshold-detector records for a specified squeezed-input linear optical circuit. For $M$ modes, a record is a binary string in $\{0,1\}^M$. The target is its circuit-specific probability distribution.
- **Primary model:** squeezed vacuum inputs, a fixed interferometer, ideal threshold detectors, and photon loss as the only modeled noise. Sweep **50%–70% total photon loss**, corresponding to intensity transmission $\eta=0.3$–$0.5$. Loss alone does not imply that a classical or thermal approximation is accurate enough.
- **Circuit controls:** complex Haar-random interferometers, heterogeneous and flat squeezing spectra, and structured circuits when testing a specialized mechanism. An average over random interferometers does not reproduce the distribution of a particular interferometer.
- **Separate tasks:** photon-number-resolving sampling, fixed-click conditional sampling, probability estimation, calibration, and graph optimization are useful possible niches, but label them explicitly. Success at one does not establish success at the primary task.
- **Resources:** local CPU work first; existing pilots used an AMD Ryzen 9 7950X with about 31 GiB installed memory and NumPy/SciPy. Exact small-system references are available. The user has authorized small or medium research tests; no cluster or photonic hardware is assumed.
- **Evaluation:** complete distribution comparisons at small scale; held-out circuits and multiple seeds; total setup and sampling cost, peak memory, numerical stability, and failed cases. Later hardware reproduction must use the experiment's calibrated model, including its specified imperfections.

**Main criterion:** lower total computation at the same required sampling accuracy, or materially better accuracy under the same resource budget. An improvement in a local error metric, an entropy proxy, or a probability kernel is insufficient by itself.

## Read these project materials first

1. [GBS Algorithm Opportunities and Validation](GBS%20Algorithm%20Opportunities%20and%20Validation.md): detailed literature survey, twelve candidates, exploratory results, limitations, and source register.
2. [GBS Classical Simulation Project Description](GBS%20Classical%20Simulation%20Project%20Description.md): scope, grant-facing reproduction plan, and earlier studies.
3. [Skeptical Audit and Stronger Benchmarks](Skeptical%20Audit%20and%20Stronger%20Benchmarks.md): why the earlier enumerated correlation-correction implementation was rejected as a computational improvement.
4. [Pilot summary](outputs/algorithm_screen_v1/summary.json), [environment](outputs/algorithm_screen_v1/environment.json), and [artifact manifest](outputs/algorithm_screen_v1/artifact_manifest.json). The detailed report links the scripts and other raw results.

**Conversation update that supersedes the earlier ranking:** the detailed report still calls adaptive non-Gaussian retention the leading hypothesis. Following the user's computational-cost objection, treat it as a **conditional candidate without preferred status**. We have not measured an end-to-end advantage. No current idea is established as the best proposal direction.

## Current ideas and evidence

### A. Adaptive retention of detection-induced non-Gaussian information

**Mechanism proposed:** use inexpensive Gaussian updates for ordinary histories; after selected photon-conditioning events, retain a low-degree polynomial multiplying a Gaussian state rather than immediately replacing the conditional state with a moment-matched Gaussian. Gaussian states admit compact mean/covariance descriptions; conditioned non-Gaussian states generally need additional information.

**Narrow evidence:** in a two-mode diagnostic, after subtraction in one mode and subsequent diagnostic attenuation of the other, its conditional click probability was about 0.5072 in the reference and 0.3397 after a Gaussian reset. The discrepancy diminished with a large classical displacement. In a separate initial one-mode ensemble, a heuristic trigger selected about 8% or 23% of initial detections at transmission 0.3 or 0.5 while removing roughly 70% or 81% of rate-weighted local reset discrepancy. These are local tests, not complete sampling trajectories or final-distribution improvements.

**Central objection:** solving and carrying non-Gaussian conditional information can cost far more than the Gaussian approximation. Successive retained events can increase representation complexity and the cost of subsequent updates. A large local correction could yield only a small final-distribution benefit. The initial trigger fractions do not establish that expensive events remain rare throughout a trajectory.

**Evaluate:** Is a bounded-degree representation practical? Can an inexpensive indicator predict final sampling error per unit of added cost? When does approximation error accumulate versus wash out? Is there a regime where this beats both Gaussian resets and an existing detailed simulator at matched accuracy? Reject or downgrade the idea if its cost grows before a useful final-distribution improvement appears.

**Overlap:** photon trajectories, covariance resets, photon subtraction, and stellar-rank representations already exist. The potentially original part would be a justified selective-retention rule, controlled representation growth, and a measured sampling benefit.

### B. Certified compression of the residual quantum source spectrum

**Mechanism:** decompose the lossy Gaussian state into a pure quantum component plus classical displacement noise. Replace sufficiently weak residual squeezed sources with vacuum while keeping the displacement channel; use a fidelity-derived bound to budget the resulting measurement error. Sample the smaller retained quantum component correctly.

**Evidence:** 36 synthetic 6-/8-/10-mode circuits and six retention ranks per circuit were compared using full distributions. For an intentionally heterogeneous spectrum with two strong sources, retaining those two gave TVD about 0.0033–0.0151. Flat-spectrum controls were worse, about 0.0409–0.1229. The certificate held in the tested cases. No end-to-end runtime improvement was measured.

**Evaluate:** Does a relevant physical spectrum support compression? Does retained source count actually control the chosen sampler's cost? Can compression and sampling be integrated into a distinctive implementation? Conditional rare-event errors need separate analysis; an unconditional guarantee may deteriorate after conditioning. Do not infer a small quantum core from loss alone or move arbitrary output-dependent loss to the inputs without justification.

**Overlap:** loss-based decomposition, low-rank hafnians, active-sector compression, and classicalization bounds substantially predate this proposal.

### C. Choose quantum/classical decompositions for actual sampling cost

**Mechanism:** optimize a feasible covariance decomposition $V=P+W$ with pure physical $P$ and positive semidefinite classical noise $W$, using the simulator's actual cost rather than minimum quantum photon number alone. Candidate objectives include cut entanglement, photon cutoffs, mode ordering, and preparation/sampling costs.

**Evidence:** on structured real-orthogonal circuits, a feasible product quantum component had zero cut entanglement while using about 30%–35% more quantum photons than the smaller-photon decomposition. The same construction failed on six complex-Haar controls. This establishes a proxy distinction, not an MPS runtime benefit.

**Evaluate:** Can decomposition optimization save more time than it consumes? Is there a scalable solver and a measurable advantage beyond existing Gaussian entanglement-of-formation and GBS decomposition work? Test complete sampling, not entropy alone.

### D. Stochastic correction and allocation of computation

**MCMC:** propose records from a cheap distribution and use acceptance/rejection to correct toward the target. Existing GBS Metropolis independence sampling is direct prior art. Target/proposal probability evaluation, convergence, and autocorrelation can erase the benefit. A proposal generator is not automatically a tractable proposal-probability oracle. Approximate acceptance probabilities generally change the stationary distribution.

**Sequential Monte Carlo / importance sampling:** maintain weighted histories and allocate particles toward important or difficult branches. This could complement selective retention or target rare high-click sectors. We have not implemented this extension. Correct weights must be computable; particle depletion and weight variance matter. Resampling cannot recover quantum information discarded by an uncontrolled approximation. A pseudo-marginal route would require suitable nonnegative unbiased likelihood estimates and variance control; a complex phase-space estimator alone is insufficient.

**Evaluate:** What exact quantity is sampled, how are weights computed, and what removes the main bottleneck? Does the method yield unweighted detector records, weighted observable estimates, or only a conditional distribution? Can it improve effective independent samples per second rather than raw update speed?

**Terminology:** quantum Monte Carlo is a family of stochastic quantum simulation methods; quasi-Monte Carlo uses structured numerical integration points. Neither name identifies a new GBS mechanism. Stochastic optimization could help choose a decomposition or approximation policy, but that is an optimization component, not automatically a faithful sampler.

### E. Other candidates to assess

| Candidate | Potential benefit | Present evidence or obstacle |
| --- | --- | --- |
| Source-rank exact marginal engine | Reduce repeated determinant queries to the smaller source or subsystem dimension. | Accurate local kernels; 19–96 times faster on some large-subsystem queries versus the tested dense implementation, slower on an unfavorable small-subsystem query. Existing identity and prior reduction; no complete sampler win. |
| Stable sparse next-click sampling | Skip long runs of no-click detectors using block vacuum probabilities. | Eight-mode checks passed and a 32-mode pilot was faster than a same-oracle modewise baseline. Rare-history cancellation caused failures at 128/256 modes. Still exponential in accumulated clicks. |
| Compressed higher-order cumulants | Avoid storing every detector group while preserving important dependencies. | Need cheap on-demand evaluation, valid nonnegative sequential probabilities, and a sampling architecture without exhaustive normalization. Earlier enumerated selective correction lost to stronger baselines. |
| Weak-link quantum clusters | Restrict expensive calculations to small interacting clusters. | Favorable local-circuit controls; substantial errors on Haar controls. Treewidth and limited-connectivity prior art. |
| Detector-adapted phase-space variance reduction | Reduce unstable weights for threshold or grouped-count observables. | Matrix-P and symmetry methods already exist. No new working estimator or record sampler established here. |
| Randomized quasi-Monte Carlo | Improve smooth phase-space integrals or calibration mixtures. | Sobol pilots beat IID integration, but the tested vacuum quantities have cheaper deterministic formulas. Needs a real niche; points are not IID detector shots. |
| Direct high-click-sector sampling | Avoid discarding most samples when studying rare sectors. | Correct tilting, normalization, effective sample size, and threshold/loss handling unresolved. Fixed photon number and fixed click number differ. |
| Controlled corrections around a classical reference | Tune accuracy while keeping most work classical. | Existing Taylor-expansion approaches overlap; convergence, positivity, and cheap normalized sampling remain central. |
| Limited non-Gaussian resources for heralded-state simulation | Parameterize cost by a small non-Gaussian resource. | Possible broader photonic-computing niche; substantial resource-theory prior art and outside the current primary target. |

## Feedback and new ideas requested

Please deliver your response in this order:

1. **Audit the premise.** Identify errors, unsupported assumptions, omitted baselines, or misleading interpretations in this brief and the existing report. State what you verified directly.
2. **Evaluate each current candidate.** Describe its actual speed mechanism, necessary assumptions, dominant cost, likely failure regime, prior overlap, and smallest decisive test. Give a keep/revise/reject decision with reasons.
3. **Propose your own approaches.** Add several materially distinct ideas. Start from physical or mathematical structure that removes work: an exact identity, a controlled approximation, a favorable scaling property, or a better representation. Explain the niche and why the mechanism could improve on the appropriate alternative. Explore outside our present shortlist.
4. **Check novelty against primary literature.** Include recent papers, supplements, and relevant code. Distinguish established ingredients from the specific proposed contribution. Cite direct sources and dates. No search hit is not proof of novelty; do not speculate about researchers' unpublished plans.
5. **Rank only after the critique.** Use separate judgments for potential impact, evidence, feasibility, novelty confidence, and end-to-end cost. Scores are not probabilities of success. Explain which unknown could reverse each ranking.
6. **Recommend a concrete next experiment.** State the inputs, reference distribution, competitors, accuracy metric, timing/memory accounting, unfavorable controls, and a stop/go criterion. Prefer a low-cost experiment capable of killing a bad idea quickly. Separate proposed tests from completed results.

If you recommend an estimator, optimization tool, or specialized conditional sampler instead of a general sampler, explain why that narrower contribution is still valuable. If no current candidate has a credible computational advantage, say so and propose the most informative next search or experiment.

## Evaluation safeguards

- Compare algorithms on the same target model and detector task. Count preprocessing, tuning, state preparation, sampling, and conversion to requested outputs.
- Freeze selection rules before held-out evaluation. Use exact small distributions for scoring, not to select the retained information on held-out circuits.
- Compare against strong exact and approximate baselines; a naive implementation is not sufficient evidence of superiority.
- Report TVD's finite-sample uncertainty. Selected moments or validation scores do not establish full-distribution fidelity.
- For stochastic methods, report weight variance, effective sample size, convergence/autocorrelation, and the computational cost of likelihoods or correction weights.
- Keep numerical cancellation, truncation, positivity, normalization, and failed configurations visible. A compact representation can still be expensive to sample.
- At larger scale, where full TVD is inaccessible, distinguish indirect evidence from a certified bound. Do not extrapolate synthetic pilots into hardware validation or a quantum-advantage disproof.

## Primary source starting points

These are starting points from the search completed for the existing report; verify current versions and extend the search yourself. The report contains the fuller source and novelty register.

- [Goodman et al., Gaussian boson sampling: Benchmarking quantum advantage](https://arxiv.org/html/2604.12330): positive-P approximate detector sampling.
- [Oh et al., Classical algorithm for simulating experimental Gaussian boson sampling](https://arxiv.org/abs/2306.03709): lossy quantum/classical decomposition and tensor-network simulation.
- [Dodd et al., A fast and frugal Gaussian Boson Sampling emulator](https://arxiv.org/html/2511.14923): cumulant-based approximate sampling.
- [Lim, Classical Simulation of Lossy Gaussian Boson Sampling beyond Square-Root Regime](https://arxiv.org/html/2610.06526): October 2026 preprint; photon trajectories, Gaussian resets, and source-space reduction. Treat its theorems as attributed results until checked.
- [Kalra and Kocharovsky, Quantum complexity resource in Gaussian boson sampling: Core structure of the semidefinite program](https://arxiv.org/html/2606.29739): active-sector structure.
- [Liu et al., Efficient simulation of low-entanglement bosonic Gaussian states in polynomial time](https://www.nature.com/articles/s41534-026-01254-7): Gaussian MPS construction; distinguish preparation from complete sampling.
- [Bulmer et al., The boundary for quantum advantage in Gaussian boson sampling](https://pmc.ncbi.nlm.nih.gov/articles/PMC8791606/): exact primitives, detector conditioning, and Metropolis independence sampling.
- [Efficient classical sampling from Gaussian boson sampling distributions on unweighted graphs](https://www.nature.com/articles/s41467-025-64442-7): graph-specific stochastic sampling; do not transfer its guarantees directly to arbitrary complex optical matrices.
- [Matrix Phase-Space Representations for Gaussian Boson Sampling](https://arxiv.org/abs/2503.12749): variance reduction and validation estimators.
- [Sequential Monte Carlo in Statistics](https://awllee.github.io/smc-tutorial/smc-tutorial.html): weighting, particle methods, and relevant stochastic machinery.

**Requested outcome:** a candid independent critique, additional ideas, and a defensible choice of what to test next. We are seeking a mechanism worth developing, not reassurance that the current favorite will succeed.
