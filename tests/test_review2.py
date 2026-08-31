# -*- coding: utf-8 -*-
"""GUARDS OF THE SECOND EXTERNAL REVIEW (D80): six confirmed holes + two
class-level findings. Each test is a reproduction that BEFORE the fix
passed with a false green."""
import json
import pathlib
import tempfile

import yaml

from onto.core import court as C, genome as G, mutgate
from onto.core.organism import Ledger, Organism

ST = {"x": "int"}
EV = {"c": "str", "v": "int"}


def test_division_negative_divisor_matches_canon():
    """Review §1: the court proved -7//-2==4 (euclidean) while the canon is 3 (floor)."""
    r = C.prove_equiv(ST, EV, (None, "s.x = (0 - 7) // (0 - 2)\n"),
                      (None, "s.x = 3\n"))
    assert r.status == "proved"          # the canonical answer is now provable
    r2 = C.prove_equiv(ST, EV, (None, "s.x = (0 - 7) // (0 - 2)\n"),
                       (None, "s.x = 4\n"))
    assert r2.status == "counterexample"  # the euclidean answer is rejected
    r3 = C.prove_equiv(ST, EV, (None, "s.x = (0 - 7) % (0 - 2)\n"),
                       (None, "s.x = 0 - 1\n"))
    assert r3.status == "proved"          # Python: sign of the divisor


def test_division_by_maybe_zero_is_unsupported():
    """Class-level finding: the canon raises on //0 — the court must not stay silent."""
    out = C.prove_rule(ST, EV, None, "s.x = 10 // s.x\n", "s.x >= 0", None)
    assert out["post"].status == "unsupported"
    # under a guard that excludes zero — provable
    out2 = C.prove_rule(ST, EV, "s.x > 0", "s.x = 10 // s.x\n",
                        "s.x >= 0", None)
    assert out2["post"].status == "proved"


def test_entity_induction_catches_deadborn():
    """Review §2a: init violates post -> ALL PROVED and dead. Now the entity
    court says counterexample."""
    rules = [("inc", None, "s.x = s.x + 1\n", "s.x >= 5", {"c": "str"})]
    v = C.prove_entity({"x": "int"}, {"x": 0}, rules, {})
    assert v.status == "counterexample"
    # a healthy variant — a strong guarantee
    rules2 = [("inc", None, "s.x = s.x + 1\n", "s.x >= 0", {"c": "str"})]
    v2 = C.prove_entity({"x": "int"}, {"x": 0}, rules2, {})
    assert v2.status == "proved"


def test_entity_induction_catches_neighbour_break():
    """Review §2b: a neighbouring Setv(-5) breaks inc's precondition."""
    rules = [("inc", None, "s.x = s.x + 1\n", "s.x >= 0", {"c": "str"}),
             ("setv", None, "s.x = ev.v\n", None, {"c": "str", "v": "int"})]
    v = C.prove_entity({"x": "int"}, {"x": 0}, rules, {})
    assert v.status == "counterexample"
    # Houdini: the reset-equivalent (== 0) legally drops out of I
    rules2 = [("dep", "ev.v > 0", "s.x = s.x + ev.v\n", "s.x >= 0",
               {"c": "str", "v": "int"}),
              ("reset", None, "s.x = 0\n", "s.x == 0", {"c": "str"})]
    v2 = C.prove_entity({"x": "int"}, {"x": 0}, rules2, {})
    assert v2.status == "proved"


def _mini_genome(guard_old):
    return {"onto": 1, "name": "m", "retry_window": 4,
            "events": {"E": {"c": "str", "v": "int"}},
            "entities": {"c": {"key": "c", "instances": ["a"],
                               "state": {"x": "int", "y": "int"},
                               "init": {},
                               "rules": {"r": {"when": "E",
                                               "guard": guard_old,
                                               "body": "s.x = s.x + 1\n",
                                               "contract": {}}}}},
            "queries": {}}


