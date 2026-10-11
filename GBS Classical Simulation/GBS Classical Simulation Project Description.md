# Evaluating Classical Simulation and Validation of Gaussian Boson Sampling

**Status (October 2, 2026):** First selective-correction study completed on 144 synthetic 6-, 8-, and 10-mode instances, including 108 held-out cases. A residual-based selection rule reduced mean full-distribution TVD by 37.2% relative to pairwise maximum-entropy fitting, but was less accurate than uniform third-order fitting in every held-out case. The architecture still enumerates all bit strings; scalable sampling and experimental benchmarking remain open. See [[First Research Draft]] for the full result, measured costs, failures, and publication assessment.

**Active research direction (October 3, 2026):** The grant-facing question is now a direct, independently reproducible test of the published positive-P phase-space sampler on the 8,176-mode Jiuzhang 4.0 L1024 configuration it explicitly left for future work. The question, literature gap, fixed evaluation metrics, matched resource protocol, preliminary evidence boundary, and stop/go gates are in [[Jiuzhang 4 Phase-Space Challenge Research Specification]]. The specification is a research plan; this Jiuzhang-scale reproduction has not yet been run.

**Resource-aware path (October 11, 2026):** Without a grant, begin with a small-system audit of that published sampler, using exact threshold-click distributions to test where its approximations and validation statistics are reliable. Reproducing a published larger benchmark is the next gate; Jiuzhang 4.0 is a contingent scale-up, not a requirement for the small-system study to produce a useful result. No new positive-P reproduction or audit result is claimed here.

**Skeptical audit update:** Independent Torontonian calculations confirmed the reference probabilities, but a stronger omitted exact baseline strictly outperformed the selected approximation on error, preprocessing time, and traced memory in 102 of 108 cases. The current enumerated implementation is therefore a **no-go as a computational improvement** on this grid. The 37.2% error reduction remains an information-allocation finding, not evidence of a cheaper practical simulator. [[Skeptical Audit and Stronger Benchmarks]] supersedes the first draft's performance interpretation and records stronger controls, repeated random trials, and matched timing measurements.

**Research area:** quantum information science, quantum photonics, classical simulation, and statistical validation of sampling experiments.

**One-sentence objective:** Independently test the accuracy and full computing cost of classical GBS sampling methods, beginning with Goodman et al.'s positive-P sampler, and determine when accessible validation statistics do or do not reflect sampling fidelity.

This is the full project description. [[Correlation-Based Classical Simulation of GBS]] contains the shorter research plan and initial evidence. [[First Research Draft]] records the completed first selective study. [[Quantum Research]] is the vault index.

## Grant-facing summary

Goodman et al. argue that their approximate positive-P sampler should extend to Jiuzhang 4.0, but they did not test that experiment. This project will independently examine the method's fidelity, validation scores, and end-to-end resource cost. A no-grant first stage will compare its threshold-click samples with exact distributions on tractable optical systems, including regimes where published-style diagnostics may miss errors. A faithful reproduction of a reported larger benchmark is the gate to any Jiuzhang 4.0 extension, which depends on calibrated inputs and sufficient compute. The completed selective-correlation study supplies small-system experience but does not establish the positive-P sampler's performance or an experimental-scale result.

## 1. The system and the computational task

**Technical description.** Gaussian boson sampling (GBS) prepares squeezed optical input states, mixes them through a linear interferometer, and measures the outputs. In the threshold-detector setting considered here, each output mode produces a binary result: click or no click. For $M$ measured modes, one shot is a string $x=(x_1,\ldots,x_M)\in\{0,1\}^M$. A characterized Gaussian optical model defines a target probability distribution $P(x)$ over these strings. Its covariance matrix has a compact description, but calculating or sampling from the complete click distribution can be computationally demanding at experimental scale. Exact threshold-click probabilities can be calculated at small scale using Gaussian-state vacuum probabilities or the Torontonian formalism [1].

**In plain language.** The photonic device repeatedly produces a long string of yes/no detector readings. The research question is whether a conventional computer can generate strings with sufficiently similar probabilities, and how much time and memory that requires. This project concerns the *software calculation* of those strings, not building or modifying optical hardware.

