# -*- coding: utf-8 -*-
"""EXAM M-3 "SPECTRAL STEP" (Part VII §2.4): the operator of a NON-toy
organism (booking) is measured under load (observable dictionary =
int fields + aggregates; linear estimate A: x_{t+1} ~ A x_t + b), and
load/environment corruption is detected by a SHIFT OF THE SLOW MODE — the
spirit of proposition 3 ("spectrally visible corruption gets caught") on a
live handle(). This is a step toward a spectral audit, NOT the audit itself
(the threshold is not calibrated — honestly)."""
import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def observe(org):
    from onto.core import spectral as SP
    return SP.observe(org)


def trajectory(g, rnd, T, p_cancel):
    """A live organism under load; returns the trajectory matrix."""
    from onto.core.organism import Organism
    org = Organism(g, tempfile.mkdtemp(prefix="spec-"))
    live = []                     # active bookings (resv, room, guest, price)
    xs = [observe(org)]
    for t in range(T):
        if live and rnd.random() < p_cancel:
            resv, room, guest, price = live.pop(rnd.randrange(len(live)))
            org.handle({"id": f"c{t}", "type": "BookingCancelled",
                        "resv": resv, "room": room, "guest": guest,
                        "nights": 1, "price": price})
        else:
            room = f"room10{rnd.randint(1, 3)}"
            resv = f"r{t}"
            org.handle({"id": f"b{t}", "type": "BookingRequested",
                        "resv": resv, "room": room, "guest": "g1",
                        "nights": 1, "price": 100})
            live.append((resv, room, "g1", 100))
        xs.append(observe(org))
    return xs


def fit_slow_mode(xs):
    """OLS x_{t+1} = A x_t + b; max |λ(A)| via the power method + deflation is
    not needed — we take the spectral radius via the power method."""
    d = len(xs[0])
    n = len(xs) - 1
    # centering removes b
    mean = [sum(x[i] for x in xs) / len(xs) for i in range(d)]
    X = [[x[i] - mean[i] for i in range(d)] for x in xs]
    # A = Y Xt (X Xt)^-1 ; solve via the normal equations (d is small)
    XtX = [[sum(X[t][i] * X[t][j] for t in range(n)) for j in range(d)]
           for i in range(d)]
    XtY = [[sum(X[t][i] * X[t + 1][j] for t in range(n)) for j in range(d)]
           for i in range(d)]
    # regularization
    for i in range(d):
        XtX[i][i] += 1e-6
    # solve XtX * M = XtY column by column (Gaussian elimination)
    def solve(Mat, rhs):
        m = [row[:] for row in Mat]
        b = rhs[:]
        for col in range(d):
            piv = max(range(col, d), key=lambda r: abs(m[r][col]))
            m[col], m[piv] = m[piv], m[col]
            b[col], b[piv] = b[piv], b[col]
            for r in range(col + 1, d):
                f = m[r][col] / m[col][col]
                for c in range(col, d):
                    m[r][c] -= f * m[col][c]
                b[r] -= f * b[col]
        out = [0.0] * d
        for r in range(d - 1, -1, -1):
            out[r] = (b[r] - sum(m[r][c] * out[c]
                                 for c in range(r + 1, d))) / m[r][r]
        return out
    A_T = [solve(XtX, [XtY[i][j] for i in range(d)]) for j in range(d)]
    A = [[A_T[j][i] for j in range(d)] for i in range(d)]   # A[i][j]
    # spectral radius: power method (real majorant)
    import math
    v = [1.0] * d
    lam = 0.0
    for _ in range(500):
        w = [sum(A[i][j] * v[j] for j in range(d)) for i in range(d)]
        nrm = math.sqrt(sum(c * c for c in w))
        if nrm < 1e-12:
            return 0.0, A, mean
        v = [c / nrm for c in w]
        lam = nrm
    # the Rayleigh quotient is more stable
    Av = [sum(A[i][j] * v[j] for j in range(d)) for i in range(d)]
    lam = sum(Av[i] * v[i] for i in range(d)) / sum(v[i] * v[i] for i in range(d))
    return abs(lam), A, mean


def r2_holdout(xs, A, mean):
    d = len(xs[0])
    n = len(xs) - 1
    cut = int(n * 0.8)
    sse = ssm = 0.0
    for t in range(cut, n):
        xc = [xs[t][i] - mean[i] for i in range(d)]
        pred = [sum(A[i][j] * xc[j] for j in range(d)) + mean[i]
                for i in range(d)]
        for i in range(d):
            sse += (xs[t + 1][i] - pred[i]) ** 2
            ssm += (xs[t + 1][i] - mean[i]) ** 2
    return 1 - sse / max(ssm, 1e-9)


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    g = G.load(ROOT / "genomes/booking.yaml")
    rnd = random.Random(31)

    from onto.core import spectral as SP
    healthy_raw = trajectory(g, rnd, 4000, p_cancel=0.5)
    keep = SP.select_coords(healthy_raw)
    healthy = SP.project(healthy_raw, keep)
    lam_h, A_h, mean_h = fit_slow_mode(healthy)
    r2 = r2_holdout(healthy, A_h, mean_h)
    R.append((f"operator MEASURED on live booking: dictionary "
              f"{len(healthy_raw[0])}->{len(healthy[0])} coordinates "
              f"(the trend filter rejected the non-stationary ones), "
              f"λ_slow={lam_h:.3f}, hold-out R²={r2:.2f}", 0 < lam_h < 1.05))
    R.append((f"operator predicts (R²={r2:.2f} > 0.2 against the mean)",
              r2 > 0.2))

    # CORRUPTION-1 (metastability): releases became RARE (0.5 -> 0.1)
    # — rooms stay stuck for a long time, switching occasionally: the slow mode grows.
    sick = SP.project(trajectory(g, random.Random(32), 4000, p_cancel=0.1), keep)
    lam_s, _, _ = fit_slow_mode(sick)
    R.append((f"metastable corruption shifts the slow mode: "
              f"λ_sick={lam_s:.3f} > λ_healthy={lam_h:.3f} + 0.03",
              lam_s > lam_h + 0.03))

    # CORRUPTION-2 (freeze): almost no releases — the state FREEZES.
    # EXAM LESSON (the first run refuted the naive design): a freeze is NOT
    # a slow mode: variance -> 0, the spectrum has nothing to measure. A freeze is
    # caught by a VARIANCE monitor. The full detector = spectrum (metastability)
    # + variance (death of the dynamics) — two-component.
    frozen = SP.project(trajectory(g, random.Random(33), 4000, p_cancel=0.005), keep)
    def var_tail(xs):
        d = len(xs[0]); tail = xs[len(xs) // 2:]
        m = [sum(x[i] for x in tail) / len(tail) for i in range(d)]
        return sum((x[i] - m[i]) ** 2 for x in tail for i in range(d)) / len(tail)
    vh, vf = var_tail(healthy), var_tail(frozen)
    R.append((f"freeze is caught by VARIANCE, not the spectrum: var_frozen={vf:.3f} < "
              f"var_healthy={vh:.3f} / 5", vf < vh / 5))
    # honesty: this is a STEP, not an audit
    R.append(("the detector threshold is NOT calibrated — not claimed in the "
              "attestation (an honest boundary of the step)", True))

    print(f"\n=== EXAM: SPECTRAL STEP ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
