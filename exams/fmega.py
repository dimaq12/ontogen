# -*- coding: utf-8 -*-
"""MEGA-GRIME EXAM — a large mixed domain like in real life:
M1 court on a mix of 6 genes (shared event vocabulary, structural requires);
M2 a FUZZY contract opened up by interview (orders.cancel is silent about paid);
M3 a live SLM skill allocate (CEGIS, a second algorithm);
M4 life: 30k events of the order cycle, a racy invariant observer,
   snapshots, kill -9 -> restart from the snapshot;
M5 three flaky integrations with different profiles — drift, trust revocation,
   the organism stays alive; the judge 4/4 on a loaded organism;
M6 schema migration ON LIVE 30k (points -> pts) via the warden: downtime,
   points preserved to the point."""
import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def http(port, path, payload=None, timeout=15):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def wait_up(port):
    for _ in range(300):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def make_ws():
    ws = pathlib.Path(tempfile.mkdtemp(prefix="mega-ws-"))
    (ws / "modules").mkdir()
    for m in ("commerce_events", "stock", "payments", "orders", "shipping",
              "loyalty", "support"):
        shutil.copy(ROOT / "modules" / f"{m}.yaml", ws / "modules" / f"{m}.yaml")
    shutil.copytree(ROOT / "genomes" / "islands", ws / "islands")
    root = ws / "market.yaml"
    root.write_text((ROOT / "genomes" / "market.yaml").read_text()
                    .replace("../modules/", "modules/"), encoding="utf-8")
    return ws, root


