# Stages 8 and 9 — Run Guide

## What these files add
- `stage8_experiments.py`: resumable orchestration using the existing classical, noiseless QAOA, noisy QAOA, graph catalogue, and ResultsStore interfaces.
- `stage9_stickers.py`: individual HTML stickers, aggregate CSV/Markdown, and an optional PNG plot from the raw JSONL results.

Existing Stage 1–7 modules are not modified.

## Important scientific distinctions
1. The current noiseless QAOA optimizer returns an **expected cut**, not a measured best bitstring. The ResultsStore records it as `expected_cut`; Stage 9 labels it as expected cut and calculates a separate expected-cut ratio for analysis. It is not called a best sampled cut.
2. Classical SA/PT returns validated bitstrings and best cuts.
3. The current noise runner supports **COBYLA and SPSA only**. Noisy Nelder-Mead and Adam are not silently substituted.
4. Density-matrix noise has a conservative node guardrail (default 10).
5. TTS is shown only when empirical success probability and runtime exist. Expected-cut-only QAOA runs do not provide a defensible success probability.
6. The runner uses fixed existing settings; it does not perform a hyperparameter search. Do not claim tuning was completed unless a separate tuning procedure is run and documented.
7. Failed configurations are saved as failure records and are not marked complete, so rerunning the same command retries them.

## Step A — Copy the two Python files
Copy `stage8_experiments.py` and `stage9_stickers.py` into the project root:
`C:\\Users\\Pooja\\Downloads\\SEMS\\Honest_Performance_Stickers_New`

Do not replace any existing project file.

## Step B — Run a small smoke grid first
From the activated `(.venv-hq)` terminal:
```powershell
python stage8_experiments.py --split benchmark --limit 2 --repeats 1
```
This runs SA/PT plus noiseless QAOA p=1,2,3 with the four existing optimizers on two benchmark instances. It is a smoke/pilot, not the complete 140-instance benchmark.

## Step C — Generate stickers
```powershell
python stage9_stickers.py
```
Open `results\\stickers\\index.html` in a browser.

## Step D — Expand the grid after checking runtime
All benchmark instances, five repeats:
```powershell
python stage8_experiments.py --split benchmark --limit 0 --repeats 5
```
Tuning split, separately:
```powershell
python stage8_experiments.py --split tuning --limit 0 --repeats 5
```
Reduced density-matrix noise pilot:
```powershell
python stage8_experiments.py --split benchmark --limit 2 --repeats 1 --include-noise
```
The noise pilot runs four specified noise levels (0, 0.001, 0.005, 0.02) for p=1,2,3 using COBYLA and SPSA only, subject to the node guardrail. It may take substantially longer.

## Resume behavior
The runner stores completed configuration IDs in:
`results\\stage8_run_ledger.jsonl`

Rerun the exact same command after interruption. Completed IDs are skipped; failed configurations are retried. Changing seeds, budgets, split, or noise parameters creates different configuration IDs.

## Outputs
- `results\\experiments.csv` and `results\\experiments.jsonl`: shared Stage 7 raw records.
- `results\\stage8_run_ledger.jsonl`: resume/failure ledger.
- `results\\stickers\\index.html`: sticker index.
- `results\\stickers\\sticker_*.html`: one sticker per raw record.
- `results\\stickers\\aggregate_summary.csv`: grouped numerical summary.
- `results\\stickers\\aggregate_summary.md`: human-readable summary.
- `results\\stickers\\plots\\quality_by_solver.png`: optional plot.

## Completion reporting
A successful smoke grid verifies the orchestration path, not the full Stage 8 experiment grid. Stage 8 is complete only after the intended planned configurations have run or are explicitly marked skipped with reasons. Stage 9 is complete when stickers and aggregate outputs are regenerated from the final raw logs and selected stickers can be traced back to their source records.

## Final workstation pilot record (11 November 2026)

- Stage 8 recorded 72 experiment records; Stage 9 generated 72 individual stickers and an aggregate report.
- The benchmark pilot used two 8-node benchmark instances, one repeat, QAOA depths p=1, 2, 3, and four noiseless optimizers, with an evaluation budget of 20.
- Classical SA and PT were included. A limited noisy pilot tested COBYLA and SPSA at noise probability 0.001.
- A preliminary tuning comparison used two 8-node tuning instances, one seed, p=1, and an evaluation budget of 20. COBYLA had the highest mean expected cut in that small comparison. This is an exploratory selection, not an exhaustive hyperparameter search.
- The full 280-instance catalogue and the planned 5-10 repeats per configuration were not completed. Results must be described as a reduced workstation pilot, not a full benchmark.
- The HybridQ C++ core was unavailable; the experiments used the documented NumPy fallback.
- The aggregate report contains recorded configurations only. Missing metrics remain unavailable, and no quantum-advantage claim is made.

