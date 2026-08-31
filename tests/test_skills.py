# -*- coding: utf-8 -*-
"""Skills+CEGIS offline: gates with teeth, the loop with a stub provider."""
import pathlib

from onto.core import genome as G, skills as SK
from onto import ribosome as R

ROOT = pathlib.Path(__file__).resolve().parents[1]

REF = '''
def naive_match_orders(bids, asks):
    bids = sorted(bids, key=lambda b: (-b.price, b.ts, b.id))
    asks = sorted(asks, key=lambda a: (a.price, a.ts, a.id))
    rb = {b.id: b.qty for b in bids}
    ra = {a.id: a.qty for a in asks}
    out = []
    for b in bids:
        for a in asks:
            if b.price < a.price or rb[b.id] == 0 or ra[a.id] == 0:
                continue
            q = min(rb[b.id], ra[a.id])
            out.append({"bid": b.id, "ask": a.id, "price": a.price, "qty": q})
            rb[b.id] -= q
            ra[a.id] -= q
    return out
'''
LAZY = "def naive_match_orders(bids, asks):\n    return []\n"
FAST_OK = REF.replace("naive_match_orders", "fast_match_orders")  # equivalent, but not faster


def _skill():
    g = G.load(ROOT / "genomes" / "exchange.yaml")
    return SK.Skill.model_validate(g.skills["match_orders"])


def test_gates_green_on_reference_and_teeth():
    sk = _skill()
    fn = SK.load_body(REF, "naive_match_orders")
    assert SK.gate_semantics(sk, fn) is None
    assert SK.gate_teeth(sk) == []          # the lazy oracle fails


def test_lazy_oracle_caught_with_counterexample():
    sk = _skill()
    cx = SK.gate_semantics(sk, SK.load_body(LAZY, "naive_match_orders"))
    assert cx is not None and cx["violated"]   # lazy oracle caught with real property violations


def test_forbidden_code_rejected():
    import pytest
    with pytest.raises(SK.SkillError, match="forbidden"):
        SK.load_body("import os\ndef naive_x(a):\n    return []", "naive_x")


class StubProvider:
    """A scripted SLM: lazy body -> correct one. We check that the counterexample
    made it into the second attempt's prompt (the heart of CEGIS)."""

    def __init__(self):
        self.calls = []
        self.skills_ladder = ["stub-model"]
        self.usage_path = None

    def generate(self, model, prompt, seed, tag):
        self.calls.append(prompt)
        if ":naive:" in tag and len([p for p in self.calls
                                     if "def naive_match_orders" in p]) == 1:
            return "```python\n" + LAZY + "```"
        if ":naive:" in tag:
            return "```python\n" + REF + "```"
        return "```python\n" + FAST_OK + "```"


def test_cegis_counterexample_reaches_prompt(tmp_path):
    sk = _skill()
    stub = StubProvider()
    tele = R.synthesize("match_orders", sk, stub, tmp_path, log=lambda *a: None)
    assert tele["phases"]["naive"]["attempts"] == 2       # the lazy one is rejected
    # the second naive attempt must carry the counterexample from the first
    naive_prompts = [p for p in stub.calls if "def naive_match_orders" in p]
    assert "counterexamples" in naive_prompts[1] and "violated" in naive_prompts[1]
    # fast: equivalent, but not faster -> island (a valid outcome)
    assert tele["island"] and "fast" in tele["why"]


def test_cache_key_is_semantic_not_prompt():
    sk = _skill()
    k1 = R.cache_key(sk, "naive", "m")
    sk2 = sk.model_copy(deep=True)
    k2 = R.cache_key(sk2, "naive", "m")
    assert k1 == k2
    sk3 = sk.model_copy(deep=True)
    sk3.properties = sk.properties + ["all(t.qty > 0 for t in out)"]
    assert R.cache_key(sk3, "naive", "m") != k1
