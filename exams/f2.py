# -*- coding: utf-8 -*-
"""EXAM F2 "Court and first tissue": (a) mutants distinguished by the court;
(b) the interview on the scar-13 case extends the genome; (c) go tissue: judge
5/5, kill -9, conformance, byte determinism, warmed path >= 10x."""
import hashlib
import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
PORT = 8492
BASE = f"http://127.0.0.1:{PORT}"
R = []


def http(path, payload=None):
    req = urllib.request.Request(BASE + path,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    t0 = time.time()
    # ---------- (a) court: contracts proved, mutants distinguished
    court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                            str(ROOT / "genomes/booking.yaml")],
                           cwd=ROOT, capture_output=True, text=True)
    n_mut = sum(int(l.split("mutants ")[1].split("/")[0])
                for l in court.stdout.splitlines() if "mutants " in l and "/" in l)
    R.append((f"court: all post PROVED, {n_mut} mutants distinguished, no blind spots",
              court.returncode == 0 and "BLIND" not in court.stdout))

    # ---------- (b) interview: scar-13 → question → answer → genome extended
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import interview
    from onto.core.interview import Patch
    ST = {"capacity": "int", "booked": "int", "available": "int"}
    EV = {"room": "str", "price": "int"}
    A = (None, "if s.booked > 0:\n  s.booked = s.booked - 1\n  s.available = s.available + 1")
    B = (None, "s.booked = max(s.booked - 1, 0)\ns.available = s.available + 1")
    q = interview.detect("room.free", ST, EV, A, B, "s.booked >= 0",
                         variants=[Patch("guard", "s.booked > 0"),
                                   Patch("post", "s.available <= s.capacity")])
    print("\n" + q.render() + "\n")
    R.append(("interview: question with an executable counterexample and variants",
              q is not None and q.variants and q.outcome_a != q.outcome_b))
    q2 = interview.detect("room.free", ST, EV,
                          ("s.booked > 0", A[1]), ("s.booked > 0", B[1]), "s.booked >= 0")
    R.append(("answer (guard) closes the question: candidates ≡ provably equal", q2 is None))

    # ---------- (c) go tissue
    build = ROOT / "build" / "booking_go"
    gen = subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                          str(ROOT / "genomes/booking.yaml"), "--out", str(build)],
                         cwd=ROOT, capture_output=True, text=True)
    R.append(("materialize + go build", gen.returncode == 0))

    from onto.core import genome as G
    from onto.dialects.go_stdlib import gates, skeleton
    with tempfile.TemporaryDirectory() as td:
        cert = gates.certificate(ROOT / "exams/conformance_expr.jsonl", td)
    R.append(("dialect certificate: printer-conformance 240/240 green",
              cert["printer_conformance"] == "green"))
    g = G.load(ROOT / "genomes/booking.yaml")
    with tempfile.TemporaryDirectory() as td:
        d1, d2 = pathlib.Path(td, "a"), pathlib.Path(td, "b")
        skeleton.generate(g, d1); skeleton.generate(g, d2)
        det = hashlib.sha256((d1 / "main.go").read_bytes()).hexdigest() == \
            hashlib.sha256((d2 / "main.go").read_bytes()).hexdigest()
    R.append(("generation is byte-for-byte deterministic", det))

    data = pathlib.Path(tempfile.mkdtemp(prefix="onto-f2-"))
    proc = subprocess.Popen([str(build / "organism"), "--port", str(PORT),
                             "--data", str(data)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.4)
    judge = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(ROOT / "exams/booking_flows.yaml"), BASE],
                           cwd=ROOT, capture_output=True, text=True)
    print(judge.stdout.strip())
    R.append(("the SAME judge 5/5 on the go organism", judge.returncode == 0))

    snap = {k: http(f"/state/{k}") for k in ("room/room101", "guest/bob")}
    os.kill(proc.pid, signal.SIGKILL); proc.wait()
    proc = subprocess.Popen([str(build / "organism"), "--port", str(PORT),
                             "--data", str(data)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.4)
    snap2 = {k: http(f"/state/{k}") for k in ("room/room101", "guest/bob")}
    os.kill(proc.pid, signal.SIGKILL)
    R.append(("kill -9 -> replay identical (go)", snap == snap2))

    bench = subprocess.run([str(build / "organism"), "bench"],
                           capture_output=True, text=True).stdout
    print(bench.strip())
    go_rule_ns = float([l for l in bench.splitlines() if "rule-path" in l][0]
                       .split(": ")[1].split(" ns")[0])
    # parity python measurement of the same path
    from onto.core import expr as E
    gu = E.parse_expr("s.booked < s.capacity")
    bo = E.parse_body("s.booked = s.booked + 1")
    po = E.parse_expr("s.booked >= 0 and s.booked <= s.capacity")
    s0 = {"capacity": 1, "booked": 0}
    ev0 = {"resv": "x", "room": "x", "guest": "x", "nights": 1, "price": 1}
    M = 100000
    t1 = time.perf_counter()
    for _ in range(M):
        if E.eval_expr(gu, {"s": s0, "ev": ev0}):
            new = E.exec_body(bo, s0, ev0)
            E.eval_expr(po, {"s": new})
    py_rule_ns = (time.perf_counter() - t1) / M * 1e9
    speedup = py_rule_ns / max(go_rule_ns, 0.1)
    print(f"python rule-path: {py_rule_ns:.0f} ns/op; speedup ~{speedup:,.0f}x")
    R.append((f"warmed path faster than interpreter >=10x (actual ~{speedup:,.0f}x)",
              speedup >= 10))

    print(f"\n=== EXAM F2 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
