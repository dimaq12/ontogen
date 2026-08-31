# -*- coding: utf-8 -*-
"""EXAM "DIALECT GROWTH" (IDEAL, pearl 5): a new language (Node.js) for hotel
— WITHOUT a single core edit and with no human in the loop. The oracle = the
canonical python phenotype; the gates = the SAME judge + fold parity +
kill -9/replay; CEGIS: judge failures -> fed into the weak model's prompt."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def http(port, path, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait_up(port):
    for _ in range(200):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growdialect
    from onto.core import genome as G
    from onto.ribosome import Provider

    core_before = subprocess.run(
        ["git", "status", "--porcelain", "v1/src/onto/core", "v1/src/onto/dialects"],
        cwd=ROOT.parent, capture_output=True, text=True).stdout

    # 1) canonical reference: python phenotype of hotel + reference snapshot
    subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                    str(ROOT / "genomes/hotel.yaml"), "--dialect",
                    "python-stdlib", "--out", str(ROOT / "build/hotel_py")],
                   cwd=ROOT, capture_output=True)
    canon_data = tempfile.mkdtemp(prefix="grow-canon-")
    proc = subprocess.Popen([str(PY), str(ROOT / "build/hotel_py/organism.py"),
                             "--port", "8722", "--data", canon_data],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert wait_up(8722)
    j = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                        str(ROOT / "exams/hotel_flows.yaml"),
                        "http://127.0.0.1:8722"],
                       cwd=ROOT, capture_output=True, text=True)
    g = G.load(ROOT / "genomes/hotel.yaml")
    canon = {en: {inst: http(8722, f"/state/{en}/{inst}")
                  for inst in ent.instances}
             for en, ent in g.entities.items()}
    proc.kill()
    R.append(("oracle: canonical python phenotype, judge 4/4",
              j.returncode == 0))

    # 2) GROWTH: the weak model grows the node organism against the gates
    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_grow.jsonl"
    tele = growdialect.grow(ROOT / "genomes/hotel.yaml",
                            ROOT / "exams/hotel_flows.yaml",
                            ROOT / "build/hotel_node",
                            provider, canon,
                            ROOT / "build/hotel_py/organism.py", ROOT)
    print(json.dumps(tele, ensure_ascii=False, indent=1)[:1200])
    R.append((f"GROWTH: node organism grown by the model "
              f"[{tele.get('model')}] in {len(tele['attempts'])} attempts "
              f"(CEGIS)", not tele["island"]))

    if not tele["island"]:
        # 3) final certification of the fresh artifact in a separate run
        data = tempfile.mkdtemp(prefix="grow-final-")
        proc = subprocess.Popen(["node", str(ROOT / "build/hotel_node/organism.js"),
                                 "--port", "8723", "--data", data],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        up = wait_up(8723)
        j2 = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                             str(ROOT / "exams/hotel_flows.yaml"),
                             "http://127.0.0.1:8723"],
                            cwd=ROOT, capture_output=True, text=True)
        print("node:", j2.stdout.strip().splitlines()[-1] if j2.stdout.strip() else "?")
        parity = all(http(8723, f"/state/{en}/{i}") == want
                     for en, insts in canon.items()
                     for i, want in insts.items())
        proc.kill()
        R.append(("certification: the SAME judge 4/4 on the GROWN node organism",
                  up and j2.returncode == 0))
        R.append(("fold parity: node == canon across all instances", parity))

    # 4) zero core/dialect edits by human or model
    core_after = subprocess.run(
        ["git", "status", "--porcelain", "v1/src/onto/core", "v1/src/onto/dialects"],
        cwd=ROOT.parent, capture_output=True, text=True).stdout
    R.append(("ZERO core and dialect edits: the new language is an artifact, not a patch",
              core_before == core_after))

    calls = [json.loads(l) for l in
             (ROOT / ".onto/usage_grow.jsonl").read_text().splitlines()]
    toks = sum((c["tokens_in"] or 0) + (c["tokens_out"] or 0) for c in calls)
    print(f"usage: {len(calls)} calls, {toks} tokens")

    print(f"\n=== EXAM DIALECT GROWTH ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else
          "ISLAND/FAIL (measurement, see telemetry)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
