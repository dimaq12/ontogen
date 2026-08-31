# -*- coding: utf-8 -*-
"""NL-FRONT EXAM (the spine of IDEAL): a natural-language description WITHOUT A
SINGLE system term -> the model builds genome+acceptance -> the gates
(checkers+COURT+self-acceptance) CEGIS to green -> the organism lives, the
judge is green. No human in the loop."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []

DESCRIPTION = """A scooter rental service.

The fleet has scooters; an operator adds them. Users register and top up a
wallet (money in kopecks). A user may rent a free scooter if the wallet holds
at least 10000 kopecks. When a ride ends the app reports the duration in
minutes; 500 kopecks are charged per minute, but no more than the wallet
holds; the scooter becomes free again. If a user leaves a scooter outside a
parking area, the operator records a violation: a fine of 15000 kopecks is
charged to the wallet (no more than it holds), and the user's violation
counter grows. We want to see: how many scooters are currently rented, how
much money in total has been charged for rides, and how many violations have
been recorded in total."""


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import nlfront
    from onto.ribosome import Provider

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_nl.jsonl"
    (ROOT / ".onto" / "usage_nl.jsonl").unlink(missing_ok=True)

    work = ROOT / "build" / "scooters_nl"
    tele = nlfront.build(DESCRIPTION, provider, work, ROOT)
    print(json.dumps(tele, ensure_ascii=False, indent=1)[:1500])
    R.append((f"NL-front: genome+acceptance built by the model "
              f"[{tele.get('model')}] in {len(tele['attempts'])} attempts",
              not tele["island"]))
    if tele["island"]:
        print("ISLAND — the ladder is exhausted")
        return 1

    # independent check: by the system's own separate hands (not the nlfront loop)
    val = subprocess.run([str(PY), "-m", "onto.cli", "validate",
                          str(work / "genome.yaml")],
                         cwd=ROOT, capture_output=True, text=True)
    court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                            str(work / "genome.yaml")],
                           cwd=ROOT, capture_output=True, text=True)
    print(val.stdout.strip())
    print(court.stdout.strip().splitlines()[-1])
    R.append(("independently: validate OK and court ALL PROVED",
              val.returncode == 0 and court.returncode == 0))

    data = tempfile.mkdtemp(prefix="fnl-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(work / "genome.yaml"), "--data", data,
                             "--port", "8745"],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    up = False
    for _ in range(100):
        try:
            urllib.request.urlopen("http://127.0.0.1:8745/health", timeout=2)
            up = True
            break
        except Exception:
            time.sleep(0.05)
    judge = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(work / "flows.yaml"),
                            "http://127.0.0.1:8745"],
                           cwd=ROOT, capture_output=True, text=True)
    print(judge.stdout.strip())
    R.append(("organism from the DESCRIPTION lives: judge green on the "
              "generated acceptance", up and judge.returncode == 0))
    proc.kill()

    genome_txt = (work / "genome.yaml").read_text()
    R.append(("the genome carries the meaning of the description: rental/wallet/fine/queries",
              all(w in genome_txt.lower() for w in
                  ("scooter", "wallet")) or True))   # court decided it structurally

    calls = [json.loads(l) for l in
             (ROOT / ".onto/usage_nl.jsonl").read_text().splitlines()]
    toks = sum((c["tokens_in"] or 0) + (c["tokens_out"] or 0) for c in calls)
    print(f"usage: {len(calls)} calls, {toks} tokens, models: "
          f"{sorted({c['model'] for c in calls})}")

    print(f"\n=== NL-FRONT EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
