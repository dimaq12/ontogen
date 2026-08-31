# -*- coding: utf-8 -*-
"""Court (SPEC §9): proofs instead of samples for the decidable fragment.

Rule transition (organism semantics, D25):
    T(s, ev) = body(s, ev) if guard(s, ev) else s
The court can:
  - prove_rule: [post(s) ∧ guard] ⇒ post(T) and guard ⇒ conserves(s)==conserves(T)
    (inductive preservation of the rule's own contract);
  - prove_equiv: T_A ≡ T_B for all s, ev — or a COUNTEREXAMPLE (concrete
    inputs + discrepancy). A counterexample is fuel for CEGIS and interview (§11).
Mutants (core/mutants.py) calibrate the court: an undetected mutant = a hole in the contract.

Encoding: int -> z3.Int (mathematical integers; the discrepancy with the dialect's
int64 is conformance/UNEXPRESSIBLE's concern), str -> z3.String (only ==/!=).
// and % — SMT semantics (matches Python when the divisor > 0; otherwise fuzzed).
Verdicts are in English (D24).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

import z3

from onto.core import expr as E


def _mk_vars(prefix: str, types: dict) -> dict:
    out = {}
    for f, t in types.items():
        out[f] = z3.String(f"{prefix}.{f}") if t == "str" else z3.Int(f"{prefix}.{f}")
    return out


# D80: the court must compute exactly like the canon. SMT div is Euclidean
# (for b<0 — NOT floor), Python is always floor; division by 0 is total in SMT,
# but the canon raises. We encode floor precisely and collect divisors as obligations.
_DIVS: list = []          # divisor collector (the court is a single-threaded CLI context)


def _py_div(a, b):
    """Exact Python floor-div: floor(a/b) = If(b>0, div(a,b), div(-a,-b))
    (SMT div with a positive divisor = floor; a/b == (-a)/(-b))."""
    return z3.If(b > 0, a / b, (-a) / (-b))


def expr_to_z3(tree, env: dict):
    """Expr AST -> z3. env: name -> z3 variable | dict of fields | list[dict]
    (bounded aggregates)."""
    def e(n, env):
        match n:
            case ast.Expression(body=b):
                return e(b, env)
            case ast.BoolOp(op=op, values=vs):
                zs = [e(v, env) for v in vs]
                return z3.And(*zs) if isinstance(op, ast.And) else z3.Or(*zs)
            case ast.UnaryOp(op=ast.Not(), operand=o):
                return z3.Not(e(o, env))
            case ast.UnaryOp(op=ast.USub(), operand=o):
                return -e(o, env)
            case ast.BinOp(left=l, op=op, right=r):
                a, b = e(l, env), e(r, env)
                match op:
                    case ast.Add(): return a + b
                    case ast.Sub(): return a - b
                    case ast.Mult(): return a * b
                    case ast.FloorDiv():
                        _DIVS.append(b)
                        return _py_div(a, b)
                    case ast.Mod():
                        _DIVS.append(b)
                        return a - b * _py_div(a, b)
            case ast.Compare(left=l, ops=[op], comparators=[r]):
                a, b = e(l, env), e(r, env)
                match op:
                    case ast.Eq(): return a == b
                    case ast.NotEq(): return a != b
                    case ast.Lt(): return a < b
                    case ast.LtE(): return a <= b
                    case ast.Gt(): return a > b
                    case ast.GtE(): return a >= b
            case ast.Name(id=x):
                return env[x]
            case ast.Attribute(value=v, attr=a):
                return e(v, env)[a]
            case ast.Constant(value=bool() as v):
                return z3.BoolVal(v)
            case ast.Constant(value=int() as v):
                return z3.IntVal(v)
            case ast.Constant(value=str() as v):
                return z3.StringVal(v)
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                items = e(gen.iter, env)
                vals = []
                for item in items:
                    ienv = dict(env); ienv[gen.target.id] = item
                    v = e(g.elt, ienv)
                    if gen.ifs:
                        c = e(gen.ifs[0], ienv)
                        v = z3.If(c, v, z3.IntVal(0)) if f == "sum" else \
                            z3.Implies(c, v) if f == "all" else z3.And(c, v)
                    vals.append(v)
                if f == "sum":
                    return z3.Sum(vals) if vals else z3.IntVal(0)
                if f == "all":
                    return z3.And(*vals) if vals else z3.BoolVal(True)
                if f == "any":
                    return z3.Or(*vals) if vals else z3.BoolVal(False)
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                return z3.IntVal(len(e(a, env)))
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                import functools
                zs = [e(a, env) for a in args]
                pick = (lambda x, y: z3.If(x < y, x, y)) if f == "min" \
                    else (lambda x, y: z3.If(x > y, x, y))
                return functools.reduce(pick, zs)
            case ast.IfExp(test=c, body=b, orelse=el):
                return z3.If(e(c, env), e(b, env), e(el, env))
        raise ValueError(f"smt: unexpected node {type(n).__name__}")
    return e(tree, env)


def sym_exec(body: ast.Module, s: dict, ev: dict) -> dict:
    """Symbolic execution of the body: dict field -> z3 expression of the new state."""
    def run(stmts, cur: dict) -> dict:
        cur = dict(cur)
        for st in stmts:
            match st:
                case ast.Assign(targets=[ast.Attribute(attr=f)], value=v):
                    cur[f] = expr_to_z3(ast.Expression(body=v), {"s": cur, "ev": ev})
                case ast.If(test=c, body=b, orelse=o):
                    cond = expr_to_z3(ast.Expression(body=c), {"s": cur, "ev": ev})
                    then_s, else_s = run(b, cur), run(o, cur)
                    cur = {f: z3.If(cond, then_s[f], else_s[f]) if
                           not (then_s[f] is else_s[f]) else then_s[f]
                           for f in cur}
                case ast.Pass():
                    pass
        return cur
    return run(body.body, s)


def transition(guard, body: ast.Module, s: dict, ev: dict) -> dict:
    """Full transition: guard ? body : s (organism semantics)."""
    new = sym_exec(body, s, ev)
    if guard is None:
        return new
    g = expr_to_z3(guard, {"s": s, "ev": ev})
    return {f: z3.If(g, new[f], s[f]) for f in s}


@dataclass
class Verdict:
    status: str                  # "proved" | "counterexample" | "unsupported"
    model: dict | None = None    # counterexample: {"s.booked": 0, ...}
    note: str = ""


def _model_dict(m: z3.ModelRef) -> dict:
    out = {}
    for d in m.decls():
        v = m[d]
        out[d.name()] = v.as_long() if isinstance(v, z3.IntNumRef) else str(v)
    return dict(sorted(out.items()))


def _check(claim) -> Verdict:
    s = z3.Solver()
    s.set("timeout", 10_000)     # P14: timeout = honest degradation into fuzzed
    s.add(z3.Not(claim))
    r = s.check()
    if r == z3.unsat:
        return Verdict("proved")
    if r == z3.sat:
        return Verdict("counterexample", _model_dict(s.model()))
    return Verdict("unsupported", note="solver timeout/unknown -> fuzzed")


def _div_obligation(guard_z3, divs_guard, divs_other) -> Verdict | None:
    """The canon RAISES on division by 0 — the court must not stay silent: if a
    divisor can be zero (guard divisors — without context, conservatively because
    of the lazy and; the rest — under guard), the verdict is unsupported."""
    for d in divs_guard:
        chk = z3.Solver()
        chk.add(d == 0)
        if chk.check() != z3.unsat:
            return Verdict("unsupported",
                           note="divisor in guard may be zero (canon raises)")
    for d in divs_other:
        chk = z3.Solver()
        chk.add(z3.And(guard_z3, d == 0))
        if chk.check() != z3.unsat:
            return Verdict("unsupported",
                           note="divisor may be zero under guard (canon raises)")
    return None


def prove_rule(state_types: dict, ev_types: dict, guard_src: str | None,
               body_src: str, post_src: str | None,
               conserves_src: str | None) -> dict[str, Verdict]:
    """Inductive preservation of the rule's contract. Keys: post, conserves."""
    s, ev = _mk_vars("s", state_types), _mk_vars("ev", ev_types)
    guard = E.parse_expr(guard_src) if guard_src else None
    body = E.parse_body(body_src)
    _DIVS.clear()
    gz = expr_to_z3(guard, {"s": s, "ev": ev}) if guard else z3.BoolVal(True)
    divs_guard = list(_DIVS)
    _DIVS.clear()
    new = transition(guard, body, s, ev)
    divs_other = list(_DIVS)
    _DIVS.clear()
    dv = _div_obligation(gz, divs_guard, divs_other)
    out: dict[str, Verdict] = {}
    if dv is not None:
        if post_src:
            out["post"] = dv
        if conserves_src:
            out["conserves"] = dv
        return out
    if post_src:
        post = E.parse_expr(post_src)
        pre = expr_to_z3(post, {"s": s})
        cur = expr_to_z3(post, {"s": new})
        out["post"] = _check(z3.Implies(pre, cur))
    if conserves_src:
        con = E.parse_expr(conserves_src)
        out["conserves"] = _check(
            expr_to_z3(con, {"s": s}) == expr_to_z3(con, {"s": new}))
    return out


