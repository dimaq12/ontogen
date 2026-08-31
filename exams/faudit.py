# -*- coding: utf-8 -*-
"""EXAM «SPECTRAL AUDIT IN WARDEN» (Part VII §2.5): the threshold is NOT set by
hand — it is calibrated from the first (healthy) window; under a healthy load
the audit STAYS SILENT; metastable corruption -> spectral_drift in the ledger;
freeze -> variance_freeze; the Markov property of the observables is tested
during calibration. The immune audit is a scheduled organ, not a human with a
stack trace at 3 a.m."""
import json
import pathlib
import random
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core.warden import Warden

    w = Warden(ROOT / "genomes/booking.yaml",
               tempfile.mkdtemp(prefix="audit-"), 8786)
    w.start()
    rnd = random.Random(41)
    live = []
    ctr = [0]

    def post(ev):
        req = urllib.request.Request("http://127.0.0.1:8786/event",
                                     data=json.dumps(ev).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)

    def traffic(p_cancel):
        ctr[0] += 1
        i = ctr[0]
        if live and rnd.random() < p_cancel:
            resv, room = live.pop(rnd.randrange(len(live)))
            post({"id": f"c{i}", "type": "BookingCancelled", "resv": resv,
                  "room": room, "guest": "g1", "nights": 1, "price": 100})
        else:
            room = f"room10{rnd.randint(1, 3)}"
            post({"id": f"b{i}", "type": "BookingRequested", "resv": f"r{i}",
                  "room": room, "guest": "g1", "nights": 1, "price": 100})
            live.append((f"r{i}", room))

    def led(kind):
        lp = w.data / "warden.jsonl"
        return [json.loads(l) for l in lp.read_text().splitlines()
                if json.loads(l)["kind"] == kind] if lp.exists() else []

    try:
        # phase 1: health — calibration (window 150)
        for _ in range(150):
            traffic(0.5)
            w.tick_spectral(window=150)
        cal = led("spectral_calibrated")
        R.append((f"threshold CALIBRATED from the healthy window (not by hand): "
                  f"λ_thr={cal[0]['lam_threshold'] if cal else '?'}",
                  len(cal) == 1 and 0 < cal[0]["lam_threshold"] <= 0.999))
        R.append((f"Markov property of observables tested during calibration: "
                  f"{cal[0].get('markov') if cal else '?'}",
                  bool(cal) and "markov_ok" in cal[0].get("markov", {})))

        # phase 2: still healthy — the audit must stay silent
        for _ in range(150):
            traffic(0.5)
            w.tick_spectral(window=150)
        quiet = len(led("spectral_drift")) + len(led("variance_freeze"))
        R.append((f"healthy load: audit stays silent ({quiet} verdicts)",
                  quiet == 0))

        # phase 3: metastable corruption (cancellations nearly gone)
        for _ in range(300):
            traffic(0.04)
            w.tick_spectral(window=150)
        drifts = led("spectral_drift")
        R.append((f"metastable corruption: spectral_drift in the ledger "
                  f"(λ={drifts[0]['lam'] if drifts else '?'} > "
                  f"{drifts[0]['threshold'] if drifts else '?'})",
                  len(drifts) >= 1))

        # phase 4: freeze (no events, snapshots keep coming)
        for _ in range(200):
            w.tick_spectral(window=150)
        freezes = led("variance_freeze")
        R.append((f"freeze: variance_freeze in the ledger ({len(freezes)} entries)",
                  len(freezes) >= 1))
    finally:
        w.stop()

    print(f"\n=== SPECTRAL AUDIT EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
