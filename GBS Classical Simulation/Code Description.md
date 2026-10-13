# Code Description

## Status and design

This code is a **smoke-test implementation of the proposed mechanism**, with comparison and correctness tools. It is not a polished research library or evidence of accurate hardware-scale simulation. The probability model is the same one measured in [Results](Results.md); the October 12 reorganization changes paths/imports and extracts shared functions from historical diagnostic scripts.

The main implementation is Python with NumPy/SciPy for Gaussian calculations and Numba for native record generation. The Dodd comparison calls the original C++ author generator through a thin C interface. The candidate itself needs neither that vendor build nor MATLAB.

## How our sampler works

1. **Represent the optical target.** `gaussian.py` generates a seeded Haar unitary; `methods.covariance` propagates aligned squeezed inputs and uniform photon loss. A supplied covariance can be used instead. Matrices use zero displacement, $\hbar=1$, and quadrature order $(q_1,\ldots,q_M,p_1,\ldots,p_M)$.
2. **Calculate exact local outcomes.** `context_tables.subset_distribution` obtains no-click probabilities on all subsets of a small detector family. For a zero-mean Gaussian state and retained set $A$,

$$
P(\text{no clicks on }A)=\det\!\left(V_A+\frac{I}{2}\right)^{-1/2}.
$$

   An inclusion–exclusion/Möbius transform produces the complete click distribution on that local family. Bit $i$ denotes detector $i$, with click encoded as one.
3. **Choose retained history.** `pair_information` evaluates pairwise detector MI. `prepare` selects at most $b$ earlier detectors with the highest scores, using deterministic tie handling and fixed detector ordering. It divides joint local probabilities by parent probabilities to build each no-click conditional table.
4. **Compile and reuse.** `methods.Context` stores parent indices, counts, and probabilities. `sample_context_kernel` walks the detector order, gathers previously sampled parent bits, looks up one probability, and makes a Bernoulli decision. Fresh random numbers generate independent records from this fixed approximate law.
5. **Score separately.** `gaussian.distribution` and `context_tables.induced_distribution` enumerate small global reference laws only for validation. Candidate generation does not enumerate the global output space. Full-history conditioning is an exact small-system control, not a scalable configuration.

The local compiler asserts nonnegative normalized probabilities. A zero-probability parent row uses no-click probability one as an explicit convention; the target conditional is undefined there. Floating-point cancellation and reached undefined rows need stronger diagnostics before a research release. Global reference calculations permit tiny roundoff negatives within a stated tolerance, then clip and normalize; that reference-side repair is distinct from candidate local-table construction.

## Source map

| File | Responsibility |
| --- | --- |
| [sample_context.py](src/sample_context.py) | Standalone candidate CLI; validates covariance, generates records, saves metadata, and optionally scores systems up to ten modes |
| [methods.py](src/methods.py) | Context kernel and model; comparison adapters; source compression, phase-space ports, Gaussian blocks, and structured product core |
| [context_tables.py](src/context_tables.py) | Exact local distributions, MI selection, conditional tables, and small-reference information diagnostics |
| [gaussian.py](src/gaussian.py) | Haar/symplectic utilities, exact small threshold distributions, independent Torontonian reference, and physicality check |
| [correlations.py](src/correlations.py) | Walsh transform and cumulant reference calculations |
| [experiment.py](src/experiment.py) | Fixed main suite, probability checks, diagnostics, and preparation/record timing |
| [followup.py](src/followup.py) | Bulk requests, structured specialization, timing-only size probes, and isolated process memory |
| [refine_accuracy.py](src/refine_accuracy.py) | Higher-precision frozen-port integration, without retuning the candidate |
| [batch_check.py](src/batch_check.py) | Goodman per-batch correction sensitivity and empirical checks |
| [analyze.py](src/analyze.py) | Aggregate saved measurements and generate the comparison figure |
| [fgbs_bridge.cpp](src/fgbs_bridge.cpp), [build_reference.py](src/build_reference.py) | Bind original FrugalGBS generation and construct a reference-only forced-path evaluator; preserve upstream attribution/license in generated material |
| [benchmark_paths.py](src/benchmark_paths.py) | Shared output-directory configuration; keeps fresh experiment outputs separate from published measurements |

## Prototype boundaries

Fixed ordering and top-pair-MI parents are starting heuristics. No scalable global error certificate, tuned ordering policy, undefined-row usage counter, comprehensive numerical repair policy, GPU context implementation, or arbitrary photon-number detector interface is supplied. Packed records support at most 64 modes in this runner; the context cap is 12 and at most $M-1$. These are implementation/resource limits, not physical sufficiency guarantees.

Numba cache files, personal environments, generated samples, and vendor binaries are excluded from Git. Saved benchmark fixtures and measurements are included. The alternative source/block mechanisms remain to reproduce the measured comparison, including their poor results; they are not the primary proposed algorithm.

## Running and reproducing

