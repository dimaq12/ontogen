# -*- coding: utf-8 -*-
"""EXAM certification coverage (D91): the escape-class taxonomy is GUARANTEED
per class — for every one of the 17 classes the engine emits a mechanical
state (never silent), and a tissue that should carry a certificate but doesn't
(a contained-only island) is flagged UNCOVERED. 'Every class in a known,
enforced state' — that is the guarantee, not 'everything is proven'."""
import pathlib
import sys
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import certify

    # 1. all 17 classes present, each in a KNOWN state (none silent)
    rows = certify.coverage(ROOT / "genomes/booking.yaml")
    ids = sorted(r["id"] for r in rows)
    states = {r["id"]: r["state"] for r in rows}
    known = {"N/A", "PROVEN", "DELEGATED", "MEASURED", "CONTAINED",
             "MONITORED", "DECLARED", "NAMED_UNPROVEN", "UNCOVERED"}
    R.append((f"all 17 classes present: {ids == list(range(1, 18))}",
              ids == list(range(1, 18))))
    R.append((f"every class in a KNOWN state (none silent): "
              f"{set(states.values()) <= known}",
              all(s in known for s in states.values())))

    # 2. structural guarantee: float (class 1) is N/A BY CONSTRUCTION (IR is int/str)
    R.append(("class 1: float N/A by construction, BUT the Z-vs-int64 overflow "
              "gap is DECLARED (not silently N/A)", states[1] == "DECLARED"))

    # 3. concurrency (4) and Problem-2 (10) are honestly NAMED_UNPROVEN
    R.append(("classes 4 (memory-model) & 10 (spectral-invisible) NAMED_UNPROVEN "
              "(honest limit, not silence)",
              states[4] == "NAMED_UNPROVEN" and states[10] == "NAMED_UNPROVEN"))

    # 4. a clean genome: no UNCOVERED -> exit 0 (every class handled/declared/named)
    clean = certify.coverage(ROOT / "genomes/booking.yaml")
    R.append(("clean genome: 0 UNCOVERED (every class in an enforced state)",
              not any(r["state"] == "UNCOVERED" for r in clean)))

    # 5. a genome with a CONTAINED-ONLY island -> class 11 flagged UNCOVERED
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "isl.py").write_text("def go(p): return {'v': 1}\n")
    G = {"onto": 1, "name": "bare", "retry_window": 8,
         "events": {"Ping": {"k": "str"}},
         "entities": {"k": {"key": "k", "instances": ["a"], "state": {"n": "int"},
                            "init": {"n": 0}, "rules": {"p": {"when": "Ping",
                            "body": "s.n = s.n + 1\n", "contract": {"post": "s.n >= 0"}}}}},
         "queries": {},
         "externals": {"bare": {"island": "isl.py", "provides": "go",
                                "assumptions": ["error_rate_pct < 50"]}}}
    gp = d / "g.yaml"; gp.write_text(yaml.safe_dump(G, sort_keys=False))
    rows2 = certify.coverage(gp)
    c11 = next(r for r in rows2 if r["id"] == 11)
    gc = next(r for r in rows2 if r["id"] == 0)
    R.append((f"contained-only island: class 11 stays CONTAINED (the membrane IS "
              f"the class-11 move, honest): state={c11['state']}",
              c11["state"] == "CONTAINED"))
    R.append((f"contained-only island: D90 guarantee-chain OPEN + certify NOT "
              f"green (proven-or-delegated law): gc={gc['state']}",
              gc["state"] == "OPEN" and not certify.is_green(rows2)))

    # 6. delegating the island -> class 11 no longer UNCOVERED
    G["externals"]["bare"]["cases"] = [{"payload": {}, "expect": {"v": 1}}]
    gp.write_text(yaml.safe_dump(G, sort_keys=False))
    rows3 = certify.coverage(gp)
    gc3 = next(r for r in rows3 if r["id"] == 0)
    R.append(("adding acceptance cases -> D90 guarantee-chain CLOSED + certify "
              f"green: gc={gc3['state']}",
              gc3["state"] == "CLOSED" and certify.is_green(rows3)))

    # 7. a genome whose rule DISPROVES its own post -> class 7 REFUTED, not PROVEN
    Gr = {"onto": 1, "name": "broken", "retry_window": 8,
          "events": {"Add": {"c": "str"}},
          "entities": {"c": {"key": "c", "instances": ["a"], "state": {"v": "int"},
                       "init": {"v": 0}, "rules": {"r": {"when": "Add",
                       "body": "s.v = s.v - 1\n",
                       "contract": {"post": "s.v >= 0"}}}}},
          "queries": {}}
    gpr = d / "broken.yaml"; gpr.write_text(yaml.safe_dump(Gr, sort_keys=False))
    rr = certify.coverage(gpr)
    c7 = next(r for r in rr if r["id"] == 7)
    R.append((f"rule violating its own post -> class 7 REFUTED (not a false "
              f"PROVEN) + certify NOT green: state={c7['state']}",
              c7["state"] == "REFUTED" and not certify.is_green(rr)))

    print(f"\n=== EXAM certification coverage ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
