# -*- coding: utf-8 -*-
"""Growing a PORT codec with a model (D89): the transport tissue joins the
same doctrine as dialects (growdialect), islands (growisland) and the dialect
generator (growgen) — you DECLARE the beast (intent + cases), the model writes
the wire codec, and the GATE certifies it. No tissue is hand-written.

A port codec is a module defining exactly:
    def decode(msg: dict) -> dict            # wire message -> canonical event
    def encode(ev_name: str, fields: dict, ev_id: str) -> dict   # event -> wire

Gates (CEGIS; counterexamples into the prompt; cache keyed by the spec hash):
  1) sanitize: compile + both functions + a stdlib import whitelist;
  2) ROUND-TRIP over the declared cases: decode(wire) ⊇ event, and
     encode(event) ⊇ wire — the codec is faithful in both directions;
  3) FOLD-PARITY (the port law, base.fold_parity): drive the genome's flows as
     WIRE (encode canonical -> wire, decode with the grown codec -> handle) and
     require the fold to be BYTE-IDENTICAL to driving the canonical events.
     This is the same certificate that governs dialects (D48/growdialect).
Offline: the whole loop runs on the in-process Bus, zero external deps — the
grown codec is proven without the real beast; a real broker is the same codec
behind a driver swap at deploy (the dependency lives in the door, not the brain).
"""
from __future__ import annotations

import hashlib
import re

from onto.ribosome import Provider, strip_code

ATTEMPTS_PER_MODEL = 4
ALLOWED_IMPORTS = {"json", "os", "time", "math", "hashlib", "base64", "re"}
_IMPORT_RE = re.compile(r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)",
                        re.M)


def sanitize(code: str) -> str | None:
    try:
        compile(code, "<port-codec>", "exec")
    except SyntaxError as e:
        return f"- syntax error: {e}"
    bad = []
    for m in _IMPORT_RE.finditer(code):
        mod = (m.group(1) or m.group(2)).split(".")[0]
        if mod not in {a.split(".")[0] for a in ALLOWED_IMPORTS}:
            bad.append(m.group(1) or m.group(2))
    if bad:
        return f"- forbidden imports (whitelist {sorted(ALLOWED_IMPORTS)}): {bad}"
    for fn in ("decode", "encode"):
        if not re.search(rf"^def {fn}\(", code, re.M):
            return f"- must define top-level 'def {fn}(...)'"
    return None


def _load(code: str):
    ns: dict = {}
    exec(compile(code, "<port-codec>", "exec"), ns)   # noqa: S102 - gated above
    return ns["decode"], ns["encode"]


def _subset(want: dict, got: dict) -> str | None:
    if not isinstance(got, dict):
        return f"expected a dict, got {type(got).__name__}"
    for k, v in want.items():
        if k not in got:
            return f"missing key '{k}' in {got}"
        if got[k] != v:
            return f"key '{k}': expected {v!r}, got {got[k]!r}"
    return None


def grow_prompt(spec: dict, counterexamples: list) -> str:
    cx = ("\nYour previous attempt FAILED these machine checks — fix exactly "
          "these:\n" + "\n".join(counterexamples)) if counterexamples else ""
    cases = "\n".join(
        f"  decode({c['wire']}) must contain {c['event']}; "
        f"encode from {c['event']} must contain {c['wire']}"
        for c in spec.get("cases", []))
    return f"""You write ONE small Python module: the WIRE CODEC of a transport port.
Only the standard library (json, base64, re, math, hashlib, os, time).

Define EXACTLY two top-level functions:
    def decode(msg: dict) -> dict
        # a wire message (already parsed to a dict) -> a canonical event dict
        # {{"id": str, "type": <event name>, <field>: <value>, ...}}
    def encode(ev_name: str, fields: dict, ev_id: str) -> dict
        # a canonical event -> a wire message dict for this beast

Wire format (source of truth):
{spec.get('intent','')}

These acceptance cases will be checked BOTH directions (subset match):
{cases}

Hard rules:
- decode and encode must be inverse on the observable content (round-trip).
- No global state, no I/O, no prints — pure functions.
- The canonical event ALWAYS has 'id' and 'type'; preserve them through the codec.
{cx}
Output ONLY the complete Python module in one ```python fence."""


