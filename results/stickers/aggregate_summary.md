# Stage 9 — Honest Performance Stickers

- Raw records processed: 72
- Configuration groups: 42
- Source: ResultsStore JSONL records.
- Missing metrics are left unavailable; no quantum-advantage claim is inferred.
- QAOA quality is its expected cut from the current optimizer interface, not a sampled best bitstring.
- TTS is reported only when an empirical success probability and runtime are available.

## Aggregate results

| Instance | Solver | Optimizer | p | Noise | Runs | Failures | Mean quality | Mean ratio | Mean runtime (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| er_n8_p25_s1001 | pt | N/A | N/A | N/A | 1 | 0 | 5 | 1 | 0.015787 |
| er_n8_p25_s1001 | qaoa_noiseless | ADAM | 1 | N/A | 1 | 0 | 3.6116 | 0.72232 | 0.92635 |
| er_n8_p25_s1001 | qaoa_noiseless | COBYLA | 1 | N/A | 1 | 0 | 4.0201 | 0.80402 | 1.4794 |
| er_n8_p25_s1001 | qaoa_noiseless | NELDER-MEAD | 1 | N/A | 1 | 0 | 4.0183 | 0.80366 | 1.2949 |
| er_n8_p25_s1001 | qaoa_noiseless | SPSA | 1 | N/A | 1 | 0 | 3.9364 | 0.78728 | 1.3398 |
| er_n8_p25_s1001 | sa | N/A | N/A | N/A | 1 | 0 | 5 | 1 | 0.013589 |
| er_n8_p25_s1002 | pt | N/A | N/A | N/A | 1 | 0 | 5 | 1 | 0.013993 |
| er_n8_p25_s1002 | qaoa_noiseless | ADAM | 1 | N/A | 1 | 0 | 3.6116 | 0.72232 | 1.0858 |
| er_n8_p25_s1002 | qaoa_noiseless | COBYLA | 1 | N/A | 1 | 0 | 4.0201 | 0.80402 | 1.3462 |
| er_n8_p25_s1002 | qaoa_noiseless | NELDER-MEAD | 1 | N/A | 1 | 0 | 4.0183 | 0.80366 | 1.3806 |
| er_n8_p25_s1002 | qaoa_noiseless | SPSA | 1 | N/A | 1 | 0 | 3.9364 | 0.78728 | 1.4057 |
| er_n8_p25_s1002 | sa | N/A | N/A | N/A | 1 | 0 | 5 | 1 | 0.013114 |
| er_n8_p25_s5001 | pt | N/A | N/A | N/A | 6 | 0 | 6 | 1 | 0.0036009 |
| er_n8_p25_s5001 | qaoa_noiseless | ADAM | 1 | N/A | 6 | 0 | 4.6433 | 0.77388 | 0.75869 |
| er_n8_p25_s5001 | qaoa_noiseless | ADAM | 2 | N/A | 1 | 0 | 5.0222 | 0.83703 | 2.8898 |
| er_n8_p25_s5001 | qaoa_noiseless | ADAM | 3 | N/A | 1 | 0 | 4.7545 | 0.79242 | 3.0022 |
| er_n8_p25_s5001 | qaoa_noiseless | COBYLA | 1 | N/A | 6 | 0 | 4.8851 | 0.81418 | 1.3186 |
| er_n8_p25_s5001 | qaoa_noiseless | COBYLA | 2 | N/A | 1 | 0 | 5.2224 | 0.8704 | 3.2615 |
| er_n8_p25_s5001 | qaoa_noiseless | COBYLA | 3 | N/A | 1 | 0 | 5.349 | 0.8915 | 4.533 |
| er_n8_p25_s5001 | qaoa_noiseless | NELDER-MEAD | 1 | N/A | 6 | 0 | 4.8571 | 0.80952 | 1.288 |
| er_n8_p25_s5001 | qaoa_noiseless | NELDER-MEAD | 2 | N/A | 1 | 0 | 5.0748 | 0.8458 | 3.2527 |
| er_n8_p25_s5001 | qaoa_noiseless | NELDER-MEAD | 3 | N/A | 1 | 0 | 5.0388 | 0.8398 | 5.053 |
| er_n8_p25_s5001 | qaoa_noiseless | SPSA | 1 | N/A | 6 | 0 | 4.8172 | 0.80287 | 1.3448 |
| er_n8_p25_s5001 | qaoa_noiseless | SPSA | 2 | N/A | 1 | 0 | 4.9839 | 0.83065 | 3.1311 |
| er_n8_p25_s5001 | qaoa_noiseless | SPSA | 3 | N/A | 1 | 0 | 5.313 | 0.88551 | 5.068 |
| er_n8_p25_s5001 | qaoa_noisy | COBYLA | 1 | 0.001 | 1 | 0 | 4.765 | 0.79417 | 11.351 |
| er_n8_p25_s5001 | qaoa_noisy | SPSA | 1 | 0.001 | 1 | 0 | 4.8502 | 0.80837 | 9.5097 |
| er_n8_p25_s5001 | sa | N/A | N/A | N/A | 6 | 0 | 6 | 1 | 0.004103 |
| er_n8_p25_s5002 | pt | N/A | N/A | N/A | 1 | 0 | 9 | 1 | 0.014751 |
| er_n8_p25_s5002 | qaoa_noiseless | ADAM | 1 | N/A | 1 | 0 | 7.1332 | 0.79257 | 1.6809 |
| er_n8_p25_s5002 | qaoa_noiseless | ADAM | 2 | N/A | 1 | 0 | 7.5645 | 0.8405 | 3.9702 |
| er_n8_p25_s5002 | qaoa_noiseless | ADAM | 3 | N/A | 1 | 0 | 7.5629 | 0.84033 | 4.0001 |
| er_n8_p25_s5002 | qaoa_noiseless | COBYLA | 1 | N/A | 1 | 0 | 7.1771 | 0.79746 | 2.1453 |
| er_n8_p25_s5002 | qaoa_noiseless | COBYLA | 2 | N/A | 1 | 0 | 7.9034 | 0.87815 | 4.0435 |
| er_n8_p25_s5002 | qaoa_noiseless | COBYLA | 3 | N/A | 1 | 0 | 8.1699 | 0.90777 | 6.0324 |
| er_n8_p25_s5002 | qaoa_noiseless | NELDER-MEAD | 1 | N/A | 1 | 0 | 7.1764 | 0.79738 | 2.3631 |
| er_n8_p25_s5002 | qaoa_noiseless | NELDER-MEAD | 2 | N/A | 1 | 0 | 7.6445 | 0.84939 | 4.2207 |
| er_n8_p25_s5002 | qaoa_noiseless | NELDER-MEAD | 3 | N/A | 1 | 0 | 7.8748 | 0.87498 | 6.5088 |
| er_n8_p25_s5002 | qaoa_noiseless | SPSA | 1 | N/A | 1 | 0 | 7.104 | 0.78933 | 2.2991 |
| er_n8_p25_s5002 | qaoa_noiseless | SPSA | 2 | N/A | 1 | 0 | 7.6338 | 0.8482 | 4.4711 |
| er_n8_p25_s5002 | qaoa_noiseless | SPSA | 3 | N/A | 1 | 0 | 7.9191 | 0.8799 | 6.1919 |
| er_n8_p25_s5002 | sa | N/A | N/A | N/A | 1 | 0 | 9 | 1 | 0.013845 |

## Interpretation and limitations

- Classical best cuts and QAOA expected cuts are different result types and must not be treated as identical measurements.
- The current noisy QAOA runner supports COBYLA and SPSA only; it does not provide noisy Nelder-Mead or Adam results.
- Density-matrix noise experiments are subject to the Stage 8 node guardrail.
- The catalogue's weighted/unweighted coverage must be described from the actual loaded data, not assumed.
- A missing TTS value means the available records do not support a defensible estimate.
- This report summarizes recorded runs only. It does not claim that unrun configurations were evaluated.
