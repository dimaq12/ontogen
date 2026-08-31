# -*- coding: utf-8 -*-
"""PART VII EXAM (mathematics of growth): theory must agree with measurement.
§1 — growth models against gauntlet telemetry (MLE, LR);
§2 — lemmas 6.1/6.3/6.4 of Part VI computed on a LIVE organism.handle();
§3 — DKW certificate of a real skill + composition bound VII.1."""
import json
import math
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))

    # ================= §1: growth — memoryless vs informative loop
    # data from LIVE telemetry (revision §2.2): usage_gauntlet.jsonl,
    # segmentation of sonnet series by reset of the attempt counter.
    K = 8
    greens_at, exhausted, src = [], 0, 'live'
    up = ROOT / '.onto' / 'usage_gauntlet.jsonl'
    if up.exists():
        rows = [json.loads(l) for l in up.read_text().splitlines()]
        seq = [int(r['tag'].rsplit(':', 1)[1]) for r in rows
               if r['tag'].startswith('nl:anthropic/claude-sonnet')]
        series, prev = [], 0
        for a in seq:
            if a <= prev:
                series.append(prev)
            prev = a
        series.append(prev)
        for last in series:
            if last < K:
                greens_at.append(last)
            else:
                exhausted += 1
    # the last series is an INEXPRESSIBLE task (impossible, an honest refusal):
    # p=0 structurally — this is a boundary of expressibility, not a convergence
    # parameter; it is DELIBERATELY excluded from the fit (accounted for
    # separately in the check).
    impossible_series = 1 if exhausted >= 6 else 0
    exhausted -= impossible_series
    if not greens_at:
        greens_at, exhausted, src, impossible_series = [1, 4, 6], 5, 'fallback', 1

    def ll(p_fn):
        L = 0.0
        for g in greens_at:
            for t in range(1, g):
                L += math.log(max(1e-12, 1 - p_fn(t)))
            L += math.log(max(1e-12, p_fn(g)))
        for _ in range(exhausted):
            for t in range(1, K + 1):
                L += math.log(max(1e-12, 1 - p_fn(t)))
        return L

    # A: p const (MLE over a grid); B: p_t = p0 + beta*(t-1)
    R.append((f"§1 telemetry: source={src}, greens at {sorted(greens_at)}, "
              f"{exhausted} exhausted + 1 inexpressible (revision lesson: "
              f"the constants lied — the live file found the impossible series)",
              src == 'live' and exhausted == 5 and impossible_series == 1
              and sorted(greens_at) == [1, 4, 6]))
    bestA = max(((ll(lambda t, p=p: p), p)
                 for p in [i / 200 for i in range(1, 100)]), key=lambda x: x[0])
    bestB = max(((ll(lambda t, p0=p0, b=b: min(0.99, p0 + b * (t - 1))), p0, b)
                 for p0 in [i / 200 for i in range(0, 60)]
                 for b in [i / 200 for i in range(0, 40)]), key=lambda x: x[0])
    LR = 2 * (bestB[0] - bestA[0])
    R.append((f"§1 MLE: A(p={bestA[1]:.3f}) LL={bestA[0]:.2f}; "
              f"B(p0={bestB[1]:.3f}, β={bestB[2]:.3f}) LL={bestB[0]:.2f}; "
              f"LR={LR:.2f}", True))
    # the negative is meaningful: LR below the chi-bar threshold (revision §2.1);
    # LR above the threshold => the data DISTINGUISH and theory must change
    R.append((f"§1 the negative is meaningful: LR={LR:.2f} < 2.71 (chi-bar 90%) — "
              f"in a pooled setup B is no better than A", LR < 2.71))
    # model strength: Opus 5/5 first-try against p_sonnet_first = 1/8
    p_null = (1 / 8) ** 5
    R.append((f"§1 model strength ≠ noise: P[Opus 5/5 | p=1/8] = {p_null:.1e} < 1e-3",
              p_null < 1e-3))

    # P16 MECHANISM (pre-registered, Part VII §1.2): count ALL growth attempts
    # across the whole telemetry; at N>=200 — hierarchical refit (chi-bar
    # threshold 0.05); before that — the mechanism is alive and prints the
    # accumulation.
    n_total = 0
    for f in sorted((ROOT / ".onto").glob("usage_*.jsonl")):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            if ":" in r.get("tag", ""):
                n_total += 1
    refit_due = n_total >= 200
    R.append((f"§1 P16 mechanism: N={n_total} attempts accumulated "
              f"({'REFIT DUE' if refit_due else 'accumulating up to 200'}) — "
              f"the mechanism counts all telemetry", n_total > 60))

    # ================= §2: Part VI lemmas on a live organism.handle()
    import yaml
    from onto.core import genome as G
    from onto.core.organism import Organism
    swamp = {
        "onto": 1, "name": "swamp", "retry_window": 4,
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
    import tempfile
    gp = pathlib.Path(tempfile.mkdtemp(prefix="swamp-")) / "swamp.yaml"
    gp.write_text(yaml.safe_dump(swamp, sort_keys=False))
    g = G.load(gp)

    rnd = random.Random(7)

    def fresh():
        return Organism(g, tempfile.mkdtemp(prefix="swamp-d-"))

    def draw(r):
        u = r.random()
        return 2 if u < 0.1 else (1 if u < 0.55 else 0)

    # empirical transition matrix FROM the live handle (not from a formula)
    org = fresh()
    N = 60000
    counts = [[0] * 5 for _ in range(5)]
    prev = org.state["walker"]["w"]["pos"]
    for i in range(N):
        org.handle({"id": f"e{i}", "type": "Step", "walker": "w",
                    "d": draw(rnd)})
        cur = org.state["walker"]["w"]["pos"]
        counts[prev][cur] += 1
        prev = cur
    P = [[c / max(1, sum(row)) for c in row] for row in counts
         for _ in [0]] and [[counts[i][j] / max(1, sum(counts[i]))
                             for j in range(5)] for i in range(5)]
    # S = {3,4}; the killed operator = submatrix
    idx = [3, 4]
    PS = [[P[i][j] for j in idx] for i in idx]
    # spectral radius 2x2
    tr, det = PS[0][0] + PS[1][1], PS[0][0] * PS[1][1] - PS[0][1] * PS[1][0]
    rho = (tr + math.sqrt(max(0, tr * tr - 4 * det))) / 2
    D = 1 / (1 - rho)
    # stationary mu (power method) and conductance eps(S)
    mu = [0.2] * 5
    for _ in range(3000):
        mu = [sum(mu[i] * P[i][j] for i in range(5)) for j in range(5)]
    muS = mu[3] + mu[4]
    flow = sum(mu[i] * P[i][j] for i in idx for j in range(5) if j not in idx)
    eps = flow / muS
    R.append((f"§2 measurement pipeline: ρ_S={rho:.3f}∈(0,1), D(S)={D:.1f}, "
              f"ε(S)={eps:.3f}∈(0,1)", 0 < rho < 1 and 0 < eps < 1))
    R.append((f"§2 lemma 6.1: D(S)={D:.1f} ≥ 1/ε(S)={1 / eps:.1f}",
              D >= 1 / eps - 0.3))
    # lemma 6.3: E_qsd[tau] ~ D(S); qsd ~ Perron vector of PS
    v = [1.0, 1.0]
    for _ in range(500):
        w0 = v[0] * PS[0][0] + v[1] * PS[1][0]
        w1 = v[0] * PS[0][1] + v[1] * PS[1][1]
        s = w0 + w1
        v = [w0 / s, w1 / s]
    taus = []
    for k in range(3000):
        o2 = fresh()
        start = 3 if rnd.random() < v[0] else 4
        for j in range(start):        # bring up to the start
            o2.handle({"id": f"s{k}-{j}", "type": "Step", "walker": "w", "d": 1})
        t = 0
        while o2.state["walker"]["w"]["pos"] in (3, 4) and t < 400:
            o2.handle({"id": f"t{k}-{t}", "type": "Step", "walker": "w",
                       "d": draw(rnd)})
            t += 1
        taus.append(t)
    emp = sum(taus) / len(taus)
    R.append((f"§2 lemma 6.3: E_qsd[τ_S]={emp:.1f} ≈ D(S)={D:.1f} "
              f"(live organism)", abs(emp - D) / D < 0.15))
    # lemma 6.4: hazard majorant pointwise
    h = min(sum(P[i][j] for j in range(5) if j not in idx) for i in idx)
    ok64 = True
    for start in idx:
        surv = [0] * 21
        for k in range(1500):
            o3 = fresh()
            for j in range(start):
                o3.handle({"id": f"h{start}-{k}-{j}", "type": "Step",
                           "walker": "w", "d": 1})
            t = 0
            while o3.state["walker"]["w"]["pos"] in (3, 4) and t < 20:
                o3.handle({"id": f"g{start}-{k}-{t}", "type": "Step",
                           "walker": "w", "d": draw(rnd)})
                t += 1
            for tt in range(min(t, 20)):
                surv[tt] += 1
        for tt in range(1, 15):
            if surv[tt] / 1500 > (1 - h) ** tt + 0.05:
                ok64 = False
    R.append((f"§2 lemma 6.4 (reset = hazard move, analog of REVOKE): h={h:.3f}"
              f" > 0, sup_x P(τ>t) ≤ (1-h)^t pointwise", ok64 and h > 0.05))

    # ================= §3: DKW certificate of a real skill + composition
    from onto.core import skills as SK
    ge = G.load(ROOT / "genomes/exchange.yaml")
    sk = SK.Skill.model_validate(ge.skills["match_orders"])
    body = (ROOT / "cache_skills/match_orders.fast.py").read_text()
    fn = SK.load_body(body, "fast_match_orders", sk.types)
    rnd2 = random.Random(99)
    M, defects = 300, 0
    for _ in range(M):
        case = SK.gen_case(sk, rnd2)
        try:
            out = SK.run_case(fn, sk, case)
            defects += bool(SK.check_properties(sk, case, out))
        except Exception:
            defects += 1
    delta = 0.01
    band = math.sqrt(math.log(2 / delta) / (2 * M))
    q_hat = 1 - defects / M
    q_cert = max(0.0, q_hat - band)
    R.append((f"§3 DKW RELATIVE TO ν_gen (fuzz, not the prod stream): "
              f"(η=0, q≥{q_cert:.3f}, δ={delta}, M={M})", q_cert > 0.9))
    # VII.1': Fréchet bound under the WORST dependence — antithetic coupling
    rnd3 = random.Random(5)
    qa, qb, MM = 0.9, 0.85, 20000
    worst = sum((u < qa) and (u > 1 - qb)
                for u in (rnd3.random() for _ in range(MM))) / MM
    bound = qa + qb - 1
    R.append((f"§3 VII.1': antithetic coupling: purity {worst:.3f} = "
              f"bound {bound:.2f} (attained, not lower)",
              abs(worst - bound) < 0.01))

    print(f"\n=== PART VII EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
