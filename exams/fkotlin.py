# -*- coding: utf-8 -*-
"""EXAM kotlin-stdlib (the "ink"): the Kotlin dialect reproduces the canonical
FOLD. For each genome: print Main.kt, compile with kotlinc, drive the flows'
events through the compiled Kotlin organism, and require FOLD-PARITY with the
core interpreter (base.fold_parity, the same certificate as D48/growdialect).
Transport is the D88 ports layer, orthogonal — this proves only the LANGUAGE.

Honest boundary: if no kotlinc/JDK is present, the exam REFUSES (skips) with a
hint rather than faking green.
"""
from __future__ import annotations

import pathlib
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

from onto.core import genome as G
from onto.core.organism import Organism
from onto.ports.base import fold_parity
from onto.dialects.kotlin_stdlib import skeleton as KSK
from onto.dialects.kotlin_stdlib import gates as KG

CONNECTOR = """
onto: 1
name: connector
retry_window: 64
events:
  CreateResourceRequested: {ref: str, name_len: int}
  ResourceConfirmed:       {ref: str, provider_id: int}
entities:
  resource:
    key: ref
    instances: dynamic
    state: {status: int, provider_id: int}
    init:  {status: 0, provider_id: 0}
    rules:
      request:
        when: CreateResourceRequested
        intent: accept a create request only if a name is present and not already active
        guard: "ev.name_len > 0 and s.status == 0"
        body: |
          s.status = 1
        contract: {post: "s.status == 1"}
      confirm:
        when: ResourceConfirmed
        intent: mark created with the provider id, only from the requested state
        guard: "s.status == 1"
        body: |
          s.status = 2
          s.provider_id = ev.provider_id
        contract: {post: "s.status == 2"}
queries:
  active: "sum(1 for r in resource if r.status == 2)"
"""

CONNECTOR_FLOWS = """
flows:
  happy:
    - post:  {id: e1, type: CreateResourceRequested, ref: x, name_len: 3}
    - post:  {id: e2, type: ResourceConfirmed, ref: x, provider_id: 99}
  validation_rejects_empty_name:
    - post:  {id: e3, type: CreateResourceRequested, ref: y, name_len: 0}
  idempotent_no_double_request:
    - post:  {id: e4, type: CreateResourceRequested, ref: x, name_len: 5}
    - post:  {id: e1, type: CreateResourceRequested, ref: x, name_len: 7}
"""

STARTER = """
onto: 1
name: starter
retry_window: 64
events:
  Counted: {counter: str, by: int}
entities:
  counter:
    key: counter
    instances: dynamic
    state: {total: int}
    init: {total: 0}
    rules:
      count:
        when: Counted
        guard: "ev.by > 0"
        body: |
          s.total = s.total + ev.by
        contract: {post: "s.total >= 0"}
queries:
  grand_total: "sum(c.total for c in counter)"
"""

STARTER_FLOWS = """
flows:
  happy:
    - post: {id: e1, type: Counted, counter: a, by: 5}
    - post: {id: e2, type: Counted, counter: a, by: 3}
    - post: {id: e3, type: Counted, counter: b, by: 10}
  guard_and_dedup:
    - post: {id: e4, type: Counted, counter: a, by: 0}
    - post: {id: e1, type: Counted, counter: a, by: 999}
"""


def _drive_ref(g):
    def drive(events):
        org = Organism(g, tempfile.mkdtemp(prefix="fk-ref-"))
        for e in events:
            org.handle(e)
        return org.snapshot()
    return drive


def _drive_kotlin(g, workdir):
    def drive(events):
        import json
        # D97: the kotlin organism now speaks the canon's flat-JSON codec
        # (file driver), same as the other dialects — one event per line.
        evf = workdir / "events.jsonl"
        evf.write_text("\n".join(json.dumps(e) for e in events) + "\n",
                       encoding="utf-8")
        ok, out = KG.run(workdir, str(evf))
        if not ok:
            raise RuntimeError("kotlin run failed:\n" + out)
        # the door prints the fold as {en:{inst:{field:val}}} JSON
        return json.loads(out.strip().splitlines()[-1])
    return drive


def _write(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
    f.write(text)
    f.close()
    return pathlib.Path(f.name)


def main():
    t0 = time.time()
    R = []

    ok, msg = KG.available()
    if not ok:
        print(f"\n=== EXAM kotlin-stdlib — SKIPPED (honest refusal) ===\n  · {msg}")
        return 0

    for name, gsrc, fsrc in [("connector", CONNECTOR, CONNECTOR_FLOWS),
                             ("starter", STARTER, STARTER_FLOWS)]:
        gpath = _write(gsrc)
        fpath = _write(fsrc)
        g = G.load(gpath)
        wd = pathlib.Path(tempfile.mkdtemp(prefix=f"fk-{name}-"))
        KSK.generate(g, wd)
        R.append((f"[{name}] Main.kt printed from genome",
                  (wd / "Main.kt").exists()))
        cok, cmsg = KG.build(wd)
        R.append((f"[{name}] kotlinc compiles the organism", cok, cmsg[-400:] if not cok else ""))
        if not cok:
            continue
        cx = fold_parity(str(gpath), str(fpath), _drive_ref(g), _drive_kotlin(g, wd), ROOT)
        R.append((f"[{name}] FOLD-PARITY with the core interpreter (byte-identical)",
                  cx is None, cx or ""))

    print(f"\n=== EXAM kotlin-stdlib (ink) ({time.time() - t0:.1f}s) ===")
    ok_all = True
    for row in R:
        label, passed = row[0], row[1]
        detail = row[2] if len(row) > 2 and not passed else ""
        print(f"  {'PASS' if passed else 'FAIL'}  {label}" + (f"\n        {detail}" if detail else ""))
        ok_all = ok_all and passed
    print("VERDICT:", "PASSED" if ok_all else "FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
