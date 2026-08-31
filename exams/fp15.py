# -*- coding: utf-8 -*-
"""P15 CHECK (Part VII §1.4): gauntlet lessons appended to the cheat sheet ->
the 5 tasks Sonnet FAILED (8/8 red, closed only by Opus) are re-run
sonnet-only with a clean cache. P15 succeeds if ≥3/5 go sonnet-green
(≤8 attempts), with ≥1 of them first-try. This is an exam of THEORY (p0
transfer), not the engine: a failure = refutation of P15, also a valuable
outcome."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
TASKS = ["library", "parking", "auction", "tickets", "leaderboard"]


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import nlfront
    from onto.ribosome import Provider
    spec = importlib.util.spec_from_file_location("fg", ROOT / "exams/fgauntlet.py")
    fg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fg)

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_p15.jsonl"

    results = {}
    for name in TASKS:
        work = ROOT / "build" / "p15" / name          # CLEAN cache (new path)
        t1 = time.time()
        tele = nlfront.build(fg.PRODUCTS[name], provider, work, ROOT,
                             ladder=["anthropic/claude-sonnet-4.5"],
                             log=lambda m: None)
        n = len(tele["attempts"])
        green = not tele["island"]
        court_ok = False
        if green:
            court_ok = subprocess.run(
                [str(PY), "-m", "onto.cli", "court", str(work / "genome.yaml")],
                cwd=ROOT, capture_output=True).returncode == 0
        results[name] = {"green": green and court_ok, "attempts": n,
                         "sec": round(time.time() - t1)}
        print(f"  {name}: {'GREEN' if green else 'ISLAND'} in {n} attempts "
              f"({results[name]['sec']} s)" + ("" if court_ok or not green
                                               else " COURT RED"), flush=True)

    greens = [n for n, r in results.items() if r["green"]]
    firsts = [n for n in greens if results[n]["attempts"] == 1]
    verdict = len(greens) >= 3 and len(firsts) >= 1
    print(f"\n=== P15: {len(greens)}/5 sonnet-green (was 0/5), "
          f"first-try: {len(firsts)} ({time.time() - t0:.0f} s) ===")
    print(json.dumps(results, ensure_ascii=False))
    print("P15:", "CONFIRMED" if verdict else "REFUTED",
          "| was: Sonnet 0/5, 40 red attempts")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
