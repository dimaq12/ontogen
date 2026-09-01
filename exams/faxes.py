# -*- coding: utf-8 -*-
"""EXAM the remaining channel axes (D97 Wave 5, rust reference): CODEC and
DIRECTION are functors selected from spec, not hardcoded.
(1) CODEC: the same fold is reached whether the wire is flat-JSON or a ';'-
    delimited key=value ('kv') codec — Wire<->Event is a fold-preserving functor.
(2) DIRECTION (async out): a genome with a D54 emission + an out-channel PUSHES
    the emitted event to a sink (filtered by `on`) — the async half of the axis.
Compiled by real rustc; skips cleanly if absent."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

WAL = """onto: 1
name: wal
retry_window: 8
events: {Deposit: {w: str, amt: int}}
entities:
  w: {key: w, instances: [bob, alice], state: {bal: int}, init: {bal: 0},
      rules: {dep: {when: Deposit, guard: "ev.amt > 0",
                    body: "s.bal = s.bal + ev.amt\\n", contract: {post: "s.bal >= 0"}}}}
queries: {}
"""
SAGA = """onto: 1
name: ships
retry_window: 64
events: {Ordered: {order: str, qty: int}, Shipped: {order: str, qty: int}}
entities:
  order: {key: order, instances: dynamic, state: {qty: int, shipped: int},
          init: {qty: 0, shipped: 0},
          rules: {place: {when: Ordered, guard: "ev.qty > 0", body: "s.qty = ev.qty\\n",
                          contract: {post: "s.qty >= 0"},
                          emit: [{event: Shipped, fields: {order: "ev.order", qty: "ev.qty"}}]},
                  ship: {when: Shipped, body: "s.shipped = s.shipped + ev.qty\\n",
                         contract: {post: "s.shipped >= 0"}}}}
queries: {}
"""


def _mat(genome_text, channels, wd):
    from onto.core import genome as G
    from onto.dialects import registry
    gp = pathlib.Path(wd) / "g.yaml"; gp.write_text(genome_text)
    registry.get("rust-stdlib")["skeleton"].generate(G.load(gp), pathlib.Path(wd),
                                                      channels=channels)
    ok, msg = registry.get("rust-stdlib")["gates"].build(pathlib.Path(wd))
    if not ok:
        raise RuntimeError(msg)
    return str(pathlib.Path(wd) / "organism")


def main():
    sys.path.insert(0, str(ROOT / "src"))
    if shutil.which("rustc") is None:
        print("=== EXAM channel axes (codec/direction): SKIPPED (no rustc) ===\nVERDICT: SKIPPED")
        return 0

    # 1. CODEC axis: kv wire -> byte-identical fold
    wd = tempfile.mkdtemp()
    binp = _mat(WAL, [{"driver": "file", "direction": "in", "codec": "kv"}], wd)
    evf = pathlib.Path(wd) / "ev.kv"
    evf.write_text("id=e1;type=Deposit;w=bob;amt=100\n"
                   "id=e2;type=Deposit;w=bob;amt=50\n"
                   "id=e4;type=Deposit;w=bob;amt=-5\n")   # guard blocks -5
    got = subprocess.run([binp, str(evf)], capture_output=True, text=True, timeout=60).stdout.strip()
    want = '{"w":{"alice":{"bal":0},"bob":{"bal":150}}}'
    R.append((f"CODEC axis: 'kv' wire (key=value;...) -> byte-identical fold "
              f"(same as json): {got}", got == want))

    # 2. DIRECTION axis: async out — emissions pushed to a sink, filtered by `on`
    wd2 = tempfile.mkdtemp()
    sink = str(pathlib.Path(wd2) / "out.jsonl")
    binp2 = _mat(SAGA, [
        {"driver": "file", "direction": "in", "codec": "json"},
        {"driver": "file", "direction": "out", "codec": "json", "path": sink,
         "on": ["Shipped"]}], wd2)
    inf = pathlib.Path(wd2) / "in.jsonl"
    inf.write_text('{"id":"o1","type":"Ordered","order":"A","qty":5}\n'
                   '{"id":"o2","type":"Ordered","order":"B","qty":3}\n')
    fold = subprocess.run([binp2, str(inf)], capture_output=True, text=True, timeout=60).stdout.strip()
    R.append((f"DIRECTION: fold from the in-channel correct (cascade qty->shipped): "
              f"{fold}",
              fold == '{"order":{"A":{"qty":5,"shipped":5},"B":{"qty":3,"shipped":3}}}'))
    pushed = [json.loads(l) for l in pathlib.Path(sink).read_text().splitlines() if l.strip()] \
        if pathlib.Path(sink).exists() else []
    ok_out = (len(pushed) == 2
              and all(p["type"] == "Shipped" for p in pushed)
              and {p["order"]: p["qty"] for p in pushed} == {"A": 5, "B": 3})
    R.append((f"DIRECTION (async out): emissions PUSHED to the sink, filtered by "
              f"`on`=[Shipped]: {pushed}", ok_out))

    print("\n=== EXAM channel axes: codec + direction (D97 Wave 5 / rust) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
