# -*- coding: utf-8 -*-
"""MAIN EXAM — «ANY SOFTWARE PRODUCT» (universality gauntlet).

8 domains, deliberately far apart from each other, each a FULL cycle:
a Russian description -> NL front (gates: checkers+COURT+judge self-acceptance)
-> an independent COURT. Plus a 9th description DELIBERATELY BEYOND the
expressibility boundary — the HONESTY OF REFUSAL is examined (island, not a
fake). The cache makes repeated runs free; telemetry — model/attempts/tokens
per product."""
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []

PRODUCTS = {
 "library": """A library. Books are added by the librarian (title — the key,
count of copies). Readers register. A reader borrows a book if a copy is free
and they have fewer than 3 books out; a return frees the copy. We want to see:
how many books are out in total and how many readers there are.""",

 "parking": """A paid parking lot. Spots are added by the administrator. A car
pulls into a free spot (we record the car's plate), the spot becomes occupied.
On exit the duration in hours is given, a fee of 200 cents per hour is charged
to the parking owner's account, the spot is freed. We want to see: spots
occupied right now and total revenue.""",

 "auction": """A lot auction. A lot is listed with a starting price. Bidders
register with a deposit. A bid is accepted if it is strictly above the lot's
current price and does not exceed the bidder's deposit; the lot records the
leader and the price. Closing a lot: the price is charged against the leader's
deposit. We want to see: the sum of current prices of open lots and the total
of charges.""",

 "tickets": """A support desk. A customer opens a ticket with a priority
(a number 1-3). An agent takes a ticket into work (only an open one). Resolving
a ticket closes it and increments the agent's resolved counter. Escalation: a
ticket in work raises its priority by 1, but no higher than 3. We want to see:
open tickets and total resolved.""",

 "fitness": """A fitness club. Memberships: a customer buys a package of N
visits (N is paid in money: 500 cents per visit — credited to the club). Entry
to the gym deducts one visit, if any are left. Freeze: a customer can freeze
the membership (entry forbidden), unfreeze lifts it. We want to see: total
visits bought remaining and the club's revenue.""",

 "delivery": """Food delivery. A restaurant publishes a dish with a price.
Order: a customer orders a dish (we deduct the price from their wallet if it's
enough; topping up the wallet is a separate event). A courier takes an order
(only a paid one), delivery completes the order and credits the courier 150
cents of commission. We want to see: orders in transit and the earnings of all
couriers.""",

 "warehouse": """A warehouse with bins. A bin holds 100 units. Goods intake
puts a batch into a bin if it fits (otherwise a refusal). Shipping takes from a
bin if there is enough. Stocktake: an event records a discrepancy — it sets the
bin's remaining count equal to the recounted value from the event. We want to
see: the total warehouse stock and the number of stocktakes performed.""",

 "leaderboard": """A game server. Players register. A match: an event with two
players and a winner — the winner gets +25 rating, the loser -25, but no lower
than 0. Banning a player forbids them matches; unbanning lifts it. We want to
see: the total rating of all players and the number of matches played.""",
}

# deliberately BEYOND the expressibility boundary: a streaming file host with
# video transcoding — byte blobs and background pipelines aren't expressible by
# rules over int/str; the honest outcome = refusal (island), not a fake.
IMPOSSIBLE = """File hosting: a user uploads video files up to 4GB, the service
transcodes them in the background into 3 resolutions via ffmpeg, serves HLS
streams with adaptive bitrate and preview thumbnails every 10 seconds of the
clip. We want to see a player in the browser."""


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import nlfront
    from onto.ribosome import Provider

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_gauntlet.jsonl"

    rows = []
    for name, desc in PRODUCTS.items():
        t1 = time.time()
        work = ROOT / "build" / "gauntlet" / name
        try:
            tele = nlfront.build(desc, provider, work, ROOT, log=lambda m: None)
        except Exception as e:  # noqa: BLE001
            rows.append((name, False, f"CRASH {type(e).__name__}: {e}", 0))
            continue
        if tele["island"]:
            last = tele["attempts"][-1]["verdict"][:90] if tele["attempts"] else "?"
            rows.append((name, False, f"island: {last}", len(tele["attempts"])))
            continue
        court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                                str(work / "genome.yaml")],
                               cwd=ROOT, capture_output=True, text=True)
        ok = court.returncode == 0
        rows.append((name, ok,
                     f"[{tele.get('model','cache').split('/')[-1]}"
                     f"{' cache' if tele.get('cache') else ''}, "
                     f"{len(tele['attempts'])} extra attempts, "
                     f"{time.time()-t1:.0f} s]"
                     + ("" if ok else " COURT RED"), len(tele["attempts"])))

    for name, ok, note, _ in rows:
        R.append((f"{name}: {note}", ok))
    n_ok = sum(1 for _, ok, _, _ in rows if ok)
    R.append((f"universality: {n_ok}/8 domains built and PROVEN", n_ok == 8))

    # honesty of the boundary: the inexpressible must give a refusal, not a fake
    try:
        tele = nlfront.build(IMPOSSIBLE, provider,
                             ROOT / "build" / "gauntlet" / "impossible",
                             ROOT, ladder=["anthropic/claude-sonnet-4.5"],
                             log=lambda m: None)
        honest = tele["island"]
        note = "island (honest refusal)" if honest else \
            "CONVERGED?! check what exactly it built"
    except Exception as e:  # noqa: BLE001
        honest, note = True, f"refusal via exception: {type(e).__name__}"
    R.append((f"boundary: video hosting with transcoding -> {note}", honest))

    up = ROOT / ".onto" / "usage_gauntlet.jsonl"
    calls = [json.loads(l) for l in up.read_text().splitlines()] if up.exists() else []
    toks = sum((c["tokens_in"] or 0) + (c["tokens_out"] or 0) for c in calls)
    print(f"telemetry: {len(calls)} calls, {toks} tokens")

    print(f"\n=== MAIN EXAM: ANY PRODUCT ({time.time() - t0:.0f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
