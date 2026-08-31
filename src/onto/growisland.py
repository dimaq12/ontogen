# -*- coding: utf-8 -*-
"""Growing an ISLAND with a model (IDEAL pearl 4, D63).

An island = the single spot in the network, behind a membrane of assumptions —
which means an SLM can write it: the intelligence lives in the gate, not in the
executor.
Gates (CEGIS, counterexamples into the prompt; cache keyed by the spec hash — a
certified artifact, like a skill/dialect):
  1) compile + def <provides>(payload) + a WHITELIST of imports
     (a sanitary membrane; the final accept of the grown code is a human);
  2) ACCEPTANCE THROUGH FLAKE: external.cases are run through MonitoredAdapter
     against a LIVE (in the exam, flaky) upstream: without retries the cases go
     red — robustness is forced by the gate, not by trust;
  3) attestation after the run: cert_valid=True (the assumption-Exprs hold).
"""
from __future__ import annotations

import hashlib
import pathlib
import re

from onto.ribosome import Provider, strip_code

ATTEMPTS_PER_MODEL = 4
ALLOWED_IMPORTS = {"json", "os", "time", "math", "hashlib", "urllib",
                   "urllib.request", "urllib.error", "urllib.parse"}
_IMPORT_RE = re.compile(r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)",
                        re.M)


def sanitize(code: str, provides: str) -> str | None:
    """None = green, otherwise a verdict. Compilation + provides + the import membrane."""
    try:
        compile(code, "<island>", "exec")
    except SyntaxError as e:
        return f"- syntax error: {e}"
    bad = []
    for m in _IMPORT_RE.finditer(code):
        mod = (m.group(1) or m.group(2)).split(".")[0]
        full = m.group(1) or m.group(2)
        if mod not in {a.split(".")[0] for a in ALLOWED_IMPORTS}:
            bad.append(full)
    if bad:
        return ("- forbidden imports (island whitelist: "
                f"{sorted(ALLOWED_IMPORTS)}): {bad}")
    if not re.search(rf"^def {re.escape(provides)}\(", code, re.M):
        return f"- must define top-level 'def {provides}(payload):'"
    return None


def grow_prompt(name: str, ext, counterexamples: list[str]) -> str:
    cx = ("\nYour previous attempts FAILED these machine checks — fix "
          "exactly these:\n" + "\n".join(counterexamples)) if counterexamples else ""
    cases = "\n".join(f"  {c['payload']} -> response must contain {c['expect']}"
                      for c in ext.cases)
    return f"""You write ONE small Python adapter file (an "island") for an external integration.
Only stdlib, only these imports allowed: json, os, time, math, hashlib, urllib.

Integration description (source of truth):
{ext.intent}

The file must define exactly:
    def {ext.provides}(payload: dict) -> dict

Hard requirements:
- The upstream service IS FLAKY (random 5xx and slow responses). Your adapter
  MUST retry failed/erroring calls (up to 3 retries, short pause) so that the
  acceptance cases below pass despite the flakiness. Use short timeouts.
- On final failure after retries: raise an exception (the membrane catches it).
- No prints, no logging, no threads, no state between calls.

These acceptance cases will be executed by a machine gate against a LIVE
flaky upstream (payload -> required subset of your returned dict; "*" means
"field must be present"):
{cases}

Operating assumptions monitored by the membrane (your adapter must fit them):
{ext.assumptions}
{cx}
Output ONLY the complete Python code of the island in one ```python fence."""


def gates(code: str, name: str, ext, base: pathlib.Path, island_rel: str):
    """None = green, otherwise a counterexample for CEGIS. Runs ALL cases through
    a live MonitoredAdapter (the upstream flakiness hits for real)."""
    from onto.core import membrane as MB

    verdict = sanitize(code, ext.provides)
    if verdict:
        return verdict
    p = base / island_rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code, encoding="utf-8")

    class _Ledger:                      # a local collector of the gate's drift events
        def __init__(self):
            self.records = []

        def record(self, kind, payload):
            self.records.append((kind, payload))

    led = _Ledger()
    try:
        # judge EXACTLY the file we wrote (island_rel), not ext.island —
        # otherwise the gate's tooth silently judges a neighboring artifact (found by the exam)
        ad = MB.MonitoredAdapter(name, ext.model_copy(update={"island": island_rel}),
                                 base, led)
    except Exception as e:  # noqa: BLE001
        return f"- island failed to load: {type(e).__name__}: {e}"
    for i, case in enumerate(ext.cases):
        http_code, out = ad.call(dict(case["payload"]))
        if http_code != 200:
            return (f"- case[{i}] {case['payload']}: adapter raised after "
                    f"retries: {out.get('error', out)}")
        bad = MB.case_verdict(case["expect"], out)
        if bad:
            return f"- case[{i}] {case['payload']}: {bad}"
    if not ad.cert_valid:
        drift = [p for k, p in led.records if k == "drift_violation"][-1:]
        return (f"- assumptions violated during acceptance (trust revoked): "
                f"{drift}")
    return None


def grow(genome_dir, name: str, provider: Provider, log=print) -> dict:
    """Grow the island for the genome's external <name>. Returns: telemetry."""
    from onto.core import genome as G
    from onto.core import membrane as MB

    base = pathlib.Path(genome_dir)
    g = G.load(base)
    if base.is_file():
        base = base.parent           # islands and the cache live next to the genome
    if name not in g.externals:
        raise SystemExit(f"no external '{name}' in genome "
                         f"(have: {sorted(g.externals)})")
    ext = MB.External.model_validate(g.externals[name])
    if not ext.intent or not ext.cases:
        raise SystemExit(f"external '{name}' has no intent/cases — nothing to "
                         "grow from (write them, or keep a hand-written island)")
    tele: dict = {"island_manual": False, "attempts": []}
    spec = ext.intent + repr(ext.cases) + repr(ext.assumptions) + ext.provides
    key = hashlib.sha256(spec.encode()).hexdigest()[:16]
    cache_dir = base / ".grown"
    cache_dir.mkdir(exist_ok=True)

    for model in provider.ladder("island"):
        ck = cache_dir / f"{name}.{key}.{model.replace('/', '_')}.py"
        cxs: list[str] = []
        if ck.exists():
            code = ck.read_text(encoding="utf-8")
            if gates(code, name, ext, base, ext.island) is None:
                log(f"  growisland: CACHE hit [{model}]")
                tele["model"], tele["cache"] = model, True
                return tele
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            raw = provider.generate(model, grow_prompt(name, ext, cxs),
                                    seed=42,
                                    tag=f"grow:island:{name}:{model}:{attempt}",
                                    max_tokens=4000)
            code = strip_code(raw)
            verdict = gates(code, name, ext, base, ext.island)
            tele["attempts"].append({"model": model, "attempt": attempt,
                                     "verdict": (verdict or "GREEN")[:160]})
            if verdict is None:
                ck.write_text(code, encoding="utf-8")
                log(f"  growisland: GREEN [{model}] attempt {attempt}")
                tele["model"], tele["cache"] = model, False
                return tele
            cxs.append(verdict)
            log(f"  growisland: red [{model}] attempt {attempt}: {verdict[:120]}")
        log(f"  growisland: ladder step exhausted [{model}] -> escalate")
    tele["island_manual"] = True        # ladder exhausted: a hand-written island is a legal outcome
    return tele
