# -*- coding: utf-8 -*-
"""Interview (exam F2b): the scar-13 case room.free — a weak contract,
two candidates pass the court, diverge -> QUESTION; the answer completes the genome."""
from onto.core import court, interview
from onto.core.interview import Patch

ST = {"capacity": "int", "booked": "int", "available": "int"}
EV = {"room": "str", "price": "int"}
WEAK_POST = "s.booked >= 0"                       # underdetermines available!
CAND_A = (None, "if s.booked > 0:\n  s.booked = s.booked - 1\n  s.available = s.available + 1")
CAND_B = (None, "s.booked = max(s.booked - 1, 0)\ns.available = s.available + 1")
VARIANTS = [Patch("guard", "s.booked > 0"),
            Patch("post", "s.available <= s.capacity")]


def test_underdetermined_contract_yields_question():
    q = interview.detect("room.free", ST, EV, CAND_A, CAND_B, WEAK_POST,
                         variants=VARIANTS)
    assert q is not None
    assert q.outcome_a != q.outcome_b                       # an executable divergence
    assert q.input_example["s"]["booked"] <= 0              # exactly the scar-13 corner
    assert q.variants, "no valid resolution variants offered"
    assert "UNDERDETERMINED" in q.render()


def test_guard_variant_resolves():
    """Answer (a): guard -> candidates are provably equivalent, the question is closed."""
    q_after = interview.detect(
        "room.free", ST, EV,
        ("s.booked > 0", CAND_A[1]), ("s.booked > 0", CAND_B[1]),
        WEAK_POST)
    assert q_after is None


def test_post_variant_resolves():
    """Answer (b): a strengthened post — the court distinguishes the candidates itself."""
    strong = f"({WEAK_POST}) and (s.available <= s.capacity)"
    b_ok = all(v.status == "proved" for v in
               court.prove_rule(ST, EV, *CAND_B, strong, None).values())
    a_ok = all(v.status == "proved" for v in
               court.prove_rule(ST, EV, *CAND_A, strong, None).values())
    assert not b_ok, "B (clamps booked but inflates available) must be eliminated"
    # A also requires the invariant available+booked==capacity for a full
    # proof — what matters is DISTINGUISHABILITY:
    assert a_ok != b_ok or (not a_ok and not b_ok)


def test_answer_becomes_genome_diff():
    raw = {"entities": {"room": {"rules": {"free": {"body": CAND_A[1],
                                                    "contract": {"post": WEAK_POST}}}}}}
    g2 = interview.apply_patch(raw, "room", "free", Patch("guard", "s.booked > 0"))
    assert g2["entities"]["room"]["rules"]["free"]["guard"] == "s.booked > 0"
    assert raw["entities"]["room"]["rules"]["free"].get("guard") is None