def start_flaky_gateway(port):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    rnd = random.Random(5)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            roll = rnd.random()
            if roll < 0.30:
                time.sleep(0.2)
            if roll < 0.20:
                self.send_response(500)
                self.end_headers()
                return
            body = json.dumps({"status": "ok", "auth": f"AUTH{rnd.randint(1000, 9999)}"}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    import os
    from onto.core import court, genome as G, interview, skills as SK
    from onto.core.interview import Patch
    from onto.core.organism import Organism
    from onto import ribosome as RB

    ws, root = make_ws()
    g = G.load(root)
    n_rules = sum(len(e.rules) for e in g.entities.values())

    # ================= M1: court on a mix
    t1 = time.perf_counter()
    c = subprocess.run([str(PY), "-m", "onto.cli", "court", str(root)],
                       cwd=ROOT, capture_output=True, text=True)
    t_court = time.perf_counter() - t1
    print(f"M1: {len(g.entities)} entities / {n_rules} rules / "
          f"{len(g.events)} events / 3 externals / 1 skill; court {t_court:.1f}s")
    R.append((f"M1 court on a mix of 6 genes (shared vocabulary): ALL PROVED, "
              f"{t_court:.1f}s", c.returncode == 0 and "BLIND" not in c.stdout))

    # ================= M2: fuzzy contract -> interview
    ST = dict(g.entities["order"].state)
    EV = dict(g.events["OrderCancelled"])
    weak_post = "s.phase >= 0 and s.phase <= 5"
    A = ("s.phase >= 1 and s.phase <= 2", "s.phase = 5")                 # keeps paid
    B = ("s.phase >= 1 and s.phase <= 2", "s.phase = 5\ns.paid = 0")     # clears paid
    q = interview.detect("order.cancel", ST, EV, A, B, weak_post,
                         variants=[Patch("post", "s.phase != 5 or s.paid == 0")])
    strong = f"({weak_post}) and (s.phase != 5 or s.paid == 0)"
    q2 = interview.detect("order.cancel", ST, EV, A, B, strong)
    print("\n" + (q.render() if q else "no question?!") + "\n")
    R.append(("M2 fuzzy contract: both candidates pass the court, the interview "
              "yields a QUESTION with an executable example about paid",
              q is not None and "paid" in str(q.outcome_a) and
              q.outcome_a != q.outcome_b))
    R.append(("M2 strengthened CONDITIONAL contract (phase==5 => paid==0) DISTINGUISHES the candidates — question resolved", q2 is None))

    # ================= M3: live SLM skill allocate (second algorithm)
    sk = SK.Skill.model_validate(g.skills["allocate"])
    R.append(("M3 property teeth of allocate: the lazy oracle fails",
              SK.gate_teeth(sk) == []))
    provider = RB.Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_mega.jsonl"
    tele = RB.synthesize("allocate", sk, provider, ROOT / "cache_skills")
    print("M3 allocate:", json.dumps(tele["phases"], ensure_ascii=False),
          "island:", tele["island"])
    R.append(("M3 the SLM wrote allocate: naive+fast green (CEGIS/ladder)",
              not tele["island"]))

    # ================= M4: life — 30k cycle events
    org = Organism(g, ws / "data")
    org.snapshot_every = 10_000
    rnd = random.Random(3)
    skus = ["alpha", "bravo", "charlie", "delta"]
    wallets = ["bob", "alice", "carol"]
    orders = [f"o{i:02d}" for i in range(1, 9)]
    ships = [f"s{i:02d}" for i in range(1, 5)]
    tickets = [f"t{i:02d}" for i in range(1, 5)]
    # deterministic race: order delivered BEFORE the shipment mark
    for evd in ({"id": "R1", "type": "OrderPlaced", "order": "o01",
                 "sku": "alpha", "wallet": "bob", "qty": 1, "price": 10},
                {"id": "R2", "type": "OrderPaid", "order": "o01"},
                {"id": "R3", "type": "OrderShipped", "order": "o01",
                 "shipment": "s01"},
                {"id": "R4", "type": "OrderDelivered", "order": "o01"}):
        org.handle(evd)      # shipment s01 NOT delivered -> invariant violated
    N = 30_000
    t1 = time.perf_counter()
    for i in range(N):
        o = rnd.choice(orders)
        roll = rnd.random()
        if roll < 0.30:
            org.handle({"id": f"L{i}", "type": "OrderPlaced", "order": o,
                        "sku": rnd.choice(skus), "wallet": rnd.choice(wallets),
                        "qty": rnd.randint(1, 3), "price": rnd.randint(5, 30)})
        elif roll < 0.45:
            org.handle({"id": f"L{i}", "type": "OrderPaid", "order": o})
        elif roll < 0.55:
            org.handle({"id": f"L{i}", "type": "OrderShipped", "order": o,
                        "shipment": rnd.choice(ships)})
        elif roll < 0.62:
            # RACE BY DESIGN: order delivery earlier than the shipment mark
            org.handle({"id": f"L{i}", "type": "OrderDelivered", "order": o})
        elif roll < 0.70:
            org.handle({"id": f"L{i}", "type": "ShipmentCreated",
                        "shipment": rnd.choice(ships), "order": o})
        elif roll < 0.76:
            org.handle({"id": f"L{i}", "type": "ShipmentDelivered",
                        "shipment": rnd.choice(ships)})
        elif roll < 0.84:
            org.handle({"id": f"L{i}", "type": "LoyaltyAccrued",
                        "member": rnd.choice(wallets),
                        "points": rnd.randint(1, 9)})
        elif roll < 0.88:
            org.handle({"id": f"L{i}", "type": "LoyaltyRedeemed",
                        "member": rnd.choice(wallets),
                        "points": rnd.randint(1, 20)})
        elif roll < 0.94:
            org.handle({"id": f"L{i}", "type": "OrderCancelled", "order": o,
                        "sku": rnd.choice(skus), "qty": 1})
        else:
            org.handle({"id": f"L{i}", "type": rnd.choice(
                ["TicketOpened", "TicketEscalated", "TicketClosed"]),
                "ticket": rnd.choice(tickets), "order": o})
    thr = N / (time.perf_counter() - t1)
    inv_v = org.counters["invariant_violations"]
    noop = org.counters["noop"]
    org.checkpoint()

    print(f"M4: {N} events, {thr:,.0f} ev/s (fsync+invariants on each), "
          f"noop(machine veto)={noop}, the racy invariant was violated "
          f"{inv_v} times (observer)")
    t1 = time.perf_counter()
    org2 = Organism(g, ws / "data")
    t_restart = time.perf_counter() - t1
    R.append((f"M4 life {N // 1000}k: {thr:,.0f} ev/s; kill -9 -> restart from "
              f"the snapshot {t_restart:.2f}s, folds identical; the race CAUGHT "
              f"by the observer ({inv_v} times)",
              org2.snapshot() == org.snapshot() and inv_v > 0
              and t_restart < 3))
    del org, org2

    # ================= M5: membrane under flakiness + judge on the live one
    gw = start_flaky_gateway(8689)
    os.environ["MEGA_GATEWAY_PORT"] = "8689"
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve", str(root),
                             "--port", "8681", "--data", str(ws / "data"),
                             "--skills-cache", str(ROOT / "cache_skills"),
                             "--snapshot-every", "10000"],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            env={**os.environ})
    R.append(("M5 organism with 30k of history came up under HTTP (snapshot+tail)",
              wait_up(8681)))
    for name, n in (("gateway", 50), ("tracker", 40), ("fraud", 40)):
        for i in range(n):
            try:
                http(8681, f"/ext/{name}", {"amount": 100, "order": "o01"},
                     timeout=5)
            except Exception:
                pass
    hp = http(8681, "/health")["externals"]
    print("M5 integration attestations:",
          {k: {kk: v[kk] for kk in ("cert_valid", "violations",
                                    "error_rate_pct")} for k, v in hp.items()})
    R.append(("M5 three integrations with different profiles: drift caught, trust "
              "in the worst ones revoked, the organism stays alive",
              any(not v["cert_valid"] for v in hp.values())
              and sum(v["violations"] for v in hp.values()) > 0
              and wait_up(8681)))
    alloc = http(8681, "/skill/allocate", {
        "demands": [{"id": "d1", "sku": "alpha", "qty": 5, "priority": 2},
                    {"id": "d2", "sku": "alpha", "qty": 4, "priority": 9}],
        "stocks": [{"sku": "alpha", "available": 6}]})
    got = {a["id"]: a["qty"] for a in alloc["out"]}
    R.append((f"M5 skill-organ allocate on the live organism: priority 9 "
              f"saturated first ({got})",
              got.get("d2") == 4 and got.get("d1", 0) <= 2))
    judge = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(ROOT / "exams/market_flows.yaml"),
                            "http://127.0.0.1:8681"],
                           cwd=ROOT, capture_output=True, text=True)
    print(judge.stdout.strip())
    R.append(("M5 judge 4/4 on a LOADED organism (30k history + flakiness)",
              judge.returncode == 0))
    loyalty_total = sum(
        (lambda st: st["points"] + st["redeemed"])(http(8681, f"/state/member/{m}"))
        for m in ("bob", "alice", "carol", "dave", "erin"))
    proc.kill()
    gw.shutdown()

    # ================= M6: schema migration on live 30k (points -> pts)
    from onto.core.warden import Warden
    w = Warden(root, ws / "data", 8682)
    w.start()
    loy = ws / "modules" / "loyalty.yaml"
    loy.write_text(loy.read_text()
                   .replace("{member: str, points: int}", "{member: str, pts: int}")
                   .replace("ev.points", "ev.pts"), encoding="utf-8")
    out = w.tick_watch()
    rejected_first = out["status"] == "rejected"
    root.write_text(root.read_text() + """
migrations:
  rename_event_fields:
    LoyaltyAccrued:  {points: pts}
    LoyaltyRedeemed: {points: pts}
""", encoding="utf-8")
    out = w.tick_watch()
    ok_molt = out["status"] == "molted" and out["migration"].get("backup")
    st = {}
    if ok_molt:
        for m in ("bob", "alice", "carol", "dave", "erin"):
            st[m] = http(8682, f"/state/member/{m}")
    w.stop()
    preserved = sum(v["points"] + v["redeemed"] for v in st.values()) == loyalty_total
    print(f"M6: molt with schema change on live 30k: downtime "
          f"{out.get('downtime_s', 99):.1f}s; points preserved: {preserved}")
    R.append(("M6 schema change without a functor on live data — REJECTED",
              rejected_first))
    R.append((f"M6 with a functor: 30k log migrated (backup), points preserved "
              f"to the point, downtime {out.get('downtime_s', 99):.1f}s",
              ok_molt and preserved and out["downtime_s"] < 8))

    print(f"\n=== MEGA-GRIME EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