**Important distinction.** The ideal lossless optical model, a calibrated model that includes known experimental imperfections, and the observed hardware samples are three different objects. A simulator may aim to approximate the calibrated model, to reproduce a chosen set of hardware statistics, or both. Those goals must be stated separately in every comparison.

## 2. Why approximations are needed

**Technical description.** A full distribution over $M$ binary outputs has $2^M$ possible patterns. Some classical methods avoid manipulating all of them by matching lower-order marginals or connected correlations, also called *cumulants*. Examples are the click probability of detector $i$, the probability that detectors $i$ and $j$ click together, and analogous quantities for small groups. Villalonga and colleagues constructed efficient samplers from low-order information [2]. Dodd and colleagues precompute cumulants through an order $K$ and use them in a sequential sampling procedure; their cost depends strongly on $K$, and they describe the choice of $K$ as heuristic [3]. Other methods, such as matrix product states, compress different aspects of the quantum state and have their own accuracy–cost parameters [4]. Recent phase-space-based sampling provides another competing approach that a later algorithmic claim would need to benchmark [6].

**In plain language.** Instead of reproducing a huge table of every possible detector pattern, a fast program learns or calculates a smaller set of clues about the patterns. This can be extremely useful. The risk is that the chosen clues may not contain all the information needed for the particular claim being made.

**What is already known.** The cited authors discuss truncation and its limitations. The mere statement that “low-order correlations do not determine the entire distribution” is therefore background, not this project's discovery. Jiuzhang 4.0 also tested and rejected one simple low-order greedy sampler using higher-order statistics [5]. Any new method must address that stronger comparison.

Sections 3–7 retain the original selective-correction question, pilot, and proposed evaluation as a research record and possible later extension. The active near-term sequence is in Section 9 and [[Jiuzhang 4 Phase-Space Challenge Research Specification]].

## 3. Original selective-correction question

**Technical description.** Existing approximation methods create an unresolved *allocation problem*: which correlations, conditional dependencies, or state features should be calculated when computing all of them is too expensive? A uniform cutoff includes every term through order $K$ and excludes every term above it. Yet terms of the same order need not contribute equally to the accuracy of a particular sampler or observable. The project will test whether a small, selected set of additional dependencies improves the full sampling distribution more per unit of computational cost than simply raising a uniform cutoff.

Let $Q_{\mathcal S}(x)$ denote a classical sampler using a selected set $\mathcal S$ of corrections. On small systems where $P$ is known, the primary error measure can be total variation distance (TVD):

$$D_{\mathrm{TV}}(P,Q_{\mathcal S})=\frac12\sum_x\left|P(x)-Q_{\mathcal S}(x)\right|.$$

For a candidate correction $S$, a direct small-system measurement of its marginal value is

$$\Delta_S=D_{\mathrm{TV}}(P,Q_{\mathcal S})-D_{\mathrm{TV}}(P,Q_{\mathcal S\cup\{S\}}).$$

The improvement $\Delta_S$ must be weighed against the extra preprocessing time, memory, and per-sample runtime. A practical method should improve the **accuracy–cost frontier**, not just accuracy with unlimited additional computation. Candidate corrections may interact, so testing them one at a time is a starting diagnostic rather than a guarantee that individually ranked terms form the best combination.

**In plain language.** If a computer can afford only a limited number of extra calculations, which ones help most? We will compare the improvement from each candidate with its price. Some calculations may look impressive but give little benefit; others may correct a pattern that the fast simulator repeatedly gets wrong.

**Why ordinary partial derivatives are not the whole answer.** Differentiating accuracy with respect to physical settings such as squeezing or photon loss answers a different question: how sensitive is the *experiment or model* to those settings? Differentiating with respect to continuous weights inside a simulator can help tune those weights. But adding a new three- or four-detector dependency is a discrete design choice. Controlled add/remove tests and cost-matched comparisons are the clearest initial tools. Physical-parameter sensitivity can later help identify regimes where the simulator is fragile, but it should not be confused with selecting simulator features.

## 4. Original proposed method: budgeted correlation selection

