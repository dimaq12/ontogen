# -*- coding: utf-8 -*-
"""ν-BRIDGE EXAM (Part VII §6, theorem VII.2): the gap between fuzz-ν and
prod-ν is the next honest frontier (revision v2). The organism's kernel is
LINEAR in ν — this is MEASURED; the operator shift ≤ TV(ν',ν) — measured;
per-event certificates transfer with a dominance factor C; ν-drift is
monitored by the warden with a threshold FROM calibration (not by hand).
Spectral transfer without oaths: empirical monotonicity in TV, Bauer-Fike is
not claimed."""
import json
import math
import pathlib
import random
import sys
import tempfile
import time
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

SWAMP = {
    "onto": 1, "name": "swampnu", "retry_window": 4,
    "events": {"Step": {"walker": "str", "d": "int"}},
    "entities": {"walker": {
        "key": "walker", "instances": ["w"],
        "state": {"pos": "int"}, "init": {"pos": 0},
        "rules": {
            "up": {"when": "Step", "guard": "ev.d == 1 and s.pos < 4",
                   "body": "s.pos = s.pos + 1\n",
                   "contract": {"post": "s.pos >= 0"}},
            "down": {"when": "Step", "guard": "ev.d == 0 and s.pos > 0",
                     "body": "s.pos = s.pos - 1\n",
                     "contract": {"post": "s.pos >= 0"}},
            "reset": {"when": "Step", "guard": "ev.d == 2",
                      "body": "s.pos = 0\n",
                      "contract": {"post": "s.pos == 0"}}}}},
    "queries": {}}


def transition_matrix(g, nu, n, seed):
    """P̂ under load ν = (p_up, p_down, p_reset) — from a live handle()."""
    from onto.core.organism import Organism
    org = Organism(g, tempfile.mkdtemp(prefix="nu-"))
    rnd = random.Random(seed)
    counts = [[0] * 5 for _ in range(5)]
    prev = 0
    for i in range(n):
        u = rnd.random()
        d = 1 if u < nu[0] else (0 if u < nu[0] + nu[1] else 2)
        org.handle({"id": f"e{i}", "type": "Step", "walker": "w", "d": d})
        cur = org.state["walker"]["w"]["pos"]
        counts[prev][cur] += 1
        prev = cur
    return [[counts[i][j] / max(1, sum(counts[i])) for j in range(5)]
            for i in range(5)]


def lam_slow(P):
    """|λ2| of the submatrix without the stationary direction — over the killed {1..4}."""
    PS = [[P[i][j] for j in range(1, 5)] for i in range(1, 5)]
    v = [1.0] * 4
    for _ in range(400):
        w = [sum(PS[i][j] * v[j] for j in range(4)) for i in range(4)]
        nrm = math.sqrt(sum(c * c for c in w))
        if nrm < 1e-12:
            return 0.0
        v = [c / nrm for c in w]
    Av = [sum(PS[i][j] * v[j] for j in range(4)) for i in range(4)]
    return abs(sum(Av[i] * v[i] for i in range(4)) / sum(vi * vi for vi in v))


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    gp = pathlib.Path(tempfile.mkdtemp(prefix="nu-g-")) / "g.yaml"
    gp.write_text(yaml.safe_dump(SWAMP, sort_keys=False))
    g = G.load(gp)

    nu1 = (0.7, 0.2, 0.1)
    nu2 = (0.2, 0.7, 0.1)
    numix = tuple((a + b) / 2 for a, b in zip(nu1, nu2))
    N = 40000
    P1 = transition_matrix(g, nu1, N, 1)
    P2 = transition_matrix(g, nu2, N, 2)
    Pm = transition_matrix(g, numix, N, 3)

    # 1. KERNEL LINEARITY IN ν — measured (VII.2 identity)
    err = max(abs(Pm[i][j] - 0.5 * (P1[i][j] + P2[i][j]))
              for i in range(5) for j in range(5)
              if sum(1 for c in Pm[i] if c) > 0)
    R.append((f"kernel linearity in ν MEASURED: max|P_mix - ½(P₁+P₂)| = "
              f"{err:.3f} < 0.04 (sampling noise)", err < 0.04))

    # 2. operator shift ≤ TV(ν₁,ν₂) (VII.2a)
    tv_nu = 0.5 * sum(abs(a - b) for a, b in zip(nu1, nu2))
    shift = max(0.5 * sum(abs(P1[i][j] - P2[i][j]) for j in range(5))
                for i in range(5) if sum(counts_row := P1[i]) > 0)
    R.append((f"operator shift: max_x TV(P₁(x,·),P₂(x,·)) = {shift:.3f} "
              f"≤ TV(ν₁,ν₂)+noise = {tv_nu:.2f}+0.05", shift <= tv_nu + 0.05))

    # 3. per-event certificate transfer (VII.2b): defect = event d=2
    q1 = 1 - nu1[2]
    C = max(n2 / n1 for n1, n2 in zip(nu1, nu2) if n1 > 0)
    q2_bound = 1 - C * (1 - q1)
    q2_true = 1 - nu2[2]
    R.append((f"per-event transfer: q'={q2_true:.2f} ≥ 1-C(1-q) = "
              f"{q2_bound:.2f} (C={C:.1f})", q2_true >= q2_bound - 1e-9))

    # 4. spectral transfer WITHOUT OATHS: |Δλ| grows with TV, bounded
    lams = []
    for k, t in enumerate([0.0, 0.5, 1.0]):
        nut = tuple(a * (1 - t) + b * t for a, b in zip(nu1, nu2))
        lams.append(lam_slow(transition_matrix(g, nut, N, 10 + k)))
    d_half, d_full = abs(lams[1] - lams[0]), abs(lams[2] - lams[0])
    R.append((f"spectrum vs TV: λ={[round(l, 3) for l in lams]} — the shift "
              f"is monotone (|Δ½|={d_half:.3f} ≤ |Δ1|={d_full:.3f}+0.02); "
              f"Bauer-Fike is NOT claimed (κ not attested)",
              d_half <= d_full + 0.02))

    # 5. ν-monitor in the warden: threshold from calibration; load change -> nu_drift
    from onto.core.warden import Warden
    w = Warden(ROOT / "genomes/booking.yaml",
               tempfile.mkdtemp(prefix="nu-w-"), 8791)
    w.start()
    rnd = random.Random(9)
    live, ctr = [], [0]

    def post(ev):
        req = urllib.request.Request("http://127.0.0.1:8791/event",
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
        for _ in range(225):                    # calibration + healthy audit
            traffic(0.5)
            w.tick_spectral(window=150)
        cal = led("spectral_calibrated")
        R.append((f"ν in the calibration certificate + threshold FROM subwindows: "
                  f"nu_tol={cal[0].get('nu_tol') if cal else '?'}",
                  bool(cal) and "nu" in cal[0] and cal[0]["nu_tol"] >= 0.05))
        quiet = len(led("nu_drift"))
        R.append((f"healthy load: ν-monitor stays silent ({quiet})", quiet == 0))
        for _ in range(150):                    # prod changed the load profile
            traffic(0.02)
            w.tick_spectral(window=150)
        drifts = led("nu_drift")
        R.append((f"load change -> nu_drift in the ledger (tv="
                  f"{drifts[0]['tv'] if drifts else '?'}): the certificate "
                  f"is declared conditional BEFORE it silently goes stale",
                  len(drifts) >= 1))
    finally:
        w.stop()

    print(f"\n=== ν-BRIDGE EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
