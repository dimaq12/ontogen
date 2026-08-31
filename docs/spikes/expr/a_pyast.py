# -*- coding: utf-8 -*-
"""Spike A: Expr = a SUBSET of PYTHON EXPRESSIONS, parser — stdlib ast.

Hypothesis (D4: borrow the lexicon): not CEL and not a custom grammar, but Python
expressions parsed by the native ast and narrowed by a WHITELIST of nodes. We own
neither the grammar nor the parser — only the list of what is allowed.

Spike criteria (PLAN F0): typecheck + printers to 2 languages + SMT + readability.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

# ---------------------------------------------------------------- whitelist

_ALLOWED = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.USub, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Name, ast.Load, ast.Attribute, ast.Constant, ast.Call,
    ast.GeneratorExp, ast.comprehension, ast.IfExp, ast.Store,
)
_ALLOWED_CALLS = {"sum", "all", "any", "len", "min", "max"}


def parse(src: str) -> ast.expression:
    tree = ast.parse(src, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise ValueError(f"node outside Expr subset: {type(node).__name__} in {src!r}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_CALLS:
                raise ValueError(f"call outside whitelist: {ast.dump(node.func)}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, bool)):
            raise ValueError(f"literal outside subset: {node.value!r}")
        if isinstance(node, ast.comprehension) and (node.is_async or len(node.ifs) > 1):
            raise ValueError("comprehension: sync only, at most one if")
    return tree


# ---------------------------------------------------------------- typechecker

@dataclass(frozen=True)
class TList:
    elem: dict  # element fields: name -> "int"|"bool"


Env = dict  # name -> "int" | "bool" | dict(fields) | TList


def typecheck(tree: ast.expression, env: Env) -> str:
    """Returns the expression's type ('int'|'bool') or raises with a coordinate."""
    def t(n) -> object:
        match n:
            case ast.Expression(body=b):
                return t(b)
            case ast.BoolOp(values=vs):
                for v in vs:
                    _want(t(v), "bool", v)
                return "bool"
            case ast.UnaryOp(op=ast.Not(), operand=o):
                _want(t(o), "bool", o); return "bool"
            case ast.UnaryOp(op=ast.USub(), operand=o):
                _want(t(o), "int", o); return "int"
            case ast.BinOp(left=l, right=r):
                _want(t(l), "int", l); _want(t(r), "int", r); return "int"
            case ast.Compare(left=l, comparators=[r]):
                lt, rt = t(l), t(r)
                if lt != rt:
                    raise TypeError(f"comparison of different types {lt} and {rt} (line {n.lineno}, col {n.col_offset})")
                return "bool"
            case ast.Name(id=name):
                if name not in env:
                    raise TypeError(f"unknown name '{name}' (col {n.col_offset})")
                return env[name]
            case ast.Attribute(value=v, attr=a):
                vt = t(v)
                if not isinstance(vt, dict):
                    raise TypeError(f"'.{a}' on non-struct (col {n.col_offset})")
                if a not in vt:
                    raise TypeError(f"no field '{a}'; available: {sorted(vt)} (col {n.col_offset})")
                return vt[a]
            case ast.Constant(value=v):
                return "bool" if isinstance(v, bool) else "int"
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                inner_env = dict(env)
                gen = g.generators[0]
                src_t = t(gen.iter)
                if not isinstance(src_t, TList):
                    raise TypeError(f"{f}(... for ... in X): X is not a list")
                inner_env[gen.target.id] = src_t.elem
                if gen.ifs:
                    _want(typecheck(ast.Expression(body=gen.ifs[0]), inner_env), "bool", gen.ifs[0])
                el = typecheck(ast.Expression(body=g.elt), inner_env)
                if f in ("all", "any"):
                    _want(el, "bool", g.elt); return "bool"
                _want(el, "int", g.elt); return "int"
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                if not isinstance(t(a), TList):
                    raise TypeError("len: argument is not a list")
                return "int"
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                for a in args:
                    _want(t(a), "int", a)
                return "int"
            case ast.IfExp(test=c, body=b, orelse=e):
                _want(t(c), "bool", c)
                bt, et = t(b), t(e)
                if bt != et:
                    raise TypeError("if-expression: branches have different types")
                return bt
            case _:
                raise TypeError(f"typecheck: unexpected node {type(n).__name__}")

    def _want(got, want, node):
        if got != want:
            raise TypeError(f"expected {want}, got {got} (line {getattr(node,'lineno','?')}, col {getattr(node,'col_offset','?')})")
    res = t(tree)
    if res not in ("int", "bool"):
        raise TypeError(f"expression must be int|bool, got {res}")
    return res


# ---------------------------------------------------------------- printers

def _goname(s: str) -> str:
    return "".join(w.capitalize() for w in s.split("_"))


