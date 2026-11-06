# HybridQ Installation and Verification Log

## Environment

- Operating system: Windows
- Project directory: `D:\HP-Stickers`
- Python version: 3.10.11
- HybridQ virtual environment: `.venv-hq`
- HybridQ version: 0.8.2

## Supporting Libraries

The following supporting libraries were installed for the HybridQ environment:

- NumPy
- SciPy
- NetworkX
- SymPy
- Numba
- Opt-Einsum
- Cotengra
- More-itertools
- TQDM
- Psutil
- Dill

## HybridQ Installation

### Installation approach

HybridQ was installed directly from the NASA GitHub repository.

```powershell
$env:HYBRIDQ_DISABLE_CPP_CORE="1"
pip install --no-deps git+https://github.com/nasa/hybridq
```

### Installation result

- HybridQ installation: Successful
- Package import verification: Successful
- HybridQ version: 0.8.2
- C++ core: Disabled

### Installation notes

- The standard PyPI installation attempt failed during build requirements discovery.
- The GitHub installation initially encountered dependency installation issues.
- A separate Python 3.10.11 virtual environment was created.
- Dependencies were installed separately.
- The C++ core was disabled because its Windows build encountered an installation error.
- HybridQ successfully imported after installation.

## Bell-State Simulation Validation

### Test file

`hybridq_bell_test.py`

### Circuit

The validation circuit contains:

1. Hadamard gate on qubit 0.
2. Controlled-X gate between qubits 0 and 1.
3. Initial state: `|00⟩`.

### Simulation configuration

- Simulator: HybridQ
- Optimization method: `evolution-einsum`
- C++ core: Disabled
- Execution: Successful

### Expected output

```text
Bell State Simulation:
[0.70710677+0.j 0.        +0.j 0.        +0.j 0.70710677+0.j]
```

### Validation result

The simulation produced the expected Bell-state amplitudes, confirming that the HybridQ installation and basic state-vector simulation work successfully.

## Current Limitations

- The HybridQ C++ core is not enabled in the current Windows environment.
- The `evolution-hybrid` optimization method is unavailable in this setup.
- Simulation currently uses the NumPy-based `evolution-einsum` method.
- Full QAOA benchmarking using HybridQ is still pending.

## Next Steps

- Implement Max-Cut circuit construction using HybridQ.
- Execute HybridQ simulations on the prepared datasets.
- Validate optimization results.
- Compare HybridQ-based results against classical optimization baselines.