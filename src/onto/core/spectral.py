# -*- coding: utf-8 -*-
"""Spectral organ (Part VII §2.4-2.5): estimates the slow mode and the
variance from the trajectory of a live organism's observables + a Markov test.

The corruption detector is TWO-COMPONENT (fspectral lesson): the spectrum
catches metastabilization (λ_slow -> 1), the variance catches freeze
(var -> 0). All quantities are CONDITIONAL ON ν (load) — revision §2.3; the
threshold is calibrated from a healthy reference window (bootstrap of
sub-windows), not set by hand."""
from __future__ import annotations

import math


def observe(org) -> list:
    """Dictionary of observables: int fields of STATIC instances (stable
    dimensionality) + a live-instance count for each dynamic entity."""
    x = []
    for en in sorted(org.g.entities):
        ent = org.g.entities[en]
        if ent.instances == "dynamic":
            x.append(len(org.state.get(en, {})))
        else:
            for inst in sorted(org.state.get(en, {})):
                st = org.state[en][inst]
                for f in sorted(ent.state):
                    if ent.state[f] == "int":
                        x.append(st[f])
    return x


def select_coords(xs: list[list]) -> list[int]:
    """Dictionary selection (fspectral v2 lesson): coordinates with ~zero
    variance or a ~monotone trend (|corr with time| > 0.95) are non-stationary
    and break the linear model — they're excluded, and the exclusion itself is
    diagnostic (the observable dictionary is part of the certificate,
    revision §2.3)."""
    d = len(xs[0])
    n = len(xs)
    tm = (n - 1) / 2
    tvar = sum((t - tm) ** 2 for t in range(n))
    stats = []
    for i in range(d):
        m = sum(x[i] for x in xs) / n
        var = sum((x[i] - m) ** 2 for x in xs)
        cov_t = (sum((xs[t][i] - m) * (t - tm) for t in range(n))
                 if var > 1e-9 else 0.0)
        corr = abs(cov_t) / math.sqrt(var * tvar) if var > 1e-9 else 0.0
        stats.append((var, corr))
    vmax = max(v for v, _ in stats) if stats else 0.0
    # two filters: trend (non-stationarity) and RELATIVE variance
    # (near-constant coordinates are noise without dynamics; fspectral v2 lesson)
    return [i for i, (v, c) in enumerate(stats)
            if v > 1e-9 and c <= 0.95 and v >= 0.02 * vmax]


def project(xs: list[list], keep: list[int]) -> list[list]:
    return [[x[i] for i in keep] for x in xs]


def _solve(Mat, rhs, d):
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
        out[r] = (b[r] - sum(m[r][c] * out[c] for c in range(r + 1, d))) / m[r][r]
    return out


def fit_lag(xs: list[list], lag: int = 1):
    """OLS x_{t+1} ~ [x_t, ..., x_{t-lag+1}] (centered).
    Returns (spectral_radius_lag1 | None, r2_holdout)."""
    d0 = len(xs[0])
    d = d0 * lag
    n = len(xs) - lag
    mean = [sum(x[i] for x in xs) / len(xs) for i in range(d0)]
    Z = [[xs[t - k][i] - mean[i] for k in range(lag) for i in range(d0)]
         for t in range(lag - 1, len(xs))]        # Z[j] ~ stack of lags
    Y = [[xs[t][i] - mean[i] for i in range(d0)]
         for t in range(lag, len(xs))]
    cut = int(len(Y) * 0.8)
    ZtZ = [[sum(Z[t][i] * Z[t][j] for t in range(cut)) for j in range(d)]
           for i in range(d)]
    for i in range(d):
        ZtZ[i][i] += 1e-6
    ZtY = [[sum(Z[t][i] * Y[t][j] for t in range(cut)) for j in range(d0)]
           for i in range(d)]
    A_cols = [_solve(ZtZ, [ZtY[i][j] for i in range(d)], d) for j in range(d0)]
    # hold-out R2
    sse = ssm = 0.0
    for t in range(cut, len(Y)):
        for i in range(d0):
            pred = sum(A_cols[i][j] * Z[t][j] for j in range(d))
            sse += (Y[t][i] - pred) ** 2
            ssm += Y[t][i] ** 2
    r2 = 1 - sse / max(ssm, 1e-9)
    lam = None
    if lag == 1:
        A = [[A_cols[i][j] for j in range(d)] for i in range(d0)]
        v = [1.0] * d0
        for _ in range(300):
            w = [sum(A[i][j] * v[j] for j in range(d0)) for i in range(d0)]
            nrm = math.sqrt(sum(c * c for c in w))
            if nrm < 1e-12:
                return 0.0, r2
            v = [c / nrm for c in w]
        Av = [sum(A[i][j] * v[j] for j in range(d0)) for i in range(d0)]
        lam = abs(sum(Av[i] * v[i] for i in range(d0))
                  / sum(v[i] * v[i] for i in range(d0)))
    return lam, r2


