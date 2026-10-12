# Project Description

## Objective

Develop a classical algorithm for threshold Gaussian boson sampling that generates useful approximate samples at a lower computational cost for a specified accuracy target. Better classical sampling can narrow the gap behind an experimental quantum-advantage claim. A challenge to such a claim requires matching its actual sampling task, error requirements, and resource comparison; improving a small simulator alone does not establish that conclusion.

Our current direction is **exact-marginal detector-context compilation**: use Gaussian physics to calculate small joint detector distributions, retain a limited amount of relevant detector history, and compile a reusable sampler. The intended niche is many independent records from the same lossy circuit at moderate tolerated error. [Measured evidence](Results.md) motivates this direction.

## The mechanism

Let $P$ be the target threshold-click distribution and $X_i\in\{0,1\}$ the outcome at detector $i$. Exact sequential sampling conditions on every preceding detector. Our approximation chooses a parent set $S_i\subseteq\{1,\ldots,i-1\}$ with at most $b$ detectors and defines

$$
Q(x)=\prod_{i=1}^{M}P(x_i\mid x_{S_i}).
$$

The prototype selects earlier detectors by pairwise mutual information, a measure of statistical dependence. It calculates each retained conditional from the exact Gaussian marginal on the parent detectors and the next detector. It then samples records with table lookups and fresh random numbers. The tables are reused across records.

The computational saving comes from replacing repeated full-history work with a one-time compilation and a small number of lookups per record. The approximation error comes from omitted history. Exact local conditionals do not make the resulting global distribution exact or guarantee preservation of all family marginals.

The graph has bounded **indegree**. Its outdegree and global treewidth need not be bounded. For fixed $b$, table storage is $O(M2^b)$, with additional $O(M^2)$ covariance and pair-score storage. Local determinant work scales approximately as $O(M(b+1)^3 2^{b+1})$, plus pair screening and bookkeeping. Record generation costs $O(Mb)$. These estimates are useful only if the width required for the desired accuracy remains affordable.

## Physical scope

- Zero-mean Gaussian inputs, squeezed-vacuum sources, and passive linear interferometers.
- Ideal threshold detection: one binary click variable per output mode.
- Photon loss is the primary noise mechanism investigated and the only modeled noise in the initial algorithm study. The target development range is **50%–70% total photon loss**, or transmission $\eta=0.3$–$0.5$.
- Both heterogeneous and flat squeezing, including brighter sources; complex Haar-random circuits are the general-circuit test family. Structured real interferometers are a separate specialization.

With $\hbar=1$, vacuum covariance is $I/2$, and the uniform-loss model is

$$
V_{\rm loss}=\eta V_{\rm ideal}+(1-\eta)\frac{I}{2}.
$$

Loss is a physical motivation for seeking simpler approximations. Total loss alone does not prove sparse detector dependence or make every lossy squeezed state classical. Other imperfections may matter when matching a particular experiment; the initial model does not establish that loss is universally the only important noise.

## What is established

The smoke implementation is a normalized, nonnegative ancestral sampler for its approximate model, subject to its numerical checks and documented zero-support convention. In the measured eight- and ten-mode comparison, a six-parent model meets a full-distribution TVD limit of 0.02 on 21 of 24 circuits and is faster than the fastest qualifying tested comparator in those 21 cases. The five-order Dodd comparator remains substantially more accurate on dense circuits. See [Results](Results.md) for the workload, comparator qualifications, and failures.

## Development priorities

1. Improve parent selection and detector ordering without allowing reference-distribution information to leak into model construction.
2. Measure the accuracy gained per additional table entry, Gaussian query, and unit of setup time. Compare tree, random-parent, recent-parent, and conditional-information controls.
3. Determine whether context width must grow with mode count, squeezing, or click density. Develop affordable error diagnostics and distinguish them from rigorous certificates.
4. Optimize compilation and bulk generation only after separating representation error from implementation overhead.
5. Add faithful Villalonga, Oh, and stronger Goodman implementations where accessible, alongside the actual Dodd author-code baseline.
6. Transfer a validated method to one published experimental configuration and its evaluation protocol. Jiuzhang 4.0 is a motivating longer-term target, not a reproduced result.

## Contribution and outcome

The potential contribution is a useful GBS-specific combination of exact optical probability queries, information-selected detector contexts, reusable conditional tables, and an evidenced accuracy–cost frontier. Bayesian networks and ancestral sampling are established techniques; [Novelty](Novelty.md) defines the narrower unresolved claim.

A successful outcome would be an open algorithm, reproducible comparisons, and a demonstrated regime of improved classical sampling. A stronger outcome would narrow or challenge a particular finite experimental advantage claim at comparable fidelity. A negative result would identify where the representation fails and prevent unsupported extrapolation. The [Proposal](Proposal.md) develops this work; [Sources](Sources.md) gives its scientific context.
