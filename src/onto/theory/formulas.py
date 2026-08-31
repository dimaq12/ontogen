# -*- coding: utf-8 -*-
"""theory/: registry of executable formulas with preconditions (SPEC §5.1).

A formula without machine-checkable preconditions does not belong here; a theorem
name outside theory/ is a review error (NOT §13). Every formula MUST be able to make
a DECISION (change the engine's output) — otherwise it is decoration (S3): the Placer
assembles the "formula -> decision" table, and an empty row is a candidate for removal.
"""
from __future__ import annotations

from dataclasses import dataclass

from onto.theory.provenance import V, derived


class PrecondError(ValueError):
    """A formula's precondition is violated — MUST NOT apply it (and not silently)."""


@dataclass(frozen=True)
class Decision:
    formula: str
    inputs: dict
    verdict: str        # human-readable decision
    value: V | None     # derived number (if any)

    def row(self) -> str:
        ins = ", ".join(f"{k}={v.value:g}({v.cls})" for k, v in self.inputs.items())
        return f"{self.formula}({ins}) -> {self.verdict}"


def warm_gain(rate_per_s: V, t_cold_ns: V, t_warm_ns: V,
              horizon_s: V, build_cost_s: V) -> Decision:
    """Payoff of warmup: gain = rate * horizon * (t_cold - t_warm).
    Decision: WARM if the time won over the horizon > the cost of materialization.
    Preconditions: rate >= 0; t_cold >= t_warm > 0; horizon > 0."""
    if rate_per_s.value < 0:
        raise PrecondError("warm_gain: rate must be >= 0")
    if not (t_cold_ns.value >= t_warm_ns.value > 0):
        raise PrecondError("warm_gain: need t_cold >= t_warm > 0 "
                           f"(got {t_cold_ns.value} vs {t_warm_ns.value})")
    if horizon_s.value <= 0:
        raise PrecondError("warm_gain: horizon must be > 0")
    ins = {"rate": rate_per_s, "t_cold_ns": t_cold_ns, "t_warm_ns": t_warm_ns,
           "horizon_s": horizon_s, "build_cost_s": build_cost_s}
    gain_s = rate_per_s.value * horizon_s.value * \
        (t_cold_ns.value - t_warm_ns.value) * 1e-9
    val = derived(gain_s, "warm_gain", ins)
    if gain_s > build_cost_s.value:
        verdict = (f"WARM (gain {gain_s:.2f}s over horizon > build "
                   f"{build_cost_s.value:.2f}s)")
    else:
        verdict = (f"STAY-INTERPRETED (gain {gain_s:.2f}s <= build "
                   f"{build_cost_s.value:.2f}s)")
    return Decision("warm_gain", ins, verdict, val)


def latency_floor(t_max_ms: V, floor_warm_ms: V) -> Decision:
    """Attainability of the demand: t_max cannot be below the MEASURED floor of the
    best materialization. Decision: REFUSE with arithmetic (how to pay for it) or OK.
    Precondition: floor is measured (> 0)."""
    if floor_warm_ms.value <= 0:
        raise PrecondError("latency_floor: floor must be measured > 0")
    ins = {"t_max_ms": t_max_ms, "floor_warm_ms": floor_warm_ms}
    if t_max_ms.value < floor_warm_ms.value:
        verdict = (f"REFUSE: demanded {t_max_ms.value:g}ms < measured warm "
                   f"floor {floor_warm_ms.value:g}ms; pay with one of: raise "
                   f"t_max >= {floor_warm_ms.value:g}ms, shrink scope, or buy "
                   f"staleness (cache tier — not in v1)")
    else:
        verdict = (f"OK (headroom {t_max_ms.value - floor_warm_ms.value:g}ms)")
    return Decision("latency_floor", ins, verdict, None)


def evict_idle(rate_per_s: V, evict_below_per_s: V, window_s: V) -> Decision:
    """Eviction of the cooled: rate over the window below threshold — the warmed
    body/service is evicted (the path falls back to the interpreter without loss of
    correctness). Precondition: window > 0."""
    if window_s.value <= 0:
        raise PrecondError("evict_idle: window must be > 0")
    ins = {"rate": rate_per_s, "evict_below": evict_below_per_s,
           "window_s": window_s}
    if rate_per_s.value < evict_below_per_s.value:
        verdict = (f"EVICT (rate {rate_per_s.value:.2f}/s < "
                   f"{evict_below_per_s.value:g}/s over {window_s.value:g}s)")
    else:
        verdict = f"KEEP-WARM (rate {rate_per_s.value:.2f}/s)"
    return Decision("evict_idle", ins, verdict, None)


REGISTRY = {
    "warm_gain": warm_gain,
    "latency_floor": latency_floor,
    "evict_idle": evict_idle,
}
