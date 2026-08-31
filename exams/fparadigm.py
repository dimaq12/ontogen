# -*- coding: utf-8 -*-
"""EXAM "ELIMINATING THE 11 SHORTCOMINGS" (D74, PARADIGM_LIMITS):
not documents — mechanisms. §1+5+9 attest (guarantee attestation + weakest
seam), §3 hardening (an escape retroactively revokes the certificate), §4
ignorance as a typed hole under a monitor, §6 declared lossiness, §11 engine
pin. (§8 — separate fcold.)"""
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def http(port, path, payload=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait(port):
    for _ in range(120):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))

    # ---------- §1+5+9: GUARANTEE ATTESTATION
    at = subprocess.run([str(PY), "-m", "onto.cli", "attest",
                         str(ROOT / "genomes/authwallet.yaml")],
                        cwd=ROOT, capture_output=True, text=True)
    a = json.loads((ROOT / "genomes/attest.json").read_text())
    R.append(("attest: attestation is printed — proved/assumed/monitored",
              at.returncode == 0 and "ATTESTATION OF GUARANTEES" in at.stdout
              and a["proved"]["obligations_proved"] == 2
              and a["engine"]["ir_fingerprint"]))
    R.append((f"weakest seam is NAMED: '{a['assumed']['weakest_seam']}'",
              a["assumed"]["weakest_seam"] == "idp"))
    at2 = subprocess.run([str(PY), "-m", "onto.cli", "attest",
                          str(ROOT / "genomes/market.yaml"),
                          "--skills-cache", str(ROOT / "cache_skills")],
                         cwd=ROOT, capture_output=True, text=True)
    a2 = json.loads((ROOT / "genomes/attest.json").read_text())
    al = a2["assumed"]["skills"].get("allocate", {})
    qc = al.get("quantile_cert", {})
    R.append((f"attest: skill with a DKW quantile (allocate: {al.get('phase')}, "
              f"q≥{qc.get('q')}) — not a boolean checkbox",
              al.get("phase") == "fast" and qc.get("q", 0) > 0.8))
    ch = a2.get("chains", {})
    R.append((f"attest: end-to-end paths ({len(ch)} chains, "
              f"{sum(1 for c in ch.values() if c['proved_end_to_end'])} "
              f"PROVED end-to-end)",
              len(ch) >= 10 and all(c["proved_end_to_end"]
                                    for c in ch.values())))
    R.append(("attest: hazard survival moves (REVOKE h=1, rollback h=1; "
              "crash_loop honestly NOT MEASURED)",
              a2["survival"]["island_storm"]["h"] == 1.0
              and a2["survival"]["bad_molt"]["h"] == 1.0
              and a2["survival"]["crash_loop"]["h"] is None))

    # ---------- §11: ENGINE PIN
    nd = pathlib.Path(tempfile.mkdtemp(prefix="pin-")) / "org"
    subprocess.run([str(ROOT / ".venv/bin/onto"), "new", str(nd),
                    "--template", "hotel"], cwd=ROOT, capture_output=True)
    pin = json.loads((nd / "engine.pin").read_text())
    R.append(("onto new writes engine.pin (version + IR fingerprint)",
              pin["version"] and pin["ir_fingerprint"]))
    (nd / "engine.pin").write_text(json.dumps(
        {"version": "0.0.1", "ir_fingerprint": "stale"}))
    data = tempfile.mkdtemp(prefix="pin-d-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(nd / "genome.yaml"), "--port", "8781",
                             "--data", data], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    wait(8781)
    proc.kill()
    err = proc.stderr.read().decode()
    led = (pathlib.Path(data) / "ledger.jsonl").read_text()
    R.append(("pin mismatch: WARNING + ledger engine_pin_mismatch "
              "(an upgrade is a molt, not a silent merge)",
              "WARNING" in err and "engine_pin_mismatch" in led))

    # ---------- §3: HARDENING — an escape retroactively revokes the certificate
    from onto.core import genome as G, skills as SK
    g = G.load(ROOT / "genomes/exchange.yaml")
    sk = SK.Skill.model_validate(g.skills["match_orders"])
    body = (ROOT / "cache_skills/match_orders.fast.py").read_text()
    fn = SK.load_body(body, "fast_match_orders", sk.types)
    case = {"bids": [{"id": "b1", "price": 105, "qty": 10, "ts": 1}],
            "asks": [{"id": "a1", "price": 100, "qty": 4, "ts": 2}]}
    true_out = SK.run_case(fn, sk, case)

    ws = pathlib.Path(tempfile.mkdtemp(prefix="harden-"))
    import shutil
    shutil.copy(ROOT / "genomes/exchange.yaml", ws / "exchange.yaml")
    cache = ws / "cache"
    cache.mkdir()
    shutil.copy(ROOT / "cache_skills/match_orders.fast.py", cache)
    # escape: the incident oracle says the correct output is DIFFERENT
    wrong_expect = [dict(true_out[0], qty=999)] if true_out else [{"x": 1}]
    hd = subprocess.run([str(ROOT / ".venv/bin/onto"), "harden",
                         str(ws / "exchange.yaml"), "--skill", "match_orders",
                         "--case", json.dumps(case),
                         "--expect", json.dumps(wrong_expect)],
                        cwd=ROOT, capture_output=True, text=True)
    R.append(("onto harden: escape -> regression corpus",
              hd.returncode == 0
              and (ws / "regressions/match_orders.jsonl").exists()))
    reg = SK.gate_regressions(sk, fn, ws / "regressions/match_orders.jsonl")
    R.append(("corpus judges the CACHED body: certificate revoked "
              "(escape from prod in the verdict)",
              reg is not None and "escape" in reg))
    # oracle refined — correct expect: the body is green again
    (ws / "regressions/match_orders.jsonl").write_text(
        json.dumps({"case": case, "expect": true_out}) + "\n")
    R.append(("correct oracle: body passes the corpus, certificate stays alive",
              SK.gate_regressions(sk, fn,
                                  ws / "regressions/match_orders.jsonl") is None))

    # ---------- §4: IGNORANCE — a typed hole under a monitor
    from onto.core import interview
    ws2 = pathlib.Path(tempfile.mkdtemp(prefix="unk-"))
    shutil.copy(ROOT / "genomes/booking.yaml", ws2 / "genome.yaml")
    lists_env = G.load(ws2 / "genome.yaml").lists_env_types()
    interview.declare_unknown(
        ws2 / "assumptions.yaml", "overbook_policy", "room", "reserve",
        "What to do on a double booking of the same room — nobody knows "
        "(the PO forwards it to another team)",
        "sum(r.booked for r in room) > 0", lists_env)
    R.append(("\"don't know\" = a legal outcome: the hole is declared in assumptions.yaml",
              (ws2 / "assumptions.yaml").exists()))
    from onto.core.warden import Warden
    w = Warden(ws2 / "genome.yaml", tempfile.mkdtemp(prefix="unk-d-"), 8782)
    w.start()
    http(8782, "/event", {"id": "u1", "type": "BookingRequested",
                          "resv": "r1", "room": "room101", "guest": "g",
                          "nights": 1, "price": 100})
    ticks = w.tick_assumptions()
    wled = (w.data / "warden.jsonl").read_text()
    R.append(("warden: entering the ignorance region -> ledger assumption_hit",
              ticks["hits"] == ["overbook_policy"]
              and "assumption_hit" in wled))
    # D93: sustained time in the ignorance region past quota -> a real
    # consequence (rights demoted to observational), not just a ledger note
    w.rights = "interventional"      # simulate rights EARNED before the region
    rights0 = w.rights
    revoked = False
    for _ in range(int(w.quota.value) + 3):
        if w.tick_assumptions().get("revoked"):
            revoked = True
            break
    wled2 = (w.data / "warden.jsonl").read_text()
    R.append((f"knowledge quota: sustained hits > quota -> rights DEMOTED "
              f"({rights0} -> {w.rights}) + revoke_assumption in ledger",
              revoked and w.rights == "observational"
              and "revoke_assumption" in wled2))
    interview.resolve_unknown(ws2 / "assumptions.yaml", "overbook_policy")
    R.append(("the world answered: the hole is retracted, the monitor stays silent",
              w.tick_assumptions()["checked"] == 0))
    w.stop()

    # ---------- §6: LOSSINESS ONLY WHEN DECLARED
    from onto.core import migrate
    fx = migrate.Migrations(drop_events=["LegacyPing"])
    unc = migrate.coverage([], fx)
    R.append(("drop without a declared loss -> gates red (LOSSY)",
              any("LOSSY" in u for u in unc)))
    fx2 = migrate.Migrations(drop_events=["LegacyPing"], declared_loss={
        "LegacyPing": "telemetry from the old agent; the product doesn't read it"})
    R.append(("declared loss -> gates clean",
              migrate.coverage([], fx2) == []))

    (ROOT / "genomes/attest.json").unlink(missing_ok=True)
    (ROOT / "genomes/attest.md").unlink(missing_ok=True)
    print(f"\n=== EXAM: ELIMINATING SHORTCOMINGS ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
