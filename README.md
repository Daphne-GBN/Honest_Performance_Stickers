# Honest Performance Stickers

Benchmarking QAOA against classical optimizers using the NASA QuAIL
framework.

## Current Status

- Python 3.10 virtual environment created.
- Supporting scientific Python libraries installed and import-verified.
- PySA import verified; QUBO smoke test is pending.
- HybridQ installation attempted twice; both attempts failed.
- Qiskit Aer installed and its AerSimulator import verified.
- Bell-state smoke test pending.
- QAOA circuit validation pending.

## Setup

Use Python 3.10 on Windows.

### Create and activate a virtual environment

 ```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
