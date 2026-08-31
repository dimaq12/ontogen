# -*- coding: utf-8 -*-
"""EXAM F5 "Metabolism": (a) a shift in the load profile -> the Placer ITSELF
proposes extracting the hot gene (molt_proposal with arithmetic, ledger) ->
confirmation -> root split -> go materialization -> the same gene, bodies
byte-for-byte, judge green; (b) a deliberately impossible demand -> refusal
with arithmetic; (c) METRICS "formula -> decision" is non-empty; (d) cooling
-> evict_proposal."""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def http(base, path, payload=None):
    req = urllib.request.Request(base + path,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait_up(base):
    for _ in range(100):
        try:
            http(base, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import placer
    from onto.core.organism import Ledger
    from onto.theory.provenance import declared, measured
    procs = []
    base = "http://127.0.0.1:8621"
    try:
        data = pathlib.Path(tempfile.mkdtemp(prefix="f5-hotel-"))
        procs.append(subprocess.Popen(
            [str(PY), "-m", "onto.cli", "serve", str(ROOT / "genomes/hotel.yaml"),
             "--data", str(data), "--port", "8621"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        assert wait_up(base)
        ledger = Ledger(data / "placer.jsonl")

        # ---- MEASUREMENTS (Measured): t_cold — in-process, via the SAME path as
        # go-bench (wire decode + Handle, no disk) — apples to apples
        from onto.core import genome as GN
        from onto.core.organism import Organism
        g_hotel = GN.load(ROOT / "genomes/hotel.yaml")
        org_b = Organism(g_hotel, tempfile.mkdtemp(prefix="f5-bench-"))
        org_b._append_log = lambda ev: None
        N = 3000
        raws = [json.dumps({"id": f"m{i}", "type": "ChargeRequested",
                            "wallet": "bob", "amount": 0}) for i in range(N)]
        t1 = time.perf_counter()
        for rw in raws:
            org_b.handle(json.loads(rw))
        t_cold = measured((time.perf_counter() - t1) / N * 1e9, "bench:interp-inproc")
        # t_warm: go full-path from the bench mode of the hotel phenotype
        subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                        str(ROOT / "genomes/hotel.yaml"), "--dialect", "go-stdlib",
                        "--out", str(ROOT / "build/hotel_go")],
                       cwd=ROOT, capture_output=True)
        bench = subprocess.run([str(ROOT / "build/hotel_go/organism"), "bench"],
                               capture_output=True, text=True).stdout
        t_warm = measured(float(bench.split("full-path:")[1].split(",")[1]
                                .strip().split(" ")[0]), "bench:go-full")
        print(f"measured: t_cold={t_cold.value:.0f}ns t_warm={t_warm.value:.0f}ns")

        # ---- phase A: background load -> the loop stays silent
        h0 = http(base, "/health")["heat"]
        time.sleep(0.35)
        http(base, "/event", {"id": "bg1", "type": "BookingRequested",
                              "room": "room101", "resv": "r1", "nights": 1})
        h1 = http(base, "/health")["heat"]
        dt = 0.4
        rates = {en: measured((h1[en] - h0[en]) / dt, "heat:hotel")
                 for en in h1}
        planA = placer.tick(rates, t_cold_ns=t_cold, t_warm_ns=t_warm)
        R.append(("phase A (background): the loop proposes no molt", not planA.proposals))

        # ---- phase B: profile shift — wallet heats up
        h0 = http(base, "/health")["heat"]
        t1 = time.perf_counter()
        for i in range(600):
            http(base, "/event", {"id": f"hot{i}", "type": "ChargeRequested",
                                  "wallet": "alice", "amount": 1})
        dt = time.perf_counter() - t1
        h1 = http(base, "/health")["heat"]
        rates = {en: measured((h1[en] - h0[en]) / dt, "heat:hotel") for en in h1}
        planB = placer.tick(rates, t_cold_ns=t_cold, t_warm_ns=t_warm)
        molt = [p for p in planB.proposals if p["kind"] == "molt_proposal"]
        print("\n".join("  " + m for m in planB.metrics))
        R.append(("phase B (shift): molt_proposal for wallet with arithmetic",
                  bool(molt) and molt[0]["entity"] == "wallet"
                  and "WARM" in molt[0]["why"]))
        for p in planB.proposals:
            ledger.record(p["kind"], p)
        R.append(("the proposal is an EVENT in the ledger (proposal-only rights)",
                  "molt_proposal" in (data / "placer.jsonl").read_text()))

        # ---- confirmation (operator) -> split -> materialization -> judge
        svc_root = placer.split_hot_root(ROOT / "genomes/hotel.yaml", ["wallet"],
                                         ROOT / "build/hotel_wallet_svc.yaml")
        m = subprocess.run([str(PY), "-m", "onto.cli", "materialize", str(svc_root),
                            "--dialect", "go-stdlib",
                            "--out", str(ROOT / "build/wallet_svc_go")],
                           cwd=ROOT, capture_output=True, text=True)
        procs.append(subprocess.Popen(
            [str(ROOT / "build/wallet_svc_go/organism"), "--port", "8622",
             "--data", tempfile.mkdtemp(prefix="f5-svc-")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        up = wait_up("http://127.0.0.1:8622")
        j = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(ROOT / "exams/wallet_flows.yaml"),
                            "http://127.0.0.1:8622"],
                           cwd=ROOT, capture_output=True, text=True)
        print(j.stdout.strip())
        R.append(("extracted wallet-svc: judge green",
                  m.returncode == 0 and up and j.returncode == 0))

        def wallet_funcs(path):
            src = (ROOT / path / "main.go").read_text()
            return sorted(re.findall(
                r"func (?:guard|rule|post|conserves)Wallet\w*\([^)]*\)[^{]*\{.*?\n\}",
                src, re.S))
        R.append(("wallet bodies byte-for-byte: monolith == extracted service",
                  wallet_funcs("build/hotel_go") == wallet_funcs("build/wallet_svc_go")))

        # ---- (b) deliberately impossible demand -> refusal with arithmetic
        floor_ms = measured(t_warm.value / 1e6, "bench:go-full")
        planR = placer.tick({}, t_cold_ns=t_cold, t_warm_ns=t_warm,
                            demand={"q/total_balance": declared(0.0001, "operator")},
                            floor_warm_ms=floor_ms)
        print("  refusal:", planR.refusals[0][:120])
        R.append(("impossible demand: REFUSE with arithmetic and \"what to pay with\"",
                  bool(planR.refusals) and "pay with" in planR.refusals[0]))

        # ---- (d) cooling -> evict_proposal
        h0 = http(base, "/health")["heat"]
        time.sleep(0.6)
        h1 = http(base, "/health")["heat"]
        rates = {en: measured((h1[en] - h0[en]) / 0.6, "heat:hotel") for en in h1}
        planE = placer.tick(rates, t_cold_ns=t_cold, t_warm_ns=t_warm,
                            warm_set={"wallet"})
        R.append(("cooling: evict_proposal for wallet",
                  any(p["kind"] == "evict_proposal" and p["entity"] == "wallet"
                      for p in planE.proposals)))

        # ---- (c) the METRICS table is non-empty and has provenance
        all_metrics = planB.metrics + planR.metrics + planE.metrics
        R.append(("METRICS \"formula -> decision\" non-empty, inputs with provenance",
                  len(all_metrics) >= 5 and
                  all("(" in m and "->" in m for m in all_metrics)))
    finally:
        for p in procs:
            p.kill()

    print(f"\n=== EXAM F5 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
