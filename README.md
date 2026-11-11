# Honest Performance Stickers

**Benchmarking QAOA against classical optimizers on Max-Cut using the NASA QuAIL HybridQ framework.**

Honest Performance Stickers is a reproducible benchmarking workflow designed to compare the Quantum Approximate Optimization Algorithm (QAOA) with classical optimization methods under clearly documented experimental conditions. Its goal is not to claim that quantum methods are universally faster or better, but to show **which solver performs well, under which conditions, and with what limitations**.

The project standardises graph ingestion, Max-Cut formulation, solver execution, experiment logging, validation, and result presentation. Results are summarised as per-configuration HTML performance stickers and aggregate reports.

---

## Project status

<details>
<summary><strong>Implementation is complete through Stage 9; full-scale experiments remain future work.</strong></summary>

The nine planned implementation stages have corresponding code or deliverables in the project branch. A reduced workstation pilot has been executed and its Stage 8/9 outputs generated.

| Recorded item | Current result |
|---|---:|
| Raw experiment records processed | 72 |
| Aggregate configuration groups | 42 |
| Individual HTML stickers generated | 72 |
| Sticker dashboard/index | 1 |
| Noise smoke-test configurations validated | 8 of 8 |

**Important scope note:** These figures describe the experiments recorded in the reduced pilot and earlier smoke/tuning runs. The full 280-instance catalogue grid and the planned 5–10 independent repeats per configuration have **not** been completed. The pilot does not establish quantum advantage.

</details>

### Implemented components

| Stage | Component | Status |
|---|---|---|
| 1 | Experiment contract: graph representation, solver interface, metrics, result schema, seeds, and tuning/benchmark separation | Implemented |
| 2 | Graph ingestion, Max-Cut formulation, QUBO/Ising conversion, and exact optima for small graphs | Implemented |
| 3 | Classical simulated annealing (SA) and parallel tempering (PT) baselines through PySA | Implemented |
| 4 | Configurable-depth QAOA implementation with cost and mixer layers | Implemented |
| 5 | Noiseless QAOA optimizer sweep: COBYLA, Nelder–Mead, SPSA, and Adam | Implemented |
| 6 | Density-matrix noise runner and noisy-QAOA pilot | Implemented; reduced pilot |
| 7 | Shared metrics and append-oriented CSV/JSONL result storage | Implemented |
| 8 | Resumable experiment-grid runner, JSONL run ledger, size guardrails, and numerical validation | Implemented; reduced workstation pilot |
| 9 | HTML performance stickers, index, aggregate summaries, and quality-by-solver plot | Implemented |

## Solvers and configurations

### Classical baselines
- **Simulated Annealing (SA)**
- **Parallel Tempering (PT)**

Both are run through the PySA-facing workflow and checked against the shared Max-Cut objective.

### QAOA
- Configurable circuit depth: **p = 1, 2, 3** in the benchmark pilot.
- Noiseless optimizer comparison: **COBYLA, Nelder–Mead, SPSA, and Adam**.
- Noisy pilot: **COBYLA and SPSA**.
- The noisy pilot used noise probability **0.001** on one small graph.

The noisy pilot does not contain noisy Nelder–Mead or Adam results. Noiseless and noisy runs are separate configurations and should be interpreted separately.

## Dataset and experiment design

The prepared catalogue contains **280 records**:

- 140 tuning instances.
- 140 benchmark instances.
- 210 Erdős–Rényi (ER) graph records and 70 3-regular graph records.
- Listed graph sizes: 8, 10, 12, 14, 16, 18, and 20 nodes.

The catalogue records are **unweighted**. The loader supports weighted inputs, but the current catalogue should not be described as a weighted dataset.

### What the reduced pilot actually covered

| Pilot component | Executed scope |
|---|---|
| Benchmark grid | Two 8-node benchmark ER instances; SA, PT, and noiseless QAOA with four optimizers at p = 1, 2, 3; one repeat; QAOA evaluation budget 20 |
| Tuning comparison | Two tuning ER instances; SA, PT, and four noiseless QAOA optimizers at p = 1; one seed; budget 20 |
| Noise pilot | Noisy QAOA with COBYLA and SPSA at noise probability 0.001 on one small graph, using a reduced evaluation budget |
| Smoke tests | Additional small benchmark runs with different seeds and a validation-focused noisy run |

The 72 raw records include the pilot, smoke, and tuning runs. The 42 aggregate groups and 72 stickers are summaries of the records that exist; they do not mean every catalogue configuration was attempted.

## Honest reporting and metrics

The reporting workflow is designed to make missing evidence and limitations visible.

- **Classical best cut:** the best sampled or returned cut from a classical solver.
- **QAOA expected cut:** the expected objective value from the QAOA optimizer interface; this is not a sampled best bitstring.
- **Approximation ratio:** reported only when the quality value and exact optimum support its calculation.
- **Success probability / time-to-solution (TTS):** left unavailable unless empirical success probability and runtime support a defensible estimate.
- **Noise metadata:** noise probability and simulator information accompany noisy runs.
- **Validation:** numerical checks, solver validation, failures, and unsupported configurations are recorded rather than silently omitted.

