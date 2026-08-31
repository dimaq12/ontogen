# -*- coding: utf-8 -*-
"""EXAM PORTS (D88): transport is a configurable, NATIVE functor on the I/O
boundary — not glue. Many different beasts (sync HTTP + async queue) over ONE
organism, all projections of the SAME fold, certified by fold-parity. Async
runs async; the web/out beast retries; delivery is a membrane (drift->REVOKE).
Dependency-free: an in-process Bus stands in for Kafka; a real broker is a
grown adapter with the same interface."""
import json
import pathlib
import sys
import tempfile
import threading
import time
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

# a genome with a SAGA: Ordered -> emits Shipped (a derived event that flies out)
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
    from onto.ports.base import Bus, fold_parity

    gp = pathlib.Path(tempfile.mkdtemp(prefix="ports-")) / "g.yaml"
    gp.write_text(yaml.safe_dump(GEN, sort_keys=False))
    fp = gp.parent / "flows.yaml"
    fp.write_text(yaml.safe_dump({"flows": {"f": [
        {"post": {"id": "o1", "type": "Ordered", "order": "A", "qty": 5}},
        {"post": {"id": "o2", "type": "Ordered", "order": "B", "qty": 3}},
    ]}}, sort_keys=False))
    g = G.load(gp)

    # ---- 1. FOLD PARITY across two DIFFERENT beasts (http-in vs queue-in)
    def drive_http(events):
        org = Organism(g, tempfile.mkdtemp())
        from onto.core.serve import make_server
        srv = make_server(org, port=8801)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        for _ in range(100):
            try:
                urllib.request.urlopen("http://127.0.0.1:8801/health", timeout=2); break
            except Exception:
                time.sleep(0.03)
        for ev in events:
            urllib.request.urlopen(urllib.request.Request(
                "http://127.0.0.1:8801/event", data=json.dumps(ev).encode(),
                headers={"Content-Type": "application/json"}), timeout=5)
        srv.shutdown()
        return org.snapshot()

    def drive_queue(events):
        org = Organism(g, tempfile.mkdtemp())
        bus = Bus()
        lock = threading.Lock()
        from onto.ports.queue import QueuePort
        pin = QueuePort({"name": "in", "kind": "queue", "direction": "in",
                         "topic": "orders"}, org, bus, lock)
        pin.start()
        for ev in events:
            bus.publish("orders", ev)
        for _ in range(100):                       # async — wait for drain
            if org.counters.get("applied", 0) >= len(events):
                break
            time.sleep(0.03)
        time.sleep(0.1)
        bus.stop()
        return org.snapshot()

    parity = fold_parity(gp, fp, drive_http, drive_queue, ROOT)
    R.append(("FOLD PARITY across HTTP-in and async queue-in: byte-identical "
              f"({'certified' if parity is None else parity})", parity is None))

    # ---- 2. ASYNC OUT is real: emitted Shipped flies to a queue topic
    org = Organism(g, tempfile.mkdtemp())
    bus = Bus()
    lock = threading.Lock()
    received = []
    bus.subscribe("shipped_out", lambda m: received.append(m))
    from onto.ports.queue import QueuePort
    pin = QueuePort({"name": "in", "kind": "queue", "direction": "in",
                     "topic": "orders_in"}, org, bus, lock)
    pout = QueuePort({"name": "out", "kind": "queue", "direction": "out",
                      "on": ["Shipped"], "to": "shipped_out", "retries": 3},
                     org, bus, lock)
    pin.start(); pout.start()
    bus.publish("orders_in", {"id": "x1", "type": "Ordered", "order": "Z", "qty": 7})
    for _ in range(100):
        if received:
            break
        time.sleep(0.03)
    R.append((f"ASYNC OUT native: emitted 'Shipped' flew to the queue topic "
              f"({len(received)} msg, qty={received[0]['qty'] if received else '?'})",
              len(received) == 1 and received[0]["type"] == "Shipped"
              and received[0]["qty"] == 7))
    R.append(("many ports over ONE fold: in+out projections consistent "
              "(order Z shipped=7)",
              org.state["order"]["Z"]["shipped"] == 7))

    # ---- 3. WEB/OUT WITH RETRIES: flaky sink -> retries -> delivered
    org2 = Organism(g, tempfile.mkdtemp())
    bus2 = Bus(); lock2 = threading.Lock()
    delivered = []
    flaky = {"n": 0}

    def flaky_send(msg):
        flaky["n"] += 1
        if flaky["n"] <= 2:                        # fail first 2 attempts
            raise RuntimeError("broker down")
        delivered.append(msg)
    pin2 = QueuePort({"name": "in", "kind": "queue", "direction": "in",
                      "topic": "in2"}, org2, bus2, lock2)
    pout2 = QueuePort({"name": "out", "kind": "queue", "direction": "out",
                       "on": ["Shipped"], "to": "out2", "retries": 5}, org2, bus2, lock2)
    pout2._send = flaky_send
    pin2.start(); pout2.start()
    bus2.publish("in2", {"id": "y1", "type": "Ordered", "order": "Q", "qty": 2})
    for _ in range(100):
        if delivered:
            break
        time.sleep(0.03)
    R.append((f"WEB/ASYNC WITH RETRIES: flaky sink -> delivered after retries "
              f"(retries={pout2.stats['retries']}, delivered={pout2.stats['delivered']})",
              len(delivered) == 1 and pout2.stats["retries"] >= 2
              and pout2.cert_valid))

    # ---- 4. MEMBRANE: dead sink -> drift -> REVOKE
    org3 = Organism(g, tempfile.mkdtemp())
    bus3 = Bus(); lock3 = threading.Lock()
    pin3 = QueuePort({"name": "in", "kind": "queue", "direction": "in",
                      "topic": "in3"}, org3, bus3, lock3)
    pout3 = QueuePort({"name": "out", "kind": "queue", "direction": "out",
                       "on": ["Shipped"], "to": "out3", "retries": 1,
                       "quota": 3}, org3, bus3, lock3)
    pout3._send = lambda m: (_ for _ in ()).throw(RuntimeError("dead"))
    pin3.start(); pout3.start()
    for i in range(6):
        bus3.publish("in3", {"id": f"d{i}", "type": "Ordered",
                             "order": f"O{i}", "qty": 1})
    for _ in range(120):
        if not pout3.cert_valid:
            break
        time.sleep(0.03)
    led = (org3.data / "ledger.jsonl")
    revoked = "port_trust_revoked" in led.read_text() if led.exists() else False
    R.append((f"MEMBRANE: dead sink -> REVOKE (cert_valid={pout3.cert_valid}, "
              f"ledger port_trust_revoked={revoked})",
              not pout3.cert_valid and revoked))

    # ---- 4b. after REVOKE the port DROPS emissions (D95): it no longer even
    #          attempts _send — REVOKE is a real gate, not just a flag
    attempts_before = pout3.stats.get("failed", 0)
    sent = []
    pout3._send = lambda m: sent.append(m)   # would succeed IF attempted
    for _ in range(50):
        pin3_ok = True
        bus3.publish("in3", {"id": "post-revoke", "type": "Ordered",
                             "order": "Z", "qty": 1})
        if pout3.stats.get("dropped_revoked", 0) > 0:
            break
        time.sleep(0.02)
    R.append((f"post-REVOKE: emissions DROPPED not attempted "
              f"(dropped_revoked={pout3.stats.get('dropped_revoked', 0)}, "
              f"_send calls={len(sent)}, failed unchanged={pout3.stats.get('failed', 0) == attempts_before})",
              pout3.stats.get("dropped_revoked", 0) >= 1 and len(sent) == 0
              and pout3.stats.get("failed", 0) == attempts_before))

    for b in (bus, bus2, bus3):
        b.stop()

    print(f"\n=== EXAM PORTS ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
