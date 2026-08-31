# -*- coding: utf-8 -*-
"""go-stdlib: a printer for Expr/bodies -> Go (the emit method of the dialect interface).

The semantics MUST match the canon (the conformance corpus is the gate):
  - int -> int64 (any divergence from the canon's mathematical integers is UNEXPRESSIBLE);
  - // and % -> floorDiv/floorMod (Go's operators truncate, Python's floor:
    -7//2 = -4, but Go -7/2 = -3 — caught by the corpus, hence the helpers);
  - min/max -> built into Go 1.21+; aggregates -> IIFE loops.
"""
from __future__ import annotations

import ast

GO_HELPERS = """\
func floorDiv(a, b int64) int64 {
\tq := a / b
\tif a%b != 0 && (a < 0) != (b < 0) {
\t\tq--
\t}
\treturn q
}

func floorMod(a, b int64) int64 {
\tm := a % b
\tif m != 0 && (m < 0) != (b < 0) {
\t\tm += b
\t}
\treturn m
}
"""

_OPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*",
        ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
        ast.Gt: ">", ast.GtE: ">="}


def goname(s: str) -> str:
    return "".join(w.capitalize() for w in s.split("_"))


def emit_expr(tree, names: dict[str, str]) -> str:
    """names: Expr name -> Go expression (e.g. {"s": "s", "ev": "ev",
    "room": "roomList()"}). Attributes are printed in PascalCase."""
    def p(n) -> str:
        match n:
            case ast.Expression(body=b):
                return p(b)
            case ast.BoolOp(op=op, values=vs):
                j = " && " if isinstance(op, ast.And) else " || "
                return "(" + j.join(p(v) for v in vs) + ")"
            case ast.UnaryOp(op=ast.Not(), operand=o):
                return f"!({p(o)})"
            case ast.UnaryOp(op=ast.USub(), operand=o):
                return f"(-{p(o)})"
            case ast.BinOp(left=l, op=ast.FloorDiv(), right=r):
                return f"floorDiv({p(l)}, {p(r)})"
            case ast.BinOp(left=l, op=ast.Mod(), right=r):
                return f"floorMod({p(l)}, {p(r)})"
            case ast.BinOp(left=l, op=op, right=r):
                return f"({p(l)} {_OPS[type(op)]} {p(r)})"
            case ast.Compare(left=l, ops=[op], comparators=[r]):
                return f"({p(l)} {_OPS[type(op)]} {p(r)})"
            case ast.Name(id=x):
                return names[x]
            case ast.Attribute(value=v, attr=a):
                return f"{p(v)}.{goname(a)}"
            case ast.Constant(value=True):
                return "true"
            case ast.Constant(value=False):
                return "false"
            case ast.Constant(value=int() as v):
                return f"int64({v})" if v < 0 else str(v)
            case ast.Constant(value=str() as v):
                return '"' + v.replace('"', '\\"') + '"'
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                return f"int64(len({p(a)}))"
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                return f"{f}({', '.join(p(a) for a in args)})"
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                var = gen.target.id
                inner = dict(names); inner[var] = var
                it = p(gen.iter)
                cond = emit_expr(ast.Expression(body=gen.ifs[0]), inner) if gen.ifs else ""
                elt = emit_expr(ast.Expression(body=g.elt), inner)
                if f == "sum":
                    body = f"acc += {elt}" if not cond else f"if {cond} {{ acc += {elt} }}"
                    return (f"func() int64 {{ var acc int64; for _, {var} := range {it} "
                            f"{{ {body} }}; return acc }}()")
                if f == "all":
                    chk = f"if !({elt}) {{ return false }}" if not cond else \
                        f"if {cond} && !({elt}) {{ return false }}"
                    return (f"func() bool {{ for _, {var} := range {it} "
                            f"{{ {chk} }}; return true }}()")
                if f == "any":
                    chk = f"if {elt} {{ return true }}" if not cond else \
                        f"if {cond} && ({elt}) {{ return true }}"
                    return (f"func() bool {{ for _, {var} := range {it} "
                            f"{{ {chk} }}; return false }}()")
            case ast.IfExp(test=c, body=b, orelse=e):
                return (f"func() int64 {{ if {p(c)} {{ return {p(b)} }}; "
                        f"return {p(e)} }}()")
        raise ValueError(f"emit(go): unexpected node {type(n).__name__}")
    return p(tree)


def emit_body(tree: ast.Module, names: dict[str, str], indent: str = "\t") -> str:
    """A rule body -> Go statements (mutates the local copy of s)."""
    out: list[str] = []

    def stmt(st, ind):
        match st:
            case ast.Assign(targets=[ast.Attribute(attr=f)], value=v):
                out.append(f"{ind}s.{goname(f)} = "
                           f"{emit_expr(ast.Expression(body=v), names)}")
            case ast.If(test=c, body=b, orelse=o):
                out.append(f"{ind}if {emit_expr(ast.Expression(body=c), names)} {{")
                for s2 in b:
                    stmt(s2, ind + "\t")
                if o:
                    out.append(f"{ind}}} else {{")
                    for s2 in o:
                        stmt(s2, ind + "\t")
                out.append(f"{ind}}}")
            case ast.Pass():
                pass
    for st in tree.body:
        stmt(st, indent)
    return "\n".join(out)