**Technical description.** The working algorithmic hypothesis is a *selective correction* to a valid, normalized baseline sampler. One possible implementation is:

1. Fix a characterized GBS instance, including its interferometer, squeezing parameters, transmission/loss model, detector type, and whether results are conditioned on total click number.
2. Build a baseline classical sampler using a tractable approximation, initially an independent or pairwise model. Compare later with a faithfully implemented published method if its code and computational needs permit.
3. Generate a limited list of candidate higher-order detector groups. Potential shortlist rules include optical connectivity, strong pairwise dependence, or low-dimensional marginal discrepancies. The shortlist must be cheap enough that searching it does not erase the proposed speed benefit.
4. Calculate exact *small-subsystem* statistics for shortlisted groups from the Gaussian covariance description where feasible. Use these to estimate which corrections are likely to matter. Do **not** use the held-out full distribution to choose corrections on evaluation instances.
5. Add the selected information through a sampling rule that remains a normalized, nonnegative probability distribution. The first study implemented an exponential-family factor model with an enumerated partition function and independent table sampling. A practical larger-system architecture still needs to be chosen and tested; a normalized sequential conditional sampler or a factor model with validated approximate fitting/sampling remains a possibility.
6. Stop when the computational budget is reached. Compare against the uncorrected baseline and a uniform increase in correlation order using matched resource limits.

An example ranking statistic is predicted reduction in validation error divided by added runtime or memory. The *prediction rule* should be developed on training instances and then frozen before held-out evaluation. On small held-out instances, the exact full distribution is used only to measure the final outcome. At larger scales, where full TVD cannot be computed, evaluation must use multiple independently chosen diagnostics rather than treating any one score as proof of full-distribution accuracy.

**In plain language.** We start with a fast simulator. We identify a small number of detector relationships it is likely missing, add only those relationships, and check whether the improved simulator justifies the extra work. To make the test honest, we choose the rule for finding those relationships *before* looking at the exact answers for our final test cases.

**Major technical risks.** Selecting useful local correlations may not fix global errors. A corrected probability model may be expensive to sample from even when its list of factors is short. A rule trained on small optical networks may not transfer to larger or brighter ones. These are substantive research questions, not implementation details to assume away.

## 5. Prototype already completed: what was calculated

**Technical description.** The current prototype is an information diagnostic, **not** the proposed selective sampler and **not** a reproduction of Dodd et al. It generated nine exact, eight-output-mode GBS click distributions: three random interferometers for each of three input settings. The settings were four squeezed inputs with $r=0.8$ and transmission $\eta=0.9$; eight squeezed inputs with $r=0.7$ and $\eta=0.7$; and eight squeezed inputs with $r=0.8$ and $\eta=0.9$. Interferometers were drawn by orthonormalizing complex Gaussian matrices with a fixed random seed. Loss was modeled as uniform linear transmission. These choices explore a few small physical instances; they are not calibrated models of Jiuzhang hardware.

For each instance, the code constructed the output Gaussian covariance matrix. It computed the probability that each subset of modes was vacuum, then used inclusion–exclusion to obtain the probability of every one of the $2^8=256$ threshold-click patterns. The probabilities were checked for normalization and nonnegativity within numerical tolerance. This exact distribution served as a small-system reference.

The prototype then fitted a *maximum-entropy* classical distribution

$$Q_K(x)=\frac{1}{Z_K}\exp\!\left(\sum_{\substack{S\subseteq[M]\\1\leq |S|\leq K}}\theta_S\prod_{i\in S}(2x_i-1)\right),$$

where $Z_K$ normalizes the distribution. Its parameters $\theta_S$ were optimized so that the surrogate matched **every** click moment through order $K$ to numerical precision. Because there are only eight modes, the partition function and TVD could both be evaluated by summing all 256 patterns. This construction isolates the question of whether low-order information is sufficient; it does not reproduce the chain-rule architecture or measured performance of any cited paper.

