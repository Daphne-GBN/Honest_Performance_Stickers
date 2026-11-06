# Honest Performance Stickers

Benchmarking QAOA and classical optimization approaches using the NASA QuAIL HybridQ framework and Max-Cut benchmark datasets.

## Current Status

- HybridQ 0.8.2 successfully installed.
- HybridQ Bell-state simulation executed successfully.
- Bell-state output verified: the expected state amplitudes were obtained.
- HybridQ C++ core disabled; simulation performed using the NumPy-based `evolution-einsum` method.
- Dataset collection contains 316 Max-Cut instances:
  - 140 tuning instances.
  - 140 benchmark instances.
  - 36 additional generated instances.

## Environment Setup

**Requirements:** Python 3.10 on Windows.

A separate virtual environment is used for HybridQ.

### 1. Create and activate the environment

```powershell
py -3.10 -m venv .venv-hq
.\.venv-hq\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. Install HybridQ

The C++ core is disabled for the Windows installation.

```powershell
$env:HYBRIDQ_DISABLE_CPP_CORE="1"
pip install --no-deps git+https://github.com/nasa/hybridq
```

### 3. Verify the installation

```powershell
python -c "import hybridq; print('HybridQ installed successfully')"
```

## HybridQ Validation

The file `hybridq_bell_test.py` contains a simple Bell-state simulation using HybridQ.

Run it using:

```powershell
python hybridq_bell_test.py
```

Expected output:

```text
Bell State Simulation:
[0.70710677+0.j 0.        +0.j 0.        +0.j 0.70710677+0.j]
```

The simulation uses:

```python
optimize='evolution-einsum'
```

The C++ core is disabled, so the NumPy-based simulation path is used.

## Dataset Structure

### Original benchmark and tuning datasets

```text
instances/
├── benchmark/
├── tuning/
└── manifest.csv
```

- Benchmark dataset: 140 instances.
- Tuning dataset: 140 instances.

### Additional Max-Cut instances

```text
maxcut_instances/
├── generate_instances.py
├── manifest.csv
└── instances/
```

- Additional instances: 36.
- Generator script: `generate_instances.py`.

## Project Structure

```text
Honest_Performance_Stickers/
│
├── hybridq_bell_test.py
├── prepare_dataset.py
├── README.md
│
├── instances/
│   ├── benchmark/
│   ├── tuning/
│   └── manifest.csv
│
├── maxcut_instances/
│   ├── generate_instances.py
│   ├── manifest.csv
│   └── instances/
│
└── logs/
    ├── dataset_log.md
    └── installation_log.md
```

## Next Steps

- Validate HybridQ on Max-Cut problem instances.
- Implement QAOA circuits using the HybridQ framework.
- Compare quantum optimization results with classical optimization baselines.
- Evaluate performance across tuning and benchmark datasets.