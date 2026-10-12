# Proposal: Exact-Marginal Detector-Context Compilation for Classical GBS

**Draft research proposal — October 12, 2026.** Existing results are a smoke study; the work below is proposed development.

The complete [four-page LaTeX proposal and prototype report](proposal/GBS_Algorithm_Proposal.pdf) is formatted for the optional BlueQubit upload. [Source and submission requirements](proposal/README.md) accompany it; the verified page limit is four, including our references.

## Motivation and research question

Experimental Gaussian boson sampling makes classical simulation expensive by generating correlated detector outcomes over a large output space. Existing classical methods compress different parts of this task: low-order marginals and connected correlations, loss-reduced quantum resources, or phase-space representations. The useful question is whether another compression axis can improve the accuracy–cost tradeoff: retaining selected detector history rather than retaining every history variable through a restricted correlation expansion. [Sources](Sources.md) documents these approaches.

We propose to develop a sampler that compiles exact Gaussian subset probabilities into bounded-parent conditional tables and reuses them to produce independent records. **Can physically informed context selection deliver a reproducible computational advantage over strong classical baselines at a common accuracy tolerance, without requiring context width to grow prohibitively with circuit size?**

The initial scope is threshold GBS with 50%–70% photon loss. Photon loss is the only modeled noise in this stage. The broader purpose is to strengthen classical competitors sufficiently to reassess a specific experimental quantum-advantage claim, rather than assume that the claim must fail.

## Proposed method

For an ordered set of $M$ detectors, choose at most $b$ earlier parents per detector and sample from

$$
Q(x)=\prod_i P(x_i\mid x_{S_i}).
$$

Each local conditional is obtained from Gaussian no-click probabilities and an inclusion–exclusion transform on at most $b+1$ modes. The one-time compiler builds a normalized local model; ancestral generation produces IID records from that fixed model. Its bias is caused by omitted conditional dependence.

For exact conditionals on supported parent events, the standard information identity is

$$
D_{\rm KL}(P\Vert Q)=\sum_i I_P\!\left(X_i;X_{<i}\setminus S_i\mid X_{S_i}\right).
$$

This identifies what must be preserved. It does not provide an efficient certificate: the full-history information terms can be expensive to evaluate. Pairwise mutual information is a starting heuristic, not a bound on those omitted terms. The proposed innovation must be demonstrated through the GBS construction, useful selection rules or diagnostics, and measured performance; the identity itself is established statistics.

## Preliminary basis

The current smoke implementation completed 429 comparisons on 39 synthetic circuits. On 24 eight- and ten-mode complex-Haar circuits, context width six meets TVD $\leq0.02$ in 21 cases, with a median 1.94-fold setup-plus-10,000-record speedup against the fastest qualifying tested comparator. A six-circuit 100,000-record supplement gives a median 17.53-fold speedup at that tolerance. These are workload-specific results; the bulk cases reuse existing circuits, and eight-mode contexts are near-global.

Fifth-order Dodd is more accurate on dense ten-mode circuits. Goodman comparisons are equation ports with disclosed calibration choices, not the original production implementation. There is no measured full-distribution fidelity beyond ten modes and no experimental advantage disproof. [Results](Results.md) provides the complete evidence and unfavorable results.

## Work plan: up to three months

| Stage | Work | Deliverable and decision |
| --- | --- | --- |
| Weeks 1–2 | Reproduce the smoke law and probability checks; establish independent calibration and evaluation circuits; specify accuracy tolerances and workloads before tuning | Versioned protocol, portable candidate, and audited comparator setup |
| Weeks 3–5 | Compare pair-MI, conditional-information, recent, random, and exact-marginal tree controls; test a small predefined set of orderings | Accuracy versus complete compilation cost, with selection costs included |
| Weeks 6–8 | Optimize determinant reuse, table construction, memory, and native bulk generation; add faithful Villalonga controls and resolve Goodman convention/build differences where possible | Pareto frontier for setup plus requested records; cold and warm timings; no substitution of ports for author code |
| Weeks 9–10 | Extend exact-scored tests within a bounded resource budget; conduct larger timing and accessible marginal/cumulant diagnostics separately | Evidence about width growth, error mechanisms, and an explicit scalable-certification gap |
| Weeks 11–12 | Apply a validated configuration to a published experimental model and available data; compare its specified validation metrics; document task mismatches | Reproducible report/preprint and a qualified assessment of one advantage claim |

The final hardware-scale step is conditional on model/data access and evidence that the candidate remains useful. Jiuzhang 4.0 supplies a concrete motivating claim. Its large configuration and detector implementation must be represented faithfully before making a claim about it. The grant-period minimum deliverable is a defensible algorithmic contribution and accuracy–cost evaluation; a complete hardware-scale disproof is a reach outcome.

## Evaluation

Full TVD is the primary small-system metric. Compare the fastest qualifying baseline on the same circuit at common limits such as 0.005, 0.02, and 0.05; also report achieved errors. Record total-count distributions, grouped counts, click-sector fidelity, low-order cumulants, and precisely defined probability-overlap/cross-entropy measures. Marginal diagnostics at large size must not be presented as full TVD.

Charge each method for preparation, parent/order selection, calibration or training, requested record generation, and memory. Report install/compile/startup separately, repeat timings, and test both cold requests and amortized bulk workloads. Keep hyperparameter selection separate from held-out evaluation. Report all unfavorable cells and uncertainty from stochastic references.

Probability checks cover vacuum, independent modes, the full-history exact limit, numerical cancellation, undefined conditional rows, and sample-to-own-law agreement. Any clipping, fallback, or repair must be counted and its effect assessed. Exact reference enumeration is restricted to validation and never used to construct the candidate.

## Success and redesign criteria

Continue if the sampler shows a repeatable end-to-end improvement at a predefined fidelity target in a clearly identified regime and remains competitive as system size increases. Retain an algorithm-development question even if a particular experimental claim survives.

Redesign if the width required for acceptable error makes compilation prohibitive, selection costs erase generation savings, unsupported parent assignments become material, or a faithful stronger comparator removes the benefit. Faster code cannot repair omitted-information bias without changing the representation. A smoke result at 75% of another method's performance does not predict that polishing will produce superiority.

## Resources and open outputs

The existing study runs on a desktop CPU. Initial development needs CPU compute and reproducible environments; modest GPU access is useful only for demonstrated batched linear-algebra or baseline acceleration. The resource request should be tied to measured pilot scaling rather than a presumed need for a supercomputer. No IBM QPU is required for the initial classical photonic study.

AI tools can assist source triage, bounded code changes, reproducibility checks, and experiment orchestration. Mathematical correctness, physical assumptions, priority claims, and final interpretation remain subject to independent checks. Public outputs will include source, environments, circuit fixtures or permitted experimental models, full results, limitations, and a report. Personal application answers remain outside Git.

See [Code Description](Code%20Description.md), [Novelty](Novelty.md), and [Sources](Sources.md).
