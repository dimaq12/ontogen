# -*- coding: utf-8 -*-
"""Membrane (DIRT wave; the DIRT doctrine from v0): a foreign organism gives
no contract — so we supply ASSUMPTIONS, compiled into drift MONITORS.

External in the genome: an island (a hand-written trusted python file behind
the membrane, the only place where network/IO is legal) + assumptions —
boolean Exprs over the WINDOWED call statistics: {latency_ms, error_rate_pct,
calls}. NOT a regex DSL (NOT §3) — the same Expr as the rest of the genome.

An assumption violation = a drift event in the ledger + a counter; hitting
the quota within the window -> cert=False (the right to trust the foreign
party is revoked — visible in /health.externals). An island error does NOT
bring the organism down: 502 to the outside, a minus in the statistics."""
from __future__ import annotations

import pathlib
import time
from collections import deque

from pydantic import BaseModel, ConfigDict, Field

from onto.core import expr as E

_STATS_TYPES = {"latency_ms": "int", "error_rate_pct": "int", "calls": "int"}
WINDOW = 50


class External(BaseModel):
    model_config = ConfigDict(extra="forbid")
    island: str                       # path to the python file (rel. to the genome root)
    provides: str                     # function name: def <provides>(payload) -> dict
    assumptions: list[str] = Field(default_factory=list)   # bool-Expr over the stats
    quota: int = 5                    # violations within the window before trust is revoked
    # D63 (pearl 4): a spec for GROWING the island with a model.
    # intent — an NL description of the integration (protocol, address/env,
    # response format, retry policy); cases — acceptance [{payload, expect}]:
    # expect is a subset of the response, the value "*" = the field must be
    # present. A hand-written island may lack them (grow is then impossible —
    # an honest refusal).
    intent: str = ""
    cases: list[dict] = Field(default_factory=list)


def validate_external(name: str, ext: External, base: pathlib.Path) -> list[str]:
    errs = []
    if not (base / ext.island).exists():
        errs.append(f"external {name}: island file not found: {ext.island}")
    for i, a in enumerate(ext.assumptions):
        try:
            t = E.typecheck_expr(E.parse_expr(a), dict(_STATS_TYPES))
            if t != "bool":
                errs.append(f"external {name}.assumptions[{i}]: must be bool")
        except E.ExprError as e:
            errs.append(f"external {name}.assumptions[{i}]: {e}")
    if not ext.assumptions:
        errs.append(f"external {name}: no assumptions — trusting a foreign "
                    f"organism blindly is contraband (v0 DIRT doctrine)")
    for i, c in enumerate(ext.cases):
        if not isinstance(c.get("payload"), dict) or not isinstance(c.get("expect"), dict):
            errs.append(f"external {name}.cases[{i}]: need payload{{}} and expect{{}}")
    return errs


def case_verdict(expect: dict, got: dict) -> str | None:
    """Check an acceptance case: expect is a subset of got; "*" = the field is
    present. None = green, otherwise a human-readable verdict (for CEGIS)."""
    for k, want in expect.items():
        if k not in got:
            return f"missing field '{k}' in response {got}"
        if want != "*" and got[k] != want:
            return f"field '{k}': expected {want!r}, got {got[k]!r}"
    return None


class MonitoredAdapter:
    """An island behind the membrane: call + windowed statistics + assumption monitors."""

    def __init__(self, name: str, ext: External, base: pathlib.Path, ledger):
        self.name = name
        self.ext = ext
        self.ledger = ledger
        self._trees = [E.parse_expr(a) for a in ext.assumptions]
        self._win: deque[tuple[int, bool]] = deque(maxlen=WINDOW)  # (ms, ok)
        self.violations = 0
        self.cert_valid = True
        ns: dict = {}
        code = (base / ext.island).read_text(encoding="utf-8")
        exec(compile(code, ext.island, "exec"), ns)   # noqa: S102 — the island is trusted
        if ext.provides not in ns:
            raise ValueError(f"island {ext.island} must define "
                             f"'{ext.provides}(payload) -> dict'")
        self._fn = ns[ext.provides]

    def stats(self) -> dict:
        calls = len(self._win)
        errs = sum(1 for _, ok in self._win if not ok)
        lat = max((ms for ms, _ in self._win), default=0)
        return {"latency_ms": lat, "error_rate_pct": (errs * 100) // max(calls, 1),
                "calls": calls}

    def call(self, payload: dict) -> tuple[int, dict]:
        t0 = time.perf_counter()
        try:
            out = self._fn(payload)
            ok = True
        except Exception as e:  # noqa: BLE001 — foreign dirt does not bring the organism down
            out = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            ok = False
        ms = int((time.perf_counter() - t0) * 1000)
        self._win.append((ms, ok))
        self._check()
        return (200 if ok else 502), out

    def _check(self) -> None:
        st = self.stats()
        for src, tree in zip(self.ext.assumptions, self._trees):
            if not E.eval_expr(tree, st):
                self.violations += 1
                self.ledger.record("drift_violation", {
                    "external": self.name, "assumption": src, "stats": st})
                if self.violations > self.ext.quota and self.cert_valid:
                    self.cert_valid = False
                    self.ledger.record("revoke_external_trust", {
                        "external": self.name,
                        "why": f"{self.violations} violations > quota "
                               f"{self.ext.quota} in window {WINDOW}"})

    def passport(self) -> dict:
        return {"cert_valid": self.cert_valid, "violations": self.violations,
                **self.stats()}