def prove_equiv(state_types: dict, ev_types: dict,
                a: tuple[str | None, str], b: tuple[str | None, str],
                assume_src: str | None = None) -> Verdict:
    """T_A ≡ T_B (full transitions guard?body:s). a/b = (guard_src, body_src).
    assume_src — an extra assumption over s (for example, reachability)."""
    s, ev = _mk_vars("s", state_types), _mk_vars("ev", ev_types)
    ga = E.parse_expr(a[0]) if a[0] else None
    gb = E.parse_expr(b[0]) if b[0] else None
    _DIVS.clear()
    gza = expr_to_z3(ga, {"s": s, "ev": ev}) if ga else z3.BoolVal(True)
    gzb = expr_to_z3(gb, {"s": s, "ev": ev}) if gb else z3.BoolVal(True)
    divs_guard = list(_DIVS)
    _DIVS.clear()
    ta = transition(ga, E.parse_body(a[1]), s, ev)
    tb = transition(gb, E.parse_body(b[1]), s, ev)
    divs_other = list(_DIVS)
    _DIVS.clear()
    dv = _div_obligation(z3.Or(gza, gzb), divs_guard, divs_other)
    if dv is not None:
        return dv
    same = z3.And(*[ta[f] == tb[f] for f in s])
    if assume_src:
        pre = expr_to_z3(E.parse_expr(assume_src), {"s": s})
        return _check(z3.Implies(pre, same))
    return _check(same)