The following instructions distinguish the portable candidate from the separate measured Windows baseline build. Read [Results](Results.md) before interpreting any timing ratio. Python dependencies are pinned; the measured environment is in [environment.json](results/smoke_v1/environment.json).

## Run our algorithm on another device

The context sampler needs Python 3.11 or a compatible newer Python, and the minimal dependencies below. It does **not** need FrugalGBS, a compiler, MATLAB, or the comparison DLL. From the repository root, create a Python environment and run:

```powershell
python -m venv .venv
& '.venv/Scripts/python.exe' -m pip install -r 'GBS Classical Simulation/src/requirements-context.txt'
Set-Location 'GBS Classical Simulation'
& '../.venv/Scripts/python.exe' src/sample_context.py --modes 10 --context 6 --shots 10000 --loss 0.6 --check-small --output samples/demo.npz
```

On Linux/macOS use `.venv/bin/python` and ordinary shell directory changes. The code path for our sampler is portable; the separate vendor baseline build below describes the measured Windows build.

`sample_context.py` calls the same `Context` implementation used in the benchmark. It writes packed records, a shot-by-detector click array, the covariance, and compiled tables to an NPZ, with metadata in a neighboring JSON. Existing output files are preserved; choose another filename to rerun. Generated records under the project `samples/` directory are ignored by Git.

To use a saved circuit, replace the generated circuit options with `--covariance path/to/cov.npy` or a benchmark `case_<seed>.npz` containing `cov`. The input convention is **zero mean, hbar=1, all q quadratures followed by all p quadratures**. The parent cap is limited to 12 by this runner and at most $M-1$; that is a resource guard, not a proven sufficient accuracy threshold. Exact-law scoring with `--check-small` enumerates distributions only for separate validation and is restricted to ten modes. Normal candidate generation does not enumerate the global output space.

The demo's first-batch time can include native compilation/cache loading. Use the original benchmark runner for comparable warmed timing. Building a fresh environment or generating demo records does not overwrite published benchmark results.

## Scope and entry points

- `methods.py`: mechanism implementations and thin FrugalGBS binding.
- `sample_context.py`: standalone CLI for our detector-context algorithm, with optional small exact-law scoring.
- `fgbs_bridge.cpp`: calls original author CPU generation; no candidate sampler substitutes for it.
- `build_reference.py`: generates a reference-only forced-bit-path evaluator from pinned author code. It includes the author's MIT license in the generated include. The original record generator remains unchanged.
- `experiment.py`: physics checks, fixed main circuit suite, scoring, 1,000/10,000-record timings. **Without `--resume`, a second run appends duplicate rows.** Preserve or move the old output directory before a full rerun; do not mix runs.
- `followup.py`: 100,000-record, structured-family, larger timing-only, and isolated-memory supplements.
- `refine_accuracy.py`: scoring precision only, no policy fitting.
- `batch_check.py`: separate paper-style Goodman batch-correction sensitivity, with empirical accuracy explicitly labeled.
- `analyze.py`: aggregates original measurements with refined scores; creates `summary.json` and the figure. It expects all supplements.

## Build provenance

All vendor repositories, builds, generated third-party reference code, and DLLs are outside the research vault. The measured cache was `C:/Users/notso/Documents/Codex/2026-10-08/ok-x20/benchmark_sources`; this is an example location, not a portable dependency path. The measured Python environment was a scoped `gbs_benchmark_env` beside it. The wrapper's Windows DLL search currently expects `C:/Strawberry/c/bin`; change that path to your compiler's runtime directory on another device.

| Source | Repository | Pinned commit |
| --- | --- | --- |
| FrugalGBS | https://github.com/tomdodd4598/FrugalGBS | `fa8b796f2afebd4845a2e335e457735952617ef8` |
| xqsim, inspected only | https://github.com/peterddrummond/xqsim | `32609f3644ae18bff872b53a32a3a7f58f883b3b` |
| Eigen | https://github.com/PX4/eigen | `e7248b26a1ed53fa030c5c459f7ea095dfd276ac` |
| xsimd | https://github.com/xtensor-stack/xsimd | `b8df57b3865cbf38576a9c7099180f9bf1efcf73` |

Compiler: Strawberry MinGW g++ 13.2.0, CMake MinGW Makefiles. Eigen 3.4.0, xsimd 14.3.0. Frugal precision is double; CUDA and vendor tests were disabled. The frontend used `-O3 -march=native`; the generation bridge used `-O3` and the compiler's default **SSE2**, with one OpenMP thread. AVX2/native-SIMD bridge builds crashed on this toolchain and are excluded from measurements. This limitation matters when comparing to optimized production builds.

The following PowerShell template assumes these four pinned repositories already exist under `$taskCache`; clone and check out the exact commits before building. Set the two paths for the new machine. Each command must succeed before running its dependent command.