| Highest matched order $K$ | Number of matched features | Mean full-distribution TVD across nine instances | Range across nine instances |
| ---: | ---: | ---: | ---: |
| 1 | 8 | 0.278 | 0.215–0.409 |
| 2 | 36 | 0.142 | 0.098–0.183 |
| 3 | 92 | 0.085 | 0.048–0.119 |
| 4 | 162 | 0.048 | 0.026–0.071 |
| 5 | 218 | 0.026 | 0.013–0.039 |

All 45 fits reported convergence, and the largest discrepancy in a matched moment was below $10^{-7}$. The numerical results show a consistent improvement with order in this small sample, while also showing that very accurate low-order moments do not force a zero full-distribution error. They **do not** establish that a selective correction beats a uniform order cutoff, that a published sampler has these TVD values, or that any experimental advantage claim fails.

The reproducible files are [prototype code](work/gbs_low_order_information_probe.py), [exact-distribution helper](work/gbs_projection_probe.py), and [recorded results](outputs/gbs_low_order_information_probe.json). The Python code requires NumPy and SciPy. The helper also contains a separate phase-space experiment that was not used to produce the table above.

**In plain language.** We made nine small examples for which the computer can know every detector pattern's correct probability. We forced a simplified simulator to match all the one-detector, then two-detector, then higher-group statistics. Its answers improved, but matching those statistics was not the same as matching every pattern. This is evidence that the question is measurable, not evidence that our proposed fix works.

## 6. A separate scaling check

**Technical description.** If an algorithm explicitly stores every correlation through order $K$, it needs at least $\sum_{j=1}^{K}\binom{M}{j}$ entries. A four-byte array through order five needs about 2 GB for 144 modes and about 1.22 exabytes for 8,176 modes, before auxiliary indices or working memory. The 144-mode estimate agrees in scale with the cumulant array reported by Dodd et al. [3]. The calculation is preserved in [scaling code](work/gbs_cumulant_scaling_probe.py) and [recorded counts](outputs/gbs_cumulant_scaling_probe.json).

**In plain language.** A method that calculates *every* group of up to five detectors works with a manageable list at 144 outputs. That list explodes when the device has thousands of outputs. This motivates asking whether a carefully chosen small subset can retain the useful information.

**Boundary.** This is a storage estimate for one explicit dense representation. It is not a lower bound on all classical GBS simulation. Compression, sparse or on-demand calculations, other algorithms, and changed target accuracy can alter the cost. It also does not show that selected fifth-order terms will be sufficient.

## 7. Original selective-correction evaluation plan

**Technical description.** The original plan called for predeclared families of exact small GBS instances. It would vary mode count, source count, squeezing, transmission, and possibly circuit structure one factor at a time where feasible. Separate instances would develop and evaluate the selection rule. For every held-out case, the proposed method would be compared against at least (a) its uncorrected baseline and (b) a uniform higher-order method at comparable cost, retaining unsuccessful and inconclusive cases.

The primary small-system endpoint is full TVD to the exact characterized distribution. Secondary endpoints are click-count distribution error; marginal and connected-correlation errors by order; performance within fixed-click sectors; preprocessing time; peak memory; and per-sample generation time. If actual experimental data become available, compare samplers and hardware on the *same* declared statistical tests, sample sizes, conditioning rules, and optical calibration. A favorable low-order score alone is insufficient for a claim of full sampling accuracy.

The main success criterion is a **Pareto improvement**: across held-out physical GBS instances, the new method obtains lower distribution error than a named baseline for equal or lower measured cost, or the same error at lower cost. A larger-scale quantum-advantage challenge would require an implemented sampler that remains competitive on the relevant experiment's task and validation tests. A negative outcome is also interpretable: the selected corrections may fail, fail to transfer, or cost as much as a uniform cutoff.

**In plain language.** This earlier plan would judge a selective-correction method on examples it was not tuned to, using both accuracy and computer resources. Its scientific value would be a clear answer about when targeted corrections help, including a reproducible negative result.

## 8. Research significance and possible scale

