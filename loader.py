
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import csv
import math

import numpy as np

@dataclass
class Graph:
    """Canonical weighted, undirected graph for MaxCut."""

    n: int
    edges: list[tuple[int, int, float]]
    name: str = "unnamed"
    source: str = "unknown"
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def m(self) -> int:
        return len(self.edges)

    @property
    def total_weight(self) -> float:
        return sum(weight for _, _, weight in self.edges)

    @property
    def density(self) -> float:
        possible_edges = self.n * (self.n - 1) / 2
        return self.m / possible_edges if possible_edges else 0.0

    @property
    def weighted(self) -> bool:
        return any(weight != 1.0 for _, _, weight in self.edges)


def make_graph(
    n: int,
    edges: Iterable[tuple[int, int] | tuple[int, int, float]],
    name: str = "unnamed",
    source: str = "unknown",
    meta: dict[str, Any] | None = None,
) -> Graph:
    """
    Create a validated canonical graph.

    Conventions:
    - Vertices are numbered 0 through n-1.
    - Edges are undirected and stored with u < v.
    - Duplicate undirected edges are combined by summing weights.
    - Self-loops and invalid vertices are rejected.
    - Negative edge weights are preserved.
    """

    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")

    combined: dict[tuple[int, int], float] = {}

    for edge in edges:
        if len(edge) == 2:
            u, v = edge
            weight = 1.0
        elif len(edge) == 3:
            u, v, weight = edge
        else:
            raise ValueError(f"Invalid edge format: {edge}")

        if not isinstance(u, int) or isinstance(u, bool):
            raise ValueError(f"Invalid vertex index: {u}")

        if not isinstance(v, int) or isinstance(v, bool):
            raise ValueError(f"Invalid vertex index: {v}")

        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Vertex out of range: ({u}, {v})")

        if u == v:
            raise ValueError(
                f"Self-loops are not supported: ({u}, {v})"
            )

        try:
            weight = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid edge weight: {weight}") from exc

        if not math.isfinite(weight):
            raise ValueError(f"Edge weight must be finite: {weight}")

        key = (min(u, v), max(u, v))
        combined[key] = combined.get(key, 0.0) + weight

    canonical_edges = [
        (u, v, weight)
        for (u, v), weight in sorted(combined.items())
        if weight != 0.0
    ]

    return Graph(
        n=n,
        edges=canonical_edges,
        name=name,
        source=source,
        meta=dict(meta or {}),
    )


def cut_value(graph: Graph, bitstring: str) -> float:
    """Calculate the weighted MaxCut value of a bitstring."""

    if len(bitstring) != graph.n:
        raise ValueError(
            f"Expected {graph.n} bits, received {len(bitstring)}"
        )

    if any(bit not in "01" for bit in bitstring):
        raise ValueError("Bitstring must contain only 0 and 1")

    return sum(
        weight
        for u, v, weight in graph.edges
        if bitstring[u] != bitstring[v]
    )


def load_gset(
    file_path: str | Path,
    name: str | None = None,
) -> Graph:
    """
    Load a weighted graph from the project's text format.

    First line: n m
    Following lines: u v weight

    Input vertices are 1-based and converted to 0-based.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Graph file not found: {path}")

    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError(f"Empty graph file: {path}")

    header = lines[0].split()

    if len(header) != 2:
        raise ValueError("Graph header must contain exactly: n m")

    try:
        n, expected_m = map(int, header)
    except ValueError as exc:
        raise ValueError(
            "Graph header must contain integer values"
        ) from exc

    if n < 1 or expected_m < 0:
        raise ValueError("Invalid vertex or edge count in graph header")

    edges = []

    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.split()

        if len(parts) != 3:
            raise ValueError(
                f"Line {line_number}: expected u v weight, got: {line}"
            )

        try:
            u, v = int(parts[0]), int(parts[1])
            weight = float(parts[2])
        except ValueError as exc:
            raise ValueError(
                f"Line {line_number}: invalid edge values: {line}"
            ) from exc

        edges.append((u - 1, v - 1, weight))

    if len(edges) != expected_m:
        raise ValueError(
            f"Expected {expected_m} edges, found {len(edges)}"
        )

    return make_graph(
        n=n,
        edges=edges,
        name=name or path.stem,
        source=str(path),
        meta={"input_vertex_indexing": "1-based"},
    )


# Generic project loader alias.
load_graph = load_gset


def load_edgelist_csv(
    file_path: str | Path,
    n: int,
    name: str | None = None,
    zero_based: bool = False,
) -> Graph:
    """Load a weighted edge list from a CSV file."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    edges = []

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file must contain a header")

        columns = {
            column.strip().lower(): column
            for column in reader.fieldnames
            if column is not None
        }

        if not {"u", "v"}.issubset(columns):
            raise ValueError("CSV must contain u and v columns")

        for line_number, row in enumerate(reader, start=2):
            try:
                u = int(row[columns["u"]])
                v = int(row[columns["v"]])

                weight_column = columns.get("weight")

                weight = (
                    float(row[weight_column])
                    if weight_column and row[weight_column].strip()
                    else 1.0
                )

            except (TypeError, ValueError, AttributeError) as exc:
                raise ValueError(
                    f"Invalid CSV values at line {line_number}"
                ) from exc

            if not zero_based:
                u -= 1
                v -= 1

            edges.append((u, v, weight))

    return make_graph(
        n=n,
        edges=edges,
        name=name or path.stem,
        source=str(path),
        meta={
            "input_format": "csv",
            "input_vertex_indexing": (
                "0-based" if zero_based else "1-based"
            ),
        },
    )


