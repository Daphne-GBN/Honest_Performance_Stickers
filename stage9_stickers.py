"""
Stage 9: generate Honest Performance Stickers and aggregate analysis.

Input:
    results/experiments.jsonl (created by ResultsStore)

Output:
    results/stickers/index.html
    results/stickers/sticker_*.html
    results/stickers/aggregate_summary.csv
    results/stickers/aggregate_summary.md
    results/stickers/plots/quality_by_solver.png (if matplotlib is installed)

Run:
    python stage9_stickers.py
"""
import csv
import html
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def finite(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def load_records(path):
    records = []
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run Stage 8 or point --input to an existing JSONL file."
        )
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"WARNING: ignoring malformed JSONL line {line_number}")
    return records


def quality_value(record):
    # QAOA's current runner returns an expected cut, not a sampled bitstring.
    # Keep it explicitly labelled as expected cut; do not call it best sampled cut.
    return finite(record.get("best_cut")) if record.get("best_cut") is not None else finite(record.get("expected_cut"))


def ratio_value(record):
    quality = quality_value(record)
    optimum = finite(record.get("exact_optimum"))
    if quality is None or optimum is None or optimum <= 0:
        return None
    return quality / optimum


def group_records(records):
    groups = defaultdict(list)
    for row in records:
        key = (
            row.get("instance"), row.get("solver"), row.get("optimizer"),
            row.get("p"), row.get("noise_probability"),
        )
        groups[key].append(row)
    return groups


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def make_sticker(record, index, destination):
    q = quality_value(record)
    ratio = ratio_value(record)
    is_expected = record.get("best_cut") is None and record.get("expected_cut") is not None
    quality_label = "Expected cut" if is_expected else "Best validated cut"
    error = record.get("error") or ""
    values = [
        ("Solver", record.get("solver")),
        ("Optimizer", record.get("optimizer") or "N/A"),
        ("Instance", record.get("instance")),
        ("Graph size", f"{record.get('nodes')} nodes / {record.get('edges')} edges"),
        ("Density", record.get("density")),
        ("QAOA depth", record.get("p") if record.get("p") is not None else "N/A"),
        ("Noise probability", record.get("noise_probability") if record.get("noise_probability") is not None else "Noiseless / N/A"),
        (quality_label, q if q is not None else "N/A"),
        ("Exact optimum", record.get("exact_optimum") if record.get("exact_optimum") is not None else "N/A"),
        ("Approximation ratio", ratio if ratio is not None else "N/A"),
        ("Runtime (seconds)", record.get("runtime_seconds") if record.get("runtime_seconds") is not None else "N/A"),
        ("Objective evaluations", record.get("function_evaluations") if record.get("function_evaluations") is not None else "N/A"),
        ("TTS 99% (seconds)", record.get("time_to_solution_99_seconds") if record.get("time_to_solution_99_seconds") is not None else "Not estimable"),
        ("Validation", record.get("validation_passed") if record.get("validation_passed") is not None else "Not reported"),
        ("Optimizer status", record.get("optimizer_success") if record.get("optimizer_success") is not None else "Not certified"),
        ("Simulator", record.get("simulator") or "Not recorded"),
        ("Error / limitation", error or "None recorded"),
    ]
    body = "\n".join(
        f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>"
        for k, v in values
    )
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Honest Performance Sticker {index}</title>
<style>
body{{font-family:Arial,sans-serif;background:#f4f6f8;margin:0;padding:28px;color:#18212b}}
main{{max-width:760px;margin:auto;background:white;border:1px solid #d9e0e7;border-radius:12px;padding:24px}}
h1{{font-size:23px;margin-top:0}}p{{color:#526170}}table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:10px;border-top:1px solid #e5e9ee;vertical-align:top}}
th{{width:34%;color:#334155}}.note{{font-size:13px;color:#5b6470;margin-top:18px}}
</style></head><body><main><h1>Honest Performance Sticker #{index}</h1>
<p>One recorded solver configuration. Values are shown only when present in the raw result.</p>
<table>{body}</table>
<p class="note">Interpretation: QAOA expected cut is not a measured best bitstring. TTS is shown only when the results store can estimate it from empirical success probability and runtime. Missing values are not inferred.</p>
</main></body></html>"""
    path = destination / f"sticker_{index:05d}.html"
    path.write_text(page, encoding="utf-8")
    return path.name


def aggregate(groups):
    rows = []
    for key, group in sorted(groups.items(), key=lambda item: tuple("" if x is None else str(x) for x in item[0])):
        instance, solver, optimizer, p, noise = key
        values = [v for v in (quality_value(r) for r in group) if v is not None]
        ratios = [v for v in (ratio_value(r) for r in group) if v is not None]
        runtimes = [v for v in (finite(r.get("runtime_seconds")) for r in group) if v is not None]
        evals = [v for v in (finite(r.get("function_evaluations")) for r in group) if v is not None]
        failures = sum(bool(r.get("error")) for r in group)
        rows.append({
            "instance": instance, "solver": solver, "optimizer": optimizer,
            "p": p, "noise_probability": noise, "records": len(group),
            "successful_records": len(group) - failures, "failures": failures,
            "mean_quality": statistics.mean(values) if values else None,
            "std_quality": statistics.pstdev(values) if len(values) > 1 else (0.0 if values else None),
            "mean_approximation_ratio": statistics.mean(ratios) if ratios else None,
            "mean_runtime_seconds": statistics.mean(runtimes) if runtimes else None,
            "mean_function_evaluations": statistics.mean(evals) if evals else None,
            "tts_99_seconds": next((r.get("time_to_solution_99_seconds") for r in group
                                    if r.get("time_to_solution_99_seconds") is not None), None),
        })
    return rows


def write_markdown(path, rows, record_count):
    lines = [
        "# Stage 9 — Honest Performance Stickers",
        "",
        f"- Raw records processed: {record_count}",
        f"- Configuration groups: {len(rows)}",
        "- Source: ResultsStore JSONL records.",
        "- Missing metrics are left unavailable; no quantum-advantage claim is inferred.",
        "- QAOA quality is its expected cut from the current optimizer interface, not a sampled best bitstring.",
        "- TTS is reported only when an empirical success probability and runtime are available.",
        "",
        "## Aggregate results",
        "",
        "| Instance | Solver | Optimizer | p | Noise | Runs | Failures | Mean quality | Mean ratio | Mean runtime (s) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        def fmt(value):
            return "N/A" if value is None else f"{value:.5g}" if isinstance(value, float) else str(value)
        lines.append(
            f"| {r['instance']} | {r['solver']} | {r['optimizer'] or 'N/A'} | "
            f"{fmt(r['p'])} | {fmt(r['noise_probability'])} | {r['records']} | "
            f"{r['failures']} | {fmt(r['mean_quality'])} | "
            f"{fmt(r['mean_approximation_ratio'])} | {fmt(r['mean_runtime_seconds'])} |"
        )
    lines += [
        "",
        "## Interpretation and limitations",
        "",
        "- Classical best cuts and QAOA expected cuts are different result types and must not be treated as identical measurements.",
        "- The current noisy QAOA runner supports COBYLA and SPSA only; it does not provide noisy Nelder-Mead or Adam results.",
        "- Density-matrix noise experiments are subject to the Stage 8 node guardrail.",
        "- The catalogue's weighted/unweighted coverage must be described from the actual loaded data, not assumed.",
        "- A missing TTS value means the available records do not support a defensible estimate.",
        "- This report summarizes recorded runs only. It does not claim that unrun configurations were evaluated.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_plot(rows, plot_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping optional plot.")
        return
    by_solver = defaultdict(list)
    for row in rows:
        if row["mean_approximation_ratio"] is not None:
            by_solver[str(row["solver"])].append(row["mean_approximation_ratio"])
    if not by_solver:
        print("No approximation-ratio data; skipping quality plot.")
        return
    labels = list(by_solver)
    means = [statistics.mean(by_solver[label]) for label in labels]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, means)
    ax.set_ylabel("Mean approximation ratio")
    ax.set_title("Recorded approximation ratio by solver")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=160)
    plt.close(fig)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Stage 9 stickers and reports")
    parser.add_argument("--input", default="results/experiments.jsonl")
    parser.add_argument("--output", default="results/stickers")
    args = parser.parse_args()

    records = load_records(Path(args.input))
    destination = Path(args.output)
    destination.mkdir(parents=True, exist_ok=True)

    sticker_files = [
        make_sticker(record, index, destination)
        for index, record in enumerate(records, start=1)
    ]
    rows = aggregate(group_records(records))
    fields = [
        "instance", "solver", "optimizer", "p", "noise_probability",
        "records", "successful_records", "failures", "mean_quality",
        "std_quality", "mean_approximation_ratio", "mean_runtime_seconds",
        "mean_function_evaluations", "tts_99_seconds",
    ]
    write_csv(destination / "aggregate_summary.csv", rows, fields)
    write_markdown(destination / "aggregate_summary.md", rows, len(records))

    links = "\n".join(
        f'<li><a href="{html.escape(name)}">{html.escape(name)}</a></li>'
        for name in sticker_files
    )
    index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Honest Performance Stickers</title></head><body>
<h1>Honest Performance Stickers</h1>
<p>Generated from {len(records)} raw records across {len(rows)} configuration groups.</p>
<p><a href="aggregate_summary.md">Aggregate interpretation</a> |
<a href="aggregate_summary.csv">Aggregate CSV</a></p><ol>{links}</ol>
</body></html>"""
    (destination / "index.html").write_text(index, encoding="utf-8")

    plot_dir = destination / "plots"
    plot_dir.mkdir(exist_ok=True)
    make_plot(rows, plot_dir / "quality_by_solver.png")

    print(f"Generated {len(sticker_files)} stickers.")
    print("Index:", destination / "index.html")
    print("Summary:", destination / "aggregate_summary.md")
    print("CSV:", destination / "aggregate_summary.csv")


if __name__ == "__main__":
    main()
