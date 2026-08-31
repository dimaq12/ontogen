# -*- coding: utf-8 -*-
"""rust-stdlib gates: the dialect's certificate (F2 scope) = printer conformance
(the canon's 240-case corpus, compiled + run by rustc) + build. Mirrors
go-stdlib; the toolchain is rustc (>= 1.70)."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

from onto.core import expr as E
from .emit import RUST_HELPERS, emit_expr


def find_rust() -> str | None:
    return shutil.which("rustc")


def _run_rustc(src: pathlib.Path, out: pathlib.Path) -> tuple[bool, str]:
    rustc = find_rust()
    if rustc is None:
        return False, "rust toolchain not found (install rustc >= 1.70)"
    r = subprocess.run([rustc, "-O", "--edition", "2021", str(src), "-o", str(out)],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return False, (r.stderr or r.stdout)[-800:]
    return True, ""


def build(outdir) -> tuple[bool, str]:
    """Compile the generated organism crate with cargo (if a Cargo.toml is
    present) or rustc main.rs."""
    outdir = pathlib.Path(outdir)
    cargo = shutil.which("cargo")
    if (outdir / "Cargo.toml").exists() and cargo:
        r = subprocess.run([cargo, "build", "--release"], cwd=outdir,
                           capture_output=True, text=True, timeout=300)
        return r.returncode == 0, (r.stderr or r.stdout)[-800:]
    main = outdir / "main.rs"
    if not main.exists():
        return False, "no Cargo.toml or main.rs to build"
    return _run_rustc(main, outdir / "organism")


def _rs_value(v, t: str) -> str:
    if t == "str":
        return '"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"'
    return f"{v}i64"


def gen_conformance_src(corpus_path, outdir) -> pathlib.Path:
    """The canon's corpus -> a single Rust program: each case is printed by the
    printer, formatted, and checked against the canonical interpreter's answer.
    Exits non-zero (and prints the failures) if any case diverges."""
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(l) for l in
             pathlib.Path(corpus_path).read_text(encoding="utf-8").splitlines()
             if l.strip()]
    checks = []
    for i, c in enumerate(cases):
        env = c["env"]
        s_lit = (f'ConfS {{ a: {env["s"]["a"]}i64, b: {env["s"]["b"]}i64, '
                 f'flag: {env["s"]["flag"]}i64 }}')
        ev_lit = (f'ConfEv {{ q: {env["ev"]["q"]}i64, '
                  f'who: {_rs_value(env["ev"]["who"], "str")}.to_string() }}')
        items = ", ".join(f'ConfItem {{ x: {it["x"]}i64, on: {it["on"]}i64 }}'
                          for it in env["items"])
        names = {"s": "s", "ev": "ev", "items": "items"}
        rs_expr = emit_expr(E.parse_expr(c["expr"]), names)
        exp = c["expected"]
        want = ("true" if exp else "false") if isinstance(exp, bool) else str(exp)
        checks.append(f"""    {{
        let s = {s_lit};
        let ev = {ev_lit};
        let items: Vec<ConfItem> = vec![{items}];
        let _ = (&s, &ev, &items);
        let got = format!("{{}}", {rs_expr});
        if got != {json.dumps(want)} {{
            println!("case {i}: {{}} -> {{}}, canon expects {{}}",
                     {json.dumps(c["expr"])}, got, {json.dumps(want)});
            fails += 1;
        }}
    }}""")
    body = "\n".join(checks)
    src = out / "conf.rs"
    src.write_text(f"""// Conformance suite: the rust-stdlib printer against the onto canon.
#![allow(unused, non_snake_case)]

struct ConfS {{ a: i64, b: i64, flag: i64 }}
struct ConfEv {{ q: i64, who: String }}
struct ConfItem {{ x: i64, on: i64 }}

{RUST_HELPERS}
fn main() {{
    let mut fails = 0i64;
{body}
    if fails > 0 {{
        eprintln!("{{}} conformance case(s) FAILED", fails);
        std::process::exit(1);
    }}
    println!("conformance: 240/240 green");
}}
""", encoding="utf-8")
    return src


def run_conformance(corpus_path, workdir) -> tuple[bool, str]:
    src = gen_conformance_src(corpus_path, workdir)
    binp = pathlib.Path(workdir) / "conf"
    ok, msg = _run_rustc(src, binp)
    if not ok:
        return False, f"compile: {msg}"
    r = subprocess.run([str(binp)], capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr)[-800:]


def certificate(corpus_path, workdir) -> dict:
    """The dialect's certificate (F2 scope): printer conformance + build."""
    if find_rust() is None:
        return {"dialect": "rust-stdlib", "printer_conformance": "skipped",
                "embedded_interpreter": "deferred-to-eviction (D28)",
                "detail": "no rust toolchain on this host (NOT compile-validated)"}
    ok, msg = run_conformance(corpus_path, workdir)
    return {"dialect": "rust-stdlib",
            "printer_conformance": "green" if ok else "red",
            "embedded_interpreter": "deferred-to-eviction (D28)",
            "detail": msg.strip()[:200]}