def test_mutgate_unknown_requires_ack(tmp_path):
    """Review §3: solver unknown -> mutgate silently accepted. Now — ack."""
    hard_a = ("s.x * s.y * s.y + s.y * s.x * s.x == "
              "1000000 + ev.v * ev.v * ev.v * ev.v * ev.v")
    hard_b = ("s.x * s.y * s.y + s.y * s.x * s.x == "
              "999999 + ev.v * ev.v * ev.v * ev.v * ev.v")
    pa, pb = tmp_path / "a.yaml", tmp_path / "b.yaml"
    pa.write_text(yaml.safe_dump(_mini_genome(hard_a), sort_keys=False))
    pb.write_text(yaml.safe_dump(_mini_genome(hard_b), sort_keys=False))
    ga, gb = G.load(pa), G.load(pb)
    assert C.prove_equiv({"x": "int", "y": "int"},
                         {"c": "str", "v": "int"},
                         (hard_a, "s.x = s.x + 1\n"),
                         (hard_b, "s.x = s.x + 1\n")).status == "unsupported"
    reasons = mutgate.judge_mutation(ga, gb, yaml.safe_load(pb.read_text()))
    assert any("NOT certified" in r for r in reasons)


def test_snapshot_corruption_dynamic(tmp_path):
    """Review §4: a corrupt snapshot + dynamic = the letters of the word 'dynamic' and a ghost."""
    raw = {"onto": 1, "name": "dyn", "retry_window": 4,
           "events": {"Born": {"u": "str"}},
           "entities": {"u": {"key": "u", "instances": "dynamic",
                              "state": {"n": "int"}, "init": {"n": 0},
                              "rules": {"b": {"when": "Born",
                                              "body": "s.n = s.n + 1\n",
                                              "contract": {"post": "s.n >= 0"}}}}},
           "queries": {"pop": "sum(1 for x in u)"}}
    gp = tmp_path / "g.yaml"
    gp.write_text(yaml.safe_dump(raw, sort_keys=False))
    g = G.load(gp)
    data = tempfile.mkdtemp()
    org = Organism(g, data)
    for i in range(3):
        org.handle({"id": f"e{i}", "type": "Born", "u": f"user{i}"})
    org.checkpoint()
    ck = pathlib.Path(data) / "checkpoint.json"
    j = json.loads(ck.read_text())
    j["state"]["u"]["ghost"] = {"n": 99}
    ck.write_text(json.dumps(j))
    org2 = Organism(g, data)                 # corrupt checkpoint -> full replay
    assert sorted(org2.state["u"].keys()) == ["user0", "user1", "user2"]
    assert org2.query("pop", {}) == 3


def test_ledger_verify_and_kind_tamper(tmp_path):
    """Review §5 + a class-level finding: the chain verifies; tampering with KIND breaks it."""
    led = Ledger(tmp_path / "l.jsonl")
    led.record("a", {"x": 1})
    led.record("b", {"y": 2})
    assert led.verify()["ok"]
    lines = (tmp_path / "l.jsonl").read_text().splitlines()
    e = json.loads(lines[0])
    e["kind"] = "FORGED"
    (tmp_path / "l.jsonl").write_text(json.dumps(e) + "\n" + lines[1] + "\n")
    v = Ledger(tmp_path / "l.jsonl").verify()
    assert not v["ok"] and v["broken_at"] == 1


def test_attest_honest_about_invariants():
    """Review §6 + D83 #5: invariants split proved|monitored, never lumped as
    proved. money_sane (refund unbounded) stays monitored; a fixed-instance
    conserves invariant proves inductively."""
    from onto import attest as AT
    a = AT.build_attest(pathlib.Path(__file__).parents[1] / "genomes/market.yaml")
    # not falsely proved
    assert a["invariants"]["money_sane"].startswith("monitored")
    assert a["invariants"]["delivery_consistency"].startswith("monitored")
    # the proved section counts obligations, not raw invariant strings
    assert "obligations_proved" in a["proved"]
    assert "invariants_monitored" in a["monitored"]
