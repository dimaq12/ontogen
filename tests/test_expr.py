# -*- coding: utf-8 -*-
"""Expr: parsing/typecheck/interpreter/bodies/limits."""
import pytest

from onto.core import expr as E

ENV = {"s": {"a": "int", "b": "int"}, "ev": {"q": "int", "who": "str"},
       "items": E.TList({"x": "int"})}


def ev(src, env_vals):
    return E.eval_expr(E.parse_expr(src), env_vals)


def test_eval_basics():
    assert ev("s.a + s.b * 2", {"s": {"a": 1, "b": 3}}) == 7
    assert ev("ev.who == 'bob'", {"ev": {"who": "bob"}}) is True
    assert ev("sum(i.x for i in items if i.x > 0)", {"items": [{"x": 2}, {"x": -1}, {"x": 3}]}) == 5


def test_typecheck_rejects():
    with pytest.raises(E.ExprError, match="no field"):
        E.typecheck_expr(E.parse_expr("s.aa > 0"), ENV)
    with pytest.raises(E.ExprError, match="str allows only"):
        E.typecheck_expr(E.parse_expr("ev.who > 'a'"), ENV)
    with pytest.raises(E.ExprError, match="outside whitelist"):
        E.parse_expr("__import__('os')")


def test_division_by_zero_is_eval_error():
    with pytest.raises(E.EvalError, match="division by zero"):
        ev("s.a // s.b", {"s": {"a": 1, "b": 0}})


def test_body_exec_and_limits():
    body = E.parse_body("if ev.q > 0:\n  s.a = s.a + ev.q\nelse:\n  pass")
    E.typecheck_body(body, {"a": "int"}, {"q": "int"})
    assert E.exec_body(body, {"a": 1}, {"q": 5}) == {"a": 6}
    assert E.exec_body(body, {"a": 1}, {"q": -1}) == {"a": 1}
    with pytest.raises(E.ExprError, match="this is a skill"):
        E.parse_body("s.a = " + " + ".join(["ev.q"] * 140))   # cap 256 (D52)
    with pytest.raises(E.ExprError, match="target must be"):
        E.parse_body("x = 1")
    with pytest.raises(E.ExprError, match="outside body subset"):
        E.parse_body("for i in range(3):\n  pass")
