# -*- coding: utf-8 -*-
"""Organism: rules/guard/contracts, WINDOWED dedup, replay, invariants."""
import json
import pathlib

import pytest

from onto.core import genome as G
from onto.core.organism import Organism

GENOME = pathlib.Path(__file__).resolve().parents[1] / "genomes" / "booking.yaml"


def _ev(i, typ="BookingRequested", room="room101", resv="r1", guest="bob",
        nights=2, price=100):
    return {"id": i, "type": typ, "room": room, "resv": resv, "guest": guest,
            "nights": nights, "price": price}


@pytest.fixture
def org(tmp_path):
    return Organism(G.load(GENOME), tmp_path)


def test_happy_and_guard(org):
    out = org.handle(_ev("e1"))
    assert out["status"] == "applied"
    assert org.state["room"]["room101"]["booked"] == 1
    assert org.state["guest"]["bob"]["credit"] == 900
    # a second request for the same room: the guard holds room, the guest is charged
    org.handle(_ev("e2", resv="r2", guest="alice", price=50))
    assert org.state["room"]["room101"]["booked"] == 1
    assert org.state["guest"]["alice"]["credit"] == 950
    assert org.counters["invariant_violations"] >= 1   # the observer noticed the split


def test_dedup_window_contract(org):
    org.handle(_ev("dup1"))
    before = org.state["room"]["room101"]["booked"]
    assert org.handle(_ev("dup1"))["status"] == "dup"          # within the window — a duplicate
    assert org.state["room"]["room101"]["booked"] == before
    # push the id out of the window (retry_window=8) with other events
    for i in range(8):
        org.handle(_ev(f"fill{i}", room="room103", resv="r3", guest="carol", price=0))
    out = org.handle(_ev("dup1", typ="BookingCancelled"))
    assert out["status"] == "applied"    # id older than the window — no longer a duplicate (contract)


def test_replay_survives_kill(tmp_path):
    org1 = Organism(G.load(GENOME), tmp_path)
    org1.handle(_ev("e1"))
    org1.handle(_ev("e2", typ="BookingCancelled"))
    snap = org1.snapshot()
    del org1                                     # "kill -9": no goodbyes
    org2 = Organism(G.load(GENOME), tmp_path)    # replay from events.jsonl
    assert org2.snapshot() == snap


def test_post_violation_rejected_and_ledgered(tmp_path):
    """D25: a body that contradicts the contract — the transition is rejected + ledger."""
    raw = G.ir.load(GENOME)
    raw["entities"]["room"]["rules"]["reserve"]["guard"] = None       # remove the guard
    g = G.Genome.model_validate(raw)
    org = Organism(g, tmp_path)
    org.handle(_ev("e1"))
    out = org.handle(_ev("e2", resv="r2"))       # second time: post catches it
    assert out["outcomes"]["room.reserve"] == "rejected(post)"
    assert org.state["room"]["room101"]["booked"] == 1
    ledger = (tmp_path / "ledger.jsonl").read_text()
    assert "contract_post" in ledger


def test_unknown_instance_is_noop_not_panic(org):
    out = org.handle(_ev("e9", room="room999"))
    assert out["outcomes"]["room.reserve"].startswith("unknown-instance")
