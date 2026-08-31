# -*- coding: utf-8 -*-
"""EXAM growport (D89): the transport tissue is GROWN, not hand-written — like
dialects/islands. Declare the beast (intent + cases); the model writes the wire
codec; the gate certifies it by ROUND-TRIP + FOLD-PARITY (the same certificate
as growdialect/D48). Offline-provable on the in-process Bus (a real broker is
the same codec behind a driver swap). Network exam (SLM); cached like fisland."""
import pathlib
import sys
import tempfile
import threading
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

GEN = {"onto": 1, "name": "ships", "retry_window": 64,
       "events": {"Ordered": {"order": "str", "qty": "int"},
                  "Shipped": {"order": "str", "qty": "int"}},
       "entities": {"order": {
           "key": "order", "instances": "dynamic",
           "state": {"qty": "int", "shipped": "int"}, "init": {"qty": 0, "shipped": 0},
           "rules": {
               "place": {"when": "Ordered", "guard": "ev.qty > 0",
                         "body": "s.qty = ev.qty\n", "contract": {"post": "s.qty >= 0"},
                         "emit": [{"event": "Shipped",
                                   "fields": {"order": "ev.order", "qty": "ev.qty"}}]},
               "ship": {"when": "Shipped", "body": "s.shipped = s.shipped + ev.qty\n",
                        "contract": {"post": "s.shipped >= 0"}}}}},
       "queries": {}}

# a NON-trivial wire format the model must reverse-engineer into a codec:
# an envelope {op, id, payload:{fields}} — different from the canonical shape.
SPEC = {"name": "envelope", "direction": "in", "topic": "orders",
        "intent": ("The wire message is an envelope: {'op': <event type>, "
                   "'id': <event id>, 'payload': {<field>: <value>, ...}}. "
                   "decode turns it into the canonical event "
                   "{'id':..., 'type': op, **payload}; encode reverses it."),
        "cases": [
            {"wire": {"op": "Ordered", "id": "o1", "payload": {"order": "A", "qty": 5}},
             "event": {"id": "o1", "type": "Ordered", "order": "A", "qty": 5}},
            {"wire": {"op": "Shipped", "id": "s1", "payload": {"order": "B", "qty": 2}},
             "event": {"id": "s1", "type": "Shipped", "order": "B", "qty": 2}}]}


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growport
    from onto.ribosome import Provider
    d = pathlib.Path(tempfile.mkdtemp(prefix="growport-"))
    gp = d / "g.yaml"; gp.write_text(yaml.safe_dump(GEN, sort_keys=False))
    fp = d / "f.yaml"
    fp.write_text(yaml.safe_dump({"flows": {"f": [
        {"post": {"id": "o1", "type": "Ordered", "order": "A", "qty": 5}},
        {"post": {"id": "o2", "type": "Ordered", "order": "C", "qty": 9}}]}},
        sort_keys=False))

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_growport.jsonl"
    tele = growport.grow(SPEC, gp, fp, provider, ROOT, out_dir=d)
    n = len(tele["attempts"])
    R.append((f"port codec GROWN by the model [{tele.get('model')}, "
              f"{n} attempts{', cache' if tele.get('cache') else ''}]",
              not tele["island"]))
    if tele["island"]:
        print(tele)
        return _report(t0)

    # the grown codec is CERTIFIED: round-trip + fold-parity (re-check)
    codec_path = d / "envelope.py"
    v = growport.gates(codec_path.read_text(), SPEC, gp, fp, ROOT)
    R.append(("grown codec GATE-PASSED (round-trip + fold-parity on the given cases+flows; fuzz-thin, skill-level assurance, NOT a proof for all wire inputs)", v is None))

    # and it PLUGS IN as a real port: wire envelopes drive the organism
    from onto.core import genome as G
    from onto.core.organism import Organism
    from onto.ports.base import Bus
    from onto.ports.queue import QueuePort
    g = G.load(gp)
    org = Organism(g, tempfile.mkdtemp())
    bus = Bus(); lock = threading.Lock()
    port = QueuePort({"name": "in", "kind": "queue", "direction": "in",
                      "topic": "orders", "codec": str(codec_path)}, org, bus, lock)
    port.start()
    bus.publish("orders", {"op": "Ordered", "id": "w1",
                           "payload": {"order": "W", "qty": 4}})
    for _ in range(100):
        if org.state.get("order", {}).get("W"):
            break
        time.sleep(0.03)
    bus.stop()
    R.append(("grown codec plugs into a live port: wire envelope -> organism "
              f"(order W qty={org.state.get('order', {}).get('W', {}).get('qty')})",
              org.state.get("order", {}).get("W", {}).get("qty") == 4))

    return _report(t0)


def _report(t0):
    print(f"\n=== EXAM growport ({time.time()-t0:.0f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
