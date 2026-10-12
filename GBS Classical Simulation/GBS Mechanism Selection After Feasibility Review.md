# Mechanism selection after the conditional-cumulant feasibility review

**Measured follow-up:** [[GBS Mechanism Smoke Benchmark]] now tests these mechanisms against original Dodd CPU code and Goodman equation ports. It supports context sampling for moderate-error, high-shot workloads and exact product cores for eligible structured circuits, while rejecting the present generic block approximation and source backend as competitive in the tested small-system regime. The original screening discussion below is retained; its statement that competitive timing was unmeasured describes that earlier stage.

**Date:** October 11, 2026. **Status:** supplied plans and results interpreted; external implementation inspected and deterministic limit checks reproduced; a new positive bounded-context sampler screened on small synthetic circuits. No competitive speedup, scalable error theorem, or cleared novelty claim is established.

## Decision

The most useful field to investigate next is **information theory and probabilistic graphical models**, specifically the relationship between conditional information and the amount of detector history a sampler must retain.

The question is: **Does loss, source structure, or circuit structure make a small set of previous detector outcomes sufficient to predict the next detector accurately?** If so, calculate exact probabilities for those small subsets, compile them once, and sample complete records through local conditional tables. This directly removes conditioning work and preserves nonnegative normalized probabilities, without tracking a non-Gaussian state or regenerating cumulants for every displacement.

Our new small screen makes this a concrete candidate rather than merely an algorithm label. Its accuracy remains imperfect and scaling unresolved. A secondary physics direction is **Gaussian separability plus convex optimization**: find small quantum blocks whose remaining cross-block correlations can be carried by positive classical displacement noise. Source compression remains a practical backup when the selected sampling backend benefits from it.

The reported conditional-cumulant failure is not a sound basis for abandoning that entire family: the supplied implementation fails elementary vacuum and independent-detector limits. Correctness must be restored before any comparative accuracy verdict. Its expensive per-record coefficient path nevertheless identifies a real implementation cost worth avoiding.

## What the supplied material actually establishes

The first plan correctly isolates coefficient overhead and requires a baseline, exact references, validity checks, and full cost accounting. Its promise of a baseline that perfectly matches theoretical accuracy is too strong: an approximate sampler needs verified equations and measured accuracy, not an assumed full-distribution guarantee. Exact repair-TVD penalties are generally available only for tractable references, not automatically for a continuous mixture or large circuit.

The second plan adds useful controls: exact-marginal diagnostic arms, same-order versus lower-order comparisons, coefficient reuse, and a separate cost-scaling study. Several qualifications matter:

- Exact table sampling is a meaningful small-system competitor, not a universal computational lower bound. Include its actual setup and amortized cost.
- Oracle-marginal arms isolate errors; they are not automatically upper bounds on every possible approximation or policy.
- Reusing a displacement can preserve each record's marginal law while correlating records. Two observable-specific variance checks do not establish IID detector output. Sampling under independent displacements remains the primary record-generation comparison.
- Operation counts with unit constants and fitted runtime exponents are projections, not measured matched-accuracy advantages at 144 modes.
- Increasing truncation order need not monotonically improve an approximate marginal-update algorithm after repairs.
- Enumerating a fixed small subset is permitted in an efficient candidate. The prohibited shortcut is enumerating the entire $2^M$ record space for candidate generation or normalization.

The reported implementation and JSON were found in a separate checkout. The artifact confirms **100 shots, order 3, one replicate**, and 54 rows representing two methods on 27 physical cells. It does not contain the proposed same-accuracy order frontier, multiple shot-count comparison, or a full production-level marginal-update implementation. Its traced allocations are not peak resident process memory. A 100-shot histogram is insufficient to identify a small full-distribution accuracy difference without IID controls.

### Reproduced correctness failure

