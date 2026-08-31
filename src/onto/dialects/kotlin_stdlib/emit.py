# -*- coding: utf-8 -*-
"""kotlin-stdlib: a printer for Expr/bodies -> Kotlin.

The genome's guards/bodies are a Python subset (ast). This walks that ast and
emits the equivalent Kotlin expression/statement. Integer math is Long (the
canon uses ints); == on Long/String is Kotlin structural equality, matching the
reference. No transformations of meaning — emit is a faithful functor, and the
certificate is fold-parity (dialects/gates.py), not trust.
"""
from __future__ import annotations

import ast

_CMP = {ast.Gt: ">", ast.Lt: "<", ast.GtE: ">=", ast.LtE: "<=",
        ast.Eq: "==", ast.NotEq: "!="}
_BIN = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}

KT_HELPERS = """\
fun floorDiv(a: Long, b: Long): Long {
    var q = a / b
    if (a % b != 0L && (a < 0L) != (b < 0L)) q -= 1L
    return q
}
fun floorMod(a: Long, b: Long): Long {
    var m = a % b
    if (m != 0L && (m < 0L) != (b < 0L)) m += b
    return m
}
"""


def kttype(t: str) -> str:
    return "String" if t == "str" else "Long"


def ktlit(v, t: str) -> str:
    if t == "str":
        return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'
    return f"{int(v)}L"


def _minmax(fn: str, args: list[str]) -> str:
    call = "minOf" if fn == "min" else "maxOf"
    acc = args[-1]
    for a in reversed(args[:-1]):
        acc = f"{call}({a}, {acc})"
    return acc


def _call(n, names, p):
    f = n.func.id if isinstance(n.func, ast.Name) else None
    if f == "len":
        return f"({p(n.args[0])}.size.toLong())"
    if f in ("min", "max"):
        return _minmax(f, [p(a) for a in n.args])
    if f in ("sum", "all", "any") and n.args and isinstance(n.args[0], ast.GeneratorExp):
        g = n.args[0]
        gen = g.generators[0]
        var = gen.target.id
        inner = dict(names); inner[var] = var
        it = p(gen.iter)
        elt = emit_expr(ast.Expression(body=g.elt), inner)
        base = it
        if gen.ifs:
            cond = emit_expr(ast.Expression(body=gen.ifs[0]), inner)
            base = f"{it}.filter {{ {var} -> {cond} }}"
        if f == "sum":
            return f"{base}.sumOf {{ {var} -> {elt} }}"
        if f == "all":
            return f"{base}.all {{ {var} -> {elt} }}"
        return f"{base}.any {{ {var} -> {elt} }}"
    raise NotImplementedError(f"kotlin call: {ast.dump(n)}")


def emit_expr(tree, names: dict[str, str]) -> str:
    """names: Expr root name -> Kotlin expression (e.g. {"s": "s", "ev": "ev"})."""
    def p(n) -> str:
        if isinstance(n, ast.Expression):
            return p(n.body)
        if isinstance(n, ast.BoolOp):
            op = " && " if isinstance(n.op, ast.And) else " || "
            return "(" + op.join(p(v) for v in n.values) + ")"
        if isinstance(n, ast.UnaryOp):
            if isinstance(n.op, ast.Not):
                return "(!(" + p(n.operand) + "))"
            if isinstance(n.op, ast.USub):
                return "(-" + p(n.operand) + ")"
            if isinstance(n.op, ast.UAdd):
                return p(n.operand)
        if isinstance(n, ast.Compare):
            if len(n.ops) != 1:
                # chained comparison a<b<c -> (a<b) && (b<c)
                parts = []
                left = n.left
                for op, comp in zip(n.ops, n.comparators):
                    parts.append("(" + p(left) + f" {_CMP[type(op)]} " + p(comp) + ")")
                    left = comp
                return "(" + " && ".join(parts) + ")"
            return "(" + p(n.left) + f" {_CMP[type(n.ops[0])]} " + p(n.comparators[0]) + ")"
        if isinstance(n, ast.BinOp):
            if isinstance(n.op, (ast.FloorDiv, ast.Div)):
                return f"floorDiv({p(n.left)}, {p(n.right)})"
            if isinstance(n.op, ast.Mod):
                return f"floorMod({p(n.left)}, {p(n.right)})"
            return "(" + p(n.left) + f" {_BIN[type(n.op)]} " + p(n.right) + ")"
        if isinstance(n, ast.Call):
            return _call(n, names, p)
        if isinstance(n, ast.IfExp):
            return f"(if ({p(n.test)}) {p(n.body)} else {p(n.orelse)})"
        if isinstance(n, ast.Attribute):
            return p(n.value) + "." + n.attr
        if isinstance(n, ast.Name):
            return names.get(n.id, n.id)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, bool):
                return "true" if n.value else "false"
            if isinstance(n.value, int):
                return f"{n.value}L"
            if isinstance(n.value, str):
                return '"' + n.value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        raise NotImplementedError(f"kotlin emit_expr: {ast.dump(n)}")
    return p(tree)


def emit_body(tree: ast.Module, names: dict[str, str], indent: str = "    ") -> str:
    """Bodies are Expr statements over `s` (mutable copy) and `ev`."""
    out: list[str] = []

    def stmt(st, ind: str) -> None:
        if isinstance(st, ast.Assign):
            tgt = st.targets[0]
            if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)):
                raise NotImplementedError(f"kotlin assign target: {ast.dump(tgt)}")
            out.append(f"{ind}{names.get(tgt.value.id, tgt.value.id)}.{tgt.attr} = "
                       + emit_expr(ast.Expression(body=st.value), names))
        elif isinstance(st, ast.AugAssign):
            tgt = st.target
            base = f"{names.get(tgt.value.id, tgt.value.id)}.{tgt.attr}"
            out.append(f"{ind}{base} = ({base} {_BIN[type(st.op)]} "
                       + emit_expr(ast.Expression(body=st.value), names) + ")")
        elif isinstance(st, ast.If):
            out.append(f"{ind}if ({emit_expr(ast.Expression(body=st.test), names)}) {{")
            for s2 in st.body:
                stmt(s2, ind + "    ")
            if st.orelse:
                out.append(f"{ind}}} else {{")
                for s2 in st.orelse:
                    stmt(s2, ind + "    ")
            out.append(f"{ind}}}")
        elif isinstance(st, ast.Pass):
            pass
        else:
            raise NotImplementedError(f"kotlin stmt: {ast.dump(st)}")

    for st in tree.body:
        stmt(st, indent)
    return "\n".join(out)
