# -*- coding: utf-8 -*-
"""EXAM SHIP P3+P4: the packaged engine installs into a CLEAN environment and
works from second zero WITHOUT the repo and WITHOUT network — templates ship
as package data, court/serve run on the reference interpreter (no dialect
toolchain). This is the "zero machine" claim, mechanized."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
UV = pathlib.Path.home() / ".local/bin/uv"
R = []


def main():
    t0 = time.time()
    # 1. build the wheel
    dist = ROOT / "dist"
    for f in dist.glob("*.whl") if dist.exists() else []:
        f.unlink()
    b = subprocess.run([str(UV), "build", "--wheel"], cwd=ROOT,
                       capture_output=True, text=True)
    wheels = list(dist.glob("*.whl")) if dist.exists() else []
    R.append(("wheel builds", b.returncode == 0 and len(wheels) == 1))
    if not wheels:
        print(b.stderr[-500:])
        return _report(t0)
    wheel = wheels[0]

    # 2. install into a CLEAN venv (no repo on the path)
    env_dir = pathlib.Path(tempfile.mkdtemp(prefix="ship-venv-"))
    subprocess.run([str(UV), "venv", str(env_dir)], capture_output=True)
    py = env_dir / "bin" / "python"
    onto = env_dir / "bin" / "onto"
    pip = subprocess.run([str(UV), "pip", "install", "--python", str(py),
                          str(wheel)], capture_output=True, text=True)
    R.append(("wheel installs into a clean venv (entry point 'onto')",
              pip.returncode == 0 and onto.exists()))

    # run everything from a temp CWD far from the repo, env stripped of PYTHONPATH
    work = pathlib.Path(tempfile.mkdtemp(prefix="ship-work-"))
    clean_env = {"PATH": "/usr/bin:/bin", "HOME": str(work)}

    def run(args, cwd=work):
        return subprocess.run([str(onto)] + args, cwd=cwd,
                              capture_output=True, text=True, env=clean_env)

    # 3. onto version (installed, no repo)
    v = run(["version"])
    R.append((f"onto version (installed, no repo): {v.stdout.strip()}",
              v.returncode == 0 and "onto 1." in v.stdout))

    # 4. onto new from PACKAGE DATA (no repo, no network)
    proj = work / "myapp"
    nw = run(["new", str(proj), "--template", "hotel"])
    R.append(("onto new --template hotel from package data (no repo)",
              nw.returncode == 0 and (proj / "genome.yaml").exists()
              and (proj / "modules").is_dir()))

    # 5. court proves the packaged template (offline, SMT only)
    ct = run(["court", "genome.yaml"], cwd=proj)
    R.append(("onto court on packaged template: ALL PROVED (offline)",
              ct.returncode == 0 and "ALL PROVED" in ct.stdout
              and "ENTITY-INDUCTIVE" in ct.stdout))

    # 6. onto schema (free IDE) works installed
    sc = run(["schema"], cwd=proj)
    R.append(("onto schema installed (JSON Schema from frozen IR)",
              sc.returncode == 0 and '"entities"' in sc.stdout))

    # 7. serve + judge + attest end-to-end on the interpreter (no toolchain)
    data = work / "data"
    proc = subprocess.Popen([str(onto), "serve", "genome.yaml", "--port",
                             "8798", "--data", str(data)], cwd=proj,
                            env=clean_env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        up = False
        for _ in range(120):
            try:
                urllib.request.urlopen("http://127.0.0.1:8798/health", timeout=2)
                up = True
                break
            except Exception:
                time.sleep(0.05)
        R.append(("onto serve: organism live from second zero (no dialect "
                  "toolchain)", up))
        ju = run(["judge", "flows.yaml", "http://127.0.0.1:8798"], cwd=proj)
        R.append(("onto judge: packaged flows green against the live organism",
                  ju.returncode == 0))
    finally:
        proc.kill()
    at = run(["attest", "genome.yaml"], cwd=proj)
    R.append(("onto attest: guarantee passport prints (installed)",
              at.returncode == 0 and "ATTESTATION OF GUARANTEES" in at.stdout))

    # 8. repo hygiene: no keys / pyc / attest artifacts tracked in git
    tracked = subprocess.run(["git", "ls-files", "v1"], cwd=ROOT.parent,
                             capture_output=True, text=True).stdout.splitlines()
    dirty = [f for f in tracked if f.endswith(".pyc")
             or "config.toml" == pathlib.Path(f).name
             or f.endswith("attest.json") or "/build/" in f
             or "/.onto/" in f]
    R.append((f"repo hygiene: no keys/pyc/artifacts tracked ({len(dirty)} bad)",
              not dirty))

    return _report(t0)


def _report(t0):
    print(f"\n=== EXAM SHIP (P3+P4) ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