def gates(code, spec, genome_path, flows_path, root) -> str | None:
    v = sanitize(code)
    if v:
        return v
    try:
        decode, encode = _load(code)
    except Exception as e:  # noqa: BLE001
        return f"- codec failed to load: {type(e).__name__}: {e}"

    # (2) round-trip over cases, both directions
    for i, c in enumerate(spec.get("cases", [])):
        try:
            got = decode(dict(c["wire"]))
        except Exception as e:  # noqa: BLE001
            return f"- decode(case[{i}]) raised: {type(e).__name__}: {e}"
        bad = _subset(c["event"], got)
        if bad:
            return f"- decode(case[{i}]) {c['wire']}: {bad}"
        ev = c["event"]
        fields = {k: val for k, val in ev.items() if k not in ("id", "type")}
        try:
            wire = encode(ev["type"], fields, ev.get("id", "x"))
        except Exception as e:  # noqa: BLE001
            return f"- encode(case[{i}]) raised: {type(e).__name__}: {e}"
        bad = _subset(c["wire"], wire)
        if bad:
            return f"- encode(case[{i}]) {ev}: {bad}"

    # (3) FOLD-PARITY: drive flows as WIRE (encode->decode) vs canonical
    import threading
    import tempfile
    from onto.core import genome as G
    from onto.core.organism import Organism
    from onto.ports.base import fold_parity
    g = G.load(genome_path)

    def drive_canonical(events):
        org = Organism(g, tempfile.mkdtemp())
        for ev in events:
            org.handle(ev)
        return org.snapshot()

    def drive_wire(events):
        org = Organism(g, tempfile.mkdtemp())
        for ev in events:
            fields = {k: v for k, v in ev.items() if k not in ("id", "type")}
            wire = encode(ev["type"], fields, ev["id"])
            back = decode(wire)                 # through the grown codec
            org.handle(back)
        return org.snapshot()

    par = fold_parity(genome_path, flows_path, drive_canonical, drive_wire, root)
    if par:
        return f"- FOLD PARITY through the codec: {par}"
    return None


def grow(spec: dict, genome_path, flows_path, provider: Provider, root,
         out_dir=None, ladder=None, log=print) -> dict:
    import pathlib
    key = hashlib.sha256(
        (spec.get("intent", "") + repr(spec.get("cases", []))).encode()
    ).hexdigest()[:16]
    out = pathlib.Path(out_dir) if out_dir else pathlib.Path(genome_path).parent / ".grown_ports"
    out.mkdir(parents=True, exist_ok=True)
    tele: dict = {"island": False, "attempts": []}
    ladder = ladder or provider.ladder("island")
    for model in ladder:
        ck = out / f"{spec.get('name','port')}.{key}.{model.replace('/', '_')}.py"
        cxs: list = []
        if ck.exists():
            if gates(ck.read_text(), spec, genome_path, flows_path, root) is None:
                (out / f"{spec.get('name','port')}.py").write_text(ck.read_text())
                log(f"  growport: CACHE hit [{model}]")
                tele.update(model=model, cache=True)
                return tele
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            raw = provider.generate(model, grow_prompt(spec, cxs), seed=42,
                                    tag=f"growport:{spec.get('name')}:{model}:{attempt}",
                                    max_tokens=3000)
            code = strip_code(raw)
            verdict = gates(code, spec, genome_path, flows_path, root)
            tele["attempts"].append({"model": model, "attempt": attempt,
                                     "verdict": (verdict or "GREEN")[:160]})
            if verdict is None:
                ck.write_text(code)
                (out / f"{spec.get('name','port')}.py").write_text(code)
                log(f"  growport: GREEN [{model}] attempt {attempt}")
                tele.update(model=model, cache=False)
                return tele
            cxs.append(verdict)
            log(f"  growport: red [{model}] attempt {attempt}: {verdict[:110]}")
    tele["island"] = True
    return tele
