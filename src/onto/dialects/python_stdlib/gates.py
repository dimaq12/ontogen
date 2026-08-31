# -*- coding: utf-8 -*-
"""python-stdlib: the gates — compilation + the conformance printer (D28 scope).

The runner is the engine's own Python interpreter (sys.executable): the dialect
runs on the same language version as the canon, so the semantics are native by construction."""
from __future__ import annotations

import ast as _ast
import json
import pathlib
import subprocess
import sys

from onto.core import expr as E


def build(outdir) -> tuple[bool, str]:
    """The "build" = compilation of the generated organism.py."""
    p = pathlib.Path(outdir) / "organism.py"
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)],
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stderr or "ok")[-500:]


def gen_conformance_script(corpus_path, outdir) -> pathlib.Path:
    """The canon's corpus -> a self-checking script: the printer (ast.unparse) +
    native Python semantics must reproduce the canon's expectations."""
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(l) for l in
             pathlib.Path(corpus_path).read_text(encoding="utf-8").splitlines()
             if l.strip()]
    checks = []
    for i, c in enumerate(cases):
        src = _ast.unparse(E.parse_expr(c["expr"]))     # the printer = unparse (D23)
        checks.append(
            f"    run({i}, {c['expr']!r}, lambda s, ev, items: ({src}), "
            f"{c['env']['s']!r}, {c['env']['ev']!r}, {c['env']['items']!r}, "
            f"{c['expected']!r})")
    body = "\n".join(checks)
    script = out / "conf_check.py"
    script.write_text(f"""# Conformance suite (D17/D28): the python-stdlib printer against the onto canon.
from types import SimpleNamespace as NS

fails = []


def run(i, expr, fn, s, ev, items, expected):
    got = fn(NS(**s), NS(**ev), [NS(**it) for it in items])
    if got != expected:
        fails.append(f"case {{i}}: {{expr}} -> {{got}}, canon expects {{expected}}")


def main():
{body}
    if fails:
        for f in fails[:20]:
            print(f)
        raise SystemExit(1)
    print("conformance: PASS")


main()
""", encoding="utf-8")
    return script


def run_conformance(corpus_path, workdir) -> tuple[bool, str]:
    script = gen_conformance_script(corpus_path, workdir)
    r = subprocess.run([sys.executable, str(script)],
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr)[-500:]


def certificate(corpus_path, workdir) -> dict:
    ok, msg = run_conformance(corpus_path, workdir)
    return {"dialect": "python-stdlib",
            "printer_conformance": "green" if ok else "red",
            "embedded_interpreter": "native (dialect language = canon language)",
            "detail": msg.strip()[:200]}
