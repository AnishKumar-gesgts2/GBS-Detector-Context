# GBS Detector Context

Classical threshold Gaussian boson sampling with exact local marginals, bounded detector history, and reusable conditional-probability tables. This repository contains a smoke prototype and reproducible accuracy–cost comparisons.

Canonical repository: [GBS-Detector-Context](https://github.com/AnishKumar-gesgts2/GBS-Detector-Context). The local Obsidian vault and folder remain named `Quantum Research`; related photonic error-correction work is retained separately below.

The previous `Quantum-Research` URLs redirect here, including the project and immutable evidence links in the existing proposal PDF.

- [Quantum Research index](Quantum%20Research.md)
- [GBS algorithm-development project](GBS%20Classical%20Simulation/README.md)

## GBS detector-context simulation

Our current candidate compiles exact Gaussian subset probabilities into a bounded-parent detector model, then generates independent records from that approximate model. The repository includes the simulation source, saved circuit fixtures, raw benchmark results, scientific limitations, and novelty assessments.

- [Project description](GBS%20Classical%20Simulation/Project%20Description.md) and [proposal](GBS%20Classical%20Simulation/Proposal.md).
- [Code description and quick start](GBS%20Classical%20Simulation/Code%20Description.md), with simulation files in [src](GBS%20Classical%20Simulation/src/).
- [Results](GBS%20Classical%20Simulation/Results.md) — accuracy, preparation and sampling cost, memory, and unfavorable cases.
- [Sources](GBS%20Classical%20Simulation/Sources.md) and [novelty boundaries](GBS%20Classical%20Simulation/Novelty.md).

The measured advantage is limited to specified small-system accuracy targets and workloads. The complete GBS combination is potentially original; its statistical ingredients are established. Large-system fidelity and hardware quantum-advantage conclusions remain unestablished.

## Photonic decoder work

The decoder landscape review and reproducible test harness for the **Fusion-Hypergraph Decoder** remain in this repository.

- [Photonic Decoder Evaluations](Photonic%20Decoder%20Evaluations.md)
- [Hypergraph decoder project](Hypergraph/Fusion%20Hypergraph%20Decoder%20Test%20Plan.md)

Quick start:

```powershell
Set-Location Hypergraph
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
fusion-hypergraph all --config configs/smoke.toml --workdir runs/smoke
pytest
```

The smoke configuration checks the pipeline. `configs/full_scale.toml` is the research sweep and should be run on appropriately provisioned compute.