def prove_entity(state_types: dict, init_vals: dict, rules: list,
                 events: dict) -> Verdict:
    """D80: entity induction via the Houdini algorithm — "post rejection is
    IMPOSSIBLE from init": I := the maximal subset of posts that are (a) true at
    init and (b) preserved by ALL rules; then (c) every post_r must follow from
    I ∧ guard_r after T_r. A post like "s.x == 0" on reset legitimately drops out
    of I (deposit breaks it) — it is checked in (c) under I. The former per-rule
    proved was only SELF-induction.
    rules: [(name, guard_src, body_src, post_src, ev_types)]."""
    posts = [(rn, E.parse_expr(p)) for rn, _, _, p, _ in rules if p]
    if not posts:
        return Verdict("unsupported", note="no posts to prove")
    s = _mk_vars("s", state_types)
    init_env = {f: (z3.IntVal(init_vals.get(f, 0)) if t == "int"
                    else z3.StringVal(init_vals.get(f, "")))
                for f, t in state_types.items()}

    def holds(claim) -> bool:
        chk = z3.Solver()
        chk.set("timeout", 5000)
        chk.add(z3.Not(claim))
        return chk.check() == z3.unsat

    # (a) candidates: posts that are true at init
    cand = [(rn, p) for rn, p in posts
            if holds(expr_to_z3(p, {"s": init_env}))]
    # (b) Houdini fixpoint: discard the non-preserved ones
    # T_body WITHOUT the noop branch: the runtime checks post only when the guard
    # passed — the guard premise is explicit, noop preserves everything trivially
    transitions = []
    for rn, g_src, b_src, _, ev_types in rules:
        ev = _mk_vars("ev", ev_types)
        _DIVS.clear()
        gz = (expr_to_z3(E.parse_expr(g_src), {"s": s, "ev": ev})
              if g_src else z3.BoolVal(True))
        raw_new = sym_exec(E.parse_body(b_src), s, ev)
        _DIVS.clear()
        transitions.append((rn, gz, raw_new))
    changed = True
    while changed and cand:
        changed = False
        I_s = z3.And(*[expr_to_z3(p, {"s": s}) for _, p in cand])
        for _, gz, new in transitions:
            for i, (prn, p) in enumerate(cand):
                if not holds(z3.Implies(z3.And(I_s, gz),
                                        expr_to_z3(p, {"s": new}))):
                    cand.pop(i)
                    changed = True
                    break
            if changed:
                break
    I_s = (z3.And(*[expr_to_z3(p, {"s": s}) for _, p in cand])
           if cand else z3.BoolVal(True))
    # (c) every post must hold from I after its own rule
    for rn, g_src, b_src, p_src, ev_types in rules:
        if not p_src:
            continue
        gz, new = next((g, nw) for nrn, g, nw in transitions if nrn == rn)
        pz = expr_to_z3(E.parse_expr(p_src), {"s": new})
        if not holds(z3.Implies(z3.And(I_s, gz), pz)):
            return Verdict("counterexample",
                           note=f"post of '{rn}' NOT guaranteed from "
                                f"reachable set (I = {len(cand)} posts); "
                                f"runtime may reject")
    return Verdict("proved",
                   note=f"entity-inductive (Houdini invariant of "
                        f"{len(cand)} posts): post rejection impossible "
                        f"from init")


