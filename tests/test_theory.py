# -*- coding: utf-8 -*-
"""theory/: provenance contagion, preconditions, Derived recomputation (CI)."""
import pytest

from onto.theory import formulas as F
from onto.theory.provenance import declared, measured


def test_contagion_worst_class_wins():
    d = F.warm_gain(measured(100, "heat"), measured(70000, "bench"),
                    measured(8000, "bench"), declared(3600, "op"),
                    declared(5, "op"))
    assert d.value.cls == "declared"          # declared inputs contaminated the output
    d2 = F.warm_gain(measured(100, "h"), measured(70000, "b"),
                     measured(8000, "b"), measured(3600, "m"), measured(5, "m"))
    assert d2.value.cls == "measured"


def test_precond_refuses_not_silently():
    with pytest.raises(F.PrecondError, match="t_cold >= t_warm"):
        F.warm_gain(measured(1, "h"), measured(10, "b"), measured(99, "b"),
                    declared(1, "o"), declared(1, "o"))
    with pytest.raises(F.PrecondError, match="floor must be measured"):
        F.latency_floor(declared(1, "o"), measured(0, "b"))


def test_derived_recompute_golden():
    """"From the theorem" — verifiable: CI recomputes Derived from its inputs."""
    d = F.warm_gain(measured(100, "h"), measured(70000, "b"),
                    measured(8000, "b"), declared(3600, "o"), declared(5, "o"))
    ins = dict(d.value.inputs)
    recomputed = ins["rate"].value * ins["horizon_s"].value * \
        (ins["t_cold_ns"].value - ins["t_warm_ns"].value) * 1e-9
    assert abs(recomputed - d.value.value) < 1e-9
    assert d.value.formula == "warm_gain"


def test_decisions_change_with_inputs():
    """The formula must CHANGE its decision with the input — otherwise it's decoration (S3)."""
    hot = F.warm_gain(measured(200, "h"), measured(70000, "b"),
                      measured(8000, "b"), declared(3600, "o"), declared(5, "o"))
    cold = F.warm_gain(measured(0.01, "h"), measured(70000, "b"),
                       measured(8000, "b"), declared(3600, "o"), declared(5, "o"))
    assert hot.verdict.startswith("WARM") and cold.verdict.startswith("STAY")
    ok = F.latency_floor(declared(50, "o"), measured(0.05, "bench"))
    bad = F.latency_floor(declared(0.001, "o"), measured(0.05, "bench"))
    assert ok.verdict.startswith("OK") and bad.verdict.startswith("REFUSE")
    assert "pay with" in bad.verdict
