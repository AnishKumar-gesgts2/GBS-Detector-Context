# GBS mechanism smoke benchmark

**October 11, 2026. Measured feasibility screen; synthetic circuits, single-thread CPU.**

## Decision

**Pursue positive bounded detector context for moderate-error, many-record sampling.** It already has a measured advantage at a common accuracy threshold on most of the tested eight- and ten-mode random circuits. **Keep exact Gaussian product-core decomposition as a structured-circuit specialization.** Reject the present generic block approximation and source-compression backend as competitive implementations in this small-system regime.

There is **no general winner against fifth-order Dodd** and no evidence that ordinary polishing will close the accuracy gap. The Goodman comparisons use transparent equation ports, with both frozen-calibration and paper-style batch-correction versions; they are not execution of the authors' MATLAB implementation. No hardware-scale quantum-advantage claim or algorithmic novelty claim follows.

This benchmark supersedes the unmeasured competitive comparisons in [[GBS Mechanism Selection After Feasibility Review]]. The earlier supplied conditional-cumulant code failed elementary limits; it was not used as a baseline here.

## What was built and checked

| Mechanism | Prototype implements | What could make it cheaper | Principal cost or error |
| --- | --- | --- | --- |
| Conditional information / graphical models | Sequential threshold records from exact probabilities conditioned on 2, 4, or 6 selected earlier detectors; parents selected by pair mutual information | Compile small probability tables once; generate each record with lookups | Ignored detector history changes the law; table cost grows exponentially with context width |
| Quantum source compression | Exact pure-residual-plus-classical-displacement decomposition; retain 2 or 4 residual squeezed sources; determinant-lemma vacuum queries and sequential threshold sampling | Small residual source rank reduces determinant size | Inclusion–exclusion over preceding clicks remains expensive; weak-source removal changes the target |
| Gaussian block separability / convex optimization | Seek 2- or 4-mode physical Gaussian blocks plus correlated positive classical displacement noise | Sample small quantum blocks independently given the shared displacement | Dense random circuits require substantial added covariance noise to fit this representation |
| Explicit product core | Analytic exact decomposition for eligible real interferometers; one-mode quantum cores plus correlated displacement | Remove the general optimization and multi-mode conditional sampling | A restricted, already structurally easy Gaussian family; not general complex Haar mixing |

All record-generation paths avoid constructing the full output distribution. Fixed local block/context enumeration is allowed. Global enumeration is reserved for scoring small systems. Source compression is not a polynomial-time sampler merely because its determinant matrices have low rank.

### Published competitors

**Dodd:** the authors' actual FrugalGBS C++ CPU sampler at cumulant orders 3 and 5, pinned to `fa8b796f2afebd4845a2e335e457735952617ef8`. A thin wrapper supplies the covariance, requests original record generation, and exports coefficients. Exact small-system scoring follows forced bit paths through the original marginal-update helpers, including their probability clamping. A 200,000-record check agrees with this induced law at normal sampling error. The original generation code was not replaced with our earlier incomplete cumulant implementation. [Paper](https://arxiv.org/html/2511.14923), [author code](https://github.com/tomdodd4598/FrugalGBS).

**Goodman:** ports of threshold projection and ten whitening–coloring iterations, using analytic target phase-space moments. Both centered covariance and literal uncentered second-moment readings of Eq. 11 are tested. Negative eigenvalues of the target phase-space moment matrix use complex spectral roots before real projection; this is not a silent positive-semidefinite repair. The main benchmark learns transformations on 16,384 independent latent samples and freezes them, permitting IID outputs and a well-defined distribution for scoring. A separate sensitivity experiment recomputes transformations on each requested batch, closer to the paper's ensemble procedure. This changes costs and introduces possible within-batch dependence. [Paper, Eqs. 8 and 10–12](https://arxiv.org/html/2604.12330).

