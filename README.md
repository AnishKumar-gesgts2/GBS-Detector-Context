<div align="center">

<h1>GBS Detector Context</h1>

<p><strong>Exact local probabilities · Bounded detector history · Reusable sampling</strong></p>

<p>
  <a href="GBS%20Classical%20Simulation/proposal/GBS_Algorithm_Proposal.pdf">Proposal PDF</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="GBS%20Classical%20Simulation/Results.md">Results</a> ·
  <a href="GBS%20Classical%20Simulation/src/">Source code</a>
</p>

</div>

---

GBS Detector Context explores a classical sampling algorithm for **threshold Gaussian boson sampling**. It calculates exact probabilities for small groups of detectors, compiles selected detector history into conditional-probability tables, and reuses those tables to generate independent records from an approximate global distribution.

The research question is whether this compilation can improve the **accuracy–cost tradeoff**, particularly when many samples are needed from the same lossy photonic circuit.

> **Research prototype.** The repository contains a smoke implementation and reproducible small-system benchmarks. Accurate large-system sampling, algorithmic novelty, and a challenge to an experimental quantum-advantage claim remain open research questions.

## How it works

1. **Calculate local probabilities.** Obtain small joint click distributions from the Gaussian covariance matrix using subset no-click probabilities and inclusion–exclusion.
2. **Compile detector contexts.** Select at most $b$ preceding detectors per output detector using pairwise mutual information, then build their exact local conditional tables.
3. **Sample and reuse.** Generate records by ancestral sampling, with fresh random numbers and table lookups. Compilation is amortized across records.

The approximate sampling law is

$$
Q(x)=\prod_{i=1}^{M}P(x_i\mid x_{S_i}),\qquad S_i\subseteq\lbrace1,\ldots,i-1\rbrace,\quad |S_i|\leq b.
$$

The approximation discards some detector history. Exact retained conditionals do not guarantee an exact global distribution. See the [method and assumptions](GBS%20Classical%20Simulation/Project%20Description.md) and [implementation guide](GBS%20Classical%20Simulation/Code%20Description.md).

## Quick start

Use **Python 3.11 or a compatible newer version**. The candidate sampler uses NumPy, SciPy, Numba, and threadpoolctl; it runs independently of the vendor comparison build.

```bash
git clone https://github.com/AnishKumar-gesgts2/GBS-Detector-Context.git
cd GBS-Detector-Context
```

<details open>
<summary><strong>Windows · PowerShell</strong></summary>

```powershell
python -m venv .venv
& '.venv/Scripts/python.exe' -m pip install -r 'GBS Classical Simulation/src/requirements-context.txt'
& '.venv/Scripts/python.exe' 'GBS Classical Simulation/src/sample_context.py' `
  --modes 10 --context 6 --shots 10000 --loss 0.6 --check-small `
  --output 'GBS Classical Simulation/samples/demo.npz'
```

</details>

<details>
<summary><strong>Linux · macOS</strong></summary>

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r 'GBS Classical Simulation/src/requirements-context.txt'
.venv/bin/python 'GBS Classical Simulation/src/sample_context.py' \
  --modes 10 --context 6 --shots 10000 --loss 0.6 --check-small \
  --output 'GBS Classical Simulation/samples/demo.npz'
```

</details>

This example generates 10,000 records for a ten-mode circuit with 60% photon loss. It saves detector outcomes and compiled tables in an NPZ file, plus a neighboring JSON containing metadata and exact small-system TVD. Choose a new output filename when rerunning; the runner preserves existing files.

`--check-small` enumerates the reference and induced distributions for validation and is limited to ten modes. Candidate record generation does not enumerate the global output space. First-run timing can include native compilation and should not be compared directly with the warmed benchmark timings.

## Preliminary results

The saved smoke study contains **429 comparisons across 39 synthetic circuits**. At a common total variation distance (TVD) limit of **0.02**, the six-parent candidate achieved:

| Workload | Circuits meeting the accuracy limit | Median total-cost speedup |
| --- | ---: | ---: |
| Setup + 10,000 records; eight- and ten-mode complex-Haar circuits | 21 / 24 | 1.94× among the 21 qualifying cases |
| Setup + 100,000 records; six reused ten-mode circuits | 6 / 6 | 17.53× |

Speedups compare against the fastest qualifying **tested** Dodd or frozen Goodman-port comparator on each circuit. Three primary cases missed the accuracy target; eight-mode contexts were near-global. Fifth-order Dodd was more accurate on dense ten-mode circuits. Goodman comparisons use equation ports, and the Dodd author-code build has a documented SIMD limitation.

[![Accuracy and computational cost in the saved smoke study](GBS%20Classical%20Simulation/results/smoke_v1/comparison.png)](GBS%20Classical%20Simulation/Results.md)

*Left: dense ten-mode accuracy–cost comparison. Right: a separate, restricted real-circuit specialization. These measurements do not establish general large-system fidelity or a quantum-advantage disproof.*

Read the [full results and limitations](GBS%20Classical%20Simulation/Results.md), [raw measurements](GBS%20Classical%20Simulation/results/smoke_v1/), and [fixed benchmark protocol](GBS%20Classical%20Simulation/results/smoke_v1/protocol.json) before interpreting a performance ratio.

## Documentation

| Resource | Contents |
| --- | --- |
| [Project description](GBS%20Classical%20Simulation/Project%20Description.md) | Research objective, physical assumptions, and development priorities |
| [Proposal PDF](GBS%20Classical%20Simulation/proposal/GBS_Algorithm_Proposal.pdf) · [LaTeX source](GBS%20Classical%20Simulation/proposal/GBS_Algorithm_Proposal.tex) | Four-page research proposal and prototype report |
| [Development plan](GBS%20Classical%20Simulation/Proposal.md) | Milestones, comparisons, and success or redesign criteria |
| [Code description](GBS%20Classical%20Simulation/Code%20Description.md) | Source map, covariance conventions, installation, and benchmark reproduction |
| [Sources](GBS%20Classical%20Simulation/Sources.md) · [Novelty assessment](GBS%20Classical%20Simulation/Novelty.md) | Background, competing methods, and established statistical ingredients |
| [Snapshot manifest](GBS%20Classical%20Simulation/results/manifest.json) | Checksums for the published project documents, code, and evidence |

## Repository notes

The primary project is in [`GBS Classical Simulation/`](GBS%20Classical%20Simulation/README.md). Its initial physical model uses squeezed-vacuum inputs, passive interferometers, ideal threshold detection, and photon loss as the only modeled noise.

<details>
<summary>Local vault and previous links</summary>

The local Obsidian vault and folder remain named `Quantum Research`. Previous `Quantum-Research` repository URLs redirect here. The current proposal PDF uses this canonical repository URL and preserves its immutable evidence snapshot.

The [vault index](Quantum%20Research.md) provides navigation for the GBS project notes.

</details>