**Technical description.** The near-term output is a controlled map of when the published positive-P sampler's threshold-click distribution agrees with exact small-system references and when its accessible validation statistics detect or miss errors. This tests the sampler's projection and correction steps without requiring an experimental-scale run. A subsequent published-benchmark reproduction would check implementation fidelity before any Jiuzhang 4.0 claim. An original sampler remains an optional extension, evaluated only against matched accuracy and resource baselines. The completed selective-correlation prototype is prior evidence about information allocation, not evidence that the positive-P method has been reproduced.

**In plain language.** The first useful question is whether the classical method gives the right answers in small cases where the complete answer can be checked. That study can be performed with modest local resources and can identify a concrete reliability boundary even if the largest experiment remains out of reach. A paper or a quantum-advantage challenge would still require a novel, reproducible finding and claims matched to the tests actually completed.

## 9. Next decisions and near-term work

The earlier selective-correction study compared pair-ranked and residual-ranked triple selection with random selection, uniform third-order fitting, and uncorrected models on 36 development and 108 held-out synthetic instances. Its measured runtime, traced memory, and unfavorable cases are retained in [[First Research Draft]]. It did not reproduce Goodman et al.'s method or use a calibrated Jiuzhang model.

The selective method reduced mean TVD from 0.10575 to 0.06641. Uniform third-order fitting reached 0.05269. Selection therefore establishes an intermediate accuracy–cost tradeoff, not a strict improvement over both baseline endpoints or a better large-system published sampler. The initial implementation cannot scale because it enumerates $2^M$ outcomes.

The resource-aware next work is:

1. Audit the public code, method description, and required inputs. Implement or run the published positive-P threshold sampler faithfully enough to reproduce its projection and whitening–coloring steps; record missing details rather than treating an inferred choice as published method.
2. On tractable 6-, 8-, and 10-mode instances, compare generated click records with independent exact threshold distributions. Vary squeezing, loss, and circuit structure using frozen development and held-out cases. Measure full-distribution TVD where feasible, published-style count and correlation scores, sampling uncertainty, and the effects of individual approximation steps. This is the no-grant core.
3. If the small-system implementation checks pass, reproduce at least one reported Jiuzhang 2 or 3 benchmark with its stated optical model, output format, validation definitions, and sample count. Reduced-shot runs are pilots, not full reproductions. Record setup, sampling, and peak memory separately and in an end-to-end total.
4. Attempt Jiuzhang 4.0 only if the published-benchmark gate passes, the calibrated inputs are available, and a pilot shows that the required sample count fits a declared resource budget. If a gate fails, report the measured boundary rather than substituting an easier target without disclosure.

**Reach task — develop and benchmark an original sampler.** After the primary independent reproduction and stress test of Goodman et al.'s positive-P method, survey the strongest current GBS samplers and identify a specific, testable limitation. If the evidence supports a promising approach, design and implement a new or substantially improved classical sampler and compare it with Goodman et al. and other relevant published methods on the same characterized optical model, detector outputs, sample counts, accuracy criteria, and complete time and memory costs. Use held-out configurations and report unfavorable results. A measured improvement could strengthen a challenge to a particular experimental quantum-advantage claim, but this exploratory task is not a promised algorithmic result or part of the current reproduction's success criteria; agreement on selected statistics alone would not establish full-distribution equivalence.

The first decision may change the final title or target system. The stable objective is an evidence-backed account of what the classical method reproduces, what it misses, and what resources it requires.

## Sources

1. [Quesada, Arrazola, and Killoran, *Gaussian Boson Sampling using threshold detectors*](https://arxiv.org/abs/1807.01639).
2. [Villalonga et al., *Efficient approximation of experimental Gaussian boson sampling*](https://arxiv.org/html/2109.11525).
3. [Dodd et al., *A fast and frugal Gaussian Boson Sampling emulator*](https://arxiv.org/html/2511.14923).
4. [Oh et al., *Classical algorithm for simulating experimental Gaussian boson sampling*](https://arxiv.org/html/2306.03709).
5. [Jiuzhang 4.0 experimental paper, *Robust quantum computational advantage with programmable 3050-photon Gaussian boson sampling*](https://arxiv.org/html/2508.09092).
6. [Goodman et al., *Gaussian boson sampling: Benchmarking quantum advantage*](https://arxiv.org/html/2604.12330).
