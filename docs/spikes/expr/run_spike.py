# -*- coding: utf-8 -*-
"""Run of the Expr spike: A (py-ast) full cycle; B (lark) and C (cel) — parse depth.

Test corpus — LIVE expressions from v0 genomes (booking, exchange):
  E1 post:      s.available >= 0 and s.available <= s.capacity
  E2 invariant: sum(r.booked for r in room) == sum(1 for r in reservation if r.active == 1)
  E3 property:  all(t.qty > 0 for t in out)
Plus an F2-level SMT task: prove that the reserve body preserves post (and catch a mutant).
"""
import a_pyast as A

ENV = {
    "s": {"available": "int", "capacity": "int", "booked": "int"},
    "room": A.TList({"booked": "int"}),
    "reservation": A.TList({"active": "int"}),
    "out": A.TList({"qty": "int"}),
}
E1 = "s.available >= 0 and s.available <= s.capacity"
E2 = "sum(r.booked for r in room) == sum(1 for r in reservation if r.active == 1)"
E3 = "all(t.qty > 0 for t in out)"

print("=== A: python-ast subset ===")
for name, src in (("E1", E1), ("E2", E2), ("E3", E3)):
    t = A.parse(src)
    ty = A.typecheck(t, ENV)
    print(f"{name} [{ty}] go:  {A.to_go(t)[:100]}")
    print(f"   py:  {A.to_python(t)}")

# rejections: foreign node, field typo, wrong type
for bad, why in (("__import__('os')", "call outside the list"),
                 ("s.availble >= 0", "field typo"),
                 ("s.available and 3", "type")):
    try:
        A.typecheck(A.parse(bad), ENV)
        print("PASSED (BAD):", bad)
    except Exception as e:
        print(f"rejected ok ({why}): {type(e).__name__}: {str(e)[:80]}")

# --- SMT: F2-level judgment on E1 + mutant -----------------------------------
import z3
av, cap, q = z3.Ints("av cap q")
state = {"available": av, "capacity": cap, "booked": cap - av}
post = A.to_z3(A.parse(E1), {"s": state})
# reference reserve body: if booked < capacity: available' = available-1 (guard)
booked = cap - av
av2_ref = z3.If(booked < cap, av - 1, av)
# mutant: no guard (clamp removed)
av2_mut = av - 1
def prove_post(av2, label):
    s = z3.Solver()
    pre = A.to_z3(A.parse(E1), {"s": {"available": av, "capacity": cap}})
    s.add(pre, cap > 0)
    s.add(z3.Not(A.to_z3(A.parse(E1), {"s": {"available": av2, "capacity": cap}})))
    r = s.check()
    verdict = "PROVEN (post preserved)" if r == z3.unsat else f"COUNTEREXAMPLE: {s.model()}"
    print(f"SMT {label}: {verdict}")
prove_post(av2_ref, "reference reserve")
prove_post(av2_mut, "mutant (guard removed)")

# SMT on an aggregate (bounded, 3 rooms) — E2 as a formula
rooms = [{"booked": z3.Int(f"b{i}")} for i in range(3)]
resv = [{"active": z3.Int(f"a{i}")} for i in range(3)]
inv = A.to_z3(A.parse(E2), {"room": rooms, "reservation": resv})
s = z3.Solver(); s.add(z3.Not(inv))
print("SMT E2 (bounded): invariant is FALSIFIABLE (expected), example:",
      "exists" if s.check() == z3.sat else "none")

print("\n=== B: lark (custom grammar) — parse depth ===")
try:
    import lark
    GRAMMAR = r"""
    ?expr: orx
    ?orx: andx ("or" andx)*
    ?andx: cmp ("and" cmp)*
    ?cmp: sum_ (CMPOP sum_)?
    ?sum_: prod (ADDOP prod)*
    ?prod: atom (MULOP atom)*
    ?atom: NUMBER | field | agg | "(" expr ")" | "not" atom -> notx
    field: NAME ("." NAME)*
    agg: AGGNAME "(" NAME ":" expr "for" NAME "in" field ")"   // custom lambda form
    AGGNAME: "sum"|"all"|"any"
    CMPOP: ">="|"<="|"=="|"!="|">"|"<"
    ADDOP: "+"|"-"
    MULOP: "*"|"//"|"%"
    %import common.CNAME -> NAME
    %import common.NUMBER
    %ignore " "
    """
    parser = lark.Lark(GRAMMAR, start="expr")
    tree = parser.parse("s.available >= 0 and s.available <= s.capacity")
    print("B parse E1: ok,", tree.data)
    print("B: custom grammar 25 lines; typecheck/printers/SMT — write it all ourselves,")
    print("   AND OWN the grammar (versioning is ours — against D4).")
except Exception as e:
    print("B FAIL:", type(e).__name__, str(e)[:120])

print("\n=== C: cel-python — parse depth ===")
try:
    import celpy
    cel_env = celpy.Environment()
    cel_ast = cel_env.compile("s.available >= 0 && s.available <= s.capacity")
    prog = cel_env.program(cel_ast)
    out = prog.evaluate({"s": celpy.json_to_cel({"available": 2, "capacity": 3})})
    print("C parse+eval E1: ok ->", out)
    cel3 = cel_env.compile("out.all(t, t.qty > 0)")
    print("C all macro: ok (CEL syntax: out.all(t, ...))")
    try:
        cel_env.compile("room.map(r, r.booked).sum()")
        print("C sum: exists?!")
    except Exception as e2:
        print("C sum: NOT in CEL (a custom function is needed) —", type(e2).__name__)
    print("C: celpy AST — internal (lark tree), typecheck/printers on top — write")
    print("   ourselves over a FOREIGN structure; error messages — CEL's, English.")
except Exception as e:
    print("C FAIL:", type(e).__name__, str(e)[:150])
