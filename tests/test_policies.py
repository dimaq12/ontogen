# -*- coding: utf-8 -*-
"""POLICIES wave (D54): cascade, depth cap, replay determinism, gates."""
import pathlib

import pytest

from onto.core import genome as G, ir, mutgate
from onto.core.organism import Organism

ROOT = pathlib.Path(__file__).resolve().parents[1]

MINI = {
    "onto": 1, "name": "mini",
    "events": {"Ping": {"a": "str"}, "Pong": {"a": "str"}},
    "entities": {
        "a": {"key": "a", "instances": "dynamic",
              "state": {"pings": "int", "pongs": "int"},
              "rules": {
                  "ping": {"when": "Ping",
                           "body": "s.pings = s.pings + 1",
                           "emit": [{"event": "Pong",
                                     "fields": {"a": "ev.a"}}]},
                  "pong": {"when": "Pong",
                           "body": "s.pongs = s.pongs + 1"}}}},
}


def _mini(tmp_path, raw=None):
    g = G.Genome.model_validate(raw or MINI)
    G.fill_defaults(g)
    assert G.validate(g) == []
    return Organism(g, tmp_path)


def test_cascade_fires_and_not_logged(tmp_path):
    org = _mini(tmp_path)
    org.handle({"id": "e1", "type": "Ping", "a": "x"})
    st = org.state["a"]["x"]
    assert st == {"pings": 1, "pongs": 1}            # the cascade fired
    assert org.store.count() == 1                    # the derived is NOT in the log
    org2 = Organism(org.g, tmp_path)                 # replay recomputes
    assert org2.snapshot() == org.snapshot()


def test_cascade_depth_capped(tmp_path):
    raw = {**MINI, "entities": {
        "a": {"key": "a", "instances": "dynamic",
              "state": {"pings": "int"},
              "rules": {"loop": {"when": "Ping",
                                 "body": "s.pings = s.pings + 1",
                                 "emit": [{"event": "Ping",
                                           "fields": {"a": "ev.a"}}]}}}}}
    org = _mini(tmp_path, raw)
    out = org.handle({"id": "e1", "type": "Ping", "a": "x"})
    assert any(k.startswith("cascade:") for k in out["outcomes"])
    assert "cascade_overflow" in (tmp_path / "ledger.jsonl").read_text()
    assert org.state["a"]["x"]["pings"] == org.MAX_CASCADE + 1


def test_emit_validation():
    bad = {**MINI, "entities": {
        "a": {"key": "a", "instances": "dynamic",
              "state": {"pings": "int"},
              "rules": {"ping": {"when": "Ping",
                                 "body": "s.pings = s.pings + 1",
                                 "emit": [{"event": "Nope",
                                           "fields": {}}]}}}}}
    g = G.Genome.model_validate(bad)
    G.fill_defaults(g)
    errs = G.validate(g)
    assert any("unknown event 'Nope'" in e for e in errs)
    bad2 = {**MINI, "entities": {
        "a": {"key": "a", "instances": "dynamic",
              "state": {"pings": "int"},
              "rules": {"ping": {"when": "Ping",
                                 "body": "s.pings = s.pings + 1",
                                 "emit": [{"event": "Pong",
                                           "fields": {"a": "s.pings"}}]}}}}}
    g2 = G.Genome.model_validate(bad2)
    G.fill_defaults(g2)
    assert any("must be str" in e for e in G.validate(g2))


def test_emit_change_requires_ack():
    old_g = G.Genome.model_validate(MINI)
    new_raw = {**MINI, "entities": {
        "a": {"key": "a", "instances": "dynamic",
              "state": {"pings": "int", "pongs": "int"},
              "rules": {
                  "ping": {"when": "Ping",
                           "body": "s.pings = s.pings + 1"},   # emit removed!
                  "pong": {"when": "Pong",
                           "body": "s.pongs = s.pongs + 1"}}}}}
    new_g = G.Genome.model_validate(new_raw)
    for g in (old_g, new_g):
        G.fill_defaults(g)
    reasons = mutgate.judge_mutation(old_g, new_g, {})
    assert any("policy change in a.ping" in r for r in reasons)
    assert mutgate.judge_mutation(old_g, new_g,
                                  {"ack_behavior_change": ["a.ping"]}) == []
