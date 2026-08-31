# -*- coding: utf-8 -*-
"""Fabric: mutgate (court+semantic-diff in the flow), propose, MCP tools."""
import pathlib
import shutil

import pytest

from onto.core import genome as G, ir, mutgate
from onto.core.propose import propose

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def ws(tmp_path):
    """A working copy of hotel (root + modules) with relative imports."""
    (tmp_path / "modules").mkdir()
    for m in ("rooms", "reservations", "payments"):
        shutil.copy(ROOT / "modules" / f"{m}.yaml", tmp_path / "modules" / f"{m}.yaml")
    root = tmp_path / "hotel.yaml"
    root.write_text((ROOT / "genomes" / "hotel.yaml").read_text()
                    .replace("../modules/", "modules/"), encoding="utf-8")
    return root


def test_court_in_flow_rejects_contract_break(ws):
    old_g = G.load(ws)
    pay = ws.parent / "modules" / "payments.yaml"
    # remove charge's guard: post (balance >= 0) becomes unprovable
    pay.write_text(pay.read_text().replace(
        '        guard: "ev.amount > 0 and s.balance >= ev.amount and s.frozen == 0"\n', ""),
        encoding="utf-8")
    new_g = G.load(ws)
    reasons = mutgate.judge_mutation(old_g, new_g, ir.load(ws))
    assert any("court:" in r and "DISPROVED" in r for r in reasons)


def test_semantic_diff_questions_then_ack(ws):
    old_g = G.load(ws)
    pay = ws.parent / "modules" / "payments.yaml"
    # same contracts, different behavior: charge stops counting charges
    pay.write_text(pay.read_text().replace(
        "          s.balance = s.balance - ev.amount\n"
        "          s.charges = s.charges + 1\n",
        "          s.balance = s.balance - ev.amount\n"), encoding="utf-8")
    new_g = G.load(ws)
    reasons = mutgate.judge_mutation(old_g, new_g, ir.load(ws))
    assert any("behavior change in wallet.charge" in r and
               "ack_behavior_change" in r for r in reasons)
    # the operator confirms it was intentional -> accepted
    raw = ir.load(ws)
    raw["ack_behavior_change"] = ["wallet.charge"]
    assert mutgate.judge_mutation(old_g, new_g, raw) == []


def test_propose_accepts_additive_and_rejects_bad(ws):
    pay_rel = "modules/payments.yaml"
    good = (ws.parent / pay_rel).read_text().replace(
        "queries:\n",
        "      tip:\n"
        "        when: ChargeRefunded\n"
        "        guard: \"ev.amount > 0\"\n"
        "        body: |\n"
        "          s.balance = s.balance + 0\n"
        "        contract: {post: \"s.balance >= 0\"}\n"
        "queries:\n")
    out = propose(ws, {pay_rel: good})
    assert out["accepted"], out["reasons"]
    assert (ws.parent / (pay_rel + ".bak")).exists()
    assert "tip" in G.load(ws).entities["wallet"].rules
    bad = good.replace('post: "s.balance >= 0"', 'post: "s.balance >= 10**9"')
    out2 = propose(ws, {pay_rel: bad})
    assert not out2["accepted"]


def test_propose_path_escape_refused(ws):
    out = propose(ws, {"../evil.yaml": "onto: 1"})
    assert not out["accepted"] and "escapes" in out["reasons"][0]


def test_mcp_server_builds_and_lists_tools():
    import asyncio
    from onto import mcp_server
    srv = mcp_server.build_server(ROOT / "genomes" / "hotel.yaml")
    tools = asyncio.run(srv.list_tools())
    names = {t.name for t in tools}
    assert {"genome_read", "validate", "court", "explain", "propose",
            "ledger_tail"} <= names
    # the validate tool really works (without transport)
    out = asyncio.run(srv.call_tool("validate", {}))
    assert out is not None
