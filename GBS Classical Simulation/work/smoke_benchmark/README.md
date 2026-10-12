# Reproducing the bounded GBS mechanism benchmark

Read [the report](../../GBS%20Mechanism%20Smoke%20Benchmark.md) before interpreting a timing ratio. This is a small synthetic mechanism comparison, not an experimental reproduction. Python requirements are pinned in `requirements.txt`; the original measured environment is in `../../outputs/smoke_comparison_v1/environment.json`.

## Run our algorithm on another device

The context sampler needs Python 3.11 or a compatible newer Python, and the minimal dependencies below. It does **not** need FrugalGBS, a compiler, MATLAB, or the comparison DLL. From the repository root, create a Python environment and run:

```powershell
python -m venv .venv
& '.venv/Scripts/python.exe' -m pip install -r 'GBS Classical Simulation/work/smoke_benchmark/requirements-context.txt'
Set-Location 'GBS Classical Simulation'
& '../.venv/Scripts/python.exe' work/smoke_benchmark/sample_context.py --modes 10 --context 6 --shots 10000 --loss 0.6 --check-small --output samples/demo.npz
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
& $taskPython -m pip install -r "$taskProject/work/smoke_benchmark/requirements.txt"
cmake -S "$taskCache/eigen" -B "$taskCache/build_eigen" -G 'MinGW Makefiles' -DBUILD_TESTING=OFF "-DCMAKE_INSTALL_PREFIX=$taskCache/prefix"
cmake --install "$taskCache/build_eigen"
cmake -S "$taskCache/xsimd" -B "$taskCache/build_xsimd" -G 'MinGW Makefiles' "-DCMAKE_INSTALL_PREFIX=$taskCache/prefix"
cmake --install "$taskCache/build_xsimd"
cmake -S "$taskCache/FrugalGBS" -B "$taskCache/build_fgbs" -G 'MinGW Makefiles' -DBUILD_TESTING=OFF -DFGBS_ENABLE_CUDA=OFF -DFGBS_REAL_PRECISION=2 -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-march=native "-DCMAKE_PREFIX_PATH=$taskCache/prefix"
cmake --build "$taskCache/build_fgbs" --target fgbs_cpu -j 4
& $taskPython "$taskProject/work/smoke_benchmark/build_reference.py" --frugal "$taskCache/FrugalGBS" --output "$taskCache/fgbs_reference.inc"
g++ -std=c++20 -O3 -fopenmp -shared -DFGBS_GPU_ENABLED=0 -Wno-deprecated-enum-enum-conversion -I "$taskCache" -I "$taskCache/FrugalGBS/include" -I "$taskCache/build_fgbs/generated" -I "$taskCache/prefix/include" -I "$taskCache/prefix/include/eigen3" "$taskProject/work/smoke_benchmark/fgbs_bridge.cpp" "$taskCache/FrugalGBS/src/fgbs/cpu/cpu_sampler.cpp" -L "$taskCache/build_fgbs/lib" -lfgbs_frontend -o "$taskCache/fgbs_bridge.dll"
```

Run correctness before the main comparison:

```powershell
& $taskPython "$taskProject/work/smoke_benchmark/experiment.py" --dll "$taskCache/fgbs_bridge.dll" --checks-only
& $taskPython "$taskProject/work/smoke_benchmark/experiment.py" --dll "$taskCache/fgbs_bridge.dll" --resume
& $taskPython "$taskProject/work/smoke_benchmark/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode bulk
& $taskPython "$taskProject/work/smoke_benchmark/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode scale
& $taskPython "$taskProject/work/smoke_benchmark/followup.py" --dll "$taskCache/fgbs_bridge.dll" --mode memory
& $taskPython "$taskProject/work/smoke_benchmark/refine_accuracy.py" --dll "$taskCache/fgbs_bridge.dll"
& $taskPython "$taskProject/work/smoke_benchmark/batch_check.py"
& $taskPython "$taskProject/work/smoke_benchmark/analyze.py"
```

`--resume` skips existing seed/method rows; on an empty output directory it runs the entire suite. A genuine fresh reproduction must not reuse old completed rows. The main script writes outputs relative to its own project location. The supported bridge mode counts are 2, 3, 6, 8, 10, 12, 16, 24, 32; arbitrary mode counts require additional template dispatches and a rebuild.

## Costs and uncertainty

Record generation is timed separately from exact reference scoring. Timing includes random generation, native sampler calls, packing, and outputs; reported total adds one measured preparation. No compile/install time, interpreter startup, or reference enumeration is charged to any algorithm. Operational timings have warm native caches. Do not label them full cold-start costs.

Goodman's main reference integrates a frozen probability map; two Sobol replicates diagnose integration sensitivity, not rigorous uncertainty. The batch supplement pools three batches and includes empirical histogram noise; output records can share transformation-dependent correlations. It cannot supply the same exact-law accuracy comparison as Frugal/context.

The source covariance oracle reduces determinant size to twice the retained source count, but its observed-click inclusion–exclusion is exponential in click count. No large-size scalability claim is appropriate. The block SDP's added covariance noise is an algorithmic approximation, not a second assumed experimental noise source. Main physical inputs have photon loss only.

Raw `memory.json` has a zero native persistent-memory field for Dodd because that wrapper field was not instrumented. `summary.json` corrects its interpretation to missing. Peak process RSS is measured separately and includes imported runtime/dependencies; Python allocations alone do not measure native peak memory.

The run ledger is `execution_notes.json`. File checksums are in `manifest.json`; hashes identify the saved snapshot and should be regenerated if files change. Text entries include `sha256_lf`, which normalizes CRLF to LF so a Git clone on another operating system can be checked; `sha256` records the original local bytes. A SHA change alone does not diagnose a physics error. Output fixture arrays and exact target probabilities are in `case_<seed>.npz` files. Source copies remain outside the vault, so cloning this repository does not automatically install compilers, vendors, Python packages, or author MATLAB software.