Because classical best cuts and QAOA expected cuts are different measurement types, they must not be compared as though they were identical quantities without explanation.

## Generated outputs

The Stage 8/9 workflow produces or uses the following files:

| Path | Purpose |
|---|---|
| `stage8_experiments.py` | Experiment-grid runner, resume ledger, size guardrails, and validation |
| `stage9_stickers.py` | Sticker and aggregate-report generator |
| `STAGE8_9_RUN_GUIDE.md` | Run instructions and workstation-pilot limitations |
| `results/experiments.csv` | Tabular experiment records |
| `results/experiments.jsonl` | Append-oriented raw experiment records |
| `results/stage8_run_ledger.jsonl` | Completed/failed configuration ledger used for resuming |
| `results/stickers/index.html` | Main sticker dashboard/index |
| `results/stickers/sticker_*.html` | Individual experiment stickers (72 in the reported pilot) |
| `results/stickers/aggregate_summary.md` | Human-readable aggregate summary |
| `results/stickers/aggregate_summary.csv` | Machine-readable aggregate summary |
| `results/stickers/plots/quality_by_solver.png` | Quality-by-solver plot |

## Environment setup

The repository's existing HybridQ validation setup uses **Python 3.10 on Windows** in a separate virtual environment.

### 1. Create and activate the environment

```powershell
py -3.10 -m venv .venv-hq
.\.venv-hq\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. Install HybridQ

The documented Windows setup disables the optional C++ core:

```powershell
$env:HYBRIDQ_DISABLE_CPP_CORE="1"
pip install --no-deps git+https://github.com/nasa/hybridq
```

### 3. Verify the installation

```powershell
python -c "import hybridq; print('HybridQ installed successfully')"
```

### 4. Run the Bell-state validation

The `hybridq_bell_test.py` file contains a small HybridQ Bell-state simulation:

```powershell
python hybridq_bell_test.py
```

Expected statevector output:

```text
Bell State Simulation:
[0.70710677+0.j 0.        +0.j 0.        +0.j 0.70710677+0.j]
```

The reported implementation used the NumPy-based `evolution-einsum` simulator path because the optional HybridQ C++ core was unavailable. Runs completed, but this is a backend/performance limitation worth disclosing.

> The commands above document the repository's HybridQ validation environment. Use the project's run guide and the environment appropriate to the experiment scripts when reproducing Stage 8/9.

## Reproduce the sticker outputs

From the project root, activate the project virtual environment and run:

```powershell
# Generate stickers and aggregate summaries from recorded experiment JSONL
python stage9_stickers.py

# Open the generated dashboard
start results\stickers\index.html

# Inspect the aggregate summary
Get-Content results\stickers\aggregate_summary.md -TotalCount 80

# Check the latest commit
git log -1 --oneline
```

For the experiment-grid runner, consult `STAGE8_9_RUN_GUIDE.md` for the exact pilot invocation and resume behaviour.

## Current limitations and remaining work

The implementation and the full-scale experimental campaign are different milestones. The following research work remains:

1. Run the full **280-instance** catalogue grid.
2. Complete the planned **5–10 independent repeats per configuration**.
3. Expand benchmark coverage across graph families, sizes, densities, and planned parameter combinations.
4. Run the complete multi-level noise sweep within a feasible, documented resource budget.
5. Regenerate the stickers and aggregate analysis when expanded full-scale results are available.

Additional limitations of the current pilot:

- Statevector and density-matrix simulation impose computational and memory constraints; size guardrails are used.
- The optional HybridQ C++ core was unavailable, so the reported run used the NumPy/evolution-einsum path.
- The noise pilot is reduced and covers only COBYLA and SPSA.
- Stochastic results from one-repeat pilot configurations are preliminary.
- No real quantum hardware validation was performed in this pilot.
- **No quantum advantage is established by the current results.**

## Repository branch and implementation record

The Stage 8/9 implementation report records the final deliverables in branch `feature/remaining-implementation`, at commit:

```text
374eada — Complete Stage 8 experiments and Stage 9 performance stickers
```

That commit was recorded locally in the implementation report as **not yet pushed to GitHub**. Check the repository's current branch and commit history before assuming that commit is present on the remote default branch.

## Project objective

The intended outcome is a reusable, reproducible benchmarking pipeline and a standardised reporting artifact that helps researchers and practitioners decide when QAOA is worth considering for a Max-Cut instance—and when a classical solver is the better choice.

> We implemented a reproducible nine-stage benchmarking workflow and validated it with a reduced workstation pilot. The pilot produced 72 experiment records and 72 individual performance stickers across classical baselines and QAOA configurations. The full catalogue-scale repeated benchmark remains future work; therefore, the current results are preliminary and do not support a claim of quantum advantage.