def _referenced_entities(inv_tree, entity_names: set) -> set:
    import ast as _ast
    used = set()
    for n in _ast.walk(inv_tree):
        if isinstance(n, _ast.comprehension) and isinstance(n.iter, _ast.Name):
            if n.iter.id in entity_names:
                used.add(n.iter.id)
    return used


def _indexes_instances(inv_tree, entity_names: set) -> bool:
    """True if the invariant references the population NON-symmetrically — i.e.
    subscripts a specific instance (entity[i]). Such an invariant is NOT
    permutation-invariant, so the single-representative proof would be UNSOUND;
    the caller must route it to 'monitored' instead of a false 'proved'. A
    symmetric invariant touches the entity ONLY as an aggregate iterable."""
    import ast as _ast
    for n in _ast.walk(inv_tree):
        if isinstance(n, _ast.Subscript) and isinstance(n.value, _ast.Name):
            if n.value.id in entity_names:
                return True
    return False


def prove_invariants(g) -> dict:
    """#5 (D83): inductively PROVE cross-nothing invariants instead of only
    monitoring them. Decidable class: an invariant referencing exactly ONE
    entity whose instances are a FIXED list. Proof = init ⊨ I and every rule
    of that entity preserves I over the population (symmetric aggregates ->
    proving a representative transitioning instance with the rest arbitrary
    is sound). Anything else -> 'unsupported' with an honest reason, so the
    passport reads invariant: proved | monitored, never a false 'proved'."""
    ent_names = set(g.entities)
    out: dict = {}
    for name, src in g.invariants.items():
        tree = E.parse_expr(src)
        refs = _referenced_entities(tree, ent_names)
        if len(refs) != 1:
            out[name] = Verdict("unsupported",
                                note=f"spans {len(refs)} entities "
                                     f"(cross-entity cascade not modelled) -> monitored")
            continue
        en = next(iter(refs))
        ent = g.entities[en]
        if ent.instances == "dynamic":
            out[name] = Verdict("unsupported",
                                note="dynamic population (unbounded N) -> monitored")
            continue
        if _indexes_instances(tree, ent_names):
            # non-symmetric (indexes a specific instance) -> the single-
            # representative proof would be unsound; monitor instead of a
            # false 'proved' (D95: symmetry is now CHECKED, not assumed).
            out[name] = Verdict("unsupported",
                                note="indexes a specific instance (non-symmetric)"
                                     " -> monitored, not proved by representative")
            continue
        N = max(1, len(ent.instances))
        st = dict(ent.state)
        pop = [_mk_vars(f"i{k}", st) for k in range(N)]
        env0 = {en: pop}
        inv_z3 = expr_to_z3(tree, env0)
        # reachability premise: every instance satisfies the entity's PROVEN
        # posts (inductive by prove_entity) — sound, and upgrades invariants
        # that only hold on reachable states.
        posts = [E.parse_expr(r.contract.post) for r in ent.rules.values()
                 if r.contract.post]
        reach = z3.And(*[expr_to_z3(pp, {"s": inst})
                         for inst in pop for pp in posts]) if posts \
            else z3.BoolVal(True)
        # init |= I
        init_env = {f: (z3.IntVal(ent.init.get(f, 0)) if t == "int"
                        else z3.StringVal(ent.init.get(f, "")))
                    for f, t in st.items()}
        init_pop = {en: [init_env for _ in range(N)]}
        chk = z3.Solver(); chk.set("timeout", 8000)
        chk.add(z3.Not(expr_to_z3(tree, init_pop)))
        if chk.check() != z3.unsat:
            out[name] = Verdict("counterexample",
                                note="init violates the invariant")
            continue
        # every rule of en preserves I (representative = instance 0)
        verdict = Verdict("proved", note=f"inductive over {N} fixed instances "
                          f"(symmetric by construction: the invariant touches the "
                          f"population only via aggregates — CHECKED, not assumed; "
                          f"a specific-instance reference is routed to monitored)")
        for rn, r in ent.rules.items():
            if r.when not in g.events:
                continue
            ev = _mk_vars("ev", dict(g.events[r.when]))
            guard = E.parse_expr(r.guard) if r.guard else None
            _DIVS.clear()
            new0 = transition(guard, E.parse_body(r.body), pop[0], ev)
            _DIVS.clear()
            new_pop = {en: [new0] + pop[1:]}
            inv_after = expr_to_z3(tree, new_pop)
            v = _check(z3.Implies(z3.And(inv_z3, reach), inv_after))
            if v.status != "proved":
                verdict = Verdict(v.status,
                                  note=f"rule '{rn}' can break invariant "
                                       f"'{name}'" + (f": {v.note}" if v.note else ""))
                break
        out[name] = verdict
    return out
