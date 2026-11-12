"""Judge for the RSI: one known series and invariants over seeded random inputs.

Written before looking at the change. It only depends on the interface in contrato.md.
"""
import math
import random

import pytest


def rsi(series):
    try:
        from backend.services import indicators
        return indicators.calculate_rsi(series)
    except Exception as exc:  # the judge reports what happened instead of hiding it
        pytest.fail(f"calculate_rsi lanzó {type(exc).__name__} con la serie {series[:3]}... (n={len(series)}): {exc}")


def test_serie_conocida():
    # 14 cambios: 10 subidas de +1 y 4 bajadas de -1 -> RS = 2.5 -> RSI = 100 - 100/3.5
    deltas = [1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, -1, 1]
    closes = [100.0]
    for d in deltas:
        closes.append(closes[-1] + d)
    assert rsi(closes) == pytest.approx(71.4286, abs=0.01)


@pytest.mark.parametrize("seed", range(25))
def test_invariante_rango_y_numero_valido(seed):
    rng = random.Random(seed)
    n = rng.randint(15, 80)
    closes = [100.0]
    for _ in range(n - 1):
        closes.append(max(1.0, closes[-1] + rng.uniform(-3, 3)))
    value = rsi(closes)
    assert not math.isnan(value), f"RSI NaN con semilla {seed}"
    assert 0 <= value <= 100, f"RSI fuera de rango ({value}) con semilla {seed}"


def test_invariante_serie_constante_tiene_valor_definido():
    value = rsi([100.0] * 20)
    assert math.isfinite(value) and 0 <= value <= 100


def test_invariante_serie_creciente_cerca_de_100():
    value = rsi([100.0 + i for i in range(30)])
    assert value >= 95, f"una serie que solo sube dio {value}"


def test_invariante_serie_decreciente_cerca_de_0():
    value = rsi([200.0 - i for i in range(30)])
    assert value <= 5, f"una serie que solo baja dio {value}"
