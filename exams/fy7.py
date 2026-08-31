# -*- coding: utf-8 -*-
"""EXAM U7 "SKILLS IN ALL FABRICS" (D71): certified skill bodies
(1) are PRINTED into the python phenotype from the ribosome cache (fast|naive)
and give byte-parity with the canon on the fuzz; (2) in the go fabric — an RPC
to the canon (ONTO_SKILL_CANON), without the canon — an honest 501. Zero
re-synthesis: printing takes ready-made certified artifacts."""
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
P_CANON, P_PY, P_GO = 8776, 8777, 8778
R = []


def http(port, path, payload=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def wait(port):
    for _ in range(120):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G, skills as SK

    g = G.load(ROOT / "genomes/market.yaml")
    sk = SK.Skill.model_validate(g.skills["allocate"])

    # 1. printing: python phenotype with the skill from the certified cache
    out_py = pathlib.Path(tempfile.mkdtemp(prefix="y7-py-"))
    mat = subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                          str(ROOT / "genomes/market.yaml"),
                          "--dialect", "python-stdlib", "--out", str(out_py),
                          "--skills-cache", str(ROOT / "cache_skills")],
                         cwd=ROOT, capture_output=True, text=True)
    src = (out_py / "organism.py").read_text(encoding="utf-8")
    R.append(("printing: skill body in the python phenotype (fast from the ribosome cache)",
              mat.returncode == 0 and "fast_allocate" in src
              and "SKILLS['allocate']" in src))

    procs = []
    try:
        # canon + printed python
        d1, d2 = tempfile.mkdtemp(prefix="y7c-"), tempfile.mkdtemp(prefix="y7p-")
        procs.append(subprocess.Popen(
            [str(PY), "-m", "onto.cli", "serve", str(ROOT / "genomes/market.yaml"),
             "--port", str(P_CANON), "--data", d1,
             "--skills-cache", str(ROOT / "cache_skills")],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        procs.append(subprocess.Popen(
            [str(PY), str(out_py / "organism.py"), "--port", str(P_PY),
             "--data", d2],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        ok = wait(P_CANON) and wait(P_PY)
        R.append(("canon and printed organism are alive", ok))

        # 2. fuzz-parity of the print with the canon (certified cases D45)
        rnd = random.Random(20260830)
        cases = [SK.gen_case(sk, rnd) for _ in range(60)]
        mism = 0
        for c in cases:
            s1, o1 = http(P_CANON, "/skill/allocate", c)
            s2, o2 = http(P_PY, "/skill/allocate", c)
            if (s1, o1.get("out")) != (s2, o2.get("out")):
                mism += 1
        R.append((f"fuzz-parity of the print with the canon: 60 cases, {mism} mismatches",
                  mism == 0))
        # 3. honest 404 on an unprinted skill
        s404, _ = http(P_PY, "/skill/ghost", {})
        R.append(("printed: unknown skill -> 404", s404 == 404))

        # 4. go fabric: build + honest 501 without the canon
        out_go = pathlib.Path(tempfile.mkdtemp(prefix="y7-go-"))
        mat = subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                              str(ROOT / "genomes/market.yaml"),
                              "--dialect", "go-stdlib", "--out", str(out_go)],
                             cwd=ROOT, capture_output=True, text=True)
        R.append(("go phenotype built (with the /skill RPC route)",
                  mat.returncode == 0))
        d3 = tempfile.mkdtemp(prefix="y7g-")
        procs.append(subprocess.Popen(
            [str(out_go / "organism"), "--port", str(P_GO), "--data", d3],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait(P_GO)
        s501, e501 = http(P_GO, "/skill/allocate", cases[0])
        R.append(("go without ONTO_SKILL_CANON -> honest 501 with a hint",
                  s501 == 501 and "ONTO_SKILL_CANON" in e501.get("error", "")))
        procs.pop().kill()

        # 5. go with the canon: RPC parity
        import os
        env = dict(os.environ)
        env["ONTO_SKILL_CANON"] = f"http://127.0.0.1:{P_CANON}"
        d4 = tempfile.mkdtemp(prefix="y7g2-")
        procs.append(subprocess.Popen(
            [str(out_go / "organism"), "--port", str(P_GO), "--data", d4],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait(P_GO)
        mism = 0
        for c in cases[:30]:
            s1, o1 = http(P_CANON, "/skill/allocate", c)
            s2, o2 = http(P_GO, "/skill/allocate", c)
            if (s1, o1.get("out")) != (s2, o2.get("out")):
                mism += 1
        R.append((f"go RPC to the canon: 30 cases, {mism} mismatches", mism == 0))
    finally:
        for pr in procs:
            pr.kill()

    print(f"\n=== EXAM U7: SKILLS IN ALL FABRICS ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