def from_adjacency(
    matrix: Any,
    name: str = "adjacency_graph",
) -> Graph:
    """Create an undirected weighted graph from an adjacency matrix."""

    try:
        adjacency = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Adjacency matrix must contain numeric values"
        ) from exc

    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("Adjacency matrix must be square")

    if adjacency.shape[0] < 1:
        raise ValueError("Adjacency matrix cannot be empty")

    if not np.all(np.isfinite(adjacency)):
        raise ValueError(
            "Adjacency matrix must contain finite values"
        )

    if not np.allclose(adjacency, adjacency.T):
        raise ValueError("Adjacency matrix must be symmetric")

    if not np.allclose(np.diag(adjacency), 0.0):
        raise ValueError("Self-loops are not supported")

    n = adjacency.shape[0]

    edges = [
        (u, v, float(adjacency[u, v]))
        for u in range(n)
        for v in range(u + 1, n)
        if adjacency[u, v] != 0.0
    ]

    return make_graph(
        n=n,
        edges=edges,
        name=name,
        source="adjacency_matrix",
        meta={"input_format": "adjacency_matrix"},
    )


def from_networkx(
    network,
    name: str | None = None,
) -> Graph:
    """Convert an undirected NetworkX graph into the canonical Graph."""

    import networkx as nx

    if not isinstance(network, nx.Graph):
        raise TypeError("Expected a NetworkX Graph object")

    if network.is_directed():
        raise ValueError("Directed graphs are not supported")

    if network.is_multigraph():
        raise ValueError(
            "MultiGraph is not supported; combine parallel edges first"
        )

    nodes = list(network.nodes())

    if not nodes:
        raise ValueError("NetworkX graph cannot be empty")

    node_to_index = {
        node: index for index, node in enumerate(nodes)
    }

    edges = []

    for u, v, data in network.edges(data=True):
        weight = data.get("weight", 1.0)
        edges.append(
            (node_to_index[u], node_to_index[v], weight)
        )

    return make_graph(
        n=len(nodes),
        edges=edges,
        name=name or str(
            network.graph.get("name", "networkx_graph")
        ),
        source="networkx",
        meta={
            "input_format": "networkx",
            "original_nodes": [str(node) for node in nodes],
        },
    )


def to_qubo(graph: Graph) -> np.ndarray:
    """
    Convert MaxCut into a QUBO matrix.

    Convention:
        x.T @ Q @ x = -Cut(x)

    Off-diagonal terms are stored symmetrically.
    """

    Q = np.zeros((graph.n, graph.n), dtype=float)

    for u, v, weight in graph.edges:
        Q[u, u] -= weight
        Q[v, v] -= weight
        Q[u, v] += weight
        Q[v, u] += weight

    return Q


