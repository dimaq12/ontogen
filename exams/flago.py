# -*- coding: utf-8 -*-
"""EXAM LAGO-CORE v0: the Lago core on onto. L1 court; L2 judge over the docs
semantics (lifecycle, transaction_id idempotency, invoice with credits,
periods, DYNAMIC subscriptions); L3 the same flows on the go phenotype; L4 the
warden closes periods (the role of Lago's billing job); L5 volume: 200
subscriptions x 200 events + reconciling invoices against a naive model."""
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def http(port, path, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait_up(port):
    for _ in range(200):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism

    # L1: court
    c = subprocess.run([str(PY), "-m", "onto.cli", "court",
                        str(ROOT / "genomes/lago.yaml")],
                       cwd=ROOT, capture_output=True, text=True)
    R.append(("L1 court: invoicing/wallet/metering PROVED, mutants told apart",
              c.returncode == 0 and "BLIND" not in c.stdout))

    # L2: judge on the interpreter
    procs = []
    for dialect, port in (("interp", 8701), ("go", 8702)):
        if dialect == "interp":
            procs.append(subprocess.Popen(
                [str(PY), "-m", "onto.cli", "serve", str(ROOT / "genomes/lago.yaml"),
                 "--data", tempfile.mkdtemp(prefix="lago-i-"), "--port", str(port)],
                cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        else:
            m = subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                                str(ROOT / "genomes/lago.yaml"), "--dialect",
                                "go-stdlib", "--out", str(ROOT / "build/lago_go")],
                               cwd=ROOT, capture_output=True, text=True)
            R.append(("L3 go phenotype with DYNAMIC instances built",
                      m.returncode == 0))
            procs.append(subprocess.Popen(
                [str(ROOT / "build/lago_go/organism"), "--port", str(port),
                 "--data", tempfile.mkdtemp(prefix="lago-g-")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        up = wait_up(port)
        j = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(ROOT / "exams/lago_flows.yaml"),
                            f"http://127.0.0.1:{port}"],
                           cwd=ROOT, capture_output=True, text=True)
        print(f"{dialect}: {j.stdout.strip().splitlines()[-1] if j.stdout.strip() else j.stderr[-200:]}")
        R.append((f"L2 judge of Lago semantics 6/6 ({dialect})",
                  up and j.returncode == 0))
    for p in procs:
        p.kill()

    # L4: warden as the billing job (closes periods for all active ones)
    from onto.core.warden import Warden
    ws = pathlib.Path(tempfile.mkdtemp(prefix="lago-w-"))
    (ws / "modules").mkdir()
    import shutil
    shutil.copy(ROOT / "modules/lago_metering.yaml", ws / "modules/lago_metering.yaml")
    root = ws / "lago.yaml"
    root.write_text((ROOT / "genomes/lago.yaml").read_text()
                    .replace("../modules/", "modules/"), encoding="utf-8")
    w = Warden(root, ws / "data", 8703)
    w.start()
    http(8703, "/event", {"id": "w1", "type": "SubscriptionStarted",
                          "subscription": "s_a", "customer": "c_a"})
    http(8703, "/event", {"id": "w2", "type": "UsageApiCall", "subscription": "s_a"})
    # billing job: close the period for each active one (Lago's cron role)
    subs = ["s_a"]
    for i, sub in enumerate(subs):
        http(8703, "/event", {"id": f"close_{i}", "type": "BillingPeriodClosed",
                              "subscription": sub, "invoice_id": f"inv_{sub}"})
    st = http(8703, "/state/subscription/s_a")
    R.append(("L4 billing job via the warden organism: invoice 4902¢ issued",
              st["last_invoice_due"] == 4902 and st["invoices"] == 1))
    w.stop()

    # L5: volume + reconciliation against a naive model (reference = independent arithmetic)
    g = G.load(ROOT / "genomes/lago.yaml")
    org = Organism(g, tempfile.mkdtemp(prefix="lago-vol-"))
    org._append_log = lambda ev: None
    rnd = random.Random(42)
    model = {}
    NS, NE = 200, 200
    t1 = time.perf_counter()
    for s_i in range(NS):
        sub = f"sub{s_i:03d}"
        org.handle({"id": f"st{s_i}", "type": "SubscriptionStarted",
                    "subscription": sub, "customer": "c_" + sub})
        model[sub] = {"calls": 0, "storage": 0, "conn": 0, "credits": 0}
    n_ev = 0
    for i in range(NS * NE):
        sub = f"sub{rnd.randint(0, NS - 1):03d}"
        roll = rnd.random()
        if roll < 0.5:
            org.handle({"id": f"u{i}", "type": "UsageApiCall", "subscription": sub})
            model[sub]["calls"] += 1
        elif roll < 0.8:
            v = rnd.randint(1, 20)
            org.handle({"id": f"u{i}", "type": "UsageStorage",
                        "subscription": sub, "value": v})
            model[sub]["storage"] += v
        elif roll < 0.95:
            v = rnd.randint(1, 40)
            org.handle({"id": f"u{i}", "type": "UsageConn",
                        "subscription": sub, "value": v})
            model[sub]["conn"] = max(model[sub]["conn"], v)
        else:
            cr = rnd.randint(1, 50)
            org.handle({"id": f"u{i}", "type": "WalletTopUp",
                        "customer": "c_" + sub, "credits": cr})
            model[sub]["credits"] += cr * 100
        n_ev += 1
    for s_i in range(NS):
        org.handle({"id": f"cl{s_i}", "type": "BillingPeriodClosed",
                    "subscription": f"sub{s_i:03d}",
                    "invoice_id": f"inv{s_i:03d}"})
    thr = (n_ev + 2 * NS) / (time.perf_counter() - t1)
    mismatches = 0
    total_due = 0
    for sub, mm in model.items():
        calls_charge = (mm["calls"] * 2 if mm["calls"] <= 100
                        else 200 + (mm["calls"] - 100) * 1)   # graduated (Lago)
        expected_total = 4900 + calls_charge + mm["storage"] * 10 + mm["conn"] * 50
        expected_due = expected_total - min(mm["credits"], expected_total)
        st = org.state["subscription"][sub]
        cust = org.state["customer"].get("c_" + sub, {"credits_cents": 0})
        inv = org.state["invoice"][f"inv{sub[3:]}"]
        total_due += st["last_invoice_due"]
        exp_remaining = mm["credits"] - min(mm["credits"], expected_total)
        if st["last_invoice_total"] != expected_total or \
                st["last_invoice_due"] != expected_due or \
                cust["credits_cents"] != exp_remaining or \
                inv["due"] != expected_due or inv["total"] != expected_total:
            mismatches += 1
    print(f"L5: {NS} dynamic subscriptions, {n_ev} usage events, "
          f"{thr:,.0f} ev/s; invoices against the independent model: "
          f"{NS - mismatches}/{NS} matched; billed {total_due / 100:.2f}")
    R.append((f"L5 volume: {NS} subscriptions, SAGA invoices and customer wallets "
              f"matched the independent model {NS - mismatches}/{NS}",
              mismatches == 0))

    print(f"\n=== EXAM LAGO-CORE v0 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
