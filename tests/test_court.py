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


def test_invariant_symmetry_is_grammar_guaranteed():
    """D95 (closes a D93 park): the single-representative invariant proof is
    sound because invariants are SYMMETRIC by construction — the Expr grammar
    forbids instance indexing (Subscript), so an invariant can only touch the
    population via aggregates. Belt-and-braces: _indexes_instances flags any
    subscript AST, and prove_invariants routes it to monitored, never a false
    'proved'."""
    import ast
    from onto.core import genome as G, court as C
    import tempfile, pathlib, yaml

    base = {"onto": 1, "name": "inv", "retry_window": 8,
            "events": {"Book": {"room": "str"}},
            "entities": {"room": {"key": "room", "instances": ["a", "b"],
                "state": {"booked": "int"}, "init": {"booked": 0},
                "rules": {"r": {"when": "Book", "body": "s.booked = s.booked + 1\n",
                          "contract": {"post": "s.booked >= 0"}}}}},
            "queries": {}}

    # (1) a symmetric (aggregate) invariant is PROVED inductively
    sym = {**base, "invariants": {"cap": "sum(r.booked for r in room) >= 0"}}
    p = pathlib.Path(tempfile.mkdtemp()) / "g.yaml"
    p.write_text(yaml.safe_dump(sym))
    verdicts = C.prove_invariants(G.load(p))
    assert verdicts["cap"].status == "proved"
    assert "symmetric by construction" in verdicts["cap"].note

    # (2) an instance-indexing invariant cannot even LOAD (grammar rejects it)
    asym = {**base, "invariants": {"eq": "room[0].booked == room[1].booked"}}
    p2 = pathlib.Path(tempfile.mkdtemp()) / "g.yaml"
    p2.write_text(yaml.safe_dump(asym))
    try:
        G.load(p2)
        assert False, "instance-indexing invariant should be rejected at load"
    except G.GenomeError as e:
        assert "Subscript" in str(e)

    # (3) belt-and-braces: _indexes_instances flags a subscript AST directly
    assert C._indexes_instances(ast.parse("room[0].booked > 0", mode="eval").body,
                                {"room"}) is True
    assert C._indexes_instances(ast.parse("sum(r.booked for r in room) > 0",
                                mode="eval").body, {"room"}) is False
