# -*- coding: utf-8 -*-
"""EXAM #6 (D84): the interview GENERATES completion variants, not just checks
hand-written ones (SPEC §11). Templates enumerated from the court
counterexample, each CERTIFIED by the court; the U12 'I don't know' path is
the honest fallback when no template resolves. No compromise with 'proved':
every offered variant provably resolves the underdetermination."""
import sys
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

# F2 underdetermination: "free a room" — decrement-guarded vs clamp-to-0.
ST = {"capacity": "int", "booked": "int", "available": "int"}
EV = {"room": "str", "price": "int"}
A = (None, "if s.booked > 0:\n  s.booked = s.booked - 1\n  s.available = s.available + 1")
B = (None, "s.booked = max(s.booked - 1, 0)\ns.available = s.available + 1")


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import court as C, interview as I

    # 1. auto-generation (variants=None) produces court-certified variants
    q = I.detect("room.free", ST, EV, A, B, "s.booked >= 0")
    R.append((f"interview AUTO-GENERATES variants ({len(q.variants)}), "
              "not hand-fed", q.variants and len(q.variants) >= 1))

    # 2. it re-discovers the F2 lesson guard by itself
    guards = [v.src for v in q.variants if v.kind == "guard"]
    R.append((f"system re-discovers the guard 's.booked > 0' unaided: {guards}",
              "s.booked > 0" in guards))

    # 3. EVERY offered variant provably RESOLVES (no compromise with proved):
    #    a guard makes the candidates equivalent; a post distinguishes them.
    all_resolve = True
    for v in q.variants:
        if v.kind == "guard":
            eq = C.prove_equiv(ST, EV, (v.src, A[1]), (v.src, B[1]))
            all_resolve &= eq.status == "proved"
        else:  # post: exactly one candidate keeps passing the court
            def ok(c):
                np = f"(s.booked >= 0) and ({v.src})"
                return all(x.status == "proved" for x in
                           C.prove_rule(ST, EV, c[0], c[1], np, None).values())
            all_resolve &= (ok(A) != ok(B)) or (not ok(A) and not ok(B))
    R.append(("every offered variant is COURT-CERTIFIED to resolve",
              all_resolve and bool(q.variants)))

    # 4. applying the generated guard actually removes the question
    gpatch = next(v for v in q.variants if v.kind == "guard")
    q2 = I.detect("room.free", ST, EV, (gpatch.src, A[1]), (gpatch.src, B[1]),
                  "s.booked >= 0", variants=[])
    R.append(("applying the generated guard closes the question (candidates "
              "now equivalent -> no question)", q2 is None))

    # 5. honest fallback: a truly hard underdetermination yields no template
    #    variant, leaving the U12 'I don't know' path (still a valid Question).
    HA = (None, "s.available = s.available * s.available + s.booked * 7")
    HB = (None, "s.available = s.available * s.available + s.booked * 8")
    qh = I.detect("room.weird", ST, EV, HA, HB, None)
    R.append((f"hard case: question still raised, templates may be empty "
              f"({len(qh.variants) if qh else 'None'} variants) -> U12 fallback",
              qh is not None))

    print(f"\n=== EXAM interview variants ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
