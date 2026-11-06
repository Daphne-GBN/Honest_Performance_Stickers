#!/usr/bin/env python3
"""
generate_instances.py  --  Max-Cut benchmark instances with EXACT optima.

Output
  instances/<name>.txt   G-set format: first line "n m", then m lines "u v w"
                         (vertices are 1-indexed, w is the edge weight)
  manifest.csv           one row per instance, optimum filled in
Run
  python generate_instances.py            # generate everything
  python generate_instances.py --verify   # re-check headers + re-solve optima

Families (3 required, plus a hand-checkable one)
  er     Erdos-Renyi G(n, p=0.5), unit weights
  reg3   random 3-regular graph, unit weights   (n must be even)
  pm1    Erdos-Renyi G(n, p=0.5), weights +1 / -1 (same style as G-set's signed graphs)
  cycle  plain n-cycle, unit weights; optimum is n for even n  (verify by hand)

Why brute force?  For n <= 20, 2^(n-1) partitions is under 600k -- trivial,
and the optimum is EXACT, not "best known".
"""
import argparse
import csv
import os
import random
import sys

import numpy as np

SIZES = [4, 6, 8, 10, 12, 14, 16, 18, 20]
SEEDS_PER_SIZE = 1          # raise to 3 for a bigger set
BASE_SEED = 2026
OUT_DIR = "instances"
MANIFEST = "manifest.csv"


# ----------------------------------------------------------------- generators
def gen_er(n, rng, signed=False, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                w = rng.choice([-1, 1]) if signed else 1
                edges.append((u, v, w))
    # guarantee at least one edge so the instance is non-trivial
    if not edges:
        edges.append((0, 1, 1))
    return edges


def gen_reg3(n, rng, max_tries=1000):
    """Random 3-regular simple graph via the pairing (configuration) model."""
    assert n % 2 == 0 and n >= 4, "3-regular needs even n >= 4"
    for _ in range(max_tries):
        stubs = [v for v in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        pairs = {(min(a, b), max(a, b)) for a, b in zip(stubs[::2], stubs[1::2])}
        # reject self-loops / multi-edges (set size shrinks)
        if len(pairs) == 3 * n // 2 and all(a != b for a, b in pairs):
            return [(a, b, 1) for a, b in sorted(pairs)]
    raise RuntimeError("could not build a 3-regular graph")


def gen_cycle(n, rng=None):
    return [(i, (i + 1) % n, 1) if i < (i + 1) % n else ((i + 1) % n, i, 1)
            for i in range(n)]


# ----------------------------------------------------------------- brute force
def brute_force_maxcut(n, edges):
    """
    Exact max-cut by exhaustive search.

    A partition is an n-bit mask (bit v = side of vertex v). Flipping every
    bit gives the same cut, so we fix vertex n-1 on side 0 and enumerate only
    masks 0 .. 2^(n-1)-1.  For each mask, an edge (u,v,w) contributes w iff
    its endpoints are on different sides, i.e. bit_u XOR bit_v == 1.
    Everything is vectorised over all masks with numpy.
    Returns (optimum_value, optimal_bitstring_as_str).
    """
    masks = np.arange(2 ** (n - 1), dtype=np.int64)
    cut = np.zeros(masks.shape, dtype=np.int64)
    for u, v, w in edges:
        cut += w * (((masks >> u) ^ (masks >> v)) & 1)
    best = int(cut.argmax())
    bits = "".join(str((best >> v) & 1) for v in range(n))  # vertex 0 first
    return int(cut[best]), bits


def cut_value(edges, bits):
    return sum(w for u, v, w in edges if bits[u] != bits[v])


# ----------------------------------------------------------------- file I/O
def write_instance(path, n, edges):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v, w in edges:
            f.write(f"{u + 1} {v + 1} {w}\n")      # 1-indexed like G-set


def read_instance(path):
    with open(path) as f:
        n, m = map(int, f.readline().split())
        edges = []
        for line in f:
            if line.strip():
                u, v, w = line.split()
                edges.append((int(u) - 1, int(v) - 1, int(w)))
    return n, m, edges


# ----------------------------------------------------------------- main
def generate():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    families = [
        ("er",    lambda n, r: gen_er(n, r, signed=False), "unweighted"),
        ("reg3",  gen_reg3,                                "unweighted"),
        ("pm1",   lambda n, r: gen_er(n, r, signed=True),  "+1/-1"),
        ("cycle", gen_cycle,                               "unweighted"),
    ]
    for fam, fn, wtype in families:
        for n in SIZES:
            if fam == "reg3" and n % 2:
                continue
            for k in range(SEEDS_PER_SIZE):
                seed = BASE_SEED + 1000 * n + 7 * k + sum(map(ord, fam))
                rng = random.Random(seed)
                edges = fn(n, rng)
                opt, bits = brute_force_maxcut(n, edges)
                assert cut_value(edges, bits) == opt          # self-check
                name = f"{fam}_n{n}_s{k}"
                write_instance(os.path.join(OUT_DIR, name + ".txt"), n, edges)
                rows.append(dict(name=name, family=fam, n=n, m=len(edges),
                                 weights=wtype, seed=seed, optimum=opt,
                                 optimal_partition=bits,
                                 file=f"{OUT_DIR}/{name}.txt"))
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} instances to {OUT_DIR}/ and {MANIFEST}")


def verify():
    ok = True
    with open(MANIFEST) as f:
        for row in csv.DictReader(f):
            n, m, edges = read_instance(row["file"])
            if m != len(edges) or n != int(row["n"]) or m != int(row["m"]):
                print("HEADER MISMATCH:", row["name"]); ok = False
            opt, _ = brute_force_maxcut(n, edges)
            if opt != int(row["optimum"]):
                print("OPTIMUM MISMATCH:", row["name"]); ok = False
            if cut_value(edges, row["optimal_partition"]) != opt:
                print("PARTITION MISMATCH:", row["name"]); ok = False
    print("ALL CHECKS PASSED" if ok else "FAILURES FOUND")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    verify() if a.verify else generate()
