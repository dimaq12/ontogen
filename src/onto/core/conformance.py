# -*- coding: utf-8 -*-
"""Conformance-suite Expr (D17, P12): a corpus of (expr, env, expectation)
from the CANONICAL interpreter. Embedded dialect interpreters (F2+) must
reproduce the corpus byte-for-byte — otherwise the dialect is not certified.

The corpus is deterministic (random with a fixed seed) and is committed as an artifact.
"""
from __future__ import annotations

import json
import pathlib
import random

from onto.core import expr as E

_ENV_TYPES = {
    "s": {"a": "int", "b": "int", "flag": "int"},
    "ev": {"q": "int", "who": "str"},
    "items": E.TList({"x": "int", "on": "int"}),
}

_TEMPLATES = [
    "s.a + s.b * {n}", "s.a - s.b", "s.a // {m}", "s.a % {m}",
    "-s.a + {n}", "min(s.a, s.b, {n})", "max(s.a, ev.q)",
    "s.a >= s.b", "s.a == {n}", "ev.who == 'bob'", "ev.who != 'alice'",
    "s.a > {n} and s.b < {n}", "not (s.a == s.b) or s.flag == 1",
    "sum(i.x for i in items)", "sum(i.x for i in items if i.on == 1)",
    "all(i.x >= 0 for i in items)", "any(i.x > {n} for i in items)",
    "len(items)", "{n} if s.a > s.b else -{n}",
    "sum(i.x for i in items) == s.a + s.b",
]


def gen_corpus(n_per: int = 12, seed: int = 42) -> list[dict]:
    rnd = random.Random(seed)
    out = []
    for tpl in _TEMPLATES:
        for _ in range(n_per):
            src = tpl.format(n=rnd.randint(-5, 9), m=rnd.randint(1, 7))
            env = {
                "s": {"a": rnd.randint(-9, 9), "b": rnd.randint(-9, 9),
                      "flag": rnd.randint(0, 1)},
                "ev": {"q": rnd.randint(-9, 9),
                       "who": rnd.choice(["bob", "alice", "carol"])},
                "items": [{"x": rnd.randint(-9, 9), "on": rnd.randint(0, 1)}
                          for _ in range(rnd.randint(0, 4))],
            }
            tree = E.parse_expr(src)
            E.typecheck_expr(tree, _ENV_TYPES)
            expected = E.eval_expr(tree, env)
            out.append({"expr": src, "env": env, "expected": expected})
    return out


def write_corpus(path: str | pathlib.Path, corpus: list[dict]) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for case in corpus:
            f.write(json.dumps(case, ensure_ascii=False, sort_keys=True) + "\n")


def check_corpus(path: str | pathlib.Path) -> list[str]:
    """Check the CANONICAL interpreter against the corpus (for F2+ dialects —
    their runners). Returns a list of discrepancies."""
    fails = []
    for i, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines()):
        case = json.loads(line)
        got = E.eval_expr(E.parse_expr(case["expr"]), case["env"])
        if got != case["expected"]:
            fails.append(f"case {i}: {case['expr']} -> {got}, expected {case['expected']}")
    return fails
