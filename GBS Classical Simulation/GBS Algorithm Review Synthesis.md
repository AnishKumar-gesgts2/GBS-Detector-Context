# GBS algorithm review synthesis and next decision

**Later experimental decision:** see [[GBS Mechanism Smoke Benchmark]] for the bounded mechanism implementations, actual Dodd CPU comparison, qualified Goodman ports, full-distribution accuracy, cost accounting, unfavorable cases, and current go/stop decisions. See [[GBS Mechanism Selection After Feasibility Review]] for the correctness audit that supersedes the supplied conditional-cumulant failure interpretation.

**Date:** October 11, 2026. **Status:** four supplied assessments consolidated; consequential claims checked against primary sources; a new small mechanism diagnostic completed. No new complete sampler, matched-accuracy speedup, or experimentally validated quantum-advantage challenge is claimed.

## Decision

**Subsequent review:** [[GBS Mechanism Selection After Feasibility Review]] audits the later supplied implementation, identifies failed vacuum/independent limits, and screens positive bounded-context sampling. Its mechanism selection supersedes the development priorities below. The earlier conditional-cumulant diagnostic remains unchanged.

There is something worth pursuing, but the current evidence supports a **bounded feasibility study**, not a confident proposal that a particular algorithm will outperform the field.

The most useful new research direction is **displacement-conditioned cumulant sampling with inexpensive coefficient evaluation**. Its prospective benefit is to sample the correlated classical displacement exactly, then approximate only the weaker residual quantum correlations. Our new six-mode diagnostic supports that mechanism in several regimes, with important counterexamples and positivity problems. The approach needs a complete positive sampler and an implementation that avoids recomputing an expensive cumulant table for every record.

This is an extension of established methods: the broad combination is explicitly anticipated in prior work. A potential original contribution would need a particular factorization, error-controlled selection rule, or implementation that demonstrably reduces total sampling cost. Novelty remains open.

**Backup:** integrate certified residual-source compression into a backend whose actual sampling work falls when sources are removed. This has stronger existing distribution evidence but a narrower spectrum-dependent niche and substantial prior overlap.

**Specialized alternative:** exact detector-permutation symmetry can remove distinct sampling histories. Investigate it only for an explicit physically relevant symmetric circuit family. It does not cover generic Haar circuits, and elementary single-source examples already have straightforward samplers.

Adaptive non-Gaussian retention is downgraded to a small diagnostic. Generic SMC, a neural generator, or relocating loss through an interferometer does not currently supply a justified new competitive mechanism.

## The four assessments and where they agree

The labels below follow the order in which the user supplied the texts. Their recommendations are external opinions, not independently reproduced results. The attachments remain the original record; instructions or claims of file edits inside them were not executed as commands.

| Assessment | Main recommendation | Useful contribution | Main limitation |
| --- | --- | --- | --- |
| 1, opening “Here's the direct response…” | Cost-aware bounded non-Gaussian retention, followed by reduced-core sampling. | Explicit cost/failure accounting and a small complete-record comparison. | Recommends retention without a new implementation or evidence that its overhead is justified; some proposed additions rephrase existing candidates. |
| 2, opening “I'll start by checking…” | Establish the cumulant emulator baseline; investigate conditional cumulants, sparse/adaptive terms, ordering, and probability-ratio scoring. | Strongest new bridge between loss decomposition and a statistical sampling architecture. | Several proposed guarantees and feasibility statements are too strong; no underlying project artifacts were checked. |
| 3, opening “My assessment is…” | Test source compression in a real backend; investigate symmetry, signed-Gaussian merging, detector removal, and prefix caching. | Clearest distinction between a smaller representation and less actual sampling work; supplies useful exact identities. | No complete implementations or novelty clearance for the new suggestions; the reported project pilots were not independently reproduced. |
| 4, opening “Audit the Premise” | Local-loss tensor networks and Gaussian-proposal SMC; also neural fine-tuning. | Highlights trajectory growth, training cost, and finite-size extrapolation risks. | Overstates novelty, error control, and feasibility; makes unsupported blanket rejections and treats resampling as stronger protection than it provides. |

All four agree that local reset error, source rank, covariance compression, and entropy proxies do not establish a complete sampling advantage. All recognize representation growth or correction-weight cost as central obstacles. Their different rankings do not constitute independent corroboration that any candidate will work.

The original brief already names Dodd, exact threshold samplers, and full pipeline accounting. The reviewers' complaint about “missing baselines” should therefore be interpreted as **missing implemented competitive comparisons**, not absence from the brief.

