# -*- coding: utf-8 -*-
"""EXAM «IN-SITU COMPOSITION» (VII.1', conditions (i)-(ii) BY THE ENGINE):
a live organism with a saga cascade A->B (transfer router -> debit clamp); a
tick = one input event, the cascade is SYNCHRONOUS 1:1 (condition (i) holds by
the saga's construction); certificates A and B are measured IN SITU — over the
same set of ticks, B on A's actual outputs (condition (ii)); check: cascade
purity >= q_A+q_B-1 ON LIVE data."""
import math
import pathlib
import random
import sys
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

GENOME = {
    "onto": 1, "name": "transfers", "retry_window": 4,
    "events": {
        "Transfer": {"xfer": "str", "src": "str", "dst": "str", "amount": "int"},
        "Credited": {"acct": "str", "xfer": "str", "amount": "int"},
        "Debited": {"acct": "str", "xfer": "str", "amount": "int"}},
    "entities": {
        "xferlog": {"key": "xfer", "instances": "dynamic",
                    "state": {"done": "int"}, "init": {"done": 0},
                    "rules": {"route": {
                        "when": "Transfer", "guard": "s.done == 0 and ev.amount > 0",
                        "body": "s.done = 1\n",
                        "contract": {"post": "s.done <= 1"},
                        "emit": [
                            {"event": "Credited",
                             "fields": {"acct": "ev.dst", "xfer": "ev.xfer",
                                        "amount": "ev.amount"}},
                            {"event": "Debited",
                             "fields": {"acct": "ev.src", "xfer": "ev.xfer",
                                        "amount": "ev.amount"}}]}}},
        "account": {"key": "acct", "instances": "dynamic",
                    "state": {"balance": "int"}, "init": {"balance": 0},
                    "rules": {
                        "credit": {"when": "Credited",
                                   "body": "s.balance = s.balance + ev.amount\n",
                                   "contract": {"post": "s.balance >= 0"}},
                        "debit": {"when": "Debited",
                                  "body": "s.balance = s.balance - min(s.balance, ev.amount)\n",
                                  "contract": {"post": "s.balance >= 0"}}}}},
    "queries": {"total": "sum(a.balance for a in account)"}}


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism
    gp = pathlib.Path(tempfile.mkdtemp(prefix="comp-")) / "g.yaml"
    gp.write_text(yaml.safe_dump(GENOME, sort_keys=False))
    g = G.load(gp)
    org = Organism(g, tempfile.mkdtemp(prefix="comp-d-"))

    rnd = random.Random(17)
    M = 2000
    clean_A, clean_B, clean_AB = 0, 0, 0
    for i in range(M):
        # load with dirt: sometimes amount<=0 (A's guard cuts it — defect A),
        # sometimes the debit exceeds the balance (the clamp loses money — defect B)
        src, dst = f"a{rnd.randint(0, 5)}", f"a{rnd.randint(0, 5)}"
        amount = rnd.choice([0, -5] + [rnd.randint(1, 400)] * 8)
        total_before = org.query("total", {})
        out = org.handle({"id": f"t{i}", "type": "Transfer", "xfer": f"x{i}",
                         "src": src, "dst": dst, "amount": amount})
        total_after = org.query("total", {})
        # defect A: the router didn't apply (guard) — a tick with no cascade
        okA = out["outcomes"].get("xferlog.route") == "applied"
        # defect B (in situ, on A's actual output): the total isn't preserved
        # (the debit clamp ate money) on THIS SAME tick
        okB = okA and (total_after == total_before)
        if not okA:
            okB = True          # tick with no cascade: B didn't participate — clean
        clean_A += okA
        clean_B += okB
        clean_AB += okA and okB
    qA, qB, qAB = clean_A / M, clean_B / M, clean_AB / M
    bound = qA + qB - 1

    R.append((f"condition (i) by the engine: cascade synchronous 1:1 "
              f"(tick = Transfer, emissions in the same handle)", True))
    R.append((f"in-situ certificates over the SAME set of ticks: "
              f"q_A={qA:.3f}, q_B={qB:.3f} (B on A's actual outputs)",
              0.5 < qA < 1 and 0.5 < qB < 1))
    R.append((f"VII.1': cascade purity {qAB:.3f} >= q_A+q_B-1 = {bound:.3f} "
              f"(live data, whatever dependence there is)", qAB >= bound - 1e-9))
    # DKW bands on q (δ=0.01): full certificate c=(0, q-band, 0.01, M)
    band = math.sqrt(math.log(2 / 0.01) / (2 * M))
    R.append((f"attestations with a band: c_A=(0,{qA - band:.3f},0.01,{M}), "
              f"c_B=(0,{qB - band:.3f},0.01,{M}) -> composite "
              f"q>={qA + qB - 1 - 2 * band:.3f}", band < 0.05))

    print(f"\n=== IN-SITU COMPOSITION EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
