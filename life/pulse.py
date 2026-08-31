# -*- coding: utf-8 -*-
"""PULSE of calendar life: light live traffic against a long-lived organism.
Once every PERIOD seconds — a random meaningful event (booking/release/
deposit); log — pulse.log. The organism's dedup/guards make any
randomness safe. Launch: run.sh (nohup)."""
import json
import random
import time
import urllib.request

PORT = 8878
PERIOD = 20
rnd = random.Random()
rooms = [f"R{i}" for i in range(1, 4)]
teams = [f"team{i}" for i in range(1, 4)]


def post(payload):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/event",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    n = 0
    # seed the world (idempotent: duplicates are cut off by guard/dedup)
    for r in rooms:
        try:
            post({"id": f"seed-room-{r}", "type": "RoomAdded", "room_id": r})
        except Exception:
            pass
    for t in teams:
        try:
            post({"id": f"seed-team-{t}", "type": "TeamRegistered", "team_id": t})
            post({"id": f"seed-dep-{t}", "type": "DepositAdded",
                  "team_id": t, "amount": 100000})
        except Exception:
            pass
    while True:
        time.sleep(PERIOD + rnd.uniform(-5, 5))
        n += 1
        t, r = rnd.choice(teams), rnd.choice(rooms)
        ev = rnd.choice([
            {"type": "DepositAdded", "team_id": t, "amount": rnd.randint(1, 500) * 100},
            {"type": "BookingRequested", "team_id": t, "room_id": r},
            {"type": "BookingEnded", "team_id": t, "room_id": r,
             "hours": rnd.randint(1, 8)},
        ])
        ev["id"] = f"pulse-{int(time.time())}-{n}"
        try:
            out = post(ev)
            print(f"{time.strftime('%F %T')} {ev['type']} -> {out['status']}",
                  flush=True)
        except Exception as e:  # organism is molting/restarting — pulse survives it
            print(f"{time.strftime('%F %T')} {ev['type']} -> RETRY ({e})",
                  flush=True)


if __name__ == "__main__":
    main()
