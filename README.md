# Quantum Research

This Obsidian vault contains quantum photonics and quantum information research. The existing decoder work and the new Gaussian boson sampling (GBS) classical-simulation project live in separate folders.

- [Quantum Research index](Quantum%20Research.md)
- [GBS classical-simulation project description](GBS%20Classical%20Simulation/GBS%20Classical%20Simulation%20Project%20Description.md)
- [GBS research plan and preliminary evidence](GBS%20Classical%20Simulation/Correlation-Based%20Classical%20Simulation%20of%20GBS.md)

## GBS detector-context simulation

Our current candidate compiles exact Gaussian subset probabilities into a bounded-parent detector model, then generates independent records from that approximate model. The repository includes the simulation source, saved circuit fixtures, raw benchmark results, scientific limitations, and novelty assessments.

- [Run our sampler and reproduce the comparisons](GBS%20Classical%20Simulation/work/smoke_benchmark/README.md) — standalone sampler quick start; the author-baseline build is separate.
- [Measured mechanism comparison](GBS%20Classical%20Simulation/GBS%20Mechanism%20Smoke%20Benchmark.md) — full-distribution accuracy, preparation and sampling cost, memory, and unfavorable cases.
- [Novelty audit](GBS%20Classical%20Simulation/GBS%20Detector%20Context%20Novelty%20Audit.md) and [external-review synthesis](GBS%20Classical%20Simulation/GBS%20External%20Novelty%20Review%20Synthesis.md).

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
