# Novelty and Prior-Work Boundaries

**Working assessment, October 12, 2026:** the complete exact-marginal, information-selected, bounded-parent GBS sampler is potentially original. The reviewed material has not established an exact published duplicate, and it has not cleared priority. AI review agreement is not independent peer review.

## What is already known

Ordered bounded-parent Bayesian networks, dependence-based candidate selection, and ancestral sampling are established. Cooper–Herskovits K2 and Friedman et al.'s Sparse Candidate algorithm are direct generic predecessors. Exact Gaussian subset probabilities are established, and Villalonga already uses efficiently calculated low-order GBS marginals. Sources and original papers are linked in [Sources](Sources.md).

The candidate contribution must therefore be the specific GBS construction, a substantive selection or error-control result, and a useful measured regime. It does not require inventing statistics from scratch, but a new label for an unchanged known construction would be insufficient.

## Distinctions that matter

| Comparison | Defensible distinction |
| --- | --- |
| Dodd cumulant emulator | Our method limits retained history variables in each conditional; Dodd limits cumulant order across history. A bounded-parent graph can still generate correlations of higher order |
| Villalonga | Our tables come directly from exact local Gaussian probabilities and generate IID records from a fixed directed model. Villalonga includes both Boltzmann/Gibbs and greedy generators; avoiding MCMC is not a comparison with the whole paper |
| Sparse Candidate / K2 | The prototype uses the largest pair-MI earlier detectors as final parents and a physical probability oracle. This is not the full iterative Sparse Candidate procedure or K2's Bayesian data score |
| Chow–Liu | The optimal one-parent tree is selected globally by a maximum spanning tree before orientation. Our fixed-order one-parent heuristic can exclude that optimum |
| Lee's local-conditionals framework | A close quantum-sampling predecessor with output-information assumptions. Its qubit noise model cannot be transferred to total optical loss without an argument |

## Probability and information caveats

“Positive” means nonnegative, not strictly greater than zero. Physical zero-probability events exist. For a zero-probability target parent assignment, the conditional is undefined; the implementation fills its no-click probability with one. Whether approximate preceding factors reach such rows needs explicit future instrumentation.

Exact subset formulas do not prevent finite-precision cancellation. The local compiler asserts nonnegativity and normalization instead of silently clipping. Nor do locally exact conditionals generally preserve their family marginals globally: the approximate parent law can drift.

The standard KL/omitted-CMI identity identifies approximation error, but its full-history terms can be as difficult as the target distribution. It is an analytical explanation, not an implemented scalable certificate. Pairwise MI can miss conditional or higher-order dependence.

Photon loss supplies a research motivation. No cited result establishes that six-parent contexts approximate arbitrary complex-Haar threshold GBS at transmission 0.3–0.5. Ordering sensitivity also remains empirical; dense Haar mixing has no automatic local detector geometry.

## What would strengthen the contribution

Compare exact-marginal trees, recent/random parents, and conditional-information selectors; include their full selection costs. Add faithful Villalonga controls and stronger accessible Goodman and Oh implementations. Separate tuning from held-out validation and measure how required width grows at common fidelity targets.

The existing small-system, many-record benefit is a useful result to develop. A polished implementation, lower error, or hardware-scale advantage challenge is a proposed outcome, not a consequence guaranteed by that result. The structured exact product-core specialization rests on known Gaussian separability; it needs a broader eligibility result or another substantive contribution to support its own novelty claim.
