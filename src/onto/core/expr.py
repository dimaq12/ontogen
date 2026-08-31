# -*- coding: utf-8 -*-
"""Expr — the language of genome expressions and rule bodies (D23: a subset of
Python, stdlib ast parser, node whitelist; spike spikes/expr/RESULTS.md).

Roles (SPEC §2.2, §10): one grammar ->
  - typecheck_*: typecheck against genome types before any execution;
  - eval_expr / exec_body: the CANONICAL INTERPRETER — reference semantics,
    the definition of correctness (§9: a dialect body must be ≡ to this);
  - (F2+) dialect printers and the SMT encoder — consumers of the same AST.

Rule/skill boundary (SPEC §10, PLAN F1): a rule body is <= MAX_BODY_NODES
AST nodes, no loops; anything more complex is a skill with an oracle (NOT a §7
prediction P7: language creep = whitelist expansion, only through UNEXPRESSIBLE).

Types: "int" | "bool" | "str" | dict of fields | TList(element fields).
str is legal only in equalities (routing keys), not in arithmetic.
Machine messages are in English (D24).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

MAX_EXPR_NODES = 96
# Wave LAGO (D52): 64 could not fit an honest invoicing rule (145 nodes of pure
# arithmetic). The rule/skill boundary is STRUCTURAL (no loops = not an algorithm);
# the node limit is a sanity cap against smuggling in walls of code.
MAX_BODY_NODES = 256

_ALLOWED_EXPR = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.USub, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Name, ast.Load, ast.Attribute, ast.Constant, ast.Call,
    ast.GeneratorExp, ast.comprehension, ast.IfExp, ast.Store,
)
_ALLOWED_CALLS = {"sum", "all", "any", "len", "min", "max"}


class ExprError(ValueError):
    """A parse/typecheck/limit error — with coordinates, in English."""


@dataclass(frozen=True)
class TList:
    elem: dict  # element fields: name -> "int" | "bool" | "str"


def _check_nodes(tree, src: str, limit: int, what: str) -> None:
    n = sum(1 for _ in ast.walk(tree))
    if n > limit:
        raise ExprError(
            f"{what} has {n} AST nodes > limit {limit} — this is a skill, "
            f"not a rule (declare it in 'skills' with an oracle): {src[:60]!r}")


def parse_expr(src: str, limit: int = MAX_EXPR_NODES) -> ast.Expression:
    try:
        tree = ast.parse(src, mode="eval")
    except SyntaxError as e:
        raise ExprError(f"syntax error in expression: {e.msg} (line {e.lineno}, col {e.offset}): {src[:80]!r}")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_EXPR):
            raise ExprError(f"node outside Expr subset: {type(node).__name__} in {src[:80]!r}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_CALLS:
                raise ExprError(f"call outside whitelist {sorted(_ALLOWED_CALLS)}: {src[:80]!r}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, bool, str)):
            raise ExprError(f"literal outside subset (int|bool|str): {node.value!r}")
        if isinstance(node, ast.comprehension) and (node.is_async or len(node.ifs) > 1):
            raise ExprError("comprehension: sync only, at most one 'if'")
    _check_nodes(tree, src, limit, "expression")
    return tree


# ------------------------------------------------------------------ typecheck

def typecheck_expr(tree: ast.Expression, env: dict) -> str:
    def want(got, need, node):
        if got != need:
            raise ExprError(f"expected {need}, got {got} (line {getattr(node, 'lineno', '?')}, "
                            f"col {getattr(node, 'col_offset', '?')})")

    def t(n):
        match n:
            case ast.Expression(body=b):
                return t(b)
            case ast.BoolOp(values=vs):
                for v in vs:
                    want(t(v), "bool", v)
                return "bool"
            case ast.UnaryOp(op=ast.Not(), operand=o):
                want(t(o), "bool", o); return "bool"
            case ast.UnaryOp(op=ast.USub(), operand=o):
                want(t(o), "int", o); return "int"
            case ast.BinOp(left=l, right=r):
                want(t(l), "int", l); want(t(r), "int", r); return "int"
            case ast.Compare(left=l, ops=[op], comparators=[r]):
                lt, rt = t(l), t(r)
                if lt != rt:
                    raise ExprError(f"comparison of different types {lt} and {rt} "
                                    f"(line {n.lineno}, col {n.col_offset})")
                if lt == "str" and not isinstance(op, (ast.Eq, ast.NotEq)):
                    raise ExprError(f"str allows only ==/!= (line {n.lineno}, col {n.col_offset})")
                return "bool"
            case ast.Name(id=name):
                if name not in env:
                    raise ExprError(f"unknown name '{name}' (col {n.col_offset}); "
                                    f"available: {sorted(env)}")
                return env[name]
            case ast.Attribute(value=v, attr=a):
                vt = t(v)
                if not isinstance(vt, dict):
                    raise ExprError(f"'.{a}' on non-struct (col {n.col_offset})")
                if a not in vt:
                    raise ExprError(f"no field '{a}'; available: {sorted(vt)} (col {n.col_offset})")
                return vt[a]
            case ast.Constant(value=bool()):
                return "bool"
            case ast.Constant(value=int()):
                return "int"
            case ast.Constant(value=str()):
                return "str"
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                src_t = t(gen.iter)
                if not isinstance(src_t, TList):
                    raise ExprError(f"{f}(... for ... in X): X is not a list")
                inner = dict(env); inner[gen.target.id] = src_t.elem
                if gen.ifs:
                    want(typecheck_expr(ast.Expression(body=gen.ifs[0]), inner), "bool", gen.ifs[0])
                el = typecheck_expr(ast.Expression(body=g.elt), inner)
                if f in ("all", "any"):
                    want(el, "bool", g.elt); return "bool"
                if f == "sum":
                    want(el, "int", g.elt); return "int"
                raise ExprError(f"{f}: generator form supports sum/all/any only")
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                if not isinstance(t(a), TList):
                    raise ExprError("len: argument is not a list")
                return "int"
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max") and args:
                for a in args:
                    want(t(a), "int", a)
                return "int"
            case ast.IfExp(test=c, body=b, orelse=e):
                want(t(c), "bool", c)
                bt, et = t(b), t(e)
                if bt != et:
                    raise ExprError("if-expression: branches have different types")
                return bt
            case _:
                raise ExprError(f"typecheck: unexpected node {type(n).__name__}")
    return t(tree)


# ------------------------------------------------------------- interpreter

class EvalError(RuntimeError):
    """An execution error (division by zero, etc.) — the transition is rejected."""


def eval_expr(tree, env: dict):
    """The canonical Expr interpreter. env: name -> int|bool|str|dict|list[dict]."""
    def e(n, env):
        match n:
            case ast.Expression(body=b):
                return e(b, env)
            case ast.BoolOp(op=op, values=vs):
                if isinstance(op, ast.And):
                    return all(e(v, env) for v in vs)
                return any(e(v, env) for v in vs)
            case ast.UnaryOp(op=ast.Not(), operand=o):
                return not e(o, env)
            case ast.UnaryOp(op=ast.USub(), operand=o):
                return -e(o, env)
            case ast.BinOp(left=l, op=op, right=r):
                a, b = e(l, env), e(r, env)
                match op:
                    case ast.Add(): return a + b
                    case ast.Sub(): return a - b
                    case ast.Mult(): return a * b
                    case ast.FloorDiv():
                        if b == 0:
                            raise EvalError("division by zero")
                        return a // b
                    case ast.Mod():
                        if b == 0:
                            raise EvalError("modulo by zero")
                        return a % b
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
            case ast.Constant(value=v):
                return v
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                items = e(gen.iter, env)
                vals = []
                for item in items:
                    ienv = dict(env); ienv[gen.target.id] = item
                    if gen.ifs and not e(gen.ifs[0], ienv):
                        continue
                    vals.append(e(g.elt, ienv))
                if f == "sum":
                    return sum(vals)
                if f == "all":
                    return all(vals)
                if f == "any":
                    return any(vals)
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                return len(e(a, env))
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                vals = [e(a, env) for a in args]
                return min(vals) if f == "min" else max(vals)
            case ast.IfExp(test=c, body=b, orelse=el):
                return e(b, env) if e(c, env) else e(el, env)
        raise EvalError(f"eval: unexpected node {type(n).__name__}")
    return e(tree, env)


# ------------------------------------------------------------- rule bodies

_ALLOWED_STMT = (ast.Module, ast.Assign, ast.If, ast.Pass)


def parse_body(src: str) -> ast.Module:
    """A rule body: `s.<field> = <expr>` assignments + if/elif/else + pass.
    No loops, no new names — anything past the limit = a skill."""
    try:
        tree = ast.parse(src, mode="exec")
    except SyntaxError as e:
        raise ExprError(f"syntax error in body: {e.msg} (line {e.lineno}, col {e.offset})")
    for node in ast.walk(tree):
        if isinstance(node, _ALLOWED_STMT):
            continue
        if isinstance(node, tuple(_ALLOWED_EXPR)) and not isinstance(node, ast.Expression):
            continue
        raise ExprError(f"statement outside body subset: {type(node).__name__}")
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.Assign):
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Attribute) \
               or not isinstance(stmt.targets[0].value, ast.Name) or stmt.targets[0].value.id != "s":
                raise ExprError("assignment target must be 's.<field>' "
                                f"(line {stmt.lineno})")
    _check_nodes(tree, src, MAX_BODY_NODES, "rule body")
    return tree


def typecheck_body(tree: ast.Module, state_types: dict, ev_types: dict) -> None:
    env = {"s": state_types, "ev": ev_types}

    def chk(stmts):
        for st in stmts:
            match st:
                case ast.Assign(targets=[ast.Attribute(attr=field)], value=v):
                    if field not in state_types:
                        raise ExprError(f"no state field '{field}'; available: "
                                        f"{sorted(state_types)} (line {st.lineno})")
                    got = typecheck_expr(ast.Expression(body=v), env)
                    if got != state_types[field]:
                        raise ExprError(f"s.{field} is {state_types[field]}, assigned {got} "
                                        f"(line {st.lineno})")
                case ast.If(test=c, body=b, orelse=o):
                    got = typecheck_expr(ast.Expression(body=c), env)
                    if got != "bool":
                        raise ExprError(f"if condition must be bool, got {got} (line {st.lineno})")
                    chk(b); chk(o)
                case ast.Pass():
                    pass
                case _:
                    raise ExprError(f"unexpected statement {type(st).__name__}")
    chk(tree.body)


def exec_body(tree: ast.Module, s: dict, ev: dict) -> dict:
    """Execute the body over a COPY of the state; return the new state."""
    new = dict(s)

    def run(stmts):
        for st in stmts:
            match st:
                case ast.Assign(targets=[ast.Attribute(attr=field)], value=v):
                    new[field] = eval_expr(ast.Expression(body=v), {"s": new, "ev": ev})
                case ast.If(test=c, body=b, orelse=o):
                    if eval_expr(ast.Expression(body=c), {"s": new, "ev": ev}):
                        run(b)
                    else:
                        run(o)
                case ast.Pass():
                    pass
    run(tree.body)
    return new
