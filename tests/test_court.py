# -*- coding: utf-8 -*-
"""Court: proofs of post/equivalence; mutants calibrate (exam F2a)."""
from onto.core import court, mutants

ST = {"capacity": "int", "booked": "int"}
EV = {"room": "str", "nights": "int", "price": "int"}
GUARD = "s.booked < s.capacity"
BODY = "s.booked = s.booked + 1"
POST = "s.booked >= 0 and s.booked <= s.capacity"


def test_post_proved_for_reference():
    v = court.prove_rule(ST, EV, GUARD, BODY, POST, None)
    assert v["post"].status == "proved"


def test_dropped_guard_yields_counterexample():
    v = court.prove_rule(ST, EV, None, BODY, POST, None)
    assert v["post"].status == "counterexample"
    assert v["post"].model["s.booked"] >= v["post"].model["s.capacity"]


def test_equiv_and_counterexample():
    same = court.prove_equiv(ST, EV, (GUARD, BODY), (GUARD, "s.booked = 1 + s.booked"))
    assert same.status == "proved"
    diff = court.prove_equiv(ST, EV, (GUARD, BODY), (None, BODY))
    assert diff.status == "counterexample"


def test_conserves():
    st = {"a": "int", "b": "int"}
    v = court.prove_rule(st, EV, None, "s.a = s.a - 1\ns.b = s.b + 1", None, "s.a + s.b")
    assert v["conserves"].status == "proved"
    v2 = court.prove_rule(st, EV, None, "s.a = s.a - 1\ns.b = s.b + 2", None, "s.a + s.b")
    assert v2["conserves"].status == "counterexample"


def test_all_mutant_classes_distinguished():
    """EXAM F2 (a): every mutant is distinguished — equivalence yields
    a counterexample OR the contract catches it."""
    muts = mutants.generate(GUARD, BODY)
    classes = {m.name for m in muts}
    assert {"drop-guard", "flip-guard-cmp", "double-const"} <= classes
    undistinguished = []
    for m in muts:
        eq = court.prove_equiv(ST, EV, (GUARD, BODY), (m.guard, m.body))
        if eq.status == "counterexample":
            continue
        pr = court.prove_rule(ST, EV, m.guard, m.body, POST, None)
        if any(v.status == "counterexample" for v in pr.values()):
            continue
        undistinguished.append(m)
    assert undistinguished == [], f"court blind to: {undistinguished}"