```powershell
$taskCache = 'C:/path/to/benchmark_sources'
$taskProject = 'C:/path/to/Quantum Research/GBS Classical Simulation'
python -m venv "$taskCache/gbs_env"
$taskPython = "$taskCache/gbs_env/Scripts/python.exe"
& $taskPython -m pip install -r "$taskProject/src/requirements.txt"
cmake -S "$taskCache/eigen" -B "$taskCache/build_eigen" -G 'MinGW Makefiles' -DBUILD_TESTING=OFF "-DCMAKE_INSTALL_PREFIX=$taskCache/prefix"
cmake --install "$taskCache/build_eigen"
cmake -S "$taskCache/xsimd" -B "$taskCache/build_xsimd" -G 'MinGW Makefiles' "-DCMAKE_INSTALL_PREFIX=$taskCache/prefix"
cmake --install "$taskCache/build_xsimd"
cmake -S "$taskCache/FrugalGBS" -B "$taskCache/build_fgbs" -G 'MinGW Makefiles' -DBUILD_TESTING=OFF -DFGBS_ENABLE_CUDA=OFF -DFGBS_REAL_PRECISION=2 -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-march=native "-DCMAKE_PREFIX_PATH=$taskCache/prefix"
cmake --build "$taskCache/build_fgbs" --target fgbs_cpu -j 4
& $taskPython "$taskProject/src/build_reference.py" --frugal "$taskCache/FrugalGBS" --output "$taskCache/fgbs_reference.inc"
g++ -std=c++20 -O3 -fopenmp -shared -DFGBS_GPU_ENABLED=0 -Wno-deprecated-enum-enum-conversion -I "$taskCache" -I "$taskCache/FrugalGBS/include" -I "$taskCache/build_fgbs/generated" -I "$taskCache/prefix/include" -I "$taskCache/prefix/include/eigen3" "$taskProject/src/fgbs_bridge.cpp" "$taskCache/FrugalGBS/src/fgbs/cpu/cpu_sampler.cpp" -L "$taskCache/build_fgbs/lib" -lfgbs_frontend -o "$taskCache/fgbs_bridge.dll"
```

Run correctness before the main comparison. For a fresh reproduction, set a new output directory outside the repository first. The shared output setting applies to the main runner, supplements, and analyzer; omit it only to analyze the published measurements. Do not append new timing rows to the saved run.

```powershell
$env:GBS_BENCHMARK_OUTPUT = "$taskCache/fresh_smoke_run"
& $taskPython "$taskProject/src/experiment.py" --dll "$taskCache/fgbs_bridge.dll" --checks-only
& $taskPython "$taskProject/src/experiment.py" --dll "$taskCache/fgbs_bridge.dll" --resume
& $taskPython "$taskProject/src/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode bulk
& $taskPython "$taskProject/src/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode scale
& $taskPython "$taskProject/src/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode memory
& $taskPython "$taskProject/src/refine_accuracy.py" --dll "$taskCache/fgbs_bridge.dll"
& $taskPython "$taskProject/src/batch_check.py"
& $taskPython "$taskProject/src/analyze.py"
```

`--resume` skips existing seed/method rows; on an empty output directory it runs the entire suite. A genuine fresh reproduction must not reuse old completed rows. Without `--resume`, rerunning in a directory containing main rows appends duplicate rows. The default output directory is `results/smoke_v1`; `GBS_BENCHMARK_OUTPUT` overrides it for all benchmark tools. The supported bridge mode counts are 2, 3, 6, 8, 10, 12, 16, 24, 32; arbitrary mode counts require additional template dispatches and a rebuild.

## Costs and uncertainty

Record generation is timed separately from exact reference scoring. Timing includes random generation, native sampler calls, packing, and outputs; reported total adds one measured preparation. No compile/install time, interpreter startup, or reference enumeration is charged to any algorithm. Operational timings have warm native caches. Do not label them full cold-start costs.

Goodman's main reference integrates a frozen probability map; two Sobol replicates diagnose integration sensitivity, not rigorous uncertainty. The batch supplement pools three batches and includes empirical histogram noise; output records can share transformation-dependent correlations. It cannot supply the same exact-law accuracy comparison as Frugal/context.

The source covariance oracle reduces determinant size to twice the retained source count, but its observed-click inclusion–exclusion is exponential in click count. No large-size scalability claim is appropriate. The block SDP's added covariance noise is an algorithmic approximation, not a second assumed experimental noise source. Main physical inputs have photon loss only.

Raw `memory.json` has a zero native persistent-memory field for Dodd because that wrapper field was not instrumented. `summary.json` corrects its interpretation to missing. Peak process RSS is measured separately and includes imported runtime/dependencies; Python allocations alone do not measure native peak memory.

The run ledger is `results/smoke_v1/execution_notes.json`. Current file checksums are in `results/manifest.json`; hashes identify the saved snapshot and should be regenerated if files change. Text entries include `sha256_lf`, which normalizes CRLF to LF so a Git clone on another operating system can be checked; `sha256` records the original local bytes. A SHA change alone does not diagnose a physics error. Output fixture arrays and exact target probabilities are in `case_<seed>.npz` files. Vendor source copies remain outside the vault, so cloning this repository does not automatically install compilers, vendors, Python packages, or author MATLAB software.
