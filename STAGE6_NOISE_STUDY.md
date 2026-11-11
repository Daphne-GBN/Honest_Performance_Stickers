# Stage 6 — Controlled Noise Study

## 1. Objective
Evaluate how depolarizing noise affects QAOA expected-cut performance using HybridQ density-matrix simulation. This is a controlled simulation study, not a hardware experiment or a claim of quantum advantage.

## 2. Framework and noise model
- Framework: HybridQ 0.8.2
- Python: 3.10.11
- Simulation: Density-matrix simulation
- Noise channel: Global depolarizing channel
- Application: After every circuit gate (`where="after"`)
- Affected operations: QAOA circuit gates, including Hadamard, CX, RZ and RX gates.
- Readout noise: Not included.
- Hardware noise calibration: Not included.

The noise probability is applied through HybridQ's `add_depolarizing_noise` utility. The same noise rate is used throughout each circuit.

## 3. Experimental configurations

### Triangle pilot
- Graph: 3-node triangle
- Noise rates: 0, 0.001, 0.005, 0.02
- QAOA depths: p = 1, 2
- Optimizers: COBYLA, SPSA
- Seeds: 42, 43, 44
- Maximum evaluations: 10
- Total experiments: 48

### 10-node pilot
Two benchmark graphs were evaluated:

| Graph | Nodes | Edges |
|---|---:|---:|
| er_n10_p25_s5021 | 10 | 8 |
| er_n10_p50_s5026 | 10 | 22 |

Configuration:
- Noise rates: 0, 0.005, 0.02
- QAOA depths: p = 1, 2
- Optimizers: COBYLA, SPSA
- Seeds: 42, 43, 44
- Maximum evaluations: 10
- Total experiments: 72

## 4. Validation
The following checks were performed:

1. Density-matrix simulation with zero noise was compared against the existing statevector simulation.
2. The absolute difference in expected cut was approximately 2.38e-7 for the triangle validation.
3. Density-matrix trace and probability sum were checked for normalization.
4. Probability values were checked for finite and nonnegative values.
5. All 120 pilot result rows passed the probability-sum validation (0.999 to 1.001).

## 5. Results storage
- `noise_pilot_results.csv`: 48 triangle experiments.
- `noise_10node_results.csv`: 72 experiments across two 10-node graphs.
- Total recorded experiments: 120.

Both CSV files contain the experiment configuration, expected cut, probability sum, density-matrix trace, evaluation count and runtime information.

## 6. Optimizer reporting limitation
The `optimizer_success` field is unavailable for SPSA because the current implementation does not certify convergence. This is represented as an empty CSV value, not as an experiment failure.

COBYLA may also report that its maximum evaluation budget was reached. Such a result indicates the configured budget limit, not a failure of density-matrix simulation.

## 7. Observations and limitations
- The triangle pilot showed decreasing mean expected-cut values as the tested noise rate increased.
- The 10-node pilot provides additional controlled observations across two graph instances. Its results should be analyzed separately before making broader claims.
- COBYLA uses deterministic initialization in the current pilot implementation. Repeated seeds therefore do not necessarily represent independent stochastic optimizer runs.
- SPSA uses the current custom implementation and does not provide convergence certification.
- The maximum evaluation budget is intentionally small for this pilot. These experiments are not sufficient to establish general optimizer rankings.
- HybridQ's native C++ core was unavailable. The simulator used the NumPy-based fallback, which affects performance.
- Density-matrix simulation becomes computationally expensive as graph size and circuit depth increase.
- No claim of quantum advantage is made.

## 8. Stage 6 conclusion
A reproducible controlled depolarizing-noise pilot was implemented and executed using HybridQ density-matrix simulation.

The study includes 48 triangle experiments and 72 experiments across two 10-node graphs. Zero-noise consistency and probability normalization were validated.

The noise model, experimental configurations, result files and limitations are documented. The results are suitable for the next stage of shared metrics, result analysis and reporting, with the stated limitations retained.
