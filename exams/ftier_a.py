# -*- coding: utf-8 -*-
"""EXAM Tier-A (D83): four pre-release upgrades that dial the existing math to
the end, no new mechanisms. #5 invariants PROVED inductively (fixed-instance)
vs monitored; #8 the spectral organ gets HANDS (verdict -> demote rights +
recalibrate proposal); #10 onto replay --until time machine; #4 entity-court
is the headline (post rejection impossible), per-rule marked as self-induction."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []

# a genome with a PROVABLE single-entity fixed-instance invariant
BANK = {
    "onto": 1, "name": "bank", "retry_window": 8,
    "events": {"Deposited": {"acct": "str", "amount": "int"},
               "Withdrawn": {"acct": "str", "amount": "int"}},
    "entities": {"acct": {
        "key": "acct", "instances": ["a", "b", "c"],
        "state": {"balance": "int"}, "init": {"balance": 0},
        "rules": {
            "dep": {"when": "Deposited", "guard": "ev.amount > 0",
                    "body": "s.balance = s.balance + ev.amount\n",
                    "contract": {"post": "s.balance >= 0"}},
            "wd": {"when": "Withdrawn",
                   "guard": "ev.amount > 0 and ev.amount <= s.balance",
                   "body": "s.balance = s.balance - ev.amount\n",
                   "contract": {"post": "s.balance >= 0"}}}}},
    # provable: every balance >= 0 (posts) => sum >= 0 over fixed population
    "invariants": {"solvent": "sum(x.balance for x in acct) >= 0"},
    "queries": {"total": "sum(x.balance for x in acct)"}}


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G, court as C

    gp = pathlib.Path(tempfile.mkdtemp(prefix="tierA-")) / "bank.yaml"
    gp.write_text(yaml.safe_dump(BANK, sort_keys=False))
    g = G.load(gp)

    # ---- #5: invariant PROVED inductively (fixed-instance conserves-class)
    inv = C.prove_invariants(g)
    R.append((f"#5 fixed-instance invariant PROVED inductively: solvent -> "
              f"{inv['solvent'].status}", inv["solvent"].status == "proved"))
    # cross-entity / monitored-by-design stays monitored (no false proof)
    gm = G.load(ROOT / "genomes/market.yaml")
    invm = C.prove_invariants(gm)
    R.append(("#5 unprovable invariant stays MONITORED, not falsely proved "
              "(money_sane: refund unbounded)",
              invm["money_sane"].status != "proved"
              and invm["delivery_consistency"].status != "proved"))
    # court still green on market (invariants don't fail court)
    cm = subprocess.run([str(PY), "-m", "onto.cli", "court",
                         str(ROOT / "genomes/market.yaml")],
                        cwd=ROOT, capture_output=True, text=True)
    R.append(("#5 monitored invariants do NOT fail court (market green, "
              "invariants line printed)",
              cm.returncode == 0 and "invariants 0/2 PROVED" in cm.stdout))
    # bank court: invariant proved shows in headline
    cb = subprocess.run([str(PY), "-m", "onto.cli", "court", str(gp)],
                        cwd=ROOT, capture_output=True, text=True)
    R.append(("#5 bank court: 'invariant solvent: PROVED' + 1/1 in headline",
              "invariant solvent: PROVED" in cb.stdout
              and "invariants 1/1 PROVED" in cb.stdout))

    # ---- #4: entity-court is the headline (strong guarantee named)
    R.append(("#4 entity-court headline: 'ENTITY-INDUCTIVE (post rejection "
              "impossible)'", "ENTITY-INDUCTIVE" in cb.stdout))
    # attest splits proved vs monitored invariants
    subprocess.run([str(PY), "-m", "onto.cli", "attest", str(gp)],
                   cwd=ROOT, capture_output=True, text=True)
    at = json.loads((gp.parent / "attest.json").read_text())
    R.append(("#4/#5 attest carries invariants{proved} + entity_induction",
              at["invariants"]["solvent"] == "proved"
              and at["proved"]["entity_induction"]["acct"] == "entity-inductive"))

    # ---- #10: onto replay --until time machine
    data = tempfile.mkdtemp(prefix="tierA-d-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve", str(gp),
                             "--port", "8796", "--data", data],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    import urllib.request
    for _ in range(100):
        try:
            urllib.request.urlopen("http://127.0.0.1:8796/health", timeout=2)
            break
        except Exception:
            time.sleep(0.05)

    def post(ev):
        req = urllib.request.Request("http://127.0.0.1:8796/event",
                                     data=json.dumps(ev).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    post({"id": "t1", "type": "Deposited", "acct": "a", "amount": 100})
    post({"id": "t2", "type": "Deposited", "acct": "a", "amount": 50})
    post({"id": "t3", "type": "Withdrawn", "acct": "a", "amount": 30})
    proc.kill()
    rp = subprocess.run([str(PY), "-m", "onto.cli", "replay", str(gp),
                         "--data", data, "--until", "t2",
                         "--entity", "acct", "--instance", "a", "--watch", "total"],
                        cwd=ROOT, capture_output=True, text=True)
    R.append((f"#10 replay --until t2: state a=150 (before withdraw), NOT 120",
              "'balance': 150" in rp.stdout and "total = 150" in rp.stdout))
    rp2 = subprocess.run([str(PY), "-m", "onto.cli", "replay", str(gp),
                          "--data", data, "--until", "t3",
                          "--entity", "acct", "--instance", "a"],
                         cwd=ROOT, capture_output=True, text=True)
    R.append(("#10 replay --until t3: state a=120 (after withdraw)",
              "'balance': 120" in rp2.stdout))
    R.append(("#10 replay is read-only (real log untouched: 3 lines)",
              len((pathlib.Path(data) / "events.jsonl").read_text().splitlines()) == 3))

    # ---- #8: spectral organ demotes rights + proposes recalibration
    from onto.core.warden import Warden
    w = Warden(ROOT / "genomes/booking.yaml",
               tempfile.mkdtemp(prefix="tierA-w-"), 8797, rights="interventional")
    w.start()
    import random
    rnd = random.Random(7)
    live, ctr = [], [0]

    def wpost(ev):
        req = urllib.request.Request("http://127.0.0.1:8797/event",
                                     data=json.dumps(ev).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)

    def traffic(pc):
        ctr[0] += 1
        i = ctr[0]
        if live and rnd.random() < pc:
            resv, room = live.pop(rnd.randrange(len(live)))
            wpost({"id": f"c{i}", "type": "BookingCancelled", "resv": resv,
                   "room": room, "guest": "g", "nights": 1, "price": 100})
        else:
            room = f"room10{rnd.randint(1,3)}"
            wpost({"id": f"b{i}", "type": "BookingRequested", "resv": f"r{i}",
                   "room": room, "guest": "g", "nights": 1, "price": 100})
            live.append((f"r{i}", room))

    def led(kind):
        lp = w.data / "warden.jsonl"
        return [json.loads(l) for l in lp.read_text().splitlines()
                if json.loads(l)["kind"] == kind] if lp.exists() else []
    try:
        for _ in range(150):
            traffic(0.5); w.tick_spectral(window=150)
        for _ in range(150):
            traffic(0.02); w.tick_spectral(window=150)   # metastable corruption
        verdicts = (led("spectral_drift") + led("variance_freeze")
                    + led("nu_drift"))
        revokes = [r for r in led("revoke") if "spectral" in r.get("why", "")]
        recal = led("recalibrate_proposal")
        R.append((f"#8 spectral verdict ({len(verdicts)}) DEMOTES rights "
                  f"(interventional->observational): {len(revokes)} revoke, "
                  f"now {w.rights}",
                  len(verdicts) >= 1 and len(revokes) >= 1
                  and w.rights == "observational"))
        R.append((f"#8 spectral proposes recalibration ({len(recal)} proposals)",
                  len(recal) >= 1))
    finally:
        w.stop()

    print(f"\n=== EXAM Tier-A ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
