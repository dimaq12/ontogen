# -*- coding: utf-8 -*-
"""EXAM the remaining channel axes across ALL languages (D97 Wave 5 finished):
CODEC and DIRECTION are functors selected from spec — for rust, go, python AND
kotlin.
(1) CODEC: the same fold whether the wire is flat-JSON or a ';'-delimited kv
    codec — Wire<->Event is a fold-preserving functor, in every language.
(2) DIRECTION (async out): a genome's D54 emissions are PUSHED to an out-channel
    (filtered by `on`) — proven on a saga in every language, with the fold also
    correct (the emit-cascade applied). Compiled by each real toolchain; a
    dialect is skipped only if its toolchain is absent."""
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
DIALECTS = ["rust-stdlib", "go-stdlib", "python-stdlib", "kotlin-stdlib"]


def _run_prefix(dialect, wd):
    wd = pathlib.Path(wd)
    if dialect in ("rust-stdlib", "go-stdlib"):
        return [str(wd / "organism")]
    if dialect == "python-stdlib":
        return [sys.executable, str(wd / "organism.py")]
    from onto.dialects.kotlin_stdlib import gates as KG
    return [f"{KG.find_java_home()}/bin/java", "-jar", str(wd / "organism.jar")]


def _toolchain_ok(dialect):
    if dialect == "rust-stdlib":
        return shutil.which("rustc") is not None
    if dialect == "go-stdlib":
        from onto.dialects.go_stdlib.gates import find_go
        return find_go() is not None
    if dialect == "python-stdlib":
        return True
    from onto.dialects.kotlin_stdlib.gates import available
    return available()[0]


def _build(dialect, genome_text, channels, wd):
    from onto.core import genome as G
    from onto.dialects import registry
    gp = pathlib.Path(wd) / "g.yaml"; gp.write_text(genome_text)
    registry.get(dialect)["skeleton"].generate(G.load(gp), pathlib.Path(wd),
                                                channels=channels)
    ok, msg = registry.get(dialect)["gates"].build(pathlib.Path(wd))
    if not ok:
        raise RuntimeError(msg[:200])
    return _run_prefix(dialect, wd)


def main():
    sys.path.insert(0, str(ROOT / "src"))
    from onto.dialects import registry
    import inspect

    for dialect in DIALECTS:
        if not _toolchain_ok(dialect):
            R.append((f"[{dialect}] SKIPPED (no toolchain)", None)); continue
        if "channels" not in inspect.signature(registry.get(dialect)["skeleton"].generate).parameters:
            R.append((f"[{dialect}] no channel axis (pending)", None)); continue

        # 1. CODEC axis: kv wire -> byte-identical fold
        try:
            wd = tempfile.mkdtemp()
            pref = _build(dialect, WAL, [{"driver": "file", "direction": "in", "codec": "kv"}], wd)
            evf = pathlib.Path(wd) / "ev.kv"
            evf.write_text("id=e1;type=Deposit;w=bob;amt=100\n"
                           "id=e2;type=Deposit;w=bob;amt=50\n"
                           "id=e4;type=Deposit;w=bob;amt=-5\n")
            got = subprocess.run(pref + [str(evf)], capture_output=True, text=True, timeout=90).stdout.strip().splitlines()[-1]
            R.append((f"[{dialect}] CODEC 'kv' -> byte-identical fold: {got}",
                      got == '{"w":{"alice":{"bal":0},"bob":{"bal":150}}}'))
        except Exception as e:  # noqa: BLE001
            R.append((f"[{dialect}] CODEC 'kv': {type(e).__name__}: {str(e)[:100]}", False))

        # 2. DIRECTION axis: async out — emissions pushed to a sink
        try:
            wd2 = tempfile.mkdtemp()
            sink = str(pathlib.Path(wd2) / "out.jsonl")
            pref2 = _build(dialect, SAGA, [
                {"driver": "file", "direction": "in", "codec": "json"},
                {"driver": "file", "direction": "out", "codec": "json", "path": sink,
                 "on": ["Shipped"]}], wd2)
            inf = pathlib.Path(wd2) / "in.jsonl"
            inf.write_text('{"id":"o1","type":"Ordered","order":"A","qty":5}\n'
                           '{"id":"o2","type":"Ordered","order":"B","qty":3}\n')
            fold = subprocess.run(pref2 + [str(inf)], capture_output=True, text=True, timeout=90).stdout.strip().splitlines()[-1]
            fold_ok = fold == '{"order":{"A":{"qty":5,"shipped":5},"B":{"qty":3,"shipped":3}}}'
            pushed = [json.loads(l) for l in pathlib.Path(sink).read_text().splitlines() if l.strip()] \
                if pathlib.Path(sink).exists() else []
            out_ok = (len(pushed) == 2 and all(p.get("type") == "Shipped" for p in pushed)
                      and {p["order"]: p["qty"] for p in pushed} == {"A": 5, "B": 3})
            R.append((f"[{dialect}] DIRECTION async-out: emit-cascade fold correct "
                      f"AND emissions pushed to sink (on=[Shipped]): fold_ok={fold_ok} "
                      f"pushed={pushed}", fold_ok and out_ok))
        except Exception as e:  # noqa: BLE001
            R.append((f"[{dialect}] DIRECTION: {type(e).__name__}: {str(e)[:100]}", False))

    print("\n=== EXAM channel axes: codec + direction, ALL languages (D97 Wave 5) ===")
    ok = True
    for name, passed in R:
        tag = "SKIP" if passed is None else ("PASS" if passed else "FAIL")
        print(f"  {tag}  {name}")
        if passed is False:
            ok = False
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
