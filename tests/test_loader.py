
import numpy as np
import pytest

from loader import (
    make_graph,
    cut_value,
    to_qubo,
    to_ising,
    normalize_manifest_partition,
    load_catalogue,
)


def test_graph_creation():
    graph = make_graph(3, [(0, 1, 3), (1, 2, -1), (0, 2, 2)])

    assert graph.n == 3
    assert graph.m == 3
    assert graph.total_weight == 4.0


def test_cut_value():
    graph = make_graph(3, [(0, 1, 3), (1, 2, -1), (0, 2, 2)])

    assert cut_value(graph, "011") == 5.0


def test_qubo_matches_negative_cut():
    graph = make_graph(3, [(0, 1, 3), (1, 2, -1), (0, 2, 2)])

    Q = to_qubo(graph)
    x = np.array([0, 1, 1])

    assert np.isclose(x @ Q @ x, -cut_value(graph, "011"))


def test_ising_matches_negative_cut():
    graph = make_graph(3, [(0, 1, 3), (1, 2, -1), (0, 2, 2)])

    J, h, offset = to_ising(graph)
    spins = np.array([1, -1, -1])

    energy = offset + sum(
        weight * spins[u] * spins[v]
        for (u, v), weight in J.items()
    ) + np.dot(h, spins)

    assert np.isclose(energy, -cut_value(graph, "011"))


def test_partition_normalization():
    graph = make_graph(3, [(0, 1, 3), (1, 2, -1), (0, 2, 2)])

    normalized = normalize_manifest_partition(
        graph, "110", 5.0
    )

    assert normalized == "011"
    assert cut_value(graph, normalized) == 5.0


def test_catalogue_loading():
    graphs = load_catalogue()

    assert len(graphs) == 280

    for graph in graphs:
        partition = graph.meta["optimal_partition"]
        optimum = graph.meta["optimum"]

        assert len(partition) == graph.n
        assert np.isclose(cut_value(graph, partition), optimum)
