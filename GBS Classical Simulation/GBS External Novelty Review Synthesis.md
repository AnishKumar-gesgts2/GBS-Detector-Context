# External novelty reviews: synthesis and fact checks

**October 11, 2026. Status: two attached assessments and one pasted assessment consolidated; consequential claims checked against primary papers and the implemented sampler. No new benchmark run or cleared priority claim.**

## Decision

**The complete detector-context GBS sampler remains potentially original and worth developing.** The supplied reviews do not establish an exact previously published GBS implementation. They do establish substantial generic predecessors. Using those predecessors does not exclude a novel GBS algorithm, formulation, application, or measured result; the contribution must be described at the level actually supported.

The two attached reviews mostly agree once their claim levels are separated: generic bounded-parent sampling is established, while the particular exact-Gaussian-marginal GBS implementation is unresolved. The pasted review shares the same narrow verdict but overstates its physical justification and several comparison claims.

The existing [[GBS Mechanism Smoke Benchmark]] provides a useful small-system performance result. It does not establish scalable accuracy, novelty clearance, or superiority over every competing implementation. [[GBS Detector Context Novelty Audit]] remains the detailed prior-work map.

## What the reviews add

| Supplied assessment | Useful contribution | Qualification after checking |
| --- | --- | --- |
| A: attached “Verdict … already known” | Separates generic construction from the GBS combination; identifies ordered-parent K2 precedent; explains marginal drift and zero-support rows | Several hyperlinks point to different papers from their surrounding claims. Replaced those pointers with independently verified primary sources below. Its opening is about the generic architecture, not proof that the whole GBS method is duplicated. |
| B: attached “Bottom line … potentially original” | Clearly identifies exact covariance-derived tables, IID generation, and the distinction from sparse-candidate learning and Dodd's cumulants | Its suggested generic conditional-MI selector and KL/CMI bound are established ingredients. They become potential contributions through a distinctive GBS result, not by renaming them. |
| C: pasted “Methodological Breakdown” | Emphasizes compilation and the different approximation axis from cumulant truncation | Its transfer of Lee's guarantee to 50%–70% GBS loss is unsupported. Strict positivity, Chow–Liu equivalence, and its description of Villalonga need corrections. |

These are AI assessments, not endorsements from independent human researchers. Agreement among them is not proof of priority or mathematical validity.

## Verified novelty distinctions