def to_go(tree, receiver_types: set[str] = frozenset()) -> str:
    """Print to Go. Aggregates — IIFE loops (the skeleton can extract a helper)."""
    OPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.FloorDiv: "/", ast.Mod: "%",
           ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}

    def p(n) -> str:
        match n:
            case ast.Expression(body=b): return p(b)
            case ast.BoolOp(op=op, values=vs):
                j = " && " if isinstance(op, ast.And) else " || "
                return "(" + j.join(p(v) for v in vs) + ")"
            case ast.UnaryOp(op=ast.Not(), operand=o): return f"!({p(o)})"
            case ast.UnaryOp(op=ast.USub(), operand=o): return f"-{p(o)}"
            case ast.BinOp(left=l, op=op, right=r): return f"({p(l)} {OPS[type(op)]} {p(r)})"
            case ast.Compare(left=l, ops=[op], comparators=[r]): return f"{p(l)} {OPS[type(op)]} {p(r)}"
            case ast.Name(id=x): return x
            case ast.Attribute(value=v, attr=a): return f"{p(v)}.{_goname(a)}"
            case ast.Constant(value=True): return "true"
            case ast.Constant(value=False): return "false"
            case ast.Constant(value=v): return str(v)
            case ast.Call(func=ast.Name(id="len"), args=[a]): return f"int64(len({p(a)}))"
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                return f"{f}({', '.join(p(a) for a in args)})"
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]; v, it = gen.target.id, p(gen.iter)
                cond = f"if {p(gen.ifs[0])} " if gen.ifs else ""
                if f == "sum":
                    return (f"func() int64 {{ var acc int64; for _, {v} := range {it} "
                            f"{{ {cond}{{ acc += {p(g.elt)} }} }}; return acc }}()")
                if f == "all":
                    return (f"func() bool {{ for _, {v} := range {it} "
                            f"{{ {cond}{{ if !({p(g.elt)}) {{ return false }} }} }}; return true }}()")
                if f == "any":
                    return (f"func() bool {{ for _, {v} := range {it} "
                            f"{{ {cond}{{ if {p(g.elt)} {{ return true }} }} }}; return false }}()")
                raise NotImplementedError(f)
            case ast.IfExp(test=c, body=b, orelse=e):
                return f"func() int64 {{ if {p(c)} {{ return {p(b)} }}; return {p(e)} }}()"
            case _:
                raise NotImplementedError(type(n).__name__)
    return p(tree)


def to_python(tree) -> str:
    return ast.unparse(tree)          # printer to the second language — free


# ---------------------------------------------------------------- SMT (z3)

def to_z3(tree, sym: dict):
    """Encoding to z3. sym: name -> z3 variable | dict of fields | list of dicts
    (bounded instances — bounded encoding of aggregates)."""
    import z3

    def e(n, env):
        match n:
            case ast.Expression(body=b): return e(b, env)
            case ast.BoolOp(op=op, values=vs):
                zs = [e(v, env) for v in vs]
                return z3.And(*zs) if isinstance(op, ast.And) else z3.Or(*zs)
            case ast.UnaryOp(op=ast.Not(), operand=o): return z3.Not(e(o, env))
            case ast.UnaryOp(op=ast.USub(), operand=o): return -e(o, env)
            case ast.BinOp(left=l, op=op, right=r):
                a, b = e(l, env), e(r, env)
                import operator as _op
                return {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul,
                        ast.FloorDiv: lambda x, y: x / y, ast.Mod: _op.mod}[type(op)](a, b)
            case ast.Compare(left=l, ops=[op], comparators=[r]):
                a, b = e(l, env), e(r, env)
                import operator as _op
                return {ast.Eq: _op.eq, ast.NotEq: _op.ne, ast.Lt: _op.lt,
                        ast.LtE: _op.le, ast.Gt: _op.gt, ast.GtE: _op.ge}[type(op)](a, b)
            case ast.Name(id=x): return env[x]
            case ast.Attribute(value=v, attr=a): return e(v, env)[a]
            case ast.Constant(value=v): return v
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                items = e(gen.iter, env)          # list of dicts (bounded)
                acc = []
                for item in items:
                    ienv = dict(env); ienv[gen.target.id] = item
                    val = e(g.elt, ienv)
                    if gen.ifs:
                        cond = e(gen.ifs[0], ienv)
                        val = z3.If(cond, val, 0) if f == "sum" else z3.Implies(cond, val) if f == "all" else z3.And(cond, val)
                    acc.append(val)
                if f == "sum": return z3.Sum(acc) if acc else 0
                if f == "all": return z3.And(*acc) if acc else True
                if f == "any": return z3.Or(*acc) if acc else False
                raise NotImplementedError(f)
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                return len(e(a, env))
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                import functools
                zs = [e(a, env) for a in args]
                pick = (lambda x, y: z3.If(x < y, x, y)) if f == "min" else (lambda x, y: z3.If(x > y, x, y))
                return functools.reduce(pick, zs)
            case ast.IfExp(test=c, body=b, orelse=el):
                return z3.If(e(c, env), e(b, env), e(el, env))
            case _:
                raise NotImplementedError(type(n).__name__)
    return e(tree, sym)
