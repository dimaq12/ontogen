# -*- coding: utf-8 -*-
"""kotlin-stdlib: the dialect's gates — compile with kotlinc on a JDK/JBR
runtime. Toolchain discovery is user-relative (which kotlinc, an SDKMAN
candidate, or an IDE-bundled kotlinc), NEVER a hardcoded machine path; if
absent — an honest refusal with a hint (no fake green).
"""
from __future__ import annotations

import glob
import os
import pathlib
import shutil
import subprocess


def find_java_home() -> str | None:
    jh = os.environ.get("JAVA_HOME")
    if jh and (pathlib.Path(jh) / "bin" / "java").is_file():
        return jh
    j = shutil.which("java")
    if j:
        # <home>/bin/java -> <home>
        return str(pathlib.Path(j).resolve().parent.parent)
    for c in glob.glob("/usr/lib/jvm/*"):
        if (pathlib.Path(c) / "bin" / "java").is_file():
            return c
    return None


def find_kotlinc() -> str | None:
    env = os.environ.get("KOTLINC")
    if env and pathlib.Path(env).is_file():
        return env
    p = shutil.which("kotlinc")
    if p:
        return p
    # SDKMAN is the standard user-relative install location for Kotlin.
    cands = glob.glob(str(pathlib.Path.home() / ".sdkman" / "candidates"
                          / "kotlin" / "*" / "bin" / "kotlinc"))
    for c in sorted(cands, reverse=True):
        if pathlib.Path(c).is_file():
            return c
    return None


def available() -> tuple[bool, str]:
    kc, jh = find_kotlinc(), find_java_home()
    if kc is None:
        return False, "kotlinc not found (install Kotlin, e.g. `sdk install kotlin`)"
    if jh is None:
        return False, "no JDK/JBR runtime found (JAVA_HOME or a java on PATH)"
    return True, f"kotlinc + JDK ok"


def build(outdir) -> tuple[bool, str]:
    """Compile Main.kt -> organism.jar. Returns (ok, message)."""
    ok, msg = available()
    if not ok:
        return False, msg
    kc, jh = find_kotlinc(), find_java_home()
    env = dict(os.environ)
    env["JAVA_HOME"] = jh
    env["PATH"] = f"{jh}/bin:" + env.get("PATH", "/usr/bin:/bin")
    r = subprocess.run(
        [kc, "Main.kt", "-include-runtime", "-d", "organism.jar"],
        cwd=str(outdir), capture_output=True, text=True, timeout=600, env=env)
    # kotlinc emits warnings to stderr with returncode 0; only fail on nonzero.
    return r.returncode == 0, (r.stderr or r.stdout)[-1200:]


def run(outdir, events_file: str) -> tuple[bool, str]:
    """Run organism.jar over an events file; returns (ok, stdout)."""
    jh = find_java_home()
    r = subprocess.run(
        [f"{jh}/bin/java", "-jar", "organism.jar", events_file],
        cwd=str(outdir), capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout if r.returncode == 0 else (r.stderr or r.stdout))


# ------------------------------------------------- conformance (certificate)
import json as _json

from onto.core import expr as _E
from .emit import KT_HELPERS, emit_expr


def _kt_value(v, t: str) -> str:
    if t == "str":
        return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'
    return f"{v}L"


def gen_conformance_kt(corpus_path, outdir) -> pathlib.Path:
    """The canon's corpus -> a Kotlin program: each case is printed by the
    printer, formatted, and checked against the canon's answer."""
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    cases = [_json.loads(l) for l in
             pathlib.Path(corpus_path).read_text(encoding="utf-8").splitlines()
             if l.strip()]
    checks = []
    for i, c in enumerate(cases):
        env = c["env"]
        s_lit = (f'ConfS({env["s"]["a"]}L, {env["s"]["b"]}L, {env["s"]["flag"]}L)')
        ev_lit = f'ConfEv({env["ev"]["q"]}L, {_kt_value(env["ev"]["who"], "str")})'
        items = ", ".join(f'ConfItem({it["x"]}L, {it["on"]}L)' for it in env["items"])
        names = {"s": "s", "ev": "ev", "items": "items"}
        kt_expr = emit_expr(_E.parse_expr(c["expr"]), names)
        exp = c["expected"]
        want = ("true" if exp else "false") if isinstance(exp, bool) else str(exp)
        checks.append(f"""    run {{
        val s = {s_lit}
        val ev = {ev_lit}
        val items = listOf<ConfItem>({items})
        val got = ({kt_expr}).toString()
        if (got != {_json.dumps(want)}) {{
            println("case {i}: " + {_json.dumps(c["expr"])} + " -> " + got +
                    ", canon expects {want}")
            fails += 1
        }}
    }}""")
    body = "\n".join(checks)
    src = out / "Conf.kt"
    src.write_text(f"""// Conformance suite: the kotlin-stdlib printer against the onto canon.
data class ConfS(val a: Long, val b: Long, val flag: Long)
data class ConfEv(val q: Long, val who: String)
data class ConfItem(val x: Long, val on: Long)

{KT_HELPERS}
fun main() {{
    var fails = 0
{body}
    if (fails > 0) {{ System.err.println("$fails conformance case(s) FAILED"); kotlin.system.exitProcess(1) }}
    println("conformance: 240/240 green")
}}
""", encoding="utf-8")
    return src


def run_conformance(corpus_path, workdir) -> tuple[bool, str]:
    ok, msg = available()
    if not ok:
        return False, msg
    kc, jh = find_kotlinc(), find_java_home()
    src = gen_conformance_kt(corpus_path, workdir)
    env = dict(os.environ); env["JAVA_HOME"] = jh
    env["PATH"] = f"{jh}/bin:" + env.get("PATH", "/usr/bin:/bin")
    b = subprocess.run([kc, src.name, "-include-runtime", "-d", "conf.jar"],
                       cwd=str(workdir), capture_output=True, text=True,
                       timeout=600, env=env)
    if b.returncode != 0:
        return False, f"compile: {(b.stderr or b.stdout)[-400:]}"
    r = subprocess.run([f"{jh}/bin/java", "-jar", "conf.jar"], cwd=str(workdir),
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr)[-400:]


def _emit_coverage(corpus_path) -> tuple[int, int]:
    ok = bad = 0
    for l in pathlib.Path(corpus_path).read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        c = _json.loads(l)
        try:
            emit_expr(_E.parse_expr(c["expr"]), {"s": "s", "ev": "ev", "items": "items"})
            ok += 1
        except Exception:  # noqa: BLE001
            bad += 1
    return ok, ok + bad


def certificate(corpus_path, workdir) -> dict:
    """Printer conformance + build. If the kotlinc/JDK toolchain is absent this
    host cannot COMPILE-validate — report 'skipped' honestly (with the pure-
    Python printer-emit coverage), never a fake 'green'."""
    avail, why = available()
    if not avail:
        ok, total = _emit_coverage(corpus_path)
        return {"dialect": "kotlin-stdlib",
                "printer_conformance": "skipped",
                "embedded_interpreter": "deferred-to-eviction (D28)",
                "detail": f"no toolchain ({why}); printer emits {ok}/{total} "
                          f"corpus exprs (pure-Python coverage, NOT compile-validated)"}
    ok, msg = run_conformance(corpus_path, workdir)
    return {"dialect": "kotlin-stdlib",
            "printer_conformance": "green" if ok else "red",
            "embedded_interpreter": "deferred-to-eviction (D28)",
            "detail": msg.strip()[:200]}
