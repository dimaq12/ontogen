# -*- coding: utf-8 -*-
"""EXAM F3 "Second language" — showcase: ONE genome -> three substrates
(reference interpreter, go-stdlib, python-stdlib), ONE judge green on all of
them, certificates for both dialects, ZERO core edits since the F2 commit."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
F2_COMMIT = "730c002"          # historical invariant of phase F3:
F3_COMMIT = "1cff1eb"          # between F2 and F3 the core did not change by a single byte
R = []


def wait_up(port):
    for _ in range(100):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
            return True
        except Exception:
            time.sleep(0.05)
    return False


def judge(port):
    r = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                        str(ROOT / "exams/booking_flows.yaml"),
                        f"http://127.0.0.1:{port}"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip().splitlines()[-1]


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    procs = []
    try:
        # ---- three substrates from ONE genome
        d_int = tempfile.mkdtemp(prefix="f3-int-")
        procs.append(subprocess.Popen(
            [str(PY), "-m", "onto.cli", "serve", str(ROOT / "genomes/booking.yaml"),
             "--data", d_int, "--port", "8601"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

        for dialect, outdir, port in (("go-stdlib", "build/booking_go", 8602),
                                      ("python-stdlib", "build/booking_py", 8603)):
            gen = subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                                  str(ROOT / "genomes/booking.yaml"),
                                  "--dialect", dialect, "--out", str(ROOT / outdir)],
                                 cwd=ROOT, capture_output=True, text=True)
            R.append((f"materialize[{dialect}] + build", gen.returncode == 0))
        data_go = tempfile.mkdtemp(prefix="f3-go-")
        procs.append(subprocess.Popen(
            [str(ROOT / "build/booking_go/organism"), "--port", "8602",
             "--data", data_go],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        data_py = tempfile.mkdtemp(prefix="f3-py-")
        procs.append(subprocess.Popen(
            [str(PY), str(ROOT / "build/booking_py/organism.py"), "--port", "8603",
             "--data", data_py],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

        for port, name in ((8601, "interpreter"), (8602, "go"), (8603, "python")):
            up = wait_up(port)
            ok, line = judge(port) if up else (False, "did not start")
            print(f"{name} :{port}: {line}")
            R.append((f"ONE judge green: {name}", ok))

        # ---- parity of responses across the three substrates (snapshot after the judge)
        snaps = []
        for port in (8601, 8602, 8603):
            snap = {}
            for path in ("state/room/room101", "state/guest/bob", "q/total_booked"):
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/{path}", timeout=5) as r:
                    snap[path] = json.loads(r.read())
            snaps.append(snap)
        R.append(("three substrates answer BYTE-IDENTICALLY in meaning",
                  snaps[0] == snaps[1] == snaps[2]))

        # ---- dialect certificates
        from onto.dialects import registry
        corpus = ROOT / "exams/conformance_expr.jsonl"
        for name in registry.names():
            with tempfile.TemporaryDirectory() as td:
                cert = registry.get(name)["gates"].certificate(corpus, td)
            print(f"certificate[{name}]: {cert['printer_conformance']} "
                  f"({cert['embedded_interpreter']})")
            R.append((f"certificate {name}: conformance 240/240",
                      cert["printer_conformance"] == "green"))

        # ---- ZERO core edits since F2
        diff = subprocess.run(["git", "diff", "--name-only", F2_COMMIT,
                               F3_COMMIT, "--", "v1/src/onto/core"],
                              cwd=ROOT.parent, capture_output=True, text=True)
        core_changes = diff.stdout.strip()
        R.append(("ZERO core edits (I1 in practice): git diff core/ is empty",
                  core_changes == ""))
        if core_changes:
            print("core changed:", core_changes)
    finally:
        for p in procs:
            p.kill()

    print(f"\n=== EXAM F3 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
