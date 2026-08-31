# -*- coding: utf-8 -*-
"""HELD-OUT TEST OF LESSONS (D80, response to the "P15 in-sample" critique):
the lessons were mined on library/parking/auction/tickets/leaderboard; here
are TWO FRESH domains with the same classes of mechanics (fan-out of two
participants; double-entry accounting) that the cheat sheet has never seen.
Sonnet-only. Success = generalization of the lessons; failure = the honest
answer "the lessons are in-sample"."""
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

HELD_OUT = {
 "chess_club": """A chess club. Players register. A game: an event with a
white and a black player and a result (1 — white, 2 — black, 0 — draw); the
winner gets +10 points, the loser -10 but not below 0, on a draw both get +1.
Disqualification bars a player from games; reinstatement lifts the ban.
We want to see: the total points of all players and the number of games played.""",

 "tool_rental": """A tool rental. Tools are added with a number of units in
stock. Customers register. A customer borrows a tool if there is a free unit
available and they are currently holding fewer than 2 tools; a return frees a
unit. We want to see: total units currently held and the number of customers.""",
}


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import nlfront
    from onto.ribosome import Provider
    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_heldout.jsonl"
    results = {}
    for name, desc in HELD_OUT.items():
        work = ROOT / "build" / "heldout" / name
        tele = nlfront.build(desc, provider, work, ROOT,
                             ladder=["anthropic/claude-sonnet-4.5"],
                             log=lambda m: None)
        n = len(tele["attempts"])
        green = not tele["island"]
        if green:
            green = subprocess.run(
                [str(ROOT / ".venv/bin/python"), "-m", "onto.cli", "court",
                 str(work / "genome.yaml")],
                cwd=ROOT, capture_output=True).returncode == 0
        results[name] = (green, n)
        print(f"  {name}: {'GREEN' if green else 'ISLAND'} in {n} attempts",
              flush=True)
    ok = sum(1 for g, _ in results.values() if g)
    print(f"\n=== HELD-OUT ({time.time() - t0:.0f} s): {ok}/2 sonnet-green "
          f"on UNSEEN domains ===")
    print("VERDICT:", "GENERALIZATION CONFIRMED" if ok == 2 else
          ("PARTIAL (1/2)" if ok == 1 else "LESSONS IN-SAMPLE (honest negative)"))
    return 0 if ok == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
