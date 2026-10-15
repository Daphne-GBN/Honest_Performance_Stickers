# Honest Performance Stickers

Benchmarking QAOA against classical optimizers using the NASA QuAIL
framework.

## Current Status

- PySA QUBO smoke test completed (20 samples, energies computed).
- Bell-state smoke test passed on Qiskit Aer.
- Qiskit Aer validated: QAOA circuit operations, small noiseless QAOA, and depolarizing-noise QAOA.
- Dataset prepared: 280 Max-Cut instances (140 tuning, 140 benchmark) with brute-force optima — see logs/dataset_log.md.

## Setup

Use Python 3.10 on Windows.

### Create and activate a virtual environment

 ```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
