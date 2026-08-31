# -*- coding: utf-8 -*-
"""rust-stdlib: a printer for Expr/bodies -> Rust (the emit method of the dialect).

The semantics MUST match the canon (the conformance corpus is the gate):
  - int -> i64 (any divergence from the canon's mathematical integers is UNEXPRESSIBLE);
  - // and % -> floor_div/floor_mod (Rust's / truncates toward zero and % follows
    the dividend's sign, Python floors: -7//2 = -4 — caught by the corpus);
  - min/max -> std::cmp (nested for >2 args); aggregates -> block expressions;
  - fields stay snake_case (canon names are already snake_case) — no renaming.
"""
from __future__ import annotations

import ast

RUST_HELPERS = """\
fn floor_div(a: i64, b: i64) -> i64 {
    let q = a / b;
    if a % b != 0 && ((a < 0) != (b < 0)) { q - 1 } else { q }
}

fn floor_mod(a: i64, b: i64) -> i64 {
    let m = a % b;
    if m != 0 && ((m < 0) != (b < 0)) { m + b } else { m }
}
"""

_OPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*",
        ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
        ast.Gt: ">", ast.GtE: ">="}


def _minmax(fn: str, args: list[str]) -> str:
    call = "std::cmp::min" if fn == "min" else "std::cmp::max"
    acc = args[-1]
    for a in reversed(args[:-1]):
        acc = f"{call}({a}, {acc})"
    return acc


def emit_expr(tree, names: dict[str, str]) -> str:
    """names: Expr name -> Rust expression (e.g. {"s": "s", "ev": "ev",
    "room": "room_list()"})."""
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
                return f"(-({p(o)}))"
            case ast.BinOp(left=l, op=ast.FloorDiv(), right=r):
                return f"floor_div({p(l)}, {p(r)})"
            case ast.BinOp(left=l, op=ast.Mod(), right=r):
                return f"floor_mod({p(l)}, {p(r)})"
            case ast.BinOp(left=l, op=op, right=r):
                return f"({p(l)} {_OPS[type(op)]} {p(r)})"
            case ast.Compare(left=l, ops=[op], comparators=[r]):
                return f"({p(l)} {_OPS[type(op)]} {p(r)})"
            case ast.Name(id=x):
                return names[x]
            case ast.Attribute(value=v, attr=a):
                return f"{p(v)}.{a}"
            case ast.Constant(value=True):
                return "true"
            case ast.Constant(value=False):
                return "false"
            case ast.Constant(value=int() as v):
                return f"{v}i64"
            case ast.Constant(value=str() as v):
                return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
            case ast.Call(func=ast.Name(id="len"), args=[a]):
                return f"({p(a)}.len() as i64)"
            case ast.Call(func=ast.Name(id=f), args=args) if f in ("min", "max"):
                return _minmax(f, [p(a) for a in args])
            case ast.Call(func=ast.Name(id=f), args=[ast.GeneratorExp() as g]):
                gen = g.generators[0]
                var = gen.target.id
                inner = dict(names); inner[var] = var
                it = p(gen.iter)
                cond = emit_expr(ast.Expression(body=gen.ifs[0]), inner) if gen.ifs else ""
                elt = emit_expr(ast.Expression(body=g.elt), inner)
                if f == "sum":
                    body = (f"acc += {elt};" if not cond
                            else f"if {cond} {{ acc += {elt}; }}")
                    return (f"{{ let mut acc: i64 = 0; for {var} in {it}.iter() "
                            f"{{ {body} }} acc }}")
                if f == "all":
                    chk = (f"if !({elt}) {{ ok = false; break; }}" if not cond
                           else f"if {cond} && !({elt}) {{ ok = false; break; }}")
                    return (f"{{ let mut ok = true; for {var} in {it}.iter() "
                            f"{{ {chk} }} ok }}")
                if f == "any":
                    chk = (f"if {elt} {{ hit = true; break; }}" if not cond
                           else f"if {cond} && ({elt}) {{ hit = true; break; }}")
                    return (f"{{ let mut hit = false; for {var} in {it}.iter() "
                            f"{{ {chk} }} hit }}")
            case ast.IfExp(test=c, body=b, orelse=e):
                return f"(if {p(c)} {{ {p(b)} }} else {{ {p(e)} }})"
        raise ValueError(f"emit(rust): unexpected node {type(n).__name__}")
    return p(tree)


def emit_body(tree: ast.Module, names: dict[str, str], indent: str = "    ") -> str:
    """A rule body -> Rust statements (mutates the local copy of s)."""
    out: list[str] = []

    def stmt(st, ind):
        match st:
            case ast.Assign(targets=[ast.Attribute(attr=f)], value=v):
                out.append(f"{ind}s.{f} = "
                           f"{emit_expr(ast.Expression(body=v), names)};")
            case ast.If(test=c, body=b, orelse=o):
                out.append(f"{ind}if {emit_expr(ast.Expression(body=c), names)} {{")
                for s2 in b:
                    stmt(s2, ind + "    ")
                if o:
                    out.append(f"{ind}}} else {{")
                    for s2 in o:
                        stmt(s2, ind + "    ")
                out.append(f"{ind}}}")
            case ast.Pass():
                pass
    for st in tree.body:
        stmt(st, indent)
    return "\n".join(out)