def to_ising(
    graph: Graph,
) -> tuple[dict[tuple[int, int], float], np.ndarray, float]:
    """
    Convert weighted MaxCut into an Ising model.

    Convention:
        E(s) = sum(J_uv * s_u * s_v)
             + sum(h_i * s_i)
             + offset

        E(s) = -Cut(x), where s_i = 1 - 2*x_i.
    """

    J: dict[tuple[int, int], float] = {}
    h = np.zeros(graph.n, dtype=float)
    offset = 0.0

    for u, v, weight in graph.edges:
        J[(u, v)] = J.get((u, v), 0.0) + weight / 2.0
        offset -= weight / 2.0

    return J, h, offset


def to_pysa_qubo(graph: Graph) -> np.ndarray:
    """
    Convert the canonical QUBO matrix to NASA PySA's
    symmetric matrix convention.

    PySA energy:
        E(x) = x.T @ C @ x / 2 + h.T @ x

    The diagonal of the input matrix becomes h.
    """

    Q = to_qubo(graph)

    Q_pysa = 2.0 * Q
    np.fill_diagonal(Q_pysa, np.diag(Q))

    return Q_pysa

def load_catalogue(
    manifest_path: str | Path = "instances/manifest.csv",
    split: str | None = None,
) -> list[Graph]:
    """
    Load graph instances listed in the project manifest.

    Args:
        manifest_path: Path to manifest.csv.
        split: Optional filter: 'tuning' or 'benchmark'.

    Returns:
        List of validated canonical Graph objects.
    """

    manifest = Path(manifest_path)

    if not manifest.is_file():
        raise FileNotFoundError(
            f"Manifest not found: {manifest}"
        )

    if split is not None and split not in {"tuning", "benchmark"}:
        raise ValueError(
            "split must be 'tuning', 'benchmark', or None"
        )

    graphs = []
    project_root = manifest.parent

    with manifest.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "name", "split", "family", "nodes",
            "edges", "seed", "optimum",
            "optimal_partition",
        }

        if not reader.fieldnames or not required_columns.issubset(
            reader.fieldnames
        ):
            raise ValueError(
                f"Manifest must contain columns: {sorted(required_columns)}"
            )

        for row in reader:
            row_split = row["split"].strip()

            if split is not None and row_split != split:
                continue

            name = row["name"].strip()
            graph_path = project_root / row_split / f"{name}.txt"

            graph = load_gset(graph_path, name=name)

            expected_nodes = int(row["nodes"])
            expected_edges = int(row["edges"])

            if graph.n != expected_nodes:
                raise ValueError(
                    f"{name}: manifest says {expected_nodes} nodes, "
                    f"but graph contains {graph.n}"
                )

            if graph.m != expected_edges:
                raise ValueError(
                    f"{name}: manifest says {expected_edges} edges, "
                    f"but graph contains {graph.m}"
                )

            graph.meta.update({
                "split": row_split,
                "family": row["family"].strip(),
                "seed": int(row["seed"]),
                "optimum": float(row["optimum"]),
                "optimal_partition": normalize_manifest_partition(
                    graph,
                    row["optimal_partition"].strip(),
                    float(row["optimum"]),
                ),
                "density": float(row["density"]),
                "generator": row["generator"].strip(),
            })

            graphs.append(graph)

    return graphs


def load_instance(
    instance_name: str,
    manifest_path: str | Path = "instances/manifest.csv",
) -> Graph:
    """Load one graph instance by its manifest name."""

    graphs = load_catalogue(manifest_path)

    for graph in graphs:
        if graph.name == instance_name:
            return graph

    raise KeyError(
        f"Instance '{instance_name}' was not found in the manifest"
    )
def normalize_manifest_partition(
    graph: Graph,
    partition: str,
    optimum: float,
    tolerance: float = 1e-9,
) -> str:
    """
    Convert a manifest partition to the canonical convention:
    bitstring character i represents graph node i.

    The dataset generator stores partitions in reversed
    bit order, so try the reversed string first.
    """

    if not isinstance(partition, str):
        raise ValueError("Partition must be a string")

    partition = partition.strip()

    if len(partition) != graph.n or any(
        bit not in "01" for bit in partition
    ):
        raise ValueError("Invalid partition bitstring")

    optimum = float(optimum)

    if not math.isfinite(optimum):
        raise ValueError("Optimum must be finite")

    reversed_partition = partition[::-1]

    if abs(cut_value(graph, reversed_partition) - optimum) <= tolerance:
        return reversed_partition

    if abs(cut_value(graph, partition) - optimum) <= tolerance:
        return partition

    raise ValueError(
        "Neither partition orientation matches the stored optimum"
    )