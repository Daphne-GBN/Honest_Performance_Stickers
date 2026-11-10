import math
import statistics
from loader import Graph, cut_value
def exact_maxcut(graph: Graph, max_n: int = 22) -> dict:
    """
    Find the exact maximum cut by checking every unique partition.

    Bitstring character i represents graph node i.
    Node 0 is fixed to 0 to avoid complementary duplicates.
    """

    if graph.n > max_n:
        raise ValueError(
            f"Graph has {graph.n} nodes; exact calculation "
            f"is limited to {max_n} nodes."
        )

    best_cut = float("-inf")
    best_partition = None
    partitions_checked = 0

    for mask in range(1 << (graph.n - 1)):
        bitstring = "0" + "".join(
            str((mask >> (node - 1)) & 1)
            for node in range(1, graph.n)
        )

        current_cut = cut_value(graph, bitstring)
        partitions_checked += 1

        if current_cut > best_cut:
            best_cut = current_cut
            best_partition = bitstring

    return {
        "optimum": best_cut,
        "partition": best_partition,
        "partitions_checked": partitions_checked,
    }

def approximation_ratio(
    achieved_cut: float,
    exact_optimum: float,
) -> float | None:
    """
    Calculate solution quality relative to the exact optimum.

    Returns None when the optimum is zero or negative.
    """

    achieved_cut = float(achieved_cut)
    exact_optimum = float(exact_optimum)

    if not math.isfinite(achieved_cut):
        raise ValueError("Achieved cut must be finite")

    if not math.isfinite(exact_optimum):
        raise ValueError("Exact optimum must be finite")

    if exact_optimum <= 0:
        return None

    return achieved_cut / exact_optimum


def repetitions_to_99(
    success_probability: float,
) -> int | None:
    """
    Estimate independent repetitions needed for at least
    a 99% probability of finding an optimal solution.

    Returns None if the success probability is zero.
    """

    p = float(success_probability)

    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError(
            "Success probability must be between 0 and 1"
        )

    if p == 0:
        return None

    if p == 1:
        return 1

    return math.ceil(math.log(0.01) / math.log1p(-p))


def distribution_metrics(
    cut_values: list[float],
    exact_optimum: float,
    tolerance: float = 1e-9,
) -> dict:
    """
    Summarize repeated solver runs using their cut values.

    A run is successful when its cut value is within
    tolerance of the exact optimum.
    """

    if not cut_values:
        raise ValueError("cut_values cannot be empty")

    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("Tolerance must be finite and non-negative")

    values = [float(value) for value in cut_values]

    if not all(math.isfinite(value) for value in values):
        raise ValueError("All cut values must be finite")

    exact_optimum = float(exact_optimum)

    if not math.isfinite(exact_optimum):
        raise ValueError("Exact optimum must be finite")

    successes = sum(
        abs(value - exact_optimum) <= tolerance
        for value in values
    )

    probability = successes / len(values)

    return {
        "runs": len(values),
        "best_cut": max(values),
        "worst_cut": min(values),
        "mean_cut": statistics.mean(values),
        "std_cut": statistics.pstdev(values),
        "successes": successes,
        "success_probability": probability,
        "repetitions_to_99": repetitions_to_99(probability),
        "mean_approximation_ratio": (
            statistics.mean(
                approximation_ratio(value, exact_optimum)
                for value in values
            )
            if exact_optimum > 0 else None
        ),
    }
