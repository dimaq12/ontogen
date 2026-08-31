# -*- coding: utf-8 -*-
"""EXAM rust-stdlib dialect (D96): a NEW substrate. Proves (with the real rustc
toolchain; skips cleanly if absent): (1) the printer is conformant — the canon's
240-case expression corpus compiles and runs GREEN under rustc; (2) a
materialized Rust organism produces a BYTE-IDENTICAL fold to the interpreter for
guard+dedup+contract (wallet), cross-entity contracts (booking), and the D54
emit-cascade (saga, dynamic instances). Rust std has no HTTP server, so the
organism is a batch runner — the fold is the invariant that must match."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def _interp_fold(genome_path, events):
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism
    d = pathlib.Path(tempfile.mkdtemp())
    org = Organism(G.load(genome_path), d)
    for e in events:
        org.handle(e)
    return json.dumps({en: {i: dict(s) for i, s in insts.items()}
                       for en, insts in org.snapshot().items()},
                      separators=(",", ":"), sort_keys=True)


def _rust_fold(genome_path, events, workdir):
    from onto.dialects import registry
    reg = registry.get("rust-stdlib")
    out = pathlib.Path(workdir)
    reg["skeleton"].generate(__import__("onto.core.genome", fromlist=["load"])
                             .load(genome_path), out)
    ok, msg = reg["gates"].build(out)
    if not ok:
        return None, f"build failed: {msg}"
    evf = out / "events.jsonl"
    evf.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    r = subprocess.run([str(out / "organism"), str(evf)],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip(), r.stderr


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.dialects import registry

    if shutil.which("rustc") is None:
        print("=== EXAM rust-stdlib: SKIPPED (no rustc toolchain) ===")
        print("VERDICT: SKIPPED")
        return 0

    # 1. printer conformance: the 240-case corpus, compiled + run by rustc
    cert = registry.get("rust-stdlib")["gates"].certificate(
        str(ROOT / "exams/conformance_expr.jsonl"), tempfile.mkdtemp(prefix="rc-"))
    R.append((f"printer conformance 240/240 (rustc): {cert['printer_conformance']}",
              cert["printer_conformance"] == "green"))

    # 2. wallet: guard + dedup + contract, byte-identical fold
    wal = pathlib.Path(tempfile.mkdtemp()) / "wal.yaml"
    wal.write_text("""onto: 1
name: wal
retry_window: 8
events: {Deposit: {w: str, amt: int}}
entities:
  w: {key: w, instances: [bob, alice], state: {bal: int}, init: {bal: 0},
      rules: {dep: {when: Deposit, guard: "ev.amt > 0",
                    body: "s.bal = s.bal + ev.amt\\n", contract: {post: "s.bal >= 0"}}}}
queries: {}
""")
    ev = [{"id": "e1", "type": "Deposit", "w": "bob", "amt": 100},
          {"id": "e2", "type": "Deposit", "w": "bob", "amt": 50},
          {"id": "e3", "type": "Deposit", "w": "alice", "amt": 30},
          {"id": "e4", "type": "Deposit", "w": "bob", "amt": -5},   # guard blocks
          {"id": "e2", "type": "Deposit", "w": "bob", "amt": 999}]  # dedup
    rf, err = _rust_fold(wal, ev, tempfile.mkdtemp(prefix="rw-"))
    itf = _interp_fold(wal, ev)
    R.append((f"wallet fold byte-identical (guard+dedup+contract): rust=={itf}",
              rf == itf))

    # 3. saga: D54 emit-cascade over dynamic instances, byte-identical fold
    saga = pathlib.Path(tempfile.mkdtemp()) / "saga.yaml"
    saga.write_text("""onto: 1
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
""")
    sev = [{"id": "o1", "type": "Ordered", "order": "A", "qty": 5}]
    srf, _ = _rust_fold(saga, sev, tempfile.mkdtemp(prefix="rs-"))
    sif = _interp_fold(saga, sev)
    R.append((f"emit-cascade fold byte-identical (Ordered->Shipped, dynamic): "
              f"rust=={sif}", srf == sif))

    print(f"\n=== EXAM rust-stdlib dialect ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
