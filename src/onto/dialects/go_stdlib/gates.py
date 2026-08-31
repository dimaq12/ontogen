# -*- coding: utf-8 -*-
"""go-stdlib: the dialect's gates — build + the conformance printer (D28 scope F2:
a dialect's certificate = the printer reproduces the canon's conformance corpus;
an embedded runtime interpreter comes at the first eviction, F5).

Toolchain — per D18: which(go) or ~/.local/go/bin/go (user-relative,
NOT a machine path); if absent — an honest refusal with a hint.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

from onto.core import expr as E
from onto.dialects.go_stdlib.emit import GO_HELPERS, emit_expr, goname


def find_go() -> str | None:
    p = shutil.which("go")
    if p:
        return p
    cand = pathlib.Path.home() / ".local" / "go" / "bin" / "go"
    return str(cand) if cand.is_file() else None


def _run_go(args: list[str], cwd) -> tuple[bool, str]:
    go = find_go()
    if go is None:
        return False, "go toolchain not found (install go >= 1.21 or put it in ~/.local/go)"
    r = subprocess.run([go, *args], cwd=cwd, capture_output=True, text=True,
                       timeout=300,
                       env={"PATH": "/usr/bin:/bin",
                            "HOME": str(pathlib.Path.home()),
                            "GOFLAGS": "-trimpath"})
    return r.returncode == 0, (r.stderr or r.stdout)[-800:]


def build(outdir) -> tuple[bool, str]:
    return _run_go(["build", "-o", "organism", "."], outdir)


def vet(outdir) -> tuple[bool, str]:
    return _run_go(["vet", "."], outdir)


# ------------------------------------------------- conformance (certificate)

def _go_value(v, t: str) -> str:
    if t == "str":
        return '"' + str(v).replace('"', '\\"') + '"'
    return str(v)


def gen_conformance_pkg(corpus_path, outdir) -> pathlib.Path:
    """The canon's corpus -> a Go package with a test: each case is printed by
    the printer and checked against the canonical interpreter's expectation."""
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "go.mod").write_text("module conformance_check\n\ngo 1.22\n")
    cases = [json.loads(l) for l in
             pathlib.Path(corpus_path).read_text(encoding="utf-8").splitlines() if l.strip()]
    checks = []
    for i, c in enumerate(cases):
        env = c["env"]
        s_lit = f'ConfS{{A: {env["s"]["a"]}, B: {env["s"]["b"]}, Flag: {env["s"]["flag"]}}}'
        ev_lit = f'ConfEv{{Q: {env["ev"]["q"]}, Who: {_go_value(env["ev"]["who"], "str")}}}'
        items = ", ".join(f'{{X: {it["x"]}, On: {it["on"]}}}' for it in env["items"])
        names = {"s": "s", "ev": "ev", "items": "items"}
        go_expr = emit_expr(E.parse_expr(c["expr"]), names)
        exp = c["expected"]
        if isinstance(exp, bool):
            got = f"fmt.Sprint({go_expr})"
            want = "true" if exp else "false"
        else:
            got = f"fmt.Sprint({go_expr})"
            want = str(exp)
        checks.append(f"""\tfunc() {{
\t\ts := {s_lit}
\t\tev := {ev_lit}
\t\titems := []ConfItem{{{items}}}
\t\t_ = s; _ = ev; _ = items
\t\tif got := {got}; got != "{want}" {{
\t\t\tt.Errorf("case {i}: %s -> %s, canon expects {want}", {json.dumps(c["expr"])}, got)
\t\t}}
\t}}()""")
    body = "\n".join(checks)
    (out / "conf_test.go").write_text(f"""// Conformance suite (D17/D28): the go-stdlib printer against the onto canon.
package main

import (
\t"fmt"
\t"testing"
)

type ConfS struct {{ A, B, Flag int64 }}
type ConfEv struct {{ Q int64; Who string }}
type ConfItem struct {{ X, On int64 }}

func TestConformance(t *testing.T) {{
{body}
}}
""")
    (out / "main.go").write_text(
        "package main\n\n" + GO_HELPERS + "\nfunc main() {}\n")
    return out


def run_conformance(corpus_path, workdir) -> tuple[bool, str]:
    pkg = gen_conformance_pkg(corpus_path, workdir)
    return _run_go(["test", "."], pkg)


def certificate(corpus_path, workdir) -> dict:
    """The dialect's certificate (F2 scope): printer conformance + build."""
    ok, msg = run_conformance(corpus_path, workdir)
    return {"dialect": "go-stdlib", "printer_conformance": "green" if ok else "red",
            "embedded_interpreter": "deferred-to-eviction (D28)", "detail": msg.strip()[:200]}