The function `piecewise_zero_probability` begins at line 154 of the inspected source. Its returned joint probability contains cumulant correction terms, but omits the required half-prefix contribution. It also uses an independent-product prefix in place of the correlated prefix/marginal tables needed for a faithful update. Adding one missing term alone would therefore not complete a published-method reproduction. The published expansion explicitly separates the half-prefix term and the correlation contribution. [Dodd et al., Appendix B](https://arxiv.org/html/2511.14923)

Deterministic checks produced:

| Input limit | Correct probability of no click at detector 2 | Supplied calculation |
| --- | ---: | ---: |
| Vacuum | 1.0 | 0.5 |
| Independent detectors with no-click probabilities 0.8 and 0.7 | 0.7 | 0.2 |

These errors exist without non-Gaussian conditioning or difficult quantum correlations. Consequently, the reported clipping counts cannot be attributed to an inherent positivity failure of the conditional idea or of the published method.

The reported roughly 14–16-fold slowdown describes that implementation at the same order and 100-shot setting. It does not establish the matched-accuracy feasibility verdict. Coefficient work is genuinely repeated per record, but the implementation also repeats small combinatorial work, generates displacements through a general multivariate routine per record, and times under allocation tracing. Numerical thread limits are set after importing NumPy and are not independently verified. No corrected benchmark was run here.

**Audit evidence:** [reproduction script](work/gbs_external_cumulant_audit.py) and [limit-check artifact](outputs/bounded_context_screen_v1/supplied_implementation_audit.json). The artifact records the inspected source checksum. It does not silently replace the external implementation.

## Field 1: conditional information and graphical models

### Mechanism

For detector $i$, select a small parent set $S_i$ from detectors already sampled. Define

$$
Q(x)=\prod_{i=1}^M P(x_i\mid x_{S_i}).
$$

Each factor is calculated from the exact Gaussian marginal on at most $b+1$ modes, where $b$ bounds the number of parents. The resulting distribution is normalized and nonnegative in exact arithmetic. These are exact reduced-context probabilities; the approximation consists of ignoring part of the history.

The statistical interpretation is precise. With logs in nats,

$$
D_{\rm KL}(P\Vert Q)=\sum_i I_P\!\left(X_i;X_{<i}\setminus X_{S_i}\mid X_{S_i}\right).
$$

Each term measures the information about the next detector that is lost after retaining its selected parents. Pinsker's inequality gives

$$
D_{\rm TV}(P,Q)\leq\sqrt{D_{\rm KL}(P\Vert Q)/2}.
$$

This is a standard chain-rule identity, not a new theorem. Its potential contribution is to identify physically relevant GBS families with cheaply selectable contexts and sufficiently small omitted information.

### Why computation could fall

With fixed $b$, table construction uses approximately $O(M b^3 2^b)$ small-subsystem determinant work, storage is $O(M2^b)$, and record generation is $O(Mb)$. A selection procedure can add cost: calculating all pair mutual informations costs quadratically many pair queries. Those costs must be included.

Coefficients do not change between records. Sampling needs no global partition function, signed polynomial reconstruction, corrective likelihood, or full conditional-state representation. This is particularly attractive for many shots from a fixed circuit.

The essential risk is that $b$ must grow with brightness or system size to preserve accuracy. Dense Haar mixing has no natural short spatial memory. Pairwise scores can miss relationships that become important only after other detectors are known, and many weak omitted dependencies can accumulate.

### Literature boundary

Tree and Bayesian-network approximations are established statistical tools. Chow–Liu dependence trees are a required baseline, not a novelty claim. [Chow and Liu](https://doi.org/10.1109/TIT.1968.1054142), [modern primary analysis](https://arxiv.org/abs/2011.04144)

Low-order GBS approximations also substantially overlap with this objective. [Villalonga et al.](https://arxiv.org/html/2109.11525)

Recent noisy-qubit-circuit work connects conditional mutual information decay to efficient sampling. This supplies a useful conceptual bridge, not a GBS theorem: its circuit geometry, noise model, and proofs cannot be imported directly into a dense passive optical circuit with fixed total loss. Classical detector CMI must also be distinguished from quantum CMI of the premeasurement Gaussian state. [Lee et al.](https://arxiv.org/html/2510.06328)

The possible new research contribution is a GBS-specific information selector, physical error bound, or context-scaling result that improves a strong accuracy–cost frontier. Applying a standard graphical model alone is insufficient.

### New positive-sampler screen

We tested 36 seeded complex-Haar circuits at 6/8/10 modes, transmissions 0.3/0.5, and heterogeneous, flat $r=0.7$, and bright-flat $r=1.0$ profiles. Two context rules were used: the most recent detectors, or the earlier detectors with greatest pair mutual information. Widths 0–4 gave 360 comparisons.

The parent selection used only pair marginals and a fixed rule, never full-distribution error. Candidate tables used exact small Gaussian marginals; full enumeration was confined to reference-side scoring and full-context validation. The tested local probabilities were nonnegative without clipping. Vacuum generation and full-context recovery were checked. Independent complex-basis Torontonian comparisons checked six-mode references. The KL/CMI identity and Pinsker bound were verified numerically in every comparison.

Ten-mode results, using pair-information-selected parents:

| Source profile | Median TVD, 2 parents | Median TVD, 4 parents |
| --- | ---: | ---: |
| Two strong sources and weak tail | 0.0556 | 0.0229 |
| Flat $r=0.7$ | 0.0731 | 0.0378 |
| Bright flat $r=1.0$ | 0.0691 | 0.0346 |

Across all mode counts, four-parent TVD ranged from about 0.00052 to 0.0553. Small six-mode cases make pooled results look better than ten-mode results, so the ten-mode medians are reported separately. Pair-based selection beat recent-context selection in 67 of 72 comparisons at widths two and four, but did not always win.

At ten modes and width four, only 111 local no-click probability entries are stored. This establishes a compact, valid complete-record sampler with measurable approximation error. It does not establish fidelity sufficient for the project target, superiority over Dodd/Goodman, or scalability to thousands of modes. The contexts are still a substantial fraction of these small circuits. This is an exploratory screen, not a frozen confirmatory benchmark.

**Artifacts:** [sampler and diagnostic](work/gbs_bounded_context_probe.py), [all results](outputs/bounded_context_screen_v1/probe.json). The script records illustrative setup and vectorized generation times, but no competitive speed claim is made. CMI was measured using full references; it is not yet a scalable certificate.

## Field 2: Gaussian separability and convex optimization

### Mechanism

Seek an output covariance decomposition

$$
V=\bigoplus_B V_B+W,\qquad W\succeq0,
$$

where every $V_B$ is a physical Gaussian covariance for a small detector block. Sample correlated classical displacement with covariance $W$, then sample each displaced quantum block independently conditional on that draw.

This can retain long-range classical detector correlations while restricting expensive quantum calculations to small blocks. It differs from simply multiplying unconditional block marginals, which destroys cross-block correlations. Physical covariance and Gaussian separability conditions already provide the foundation; feasibility can be expressed through linear matrix inequalities for a fixed partition. [Werner and Wolf](https://arxiv.org/html/quant-ph/0009118), [Ma et al.](https://arxiv.org/abs/2007.01731)

If the decomposition is exact and the local samplers are exact, the full mixture is an exact positive sampler. For an approximate physical target, a separate Gaussian-state distance bound and measurement-contraction argument are needed.

**Niche:** lossy structured circuits or states with small entangled groups plus shared classical fluctuations. **Failure condition:** substantial interblock quantum entanglement makes the required positive split infeasible or requires large blocks. Arbitrary changes of optical basis cannot be used freely because detectors measure the original modes.

This is a promising physics relationship, but separability and quantum/classical decomposition are old ingredients. Any original contribution must come from a useful partition/approximation rule and an actual sampling advantage. No block-decomposition prototype or new certificate was run in this review.

## Other fields and their present role

| Connection | Expensive operation it could remove | Main unresolved condition |
| --- | --- | --- |
| Error-budgeted source compression plus parameterized matrix algorithms | Work driven by weak residual quantum sources. | The backend must actually benefit; source count and photon/click count differ. Strong prior overlap. |
| Detector symmetry and group-count sampling | Distinct but symmetry-equivalent detector histories. | The fixed state/loss/measurement model must have the symmetry, and orbit probabilities must be cheap and stable. |
| Numerical linear algebra and compilation | Repeated factorizations and marginal calculations across many records. | Savings must exceed cache/selection cost; usually engineering rather than a new physical mechanism. |
| Stochastic correction and rare-event simulation | Wasteful exploration or rejection for a specified conditional task. | A cheap valid correction oracle, support coverage, and variance/mixing control. |

## Next research question and stop conditions

**Recommended question:** Can a small, physically chosen detector context capture enough conditional information that valid local-marginal sampling beats a strong cumulant or phase-space competitor at matched accuracy?

First repair and validate the published-method baseline independently of any algorithm ranking. Compare bounded contexts against Chow–Liu, stronger low-order methods, and that corrected baseline on the same target and shot counts. Freeze selection on development circuits, then evaluate fresh circuits. Include brightness, source-spectrum, and structured-versus-Haar controls.

Grow reference size only when determinant cost and numerical precision support it. Measure how the context width required for a fixed TVD changes with mode count. Account for all parent selection, table preparation, record generation, and memory; a small exact table is still a useful cost competitor.

Stop or narrow the niche if context size grows too quickly, if pair information misses the needed dependence, or if the method loses its advantage against strong baselines. A global CMI certificate must come from a tractable physical bound or a justified scaling argument, not an inaccessible large-system full distribution.

**Current judgment:** this field supplies a concrete computational relationship, a valid prototype, and a measurable failure criterion. It merits the next investigation. The stronger claim that it supplies the novel competitive GBS algorithm remains unproven.