def variance(xs: list[list]) -> float:
    d = len(xs[0])
    m = [sum(x[i] for x in xs) / len(xs) for i in range(d)]
    return sum((x[i] - m[i]) ** 2 for x in xs for i in range(d)) / len(xs)


def markov_test(xs: list[list]) -> dict:
    """Revision §2.3: are the observables Markov? An order-2 model is
    significantly better than order-1 => non-Markov => P̂ is a MODEL, not a
    measurement (flag)."""
    _, r2_1 = fit_lag(xs, lag=1)
    _, r2_2 = fit_lag(xs, lag=2)
    return {"r2_lag1": round(r2_1, 3), "r2_lag2": round(r2_2, 3),
            "markov_ok": r2_2 - r2_1 < 0.05}


def calibrate(xs_healthy: list[list], seg_len: int = 50) -> dict:
    """Threshold from a HEALTHY window: first dictionary selection
    (select_coords — remembered in the calibration certificate), then
    sub-windows of seg_len -> spread of λ and var; threshold = max + 3*std
    (conservatively). Nothing by hand."""
    keep = select_coords(xs_healthy)
    if not keep:
        raise ValueError("calibrate: no informative coordinates in window")
    xs = project(xs_healthy, keep)
    n = len(xs)
    k = n // seg_len
    if k < 2:
        raise ValueError(f"calibrate: window too small ({n} pts, "
                         f"need >= {2 * seg_len})")
    lams, vars_ = [], []
    for i in range(k):
        seg = xs[i * seg_len:(i + 1) * seg_len + 1]
        lam, _ = fit_lag(seg, lag=1)
        lams.append(lam)
        vars_.append(variance(seg))
    ml = sum(lams) / len(lams)
    sl = math.sqrt(sum((l - ml) ** 2 for l in lams) / len(lams))
    mv = sum(vars_) / len(vars_)
    return {"keep": keep, "lam_ref": round(ml, 3),
            "lam_threshold": round(min(0.999, max(lams) + 3 * sl), 3),
            "var_ref": round(mv, 3), "var_floor": round(mv / 5, 3)}


def audit(xs_window: list[list], cal: dict) -> list[dict]:
    """Window verdicts against the calibrated thresholds (the dictionary comes
    from calibration)."""
    out = []
    xs_window = project(xs_window, cal["keep"])
    lam, r2 = fit_lag(xs_window, lag=1)
    var = variance(xs_window)
    if var < cal["var_floor"]:
        out.append({"kind": "variance_freeze", "var": round(var, 3),
                    "floor": cal["var_floor"]})
    elif lam is not None and lam > cal["lam_threshold"]:
        out.append({"kind": "spectral_drift", "lam": round(lam, 3),
                    "threshold": cal["lam_threshold"], "r2": round(r2, 2)})
    return out