**An additional generic predecessor is K2.** Cooper and Herskovits, *A Bayesian Method for the Induction of Probabilistic Networks from Data* (1992), Sections 3.1.1–3.1.2, already fix an ordering, limit the number of parents, and select from preceding variables. It uses a data-based Bayesian score rather than our exact optical oracle and pair-MI ranking. [Original paper, K2 pseudocode on p. 322](https://link.springer.com/content/pdf/10.1023/A:1022649401552.pdf).

**Our selector is not the full Sparse Candidate algorithm.** Friedman et al. use pair dependence to identify candidate parents, search for a scored graph, and iteratively refine candidates. Our implementation takes the top pair-MI earlier detectors as final parents. Their Section 4 already warns about redundant parents and hidden conditional relevance. [Friedman et al.](https://arxiv.org/pdf/1301.6696).

**Our model is not simply Dodd's emulator.** The relevant distinction is limiting the number of history variables used by each conditional versus truncating the order of cumulant contributions across the history. Small-parent DAGs can produce higher-order correlations through paths; they do not generally set all cumulants above $b+1$ to zero. Both architectures can be valid approximate samplers, with different errors and costs. [Dodd et al., Section I.2](https://arxiv.org/html/2511.14923).

Thus, the defended contribution can be the complete GBS construction and its useful regime. A new general statistical theorem is not mandatory. A routine restatement of the existing framework, without an original application or substantive result, would leave the novelty case weak.

## Corrections to the pasted review

### 1. Photon loss does not supply the claimed guarantee

[Lee et al.](https://arxiv.org/html/2510.06328), Section II, Proposition 1, assumes an approximate-Markov condition expressed through **classical output conditional mutual information**. Its circuit setting is noisy qubits on a geometric graph, with noise after circuit layers. It does not prove that arbitrary lossy optical circuits at transmission $\eta=0.3$–$0.5$ have accurate fixed-width detector contexts.

Total transmission alone does not establish that retained detectors shield the next detector from the rest of its history. Pair MI and omitted-history CMI are different quantities. Quantum entanglement decay, Gaussian quadrature correlations, and classical threshold-detector CMI must also be distinguished.

**Correct statement:** photon loss motivates testing compressibility. The required small residual detector information remains a hypothesis for our family, not a theorem borrowed from Lee. [Goodman et al.](https://arxiv.org/html/2604.12330), Background and Methods, also explicitly distinguish pure loss from noise that removes nonclassical behavior. Persistent nonclassicality does not itself prove failure of our approximation, but rules out that shortcut to its justification.

### 2. Positivity means nonnegative, not strictly positive

Exact physical subset distributions give conditional rows in $[0,1]$ whenever the parent probability is positive. Vacuum supplies a simple counterexample to strict positivity: click probability is exactly zero.

For target parent assignments of zero probability, $P(x_i\mid x_{S_i})$ is undefined. The current implementation explicitly fills such rows with no-click probability one; this is a normalized convention, not a uniquely determined target conditional. A preceding approximation can, in general, assign mass to parent configurations forbidden by the target. Future diagnostics should record whether undefined rows are reached.

Numerical inclusion–exclusion can also suffer cancellation. The current local compiler asserts nonnegativity and normalization instead of silently clipping negative masses. Exact formulas are not an unconditional finite-precision guarantee.

### 3. Villalonga includes more than its Boltzmann sampler

[Villalonga et al.](https://arxiv.org/html/2109.11525) present a TAP/mean-field Boltzmann generator with Gibbs sampling **and** a separate greedy batch generator. The latter is not MCMC; its records are not generally IID. Our fixed-table ancestral generation avoids those particular dependencies, but does not automatically establish an end-to-end speed win over both methods. Include compilation and compare achieved accuracy.

### 4. Dodd already has an operational record generator

Truncated reconstructions need probability handling, but this does not make the published comparator an invalid sampler. The pinned FrugalGBS CPU implementation used in our study includes `clamped_prob` guards and a working sequential bit generator. Its approximation bias and repairs should be measured rather than characterized as a hurdle nobody has solved.

Our exact-subset tables provide a cleaner local probability construction. That is a useful property, but not by itself a measured accuracy or runtime victory. The existing benchmark already compares the implemented laws and finds much lower dense-circuit TVD for fifth-order Dodd.

**Implementation evidence:** FrugalGBS commit `fa8b796f2afebd4845a2e335e457735952617ef8`, `include/fgbs/cpu/cpu_sampler.hpp`, `clamped_prob` and `update_result`; [author repository](https://github.com/tomdodd4598/FrugalGBS). [Benchmark and limitations](GBS%20Mechanism%20Smoke%20Benchmark.md).

### 5. Sparse parents are not automatically a Chow–Liu optimum

For $b=1$, our fixed-order procedure produces a tree or forest-type factorization. Unrestricted Chow–Liu selects a maximum-weight spanning tree first and then orients it. Fixing an ordering beforehand can exclude that optimum. Nor is our top-MI final-parent heuristic a direct implementation of Friedman's full iterative algorithm. These are appropriate baselines, not identical descriptions.

The accurate structural term is **bounded indegree**. A detector can be a parent of many later detectors, so outdegree and global graph treewidth need not be bounded.

### 6. Ordering matters, but random ordering is not proved to fail

The representation depends on detector order. However, a dense Haar-random interferometer has no inherent geometric detector neighborhood that random ordering necessarily destroys. The assertion that a random ordering will likely fail is not established by the supplied sources. Test ordering sensitivity and include its selection cost.

### 7. A global exact bound has not become a scalable certificate

For fixed parent sets and natural logarithms,

$$
D_{\rm KL}(P\Vert Q)=\sum_i I_P\!\left(X_i;X_{<i}\setminus S_i\mid X_{S_i}\right).
$$

This standard chain-rule identity explains the actual approximation error. Computing its full-history terms can be as difficult as the reference problem. A bound expressed through inaccessible terms is useful analysis, but not an efficient GBS certificate.

Exact local conditionals also do not ensure that every chosen family marginal is preserved under $Q$: $Q(x_i,x_{S_i})=Q(x_{S_i})P(x_i\mid x_{S_i})$, and the parent marginal can drift. In the one-parent forest limit, exact root and parent-child tables do preserve the node and selected edge marginals by induction; that makes the tree comparison especially informative.

## Compilation and fair comparisons

The compiler evaluates all subset vacuum probabilities for each local family once, then uses a subset transform. It need not recompute every vacuum subset separately for every output pattern. A straightforward cost estimate is

$$
O\!\left(M^2+M(b+1)^3 2^{b+1}\right)
$$

for pair screening and determinant work, plus selection/bookkeeping and transform costs. Conditional-table storage is $O(M2^b)$; the dense input covariance and pair-score matrix add $O(M^2)$ storage. Gathering parent bits gives $O(Mb)$ work per record. These are arithmetic estimates for the specified implementation, not proof that the necessary $b$ stays small at fixed error.

Outperforming every competitor, proving a universal theorem, optimizing every ordering, or using exactly 50 modes is not a blanket prerequisite for novelty. The evidence must support the scope claimed. A useful new niche, construction, or measured frontier can be a contribution; a general scalable guarantee requires stronger evidence.

## Next bounded validation pass

Keep the current mechanism, and target the question: **does exact-marginal detector-context compilation add a useful GBS-specific tradeoff beyond standard graphical approximations and existing GBS emulators?**

The next comparison should add:

1. An exact-Gaussian-marginal Chow–Liu baseline, fixed-order one-parent control, and random/recent-parent controls.
2. A conditional-information parent selector, with all extra Gaussian queries charged to preparation. Treat it as a standard comparator, not an automatically novel invention.
3. A small set of predeclared detector orderings evaluated separately from held-out selection; compare equal widths and common full-TVD tolerances.
4. Faithful Villalonga greedy/TAP baselines, alongside the existing original Dodd CPU implementation and qualified Goodman ports.
5. A modest accuracy-controlled size extension where exact references are affordable, plus separate large-size marginal diagnostics. Do not label marginal agreement full-distribution fidelity.

Record undefined conditional rows, numerical repairs, preparation, warm and cold costs, batch counts, memory, and unfavorable cells. Do not rerun the entire earlier study merely to add these controls; reuse its immutable measurements where compatible. No new experiments were launched during this synthesis.

**Working claim:** a potentially original exact-marginal, information-selected, bounded-parent GBS emulator with a measured small-system many-record benefit. Its physical approximation guarantee and exact novelty remain unresolved. Develop the complete GBS contribution rather than claiming invention of Bayesian networks or assuming that loss has already proved the sparse-context hypothesis.

## Evidence provenance

The two attached reviews remain in the original user attachments. [Review provenance and hashes](outputs/novelty_review_synthesis_v1/provenance.json) identify the texts inspected. Assessment C is the user's pasted “Methodological Breakdown and Prior Art” text.

Assessment A's Springer link is Cooper–Herskovits, despite being used repeatedly for Friedman claims; its JAIR link resolves to Yuan–Malone's 2013 *Learning Optimal Bayesian Networks: A Shortest Path Perspective*, not the 1992 K2 original. It also attaches a Friedman arXiv link to Dodd discussion and a Lee link to threshold-probability attribution. The corrected argument uses verified primary papers, not those mismatched citations.

This is a synthesis of supplied reviews with targeted factual verification. It is not a new exhaustive literature search, a human peer review, or a proof of priority.
