import os, csv
import numpy as np
import networkx as nx

# dataset preparation for the Max-Cut benchmark
# writes G-set format files + a manifest with exact optima
# tuning and benchmark sets use disjoint seed ranges so neither leaks into the other

OUT = "instances"
SIZES = [8, 10, 12, 14, 16, 18, 20]
DENSITIES = [0.25, 0.5, 0.75]
REPS = 5
BRUTE_LIMIT = 22

# disjoint seed ranges -> disjoint instance sets
TUNE_SEED0 = 1000
BENCH_SEED0 = 5000


def brute_force(g):
    # exact max-cut: enumerate half the assignments (node 0 fixed), vectorised over masks
    n = g.number_of_nodes()
    idx = {v: i for i, v in enumerate(sorted(g.nodes()))}
    masks = np.arange(1 << (n - 1), dtype=np.int64)
    cut = np.zeros(masks.shape, dtype=np.int64)
    for u, v, d in g.edges(data=True):
        a, b = idx[u], idx[v]
        cut += (((masks >> a) & 1) ^ ((masks >> b) & 1)) * int(d.get("weight", 1))
    k = int(cut.argmax())
    return int(cut[k]), format(int(masks[k]), "0%db" % n)


def write_gset(g, path):
    nodes = sorted(g.nodes())
    idx = {v: i + 1 for i, v in enumerate(nodes)}
    with open(path, "w") as f:
        f.write("%d %d\n" % (g.number_of_nodes(), g.number_of_edges()))
        for u, v, d in g.edges(data=True):
            f.write("%d %d %d\n" % (idx[u], idx[v], int(d.get("weight", 1))))


def make_row(g, name, split, family, n, p, seed, outdir):
    write_gset(g, os.path.join(outdir, name + ".txt"))
    opt, part = (None, None)
    if n <= BRUTE_LIMIT:
        opt, part = brute_force(g)
    return {
        "name": name,
        "split": split,
        "family": family,
        "nodes": n,
        "edges": g.number_of_edges(),
        "density": round(nx.density(g), 4),
        "er_p": p if p is not None else "",
        "seed": seed,
        "optimum": int(opt) if opt is not None else "",
        "optimal_partition": part if part is not None else "",
        "generator": "networkx %s" % nx.__version__,
    }


def build(split, seed0, outdir):
    os.makedirs(outdir, exist_ok=True)
    rows = []
    seed = seed0
    for n in SIZES:
        for p in DENSITIES:
            for _ in range(REPS):
                seed += 1
                g = nx.erdos_renyi_graph(n, p, seed=seed)
                if g.number_of_edges() == 0:
                    continue
                name = "er_n%d_p%02d_s%d" % (n, int(p * 100), seed)
                rows.append(make_row(g, name, split, "erdos_renyi", n, p, seed, outdir))
        if n % 2 == 0:
            for _ in range(REPS):
                seed += 1
                g = nx.random_regular_graph(3, n, seed=seed)
                name = "reg3_n%d_s%d" % (n, seed)
                rows.append(make_row(g, name, split, "3_regular", n, None, seed, outdir))
    return rows


def verify(rows, outdir):
    # two independent checks: optimum == |E| iff bipartite, and random sampling never beats it
    bad = 0
    for r in rows:
        if r["optimum"] == "":
            continue
        g = nx.Graph()
        with open(os.path.join(outdir, r["name"] + ".txt")) as f:
            n, m = map(int, f.readline().split())
            g.add_nodes_from(range(1, n + 1))
            for line in f:
                u, v, w = line.split()
                g.add_edge(int(u), int(v))
        opt = int(r["optimum"])
        if (opt == g.number_of_edges()) != nx.is_bipartite(g):
            print("BIPARTITE MISMATCH", r["name"])
            bad += 1
        nn = g.number_of_nodes()
        idx = {v: i for i, v in enumerate(sorted(g.nodes()))}
        trials = np.random.randint(0, 2, size=(2000, nn))
        tot = np.zeros(2000, dtype=np.int64)
        for u, v in g.edges():
            tot += trials[:, idx[u]] ^ trials[:, idx[v]]
        best = int(tot.max())
        if best > opt:
            print("SAMPLING BEAT OPTIMUM", r["name"], best, opt)
            bad += 1
    return bad


def main():
    all_rows = []
    for split, seed0 in [("tuning", TUNE_SEED0), ("benchmark", BENCH_SEED0)]:
        d = os.path.join(OUT, split)
        rows = build(split, seed0, d)
        all_rows += rows
        print("%s: %d instances -> %s/" % (split, len(rows), d))

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    tune = [r for r in all_rows if r["split"] == "tuning"]
    bench = [r for r in all_rows if r["split"] == "benchmark"]
    assert not (set(r["seed"] for r in tune) & set(r["seed"] for r in bench))

    bad = 0
    for split in ("tuning", "benchmark"):
        bad += verify([r for r in all_rows if r["split"] == split], os.path.join(OUT, split))

    print("total %d | tuning %d | benchmark %d | seed overlap: none | verification failures: %d"
          % (len(all_rows), len(tune), len(bench), bad))
    print("manifest: %s/manifest.csv" % OUT)


if __name__ == "__main__":
    main()
