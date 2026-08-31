# -*- coding: utf-8 -*-
"""EXAM «connective tissue»: (a) court in the mutation stream (warden rejects
an unprovable contract); (b) semdiff interview in the stream (behavior change
without ack rejected, with ack accepted); (c) skill — an organ of the organism
(HTTP from the certified cache); (d) propose — the only write path, the same
gates; (e) MCP mouth is alive; (f) warden DAEMON (CLI) picks up the mutation on
its own; (g) delivery: uv tool install -> onto + systemd unit."""
import json
import pathlib
import shutil
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
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def make_ws():
    ws = pathlib.Path(tempfile.mkdtemp(prefix="f8-ws-"))
    (ws / "modules").mkdir()
    for m in ("rooms", "reservations", "payments"):
        shutil.copy(ROOT / "modules" / f"{m}.yaml", ws / "modules" / f"{m}.yaml")
    root = ws / "hotel.yaml"
    root.write_text((ROOT / "genomes" / "hotel.yaml").read_text()
                    .replace("../modules/", "modules/"), encoding="utf-8")
    return ws, root


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core.propose import propose
    from onto.core.warden import Warden

    # ---------- (a)+(b): court and semdiff in the warden stream
    ws, root = make_ws()
    w = Warden(root, ws / "data", 8651)
    procs = []
    try:
        w.start()
        pay = ws / "modules" / "payments.yaml"
        orig = pay.read_text()
        # (a) drop the guard: post is unprovable -> court rejects
        pay.write_text(orig.replace(
            '        guard: "ev.amount > 0 and s.balance >= ev.amount and s.frozen == 0"\n', ""))
        out = w.tick_watch()
        R.append(("court in the stream: unprovable contract REJECTED (DISPROVED)",
                  out["status"] == "rejected"
                  and any("DISPROVED" in r for r in out["reasons"])))
        pay.write_text(orig)
        w.tick_watch()
        # (b) behavior change under the same contracts
        changed = orig.replace(
            "          s.balance = s.balance - ev.amount\n"
            "          s.charges = s.charges + 1\n",
            "          s.balance = s.balance - ev.amount\n")
        pay.write_text(changed)
        out = w.tick_watch()
        R.append(("semdiff interview in the stream: behavior change without ack — QUESTION",
                  out["status"] == "rejected"
                  and any("behavior change" in r and "ack_behavior_change" in r
                          for r in out["reasons"])))
        root.write_text(root.read_text()
                        + '\nack_behavior_change: ["wallet.charge"]\n')
        out = w.tick_watch()
        R.append(("operator answer (ack) -> mutation accepted, molt",
                  out["status"] == "molted"))
    finally:
        w.stop()

    # ---------- (c) skill — an organ of the organism
    p = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                          str(ROOT / "genomes/exchange.yaml"),
                          "--port", "8652", "--data",
                          tempfile.mkdtemp(prefix="f8-exch-"),
                          "--skills-cache", str(ROOT / "cache_skills")],
                         cwd=ROOT, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    procs.append(p)
    time.sleep(0.6)
    out = http(8652, "/skill/match_orders",
               {"bids": [{"id": "b1", "price": 10, "qty": 5, "ts": 1}],
                "asks": [{"id": "a1", "price": 8, "qty": 3, "ts": 2}]})
    R.append(("skill-organ: POST /skill/match_orders from the certified "
              f"cache (body={out.get('body')})",
              out.get("out") == [{"bid": "b1", "ask": "a1", "price": 8,
                                  "qty": 3}] and out.get("body") == "fast"))
    p.kill()

    # ---------- (d) propose: the only write path, the same gates
    ws2, root2 = make_ws()
    pay_rel = "modules/payments.yaml"
    good = (ws2 / pay_rel).read_text().replace(
        "queries:\n",
        "      bonus:\n"
        "        when: ChargeRefunded\n"
        "        guard: \"ev.amount > 0\"\n"
        "        body: |\n"
        "          s.balance = s.balance + ev.amount\n"
        "        contract: {post: \"s.balance >= 0\"}\n"
        "queries:\n")
    ok1 = propose(root2, {pay_rel: good})
    bad = good.replace('"s.balance >= 0"', '"s.balance <= 100"')
    ok2 = propose(root2, {pay_rel: bad})
    R.append(("propose: additive feature accepted (with .bak), broken contract "
              "rejected by the court through the SAME gates",
              ok1["accepted"] and ok1["backups"] and not ok2["accepted"]))

    # ---------- (e) MCP mouth
    import asyncio
    from onto import mcp_server
    srv = mcp_server.build_server(root2)
    tools = {t.name for t in asyncio.run(srv.list_tools())}
    R.append(("MCP mouth: genome_read/validate/court/explain/propose/ledger_tail",
              {"genome_read", "validate", "court", "explain", "propose",
               "ledger_tail"} <= tools))

    # ---------- (f) warden DAEMON (CLI) picks up the mutation on its own
    ws3, root3 = make_ws()
    daemon = subprocess.Popen(
        [str(PY), "-m", "onto.cli", "warden", str(root3),
         "--data", str(ws3 / "data"), "--port", "8653", "--interval", "0.4"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(daemon)
    time.sleep(1.2)
    pay3 = ws3 / "modules" / "payments.yaml"
    pay3.write_text((ws3 / "modules" / "payments.yaml").read_text().replace(
        "queries:\n",
        "      gift:\n"
        "        when: ChargeRefunded\n"
        "        guard: \"ev.amount > 0\"\n"
        "        body: |\n"
        "          s.balance = s.balance + 0\n"
        "queries:\n"))
    molted = False
    for _ in range(20):
        time.sleep(0.4)
        led = (ws3 / "data" / "warden.jsonl")
        if led.exists() and '"kind": "molt"' in led.read_text():
            molted = True
            break
    R.append(("warden daemon (CLI): mutation picked up WITHOUT manual ticks", molted))
    daemon.kill()

    # ---------- (g) delivery
    installed = shutil.which("onto")
    ver = subprocess.run([installed, "version"], capture_output=True,
                         text=True).stdout if installed else ""
    unit = subprocess.run([installed, "unit", str(root2), "--port", "8090"],
                          capture_output=True, text=True).stdout if installed else ""
    R.append(("delivery: uv tool install -> global onto + systemd unit",
              bool(installed) and "hub v1" in ver and "[Service]" in unit))

    for p in procs:
        p.poll() is None and p.kill()
    print(f"\n=== TISSUE EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