The retrieved [xqsim repository](https://github.com/peterddrummond/xqsim), commit `32609f3644ae18bff872b53a32a3a7f58f883b3b`, provided older phase-space routines; the new projected whitening sampler was not located in that checkout. MATLAB/Octave was unavailable. These results therefore compare mechanisms and our stated ports, not the published MATLAB program's performance.

## Fixed experiment and accuracy measurement

The main run has **429 completed circuit–method rows and zero failed rows**: 36 fresh complex-Haar circuits plus three real-orthogonal controls, each with 11 methods. Sizes are 6, 8, and 10 modes. Transmission is 0.3 or 0.5 for Haar circuits (70% or 50% total loss), and 0.4 for the real controls. Profiles are two strong sources with a weak tail, flat squeezing 0.7, and flat bright squeezing 1.0. Source squeezing axes and covariance convention are consistent across competitors.

These seeds differ from the earlier exploratory screen. Mechanisms and parent-selection policy were fixed without fitting to these circuits' exact reference errors. Only two circuits per size/profile/loss cell were used: this is a bounded feasibility screen, not statistical coverage of all Haar instances. No threshold was tuned per case using its reference distribution.

Exact references use all-subset vacuum probabilities and a Möbius transform. Candidate induced distributions are exact for Dodd's implemented update, context tables, and Gaussian target covariances of source/block methods. Goodman frozen-map distributions use two independently scrambled Sobol integrations with 32,768 points each; 22 uncertain rows were refined to 131,072 points each. The maximum remaining replicate-distribution TVD is 0.01037, mostly in structured controls. Replicate spread is a sensitivity diagnostic, **not a rigorous confidence interval**. Unrefined originals remain available.

Primary accuracy is full total variation distance:

$$
\operatorname{TVD}(P,Q)=\frac12\sum_x |P(x)-Q(x)|.
$$

A TVD limit of 0.02 bounds the difference in probability assigned to any event by 0.02. It does not mean every individual probability is accurate to 2% relative error.

Published-style diagnostics are also recorded: click cumulants through order 5 with RMSE, maximum error, correlation, and slope; total-count and two-group count distributions; per-click-sector conditional TVD; Goodman-style logarithmic cross entropy; and Dodd-style linear probability-overlap ratio. The latter two have different definitions and are retained separately. Pearson discrepancy per shot is a systematic distribution discrepancy, not an experimental chi-squared p-value. None of these synthetic values is presented as a reproduced Jiuzhang score.

Requested batches are 1,000 and 10,000 records, with three generation timing repeats and rotating method order. The report uses one measured setup plus median generation time. Reference scoring is excluded. Native kernels are warmed/cached, so these are **operational batch costs**, not Python/Numba first-launch latency. Setup itself was measured once per row; small timing differences should not be overinterpreted. BLAS/OpenMP use one thread on the local Ryzen 9 7950X machine.

## Main accuracy–speed comparison

The following are medians across the **12 ten-mode complex-Haar circuits**, including setup and 10,000 records. Medians summarize different cells; they do not alone prove matched-accuracy superiority.

| Method | Full TVD ↓ | Total seconds ↓ | Interpretation |
| --- | ---: | ---: | --- |
| Dodd order 3 | 0.01465 | 0.02658 | Strong moderate-accuracy comparator |
| Dodd order 5 | **0.00250** | 0.05163 | Most accurate tested dense-circuit approximation |
| Goodman centered frozen port | 0.03131 | 0.03042 | Port with independently calibrated fixed map |
| Goodman literal frozen port | 0.03572 | 0.03632 | Sensitivity to Eq. 11 moment convention |
| Context 2 | 0.05845 | **0.00418** | Fast, too inaccurate for a 0.02 target |
| Context 4 | 0.03287 | 0.00571 | Useful when tolerance is looser |
| Context 6 | 0.01683 | 0.01019 | Best general-circuit candidate here |
| Retain 2 residual sources | 0.05792 | 0.21802 | Reduced quantum rank does not offset sampling cost |
| Retain 4 residual sources | 0.04640 | 0.34936 | More accuracy, still slower |
| Gaussian blocks of 2 | 0.25524 | 0.38637 | Approximation error and setup both excessive |
| Gaussian blocks of 4 | 0.25444 | 0.40591 | Larger blocks do not rescue this implementation |

![Measured accuracy–speed comparison](outputs/smoke_comparison_v1/comparison.png)

### The requested 75% screen

We operationalized a provisional pass as **at least 75% of competitor throughput and at most 1.25 times its TVD**, using total batch cost. These are two distinct quantities; there is no meaningful single percentage of algorithm quality.

Across the **24 eight- and ten-mode Haar circuits**, context 6 passes against Dodd order 3 in **19/24**, against order 5 in **0/24**, and against both frozen Goodman ports in **24/24**. Context 4 passes in 2/24, 0/24, and 21/24 against order 3, order 5, and centered Goodman respectively. Source and block variants pass in zero cases against each comparator. The Goodman pass counts remain unchanged under a conservative variation by half the two-integration distribution spread; that variation is not a statistical certification.

Six-mode context 6 is a full-history exact control and is excluded from these development claims. At eight modes, a six-parent context still uses seven-mode marginals and is near-global. Therefore the favorable small-system screen does not establish that width 6 suffices at hundreds of modes.

### A stronger decision: same allowed error

At each fixed TVD tolerance, compare with the fastest tested published-method implementation that also meets it on that same circuit. This is a **common tolerance**, not identical achieved errors.

| Candidate | TVD ≤0.005: qualifying / faster | TVD ≤0.02: qualifying / faster | TVD ≤0.05: qualifying / faster |
| --- | ---: | ---: | ---: |
| Context 4 | 0 / 0 | 6 / 6 | 24 / 24 |
| Context 6 | 6 / 6 | **21 / 21** | 24 / 24 |
| Retain 2 sources | 1 / 0 | 8 / 0 | 11 / 0 |
| Retain 4 sources | 3 / 0 | 8 / 0 | 14 / 0 |
| Blocks 2 or 4 | 0 / 0 | 0 / 0 | 0 / 0 |

Each denominator is 24. Context 6 has a median **1.94× total-cost speedup** among its 21 qualifying wins at TVD ≤0.02. Three cases fail that accuracy limit. Its successes at 0.005 are confined to near-global eight-mode contexts; they do not overturn its 0/24 relative-accuracy pass rate against fifth-order Dodd.

On six ten-mode Haar circuits at **100,000 records**, context 6 meets TVD ≤0.02 in all six and has a median **17.53×** total-cost speedup over the fastest qualifying frozen-port/Dodd comparator. This measured amortization is its most useful niche. It does not extend to high-precision targets. The bulk supplement reuses a subset of benchmark circuits rather than adding independent accuracy evidence.

### Goodman batch-correction sensitivity

On the same six bulk Haar circuits, the paper-style centered batch port takes median total times **0.00222, 0.01170, and 0.21993 seconds** for 1,000, 10,000, and 100,000 records. The literal version takes 0.00257, 0.01233, and 0.22087 seconds. This is substantially cheaper than frozen calibration for small requests, and makes the speed comparison workload-dependent. Context setup can lose to this port at 1,000 records.

For these batch ports, pooled empirical histograms from three 100,000-record batches give median TVDs 0.03617 and 0.03755. An exact-target IID histogram at the same pooled count can itself have TVD as large as approximately 0.022 in the brightest cell. Consequently these empirical values are **not equivalent in precision to the exact-law TVDs** in the main table and cannot certify a strict accuracy ranking. The supplemental cumulant/count/sector diagnostics are retained in the batch artifact. Within-batch dependence is not certified absent.

## Structured-circuit result: a physically exact specialization

For a real orthogonal interferometer with consistently aligned squeezing, write

$$
a_j=1-\eta+\eta e^{-2r_j},\qquad b_j=1-\eta+\eta e^{2r_j}.
$$

Let $a_*=\min_j a_j$. When $\min_j b_j\geq 1/a_*$, the product covariance

$$
V_{\rm core}=\frac12\operatorname{diag}(a_* I_M,a_*^{-1}I_M)
$$

is physical and $W=V-V_{\rm core}$ is positive semidefinite. Draw a correlated classical displacement with covariance $W$, then independently sample each displaced one-mode core. This preserves all output correlations after averaging the shared displacement. It is an exact state decomposition, not a replacement of correlations by independent thermal light.

The nontrivial supplement uses varying squeezings 0.45–0.8, ten modes, real random interferometers, and transmissions 0.3, 0.4, 0.5. The sufficient condition holds in all three cases. Target covariance matches exactly in floating-point arithmetic; direct distribution scoring gives zero target-TVD by construction. Independent sample-law checks, rather than this target identity alone, validate record generation.

For 100,000 records the explicit prototype takes **0.179–0.189 seconds**, versus Dodd order 5 at **0.435–0.446 seconds** and centered frozen Goodman at **0.220–0.232 seconds**. This is about **2.4× faster than the tested order-5 Dodd build** while preserving the exact Gaussian target. General SDP construction attains essentially exact target accuracy in this family but costs roughly 0.43–0.62 seconds, showing why the analytic construction matters.

This is a useful specialization, **not yet a novel research contribution**. Product Gaussian cores, classical displacement mixtures, and Gaussian separability are established ideas. The family is structurally easy and excludes generic complex Haar interferometers. A paper would need a meaningful new eligibility criterion, broader circuit family, or demonstrable practical benefit beyond this known sufficient construction.

## Larger timing probes and memory

Timing-only probes at 16, 24, and 32 modes confirm that generation runs without global output enumeration. At 32 modes, flat complex-Haar circuits take 0.0584 seconds for context 6 versus 4.971 seconds for fifth-order Dodd, for setup plus 1,000 records. **There is no measured matched accuracy at these sizes.** A 16-mode exhaustive scorer was halted after roughly 235 CPU seconds to respect the resource bound; its partial results were not used.

For the eligible real family, the sufficient decomposition remains algebraically exact at larger sizes. At 32 modes and 10,000 records the explicit product core takes 0.0659 seconds, centered frozen Goodman 0.2031 seconds, and fifth-order Dodd 14.8445 seconds. This is a restricted-family cost observation, not evidence about a difficult hardware experiment. No large-system floating-point error certificate was established.

Isolated ten-mode Python workers have peak process resident memory of about **119 MiB for Dodd 5, 164 MiB for centered Goodman, 152 MiB for context 6, 231 MiB for source 2, and 205 MiB for blocks 2**. The common Python/import baseline is about 118 MiB. These include dependencies, cache loading, and output buffers; they are not standalone C++ executable footprints. Context tables are small, but context is not the lowest-RSS implementation here. Native Dodd persistent storage was not instrumented: the raw artifact's default zero means **missing**, not zero storage.

## Validity, limitations, and next decision

The author-code cumulants agree with independent exact cumulants to $1.90\times10^{-14}$. Vacuum and independent-detector limits pass. Across the main run, sample-to-own-law histogram TVD is at most 1.17 times the 95th-percentile IID control; this is a sanity check, not a complete distributional proof. A separate 200,000-record varying-source product-core check gives sample TVD 0.01131 versus the largest exact-target IID control 0.01178. Both Goodman batch conventions pass vacuum. Source certificates have no measured violations, source conditional roundoff guards report zero excursions, and the smallest recorded block local probability is positive. Context tables assert positivity and normalization without clipping. Block physicality/noise repairs and approximation noise are recorded separately.

The Frugal frontend was optimized with native CPU flags, but original generation used an SSE2 build: AVX2/native-SIMD bridge attempts crashed under this Windows toolchain. This is a real author-code CPU comparison, with a disclosed build limitation. It does not measure their best SIMD/GPU configuration. Goodman port and language differences similarly preclude a production-performance ranking.

The source prototype achieves median TVDs approximately 0.0094 and 0.0067 on the heterogeneous eight-/ten-mode cells, but is still slower. Retaining fewer quantum sources helps its determinant dimension while leaving a costly click-history expansion. **A different backend would be a redesign, not evidence that this prototype is 75% of a future winner.**

The bounded development decision is:

1. **Go:** detector-context sampling at moderate tolerated error and large batch counts. Next gate: establish an affordable error diagnostic and test whether required context width stays bounded as circuit size grows. Pair mutual information can miss higher-order dependence; it is not an error certificate.
2. **Conditional go:** exact product/block cores for demonstrably eligible structured circuits. First audit novelty and broaden eligibility; do not relabel this easy family as general GBS simulation.
3. **Stop this implementation:** source-rank inclusion–exclusion backend and noise-added small-block approximation on dense Haar circuits. Preserve results and reconsider only with a concrete replacement mechanism.
4. **Do not claim:** likely superiority after polishing, faithful hardware reproduction, a cleared novel algorithm, or a quantum-advantage disproof. The measured advantages already suffice to motivate a narrower proposal; stronger claims need stronger evidence.

## Reproducible artifacts

- [Aggregate results](outputs/smoke_comparison_v1/summary.json), [unchanged main rows](outputs/smoke_comparison_v1/rows.jsonl), [fixed protocol](outputs/smoke_comparison_v1/protocol.json).
- [Higher-precision scoring](outputs/smoke_comparison_v1/accuracy_refinement.json), [bulk and structured supplement](outputs/smoke_comparison_v1/bulk.json), [batch-correction sensitivity](outputs/smoke_comparison_v1/goodman_batch_check.json).
- [Timing-only scale probes](outputs/smoke_comparison_v1/scale.json), [isolated memory](outputs/smoke_comparison_v1/memory.json), [physics checks](outputs/smoke_comparison_v1/checks.json), [supplement checks](outputs/smoke_comparison_v1/supplement_checks.json), [environment](outputs/smoke_comparison_v1/environment.json).
- [Reproduction instructions and limits](work/smoke_benchmark/README.md), [mechanism implementations](work/smoke_benchmark/methods.py), [main runner](work/smoke_benchmark/experiment.py), [analysis](work/smoke_benchmark/analyze.py).

The simulation source, circuit fixtures, and measured results are included in this repository. The [sampler quick start](work/smoke_benchmark/README.md) runs our candidate without the vendor comparison build. Use Git history to identify the published source revision; measurement provenance remains in the saved artifacts.
