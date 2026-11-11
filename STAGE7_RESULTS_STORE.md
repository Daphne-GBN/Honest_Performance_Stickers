
# Stage 7: Shared Metrics and Results Store

## 1. Objective

Implement a common results schema and incremental storage system for classical, noiseless QAOA, optimizer comparison, and noisy QAOA experiments.

The results store provides consistent experiment records in CSV and JSONL formats.

## 2. Shared Metrics

The results store records:

- Instance name, node count, edge count, and graph density.
- Solver and optimizer configuration.
- QAOA depth (p), random seed, and noise probability.
- Best actual cut and expected cut as separate metrics.
- Exact optimum for instances within the configured exact-solver size limit.
- Approximation ratio when an actual cut and exact optimum are available.
- Success probability from repeated independent runs.
- Runtime and function evaluation count.
- Validation status and optimizer convergence status.
- Simulator information and error details.

Unavailable metrics are stored as null rather than fabricated values.

## 3. Repeated-Run Metrics

The existing `distribution_metrics()` function is reused to calculate:

- Number of runs.
- Best and worst cut.
- Mean and standard deviation.
- Number of successful runs.
- Success probability.
- Repetitions required to achieve at least 99% probability of finding the exact optimum.
- Mean approximation ratio.

A run is successful when its cut value is within the configured tolerance of the exact optimum.

## 4. Time-to-Solution Convention

The project uses the following convention:

TTS99 = R99 × T_run

Where:

- R99 is the number of independent repetitions required to achieve at least 99% probability of finding an optimal solution.
- T_run is the measured runtime per run in seconds.

TTS99 is unavailable when the observed success probability is zero or runtime is unavailable.

This estimate uses the observed repeated-run success probability and assumes independent, identically distributed repetitions. It is not a hardware-independent performance guarantee.

## 5. Storage Formats

Two incremental output files are maintained:

- `results/experiments.csv`
- `results/experiments.jsonl`

Each experiment is appended immediately, supporting partial results and resumable experiment execution.

## 6. Validation

Validation includes:

- Classical result normalization.
- QAOA result normalization.
- Exact optimum and approximation ratio handling.
- Missing metric handling.
- Incremental CSV and JSONL storage.
- Repeated-run statistics and TTS calculation.
- Integration across SA, PT, noiseless QAOA, optimizer comparison, and noisy QAOA.
- Persistence of repeated-run metrics in both output formats.

## 7. Simulator and Reproducibility Notes

Experiments use HybridQ 0.8.2 with the NumPy fallback because the native C++ HybridQ core is unavailable in the current environment.

The fallback warnings are documented as an environment limitation. They are not treated as experiment failures.

Random seeds and experiment metadata are retained to support reproducibility.

## 8. Limitations

- Exact optimum calculation is limited by the configured maximum graph size.
- Success probability requires repeated independent runs; it must not be inferred from a single run.
- TTS99 is an empirical estimate based on observed success probability and measured runtime.
- Missing or unvalidated metrics remain explicitly unavailable.
- Results from the NumPy fallback should not be interpreted as native HybridQ performance.

## 9. Stage 7 Completion

The shared results store, repeated-run metrics, TTS convention, CSV/JSONL persistence, and runner integration have been implemented and tested.

Stage 7 is ready for review and integration with the full experiment grid.
