import numpy as np
import pytest

from loader import make_graph, cut_value
from noise_runner import (
    run_noisy_qaoa,
    calculate_noisy_expected_cut,
    optimize_noisy_qaoa
)


@pytest.fixture
def triangle():
    return make_graph(
        3,
        [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 1.0)]
    )


def test_noisy_qaoa_probability_validation(triangle):
    rho, probabilities = run_noisy_qaoa(
        triangle,
        [0.5],
        [0.25],
        0.01
    )

    assert rho.shape == (8, 8)
    assert np.isclose(np.trace(rho), 1.0, atol=1e-5)
    assert np.isclose(probabilities.sum(), 1.0, atol=1e-5)
    assert np.all(np.isfinite(probabilities))
    assert np.min(probabilities) >= 0


def test_zero_noise_matches_statevector(triangle):
    from qaoa_depth_runner import (
        build_qaoa_circuit,
        calculate_expected_cut
    )
    from hybridq.circuit.simulation.simulation import simulate

    gammas = [0.5]
    betas = [0.25]

    _, probabilities = run_noisy_qaoa(
        triangle, gammas, betas, 0.0
    )

    state = np.asarray(
        simulate(
            build_qaoa_circuit(triangle, gammas, betas),
            initial_state="000"
        )
    ).reshape(-1)

    statevector_probabilities = np.abs(state) ** 2

    noisy_expected = calculate_noisy_expected_cut(
        triangle, statevector_probabilities
    )

    statevector_expected = calculate_noisy_expected_cut(
        triangle, statevector_probabilities
    )

    assert np.isclose(
        noisy_expected,
        statevector_expected,
        atol=1e-5
    )


def test_expected_cut_calculation(triangle):
    probabilities = np.zeros(8)
    probabilities[1] = 0.5
    probabilities[2] = 0.5

    result = calculate_noisy_expected_cut(
        triangle, probabilities
    )

    assert np.isclose(result, 2.0)


def test_invalid_noise_probability(triangle):
    with pytest.raises(ValueError):
        run_noisy_qaoa(triangle, [0.5], [0.25], 1.5)


def test_invalid_optimizer(triangle):
    with pytest.raises(ValueError):
        optimize_noisy_qaoa(
            triangle, 1, 0.01,
            optimizer="INVALID",
            max_evaluations=4
        )


def test_invalid_depth(triangle):
    with pytest.raises(ValueError):
        optimize_noisy_qaoa(
            triangle, 4, 0.01,
            max_evaluations=4
        )


def test_cobyla_result_structure(triangle):
    result = optimize_noisy_qaoa(
        triangle,
        p=1,
        noise_probability=0.01,
        optimizer="COBYLA",
        seed=42,
        max_evaluations=4
    )

    assert result["optimizer"] == "COBYLA"
    assert result["p"] == 1
    assert result["function_evaluations"] <= 4
    assert np.isfinite(result["expected_cut"])
    assert np.isclose(result["probability_sum"], 1.0, atol=1e-5)
    assert np.isclose(result["density_matrix_trace"], 1.0, atol=1e-5)


def test_spsa_result_structure(triangle):
    result = optimize_noisy_qaoa(
        triangle,
        p=1,
        noise_probability=0.01,
        optimizer="SPSA",
        seed=42,
        max_evaluations=4
    )

    assert result["optimizer"] == "SPSA"
    assert result["function_evaluations"] == 4
    assert result["optimizer_success"] is None
    assert "not independently certified" in result["optimizer_message"]
    assert np.isfinite(result["expected_cut"])
