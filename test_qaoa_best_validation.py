
import numpy as np

from loader import load_gset, cut_value
from metrics import exact_maxcut
from qaoa_depth_runner import run_qaoa, calculate_expected_cut

graph = load_gset(
    "maxcut_instances/instances/cycle_n10_s0.txt",
    name="cycle_n10_s0"
)

known_optimum = exact_maxcut(graph)["optimum"]

best_parameters = {
    2: [
        2.4834222594994344,
        1.8964410035230965,
        0.9499264843039433,
        1.2437372541959473
    ],
    3: [
        1.4733736455973159,
        0.603463449984284,
        1.8934214553008168,
        1.0058934640384127,
        0.27788146562448895,
        0.6908254584175743
    ]
}

print("=" * 55)
print("BEST QAOA PARAMETER VALIDATION")
print("=" * 55)

for p, parameters in best_parameters.items():

    gammas = parameters[:p]
    betas = parameters[p:]

    statevector = run_qaoa(graph, gammas, betas)

    probabilities = np.abs(statevector) ** 2
    expected_cut = calculate_expected_cut(graph, statevector)

    best_index = int(np.argmax(probabilities))
    best_bitstring = format(best_index, f"0{graph.n}b")
    best_cut = cut_value(graph, best_bitstring)

    print(f"\nQAOA p={p}")
    print("Expected cut:", expected_cut)
    print("Most probable bitstring:", best_bitstring)
    print("Most probable cut:", best_cut)
    print("Probability sum:", probabilities.sum())
    print("Statevector size:", len(statevector))

    assert len(statevector) == 2 ** graph.n
    assert np.isclose(probabilities.sum(), 1.0, atol=1e-5)
    assert -1e-6 <= expected_cut <= known_optimum + 1e-5
    assert best_cut <= known_optimum

    print(f"p={p}: VALIDATION PASSED")

print("\nALL BEST-PARAMETER VALIDATIONS PASSED")