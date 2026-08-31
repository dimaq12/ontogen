# -*- coding: utf-8 -*-
"""Skills (SPEC §12.1, lesson from v0 wave 5): the algorithmic core — what is
NOT expressible by a rule (the AST Expr limit). A skill = a gene with TWO
contracts: SEMANTICS (properties — Expr over the parameters and out; machine-
checked on a fuzz by the canonical interpreter) and BUDGET (fast must be
faster than naive by a factor of min_speedup — a relative budget, portable
across machines).

Two-phase: naive (correctness, judged by properties) -> fast (equivalent to
naive on the fuzz + budget). The body is written by an SLM in the CANONICAL
LANGUAGE (Python) — judged in-process; emitting to other dialects is a
separate wave.

v0 lesson: properties MUST contain "completeness guards" — otherwise a lazy
oracle (returning []) passes. We validate this too: an empty output must
violate at least one property on a non-empty overlapping input (see
gate_teeth).
"""
from __future__ import annotations

import ast
import random
import time
from types import SimpleNamespace

from pydantic import BaseModel, ConfigDict, Field

from onto.core import expr as E

MAX_PROPERTY_NODES = 400          # properties are spec — they may exceed the body
FUZZ_CASES = 60
FUZZ_MAX_LEN = 24        # D95: widened from 8 — catch large-N / ordering bugs


class Skill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    params: dict[str, str]            # name -> "list[Order]"
    returns: str                      # "list[Trade]"
    types: dict[str, dict[str, str]]  # Order -> {id: str, price: int, ...}
    intent: str
    properties: list[str]
    budget: dict = Field(default_factory=lambda: {"n": 800, "min_speedup": 2})
    ladder: list[str] = Field(default_factory=list)


class SkillError(ValueError):
    pass


def _elem_type(t: str, types: dict) -> dict:
    if not (t.startswith("list[") and t.endswith("]")):
        raise SkillError(f"only list[T] param/return types in v1, got '{t}'")
    name = t[5:-1]
    if name not in types:
        raise SkillError(f"unknown type '{name}' (declared: {sorted(types)})")
    return types[name]


def property_env_types(sk: Skill) -> dict:
    env = {p: E.TList(dict(_elem_type(t, sk.types)))
           for p, t in sk.params.items()}
    env["out"] = E.TList(dict(_elem_type(sk.returns, sk.types)))
    return env


def validate_skill(name: str, sk: Skill) -> list[str]:
    errs = []
    try:
        env = property_env_types(sk)
    except SkillError as e:
        return [f"skill {name}: {e}"]
    for i, p in enumerate(sk.properties):
        try:
            t = E.typecheck_expr(E.parse_expr(p, limit=MAX_PROPERTY_NODES), env)
            if t != "bool":
                errs.append(f"skill {name}.properties[{i}]: must be bool, got {t}")
        except E.ExprError as e:
            errs.append(f"skill {name}.properties[{i}]: {e}")
    if not sk.properties:
        errs.append(f"skill {name}: no properties — an unjudgeable oracle "
                    f"is contraband (v0 wave-5 lesson)")
    return errs


# ---------------------------------------------------------------- fuzz

def gen_case(sk: Skill, rnd: random.Random, size: int | None = None) -> dict:
    """Random inputs by type; str fields = unique ids (per-parameter)."""
    case = {}
    for pi, (pname, t) in enumerate(sorted(sk.params.items())):
        fields = _elem_type(t, sk.types)
        n = rnd.randint(0, FUZZ_MAX_LEN) if size is None else size
        items = []
        for i in range(n):
            item = {}
            for f, ft in sorted(fields.items()):
                if ft != "str":
                    # D95: widened domain — mostly 0..10_000, ~10% a LARGE value
                    # (up to 10^12) to probe scaling / int overflow. Non-negative:
                    # the declared commerce fields (price/qty/ts) have no sign,
                    # and the types carry no bounds to fuzz against.
                    item[f] = (rnd.randint(10**6, 10**12)
                               if rnd.random() < 0.1 else rnd.randint(0, 10_000))
                elif f == "id":
                    item[f] = f"{pname[0]}{pi}_{i}"      # id is unique
                else:
                    # categorical field (sku etc.): a SMALL shared pool —
                    # otherwise cross-parameter properties (guards) are never
                    # active (MEGADIRT harness lesson)
                    item[f] = f"k{rnd.randint(0, 3)}"
            items.append(item)
        case[pname] = items
    return case


# ------------------------------------------------------------- execution

_FORBIDDEN = (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)
_SAFE_BUILTINS = {"sorted": sorted, "len": len, "min": min, "max": max,
                  "range": range, "list": list, "dict": dict, "enumerate":
                  enumerate, "sum": sum, "abs": abs, "reversed": reversed,
                  "any": any, "all": all, "set": set, "tuple": tuple}


def _type_ctor(fields: list[str]):
    """Constructor for a declared type: positionally in genome field order, or
    kwargs — it's natural for the model to write Order(...)/Trade(...) (live-SLM
    lesson)."""
    def ctor(*args, **kw):
        d = dict(zip(fields, args))
        d.update(kw)
        return SimpleNamespace(**d)
    return ctor


