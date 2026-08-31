# -*- coding: utf-8 -*-
"""Placer loop: warming by heat, eviction, refusal, root split."""
import pathlib

from onto.core import genome as G, placer
from onto.theory.provenance import declared, measured

ROOT = pathlib.Path(__file__).resolve().parents[1]
T_COLD = measured(76000, "bench:interp")
T_WARM = measured(8000, "bench:go")


def test_hot_entity_proposed_cold_stays():
    plan = placer.tick({"wallet": measured(150, "heat"),
                        "room": measured(0.2, "heat")},
                       t_cold_ns=T_COLD, t_warm_ns=T_WARM)
    assert plan.warm == ["wallet"]
    assert plan.proposals[0]["kind"] == "molt_proposal"
    assert "proposal-only" in plan.proposals[0]["rights"]
    assert any("STAY" in m for m in plan.metrics)          # room stayed


def test_idle_warm_gets_evicted():
    plan = placer.tick({"wallet": measured(0.0, "heat")},
                       t_cold_ns=T_COLD, t_warm_ns=T_WARM,
                       warm_set={"wallet"})
    assert plan.evict == ["wallet"]
    assert plan.proposals[0]["kind"] == "evict_proposal"


def test_impossible_demand_refused_with_arithmetic():
    plan = placer.tick({}, t_cold_ns=T_COLD, t_warm_ns=T_WARM,
                       demand={"q/total_balance": declared(0.001, "op")},
                       floor_warm_ms=measured(0.06, "bench:go-http"))
    assert plan.refusals and "pay with" in plan.refusals[0]


def test_metrics_table_nonempty():
    plan = placer.tick({"wallet": measured(150, "heat")},
                       t_cold_ns=T_COLD, t_warm_ns=T_WARM)
    assert plan.metrics and all("->" in m for m in plan.metrics)


def test_split_hot_root(tmp_path):
    out = placer.split_hot_root(ROOT / "genomes" / "hotel.yaml", ["wallet"],
                                tmp_path / "hotel_wallet_svc.yaml")
    g = G.load(out)
    assert set(g.entities) == {"wallet"}                 # the closure is minimal
    assert g.name == "hotel_wallet_svc"
    assert g.entities["wallet"].instances == ["bob", "alice"]
