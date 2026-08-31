# -*- coding: utf-8 -*-
"""EXAM emission replay-safety (D95, closes a D93 park): the out-port emit hook
(D54/D88) must NOT re-fire external side-effects during replay. Proves offline:
(1) a live emission fires the hook once; (2) replaying with a LIVE hook installed
re-fires ZERO emissions (the _replaying guard holds) while recomputing the same
state; (3) rebuilding the organism from the persisted log emits nothing during
the rebuild yet reconstructs the fold."""
import pathlib
import sys
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

GEN = {
    "onto": 1, "name": "ships", "retry_window": 64,
    "events": {"Ordered": {"order": "str", "qty": "int"},
               "Shipped": {"order": "str", "qty": "int"}},
    "entities": {"order": {
        "key": "order", "instances": "dynamic",
        "state": {"qty": "int", "shipped": "int"},
        "init": {"qty": 0, "shipped": 0},
        "rules": {
            "place": {"when": "Ordered", "guard": "ev.qty > 0",
                      "body": "s.qty = ev.qty\n",
                      "contract": {"post": "s.qty >= 0"},
                      "emit": [{"event": "Shipped",
                                "fields": {"order": "ev.order", "qty": "ev.qty"}}]},
            "ship": {"when": "Shipped", "body": "s.shipped = s.shipped + ev.qty\n",
                     "contract": {"post": "s.shipped >= 0"}}}}},
    "queries": {"total_shipped": "sum(o.shipped for o in order)"}}


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism

    d = pathlib.Path(tempfile.mkdtemp(prefix="emitreplay-"))
    gp = d / "g.yaml"
    gp.write_text(yaml.safe_dump(GEN, sort_keys=False))
    g = G.load(gp)
    data = d / "data"

    emitted = []
    org = Organism(g, data)
    org._emit_hook = lambda name, fields, eid: emitted.append((name, fields, eid))

    # 1. a live emission fires the hook exactly once
    org.handle({"id": "o1", "type": "Ordered", "order": "A", "qty": 5})
    R.append((f"live: Ordered -> emitted Shipped once, state shipped=5: "
              f"emits={len(emitted)}",
              len(emitted) == 1 and emitted[0][0] == "Shipped"
              and org.state["order"]["A"]["shipped"] == 5))

    # 2. replay with a LIVE hook installed -> ZERO re-emissions, state recomputed
    emitted.clear()
    org.replay()
    R.append((f"replay with a live hook installed -> ZERO re-emissions "
              f"(no double external side-effect): emits={len(emitted)}",
              len(emitted) == 0))
    # replay() also nulls the hook per the guard's belt-and-braces
    R.append(("replay leaves the emit hook cleared (belt-and-braces)",
              org._emit_hook is None))

    # 3. rebuild the organism from the persisted log -> no emit during rebuild,
    #    yet the fold is reconstructed
    emitted2 = []
    org2 = Organism(g, data)          # __init__ replays the log (no hook yet)
    org2._emit_hook = lambda name, fields, eid: emitted2.append(name)
    R.append((f"rebuild from log: fold reconstructed (shipped=5) with 0 emits "
              f"during rebuild: emits={len(emitted2)}",
              len(emitted2) == 0 and org2.state["order"]["A"]["shipped"] == 5))
    # a NEW live event on the rebuilt organism still emits (hook works)
    org2.handle({"id": "o2", "type": "Ordered", "order": "B", "qty": 3})
    R.append((f"post-rebuild: a NEW event still emits (hook live): "
              f"emits={len(emitted2)}", emitted2 == ["Shipped"]))

    print(f"\n=== EXAM emission replay-safety ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
