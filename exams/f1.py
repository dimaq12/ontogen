# -*- coding: utf-8 -*-
"""EXAM F1 "Living reference" (PLAN): the booking genome LIVES via the
interpreter — the judge is green over HTTP, kill -9 -> replay with no losses,
window dedup, rule/skill boundary. Run: .venv/bin/python exams/f1.py"""
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
PORT = 8391
BASE = f"http://127.0.0.1:{PORT}"


def http(path, payload=None):
    req = urllib.request.Request(BASE + path,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def start(data):
    proc = subprocess.Popen(
        [str(PY), "-m", "onto.cli", "serve", str(ROOT / "genomes/booking.yaml"),
         "--data", str(data), "--port", str(PORT)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            http("/health")
            return proc
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("organism did not start")


def main():
    results = []
    data = pathlib.Path(tempfile.mkdtemp(prefix="onto-f1-"))

    proc = start(data)
    t0 = time.time()

    # 1. Judge (external black box) — the organism is interpreted, no code
    judge = subprocess.run(
        [str(PY), "-m", "onto.cli", "judge", str(ROOT / "exams/booking_flows.yaml"), BASE],
        cwd=ROOT, capture_output=True, text=True)
    print(judge.stdout.strip())
    results.append(("judge on the interpreter", judge.returncode == 0))

    # 2. kill -9 -> replay: state must regenerate from the log
    snap_before = {e: http(f"/state/{e}/{i}") for e, i in
                   [("room", "room101"), ("guest", "bob"), ("reservation", "r1")]}
    os.kill(proc.pid, signal.SIGKILL)
    proc.wait()
    proc = start(data)
    snap_after = {e: http(f"/state/{e}/{i}") for e, i in
                  [("room", "room101"), ("guest", "bob"), ("reservation", "r1")]}
    results.append(("kill -9 -> replay: state identical", snap_before == snap_after))

    # 3. window dedup SURVIVES restart: e3 (already in log) is a duplicate after replay
    out = http("/event", {"id": "e3", "type": "BookingCancelled", "resv": "r1",
                          "room": "room101", "guest": "bob", "nights": 2, "price": 100})
    results.append(("dedup window restored by replay (e3 -> dup)", out["status"] == "dup"))

    # 4. rule/skill boundary: the smuggler is rejected
    val = subprocess.run([str(PY), "-m", "onto.cli", "validate",
                          str(ROOT / "genomes/skill_smuggler.yaml")],
                         cwd=ROOT, capture_output=True, text=True)
    results.append(("smuggler-algorithm rejected as a skill",
                    val.returncode == 2 and "this is a skill" in val.stderr))

    # 5. the invariant observer left a trace in the ledger
    ledger = (data / "ledger.jsonl").read_text()
    results.append(("invariant observer in ledger", "invariant_violation" in ledger))

    os.kill(proc.pid, signal.SIGKILL)
    print(f"\n=== EXAM F1 ({time.time() - t0:.1f} s, data={data}) ===")
    ok = True
    for name, passed in results:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