## Claims that needed correction

### Threshold conditioning is already a signed-Gaussian method

When a measured threshold mode is discarded, its unnormalized click-conditioned remainder is

$$
\widetilde\rho_{\rm click}=\operatorname{Tr}_m\rho-\langle0_m|\rho|0_m\rangle.
$$

Both terms are Gaussian when the input is Gaussian. Repeated clicks can therefore produce a signed Gaussian expansion with exponentially many components. This is explicitly the basis of the 2018 exact threshold sampler, rather than a new derivation from the reviews. [Quesada, Arrazola, and Killoran](https://arxiv.org/html/1807.01639)

Photon subtraction is a different instrument. A polynomial-Gaussian trajectory requires a specified mapping to threshold detection, such as the established auxiliary first-arrival construction. A two-mode subtraction diagnostic alone does not determine the frequency or importance of errors in the eventual threshold-record algorithm. [Bulmer et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8791606/)

A hard degree cap limits part of the representation cost, but does not bound approximation error. Degree $d$ in $r$ variables can still require $\binom{r+d}{d}$ coefficients unless further structure is exploited. Conversely, polynomial complexity is representation-dependent; an exponential coefficient count cannot simply be asserted for every implementation.

Retaining the first few clicks exactly and resetting later is a useful diagnostic, not a mathematical upper bound on what an optimally selected retention scheme could achieve.

### Conditional cumulants are promising, but explicitly anticipated

[Dodd et al.](https://arxiv.org/html/2511.14923) present a cumulant-based binary sampler with approximate marginal updates. Their discussion explicitly proposes adapting it to noisy-state decompositions into displaced low-brightness pure states. Their large-system validation uses selected diagnostics, rather than a full TVD guarantee. We must compare against their actual architecture; sparse/adaptive coefficient evaluation would require a distinct implementation and evidence.

The latent displacement introduces a new cost: displacement-dependent coefficients change between records. A determinant factorization can be reused, but exponentials, cumulant products, and marginal updates remain. A per-record recomputation can erase the savings from a lower truncation order. This is the main computational question, alongside validity of the reconstructed probabilities.

Conditioning does not universally shrink cumulants. Mixture cumulants include correlations between conditional means as well as conditional fluctuations, and removing the latent mixture can expose cancellations that were previously hiding larger conditional terms.

### Moving loss into local layers is not a new loss mechanism

Uniform vacuum loss commutes with passive interference. At the covariance level, for an orthogonal passive symplectic transformation $S$,

$$
S\left[\eta V+(1-\eta)I/2\right]S^T=\eta SVS^T+(1-\eta)I/2.
$$

Thus an equivalent placement of uniform loss can be useful computationally, but does not itself add more decoherence or establish a new algorithm. Uniform layers must multiply to the original transmission. Moving mode-dependent loss across arbitrary gates can change the target. [Oszmaniec and Brod](https://arxiv.org/abs/1801.06166), [Lim](https://arxiv.org/html/2610.06526)

Lossy GBS tensor-network simulation with matrix-product operators already exists. After tracing an environment, the system is generally mixed; an ordinary pure-state MPS is insufficient without trajectories, purification, or another mixed-state representation. Local SVD discarded weight needs a global error argument and appropriate norm before it becomes a final-record TVD guarantee. [Liu et al., 2023](https://arxiv.org/html/2301.12814)

A better loss placement or contraction schedule remains conceivable, but the fourth review's high-feasibility/moderate-novelty ranking is unsupported.

### SMC and neural sampling retain unresolved bottlenecks

SMC requires suitable incremental target/proposal ratios, not necessarily a full final-pattern probability at every step. Therefore it cannot be dismissed as mathematically incapable of generating records. However, no cheap valid correction oracle has been supplied here. Resampling controls allocation, not bias from discarded physics; ESS after resampling can hide genealogy collapse. One 1,000-particle failure at one circuit is evidence against that configuration, not proof that all SMC proposals are unviable. [Anthony Lee's SMC tutorial](https://awllee.github.io/smc-tutorial/smc-tutorial.html)

A neural autoregressive model can generate normalized records quickly once trained. Fast inference establishes neither target fidelity nor cheap training. Training only on high-probability patterns can miss important aggregate mass. The source-rank vacuum kernel does not make arbitrary exact click probabilities cheap. No retrieved primary source establishes the proposed neural method as a necessary standard GBS baseline or the claimed general sampling improvement.

The fourth review's assertion that decomposition optimization will consistently cost more than it saves is also unsupported. Keep structured, explicit decompositions as a narrow possibility; measure the crossover before developing a general optimizer.

### Larger-scale TVD estimates and exact references need qualifications

For a normalized proposal with support covering the target,

$$
D_{\rm TV}(P,Q)=\frac12\mathbb E_{x\sim Q}\left|\frac{P(x)}{Q(x)}-1\right|.
$$

This avoids the histogram comparison's number-of-bins burden, but can have large or poorly controlled variance when $Q$ undersamples important target regions. Finite observations do not certify unseen tails. Sector-restricted estimates also need the correct sector normalizations. This is evaluation infrastructure, not a new record sampler.

All-subset vacuum probabilities followed by a Möbius transform give exact threshold distributions, but “24 modes is feasible” is not a universal resource claim. One float64 vector already needs 128 MiB at 24 modes; determinant work, extra arrays, and cancellation also matter. Increase reference size based on measured costs and precision, rather than promising a broad 24-mode sweep.

## New diagnostic performed for this synthesis

### Conditional cumulant screen

We used twelve six-mode complex-Haar circuits: two seeds for each of three squeezing profiles and transmissions 0.3/0.5. Profiles were two strong sources plus a weak tail, flat squeezing $r=0.7$, and bright flat squeezing $r=1.0$. Photon loss was the only noise.

The lossy covariance was decomposed exactly into a pure Gaussian covariance and classical displacement noise. We calculated exact conditional threshold distributions for latent displacement points, then their parity cumulants. Two independent scrambled Sobol sequences were evaluated at 2,048 and 16,384 nested points per circuit. Independent complex-basis Torontonian comparisons checked the unconditional references; coherent-state factorization and full cumulant reconstruction identities were checked separately.

At 16,384 points, the ratio of mean absolute conditional cumulant sums to unconditional sums, across orders 3–5, had:

| Diagnostic | Observed value | Interpretation |
| --- | ---: | --- |
| Median conditional/unconditional ratio | 0.314 | Conditional higher-order information was often substantially smaller. |
| Range of that ratio | 0.0485–1.233 | Conditioning sometimes increased a cumulant order; no universal suppression. |
| Maximum discrepancy between integrated exact conditional distribution and exact target | TVD 0.000555 | The numerical latent-mixture integral has a measurable residual error. |
| Fraction of latent points with a negative probability below $-10^{-10}$ after raw order-3 reconstruction | 5.90%–52.19% | Naive cumulant truncation is not automatically a valid conditional sampler. |
| Mean negative mass in those order-3 reconstructions | $2.66\times10^{-7}$–$1.84\times10^{-5}$ | The violations were often small; they need accounting and a scalable positive construction, not automatic rejection. |

The mixed raw order-3 reconstruction had smaller half-L1 discrepancy than its unconditional counterpart in these cells. We do **not** call this a demonstrated sampler-TVD improvement: individual reconstructions can be signed, the integration is approximate, and no Dodd marginal-update algorithm or practical conditional sampler was implemented. Higher order did not uniformly improve the numerically integrated comparison.

**What passed:** the conditional-correlation mechanism warrants investigation. **What remains open:** positive sampling, coefficient cost, end-to-end comparisons, generalization, and novelty.

### Signed-Gaussian conditioning risk

For a prefix with no-click set $Z$ and click set $C$, the unreduced normalized Gaussian expansion has absolute coefficient sum

$$
\Lambda(Z,C)=\frac{\sum_{D\subseteq C}P_0(Z\cup D)}{P(X_Z=0,X_C=1)}.
$$

We evaluated this directly from exact vacuum probabilities. After four measured modes, with two modes still unmeasured, its probability-weighted mean was about **27.1–70.3** across the twelve circuits. This warns that merge-distance error bounds multiplied by signed coefficients can become expensive early.

This is not a lower bound on every representation or proof that merging fails. Components may coincide or be combined algebraically; large means can reflect rare histories. The test did not compute Gaussian-state distances, implement merging, or measure final sampler errors. It argues against promoting signed merging before its coefficient-weighted certificates are actually tested.

**Reproducibility:** [diagnostic script](work/gbs_review_mechanism_probe.py), [raw results](outputs/review_synthesis_v1/mechanism_probe.json). The final diagnostic ran in approximately 6.23 seconds inside its measured analysis loop, excluding interpreter/import startup. This is a diagnostic runtime, not a sampler benchmark. The JSON records seeds, conventions, point counts, and the script's LF-normalized checksum. Original pilots remain in [[GBS Algorithm Opportunities and Validation]].

## Consolidated priorities

These are experiment priorities, not predicted probabilities of success or publication. None has passed a competitive end-to-end test.

| Priority | Direction | Benefit if it works | Evidence and novelty boundary | Decision |
| ---: | --- | --- | --- | --- |
| 1 | Conditional cumulants with cheap displacement-dependent coefficients | Lower the expensive correlation order without explicit non-Gaussian state tracking. | New local diagnostic supports the mechanism; broad extension already anticipated. | First feasibility study; require positive conditionals and operation-level cost reduction. |
| 2 | Certified source compression integrated with one backend | Remove weak quantum resources that actually drive backend cost. | Existing full small-distribution evidence; strong prior overlap and heterogeneous-spectrum restriction. | Most concrete backup; compressed/uncompressed comparison must use the same backend. |
| 3 | Exact symmetry quotient sampling | Replace distinct detector histories with group-count states. | Exact symmetry argument; no relevant complete implementation or novelty clearance. | Pursue only with a useful symmetric physical family and stable count probabilities. |
| 4 | Sparse/adaptive cumulants and correlation-informed mode ordering | Avoid unnecessary terms or improve marginal approximations. | Plausible engineering extensions; omitted terms and normalization need control. | Test against fixed-order published architecture; a magnitude threshold is not an error certificate. |
| 5 | Exact prefix caching and certified near-deterministic detector removal | Remove repeated evaluations or almost-fixed output bits. | Clear mathematical mechanisms; low novelty confidence and narrow niches. | Low-cost modules, especially for many shots from a fixed circuit. |
| 6 | Explicit structured cost-aware decomposition | Reduce entanglement or cutoff cost without costly general optimization. | Existing proxy example; generic complex-Haar benefit unresolved. | Small same-backend comparison only. |
| 7 | Bounded retention / certified signed-component merging | Preserve important conditional information with controlled state growth. | Local error signal, early signed-mass warning, no full sampling benefit. | Diagnostic status; no longer the favored lead. |
| Separate task | High-click conditional importance sampling / MCMC | Avoid rare-sector rejection or improve estimators. | Existing stochastic machinery; likelihoods, support, and mixing unresolved. | Define the conditional task and primitive first. |
| Defer | Generic SMC, neural fine-tuning, local-loss tensor networks, standalone RQMC | Possible tools within a concrete algorithm. | No demonstrated new bottleneck-removing mechanism here. | Do not lead the proposal with these labels. |

Near-deterministic detector removal is valid when sampling the **unconditioned marginal** of the retained detectors and appending fixed bits; a union bound controls the replaced bits' total error without independence. Symmetry requires actual invariance of the specified state/loss/measurement model. Neither similar marginal brightness nor averaging over Haar circuits establishes it.

## Smallest useful next implementation

Build a faithful small-system baseline of the published cumulant sampler and verify its marginal-update conventions. Begin at 6–10 modes, then grow exact references toward 12–16 modes as costs allow. Compare flat and heterogeneous spectra, transmissions 0.3/0.4/0.5, multiple brightness levels, complex Haar circuits, and a structured control.

Test the conditional variant only after defining a positive normalized sampling rule. Instrument coefficient generation, covariance factorizations, displacement work, marginal updates, and any fallback. Include the cost of changing coefficients for every displacement. Compare cold and amortized totals for different requested shot counts; exact table sampling is a meaningful small-scale cost competitor when many records are requested.

Freeze policies before fresh held-out evaluation. Use full-distribution references where possible and exact IID histogram controls to expose finite-sample error. A useful development gate is a repeatable improvement on the same accuracy–cost frontier against the strongest available matched competitor, with identifiable operations saved. Any numerical threshold is a declared project choice, not a scientific constant.

**Stop or redesign** if conditional coefficients erase the lower-order benefit, if validity requires enumerating all strings, if the gain is confined to a weak baseline, or if favorable mechanisms vanish on the intended physical family. If this fails, run source compression through a single appropriate backend rather than returning immediately to expensive retained-state development.

The immediate proposal question is: **Can conditioning on classical displacement reduce the correlation information needed for a positive threshold sampler enough to offset its per-record coefficient cost?** The diagnostic justifies asking that question. It does not yet justify claiming its answer is yes.