def load_body(code: str, fname: str, types: dict | None = None):
    """Compiles the skill body (full Python — skills are legally Turing-complete,
    unlike rules), without imports/globals; returns a function.
    types: declared genome types -> their constructors are placed in the sandbox."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, _FORBIDDEN):
            raise SkillError(f"forbidden in skill body: {type(node).__name__}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise SkillError(f"dunder access forbidden: {node.attr}")
    ns: dict = {"__builtins__": dict(_SAFE_BUILTINS)}
    for tname, tfields in (types or {}).items():
        ns[tname] = _type_ctor(list(tfields))
    exec(compile(tree, "<skill>", "exec"), ns)              # noqa: S102 — sandbox above
    if fname not in ns:
        raise SkillError(f"body must define function '{fname}'")
    return ns[fname]


def run_case(fn, sk: Skill, case: dict) -> list[dict]:
    # argument order = params declaration order in the genome (not sorted!)
    args = [[SimpleNamespace(**it) for it in case[p]]
            for p in sk.params]
    out = fn(*args)
    if not isinstance(out, list):
        raise SkillError(f"skill must return list, got {type(out).__name__}")
    ret_fields = _elem_type(sk.returns, sk.types)
    norm = []
    for o in out:
        d = o if isinstance(o, dict) else vars(o)
        missing = [f for f in ret_fields if f not in d]
        if missing:
            raise SkillError(f"output item missing fields {missing}")
        norm.append({f: d[f] for f in ret_fields})
    return norm


# ------------------------------------------------------------------ gates

def check_properties(sk: Skill, case: dict, out: list[dict]) -> list[str]:
    env = dict(case)
    env["out"] = out
    fails = []
    for p in sk.properties:
        if not E.eval_expr(E.parse_expr(p, limit=MAX_PROPERTY_NODES), env):
            fails.append(p)
    return fails


def gate_semantics(sk: Skill, fn, seed: int = 7) -> dict | None:
    """Fuzz against the properties. None = green; otherwise a COUNTEREXAMPLE
    (CEGIS fuel)."""
    rnd = random.Random(seed)
    for i in range(FUZZ_CASES):
        case = gen_case(sk, rnd)
        try:
            out = run_case(fn, sk, case)
        except Exception as e:  # noqa: BLE001 — any crash = counterexample
            return {"case": case, "error": f"{type(e).__name__}: {e}", "out": None}
        fails = check_properties(sk, case, out)
        if fails:
            return {"case": case, "out": out, "violated": fails}
    return None


def gate_teeth(sk: Skill) -> list[str]:
    """Property guards (v0 lesson): a lazy oracle `return []` must fail on at
    least one fuzz case — otherwise the properties are toothless."""
    lazy = lambda *a: []                                    # noqa: E731
    cx = gate_semantics(sk, lazy, seed=11)
    return [] if cx else ["properties are toothless: lazy oracle "
                          "(return []) passes the whole fuzz"]


def gate_equivalence(sk: Skill, naive_fn, fast_fn, seed: int = 13) -> dict | None:
    rnd = random.Random(seed)
    for _ in range(FUZZ_CASES):
        case = gen_case(sk, rnd)
        a = run_case(naive_fn, sk, case)
        b = run_case(fast_fn, sk, case)
        if a != b:
            return {"case": case, "naive": a, "fast": b}
    return None


def gate_budget(sk: Skill, naive_fn, fast_fn, seed: int = 17) -> dict:
    """COMPLEXITY budget (D38): the growth of fast's time under a k-fold growth
    of the input. O(n^2) at k=4 gives ratio ~16; O(n log n) ~5. The max_ratio
    threshold is declared with headroom. Independent of naive's speed (live-SLM
    lesson: the model writes an efficient naive, so "X times faster than naive"
    is a false contract)."""
    n = int(sk.budget.get("n", 600))
    k = int(sk.budget.get("growth", 4))
    max_ratio = float(sk.budget.get("max_ratio", 8))
    small = gen_case(sk, random.Random(seed), size=n)
    big = gen_case(sk, random.Random(seed + 1), size=n * k)

    def t(fn, case):
        best = None
        for _ in range(3):
            t0 = time.perf_counter()
            run_case(fn, sk, case)
            dt = time.perf_counter() - t0
            best = dt if best is None else min(best, dt)
        return best
    t_small, t_big = t(fast_fn, small), t(fast_fn, big)
    ratio = t_big / max(t_small, 1e-9)
    return {"n": n, "growth": k, "t_n_ms": t_small * 1e3,
            "t_kn_ms": t_big * 1e3, "ratio": ratio, "max_ratio": max_ratio,
            "ok": ratio <= max_ratio}


def gate_regressions(sk: Skill, fn, corpus_path) -> str | None:
    """U11 (D74): HARDENING — corpus of escapes (regressions/<skill>.jsonl,
    lines {"case": ..., "expect": [...]}). An escape = wrong-but-passes, caught
    in prod: the property fuzz missed it, and the incident oracle gave the
    exact expected output. A body that doesn't pass the corpus is NOT certified
    (and NOT mounted — an escape retroactively revokes the certificate)."""
    import json as _json
    import pathlib as _pl
    cp = _pl.Path(corpus_path)
    if not cp.exists():
        return None
    for i, line in enumerate(cp.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        rec = _json.loads(line)
        try:
            out = run_case(fn, sk, rec["case"])
        except Exception as e:  # noqa: BLE001
            return f"regression[{i}]: raised {type(e).__name__}: {e}"
        if out != rec["expect"]:
            return (f"regression[{i}] (escape from prod): case {rec['case']} "
                    f"-> {out}, incident oracle says {rec['expect']}")
    return None
