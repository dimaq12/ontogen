# -*- coding: utf-8 -*-
"""EXAM F6 "Life" (compressed week): (a) a feature by genome edit ONLY ->
the warden molts, data stays alive; (b) a breaking schema change WITHOUT a
functor is rejected, WITH a functor — the log is migrated, state identical in
meaning, downtime in seconds; (c) a storm of violations -> quota -> REVOKE of
rights; (d) auto-molt driven by monitor data under interventional rights;
(e) replay does not inflate monitors/heat (subtracting one's own actions).
Calendar week/month — a background criterion outside the session."""
import json
import pathlib
import shutil
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def http(port, path, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core.warden import Warden
    from onto.theory.provenance import declared, measured

    # --- working copy of the genome (we don't touch the repo): root + modules
    ws = pathlib.Path(tempfile.mkdtemp(prefix="f6-ws-"))
    (ws / "modules").mkdir()
    for mod in ("rooms", "reservations", "payments"):
        shutil.copy(ROOT / "modules" / f"{mod}.yaml", ws / "modules" / f"{mod}.yaml")
    root = ws / "hotel.yaml"
    root.write_text((ROOT / "genomes" / "hotel.yaml").read_text()
                    .replace("../modules/", "modules/"), encoding="utf-8")

    w = Warden(root, ws / "data", 8631, rights="interventional",
               quota_inv_violations=declared(3.0, "operator"))
    try:
        w.start()
        # a bit of live data
        http(8631, "/event", {"id": "l1", "type": "ChargeRequested",
                              "wallet": "bob", "amount": 100})
        http(8631, "/event", {"id": "l2", "type": "BookingRequested",
                              "room": "room101", "resv": "r1", "nights": 2})
        assert http(8631, "/state/wallet/bob")["balance"] == 900

        # ---------- (a) feature by genome edit only: bonus in the payments gene
        pay = ws / "modules" / "payments.yaml"
        bonus_rule = (
            "      bonus:\n"
            "        when: BonusGranted\n"
            "        intent: grant bonus\n"
            "        guard: \"ev.amount > 0\"\n"
            "        body: |\n"
            "          s.balance = s.balance + ev.amount\n"
            "        contract: {post: \"s.balance >= 0\"}\n")
        txt = pay.read_text().replace(
            "events:\n  ChargeRequested: {wallet: str, amount: int}",
            "events:\n  BonusGranted:    {wallet: str, amount: int}\n"
            "  ChargeRequested: {wallet: str, amount: int}")
        txt = txt.replace("queries:\n", bonus_rule + "queries:\n")
        pay.write_text(txt, encoding="utf-8")
        out = w.tick_watch()
        feature_ok = out["status"] == "molted" and out["breaking"] == []
        http(8631, "/event", {"id": "b1", "type": "BonusGranted",
                              "wallet": "bob", "amount": 50})
        st = http(8631, "/state/wallet/bob")
        R.append(("feature by genome ONLY: additive molt, data stays alive "
                  f"(950=900+50, downtime {out['downtime_s']:.1f}s)",
                  feature_ok and st["balance"] == 950
                  and out["downtime_s"] < 3))

        # ---------- (b1) breaking change WITHOUT a functor — rejected
        pay.write_text(pay.read_text().replace("amount: int", "sum: int")
                       .replace("ev.amount", "ev.sum"), encoding="utf-8")
        out = w.tick_watch()
        R.append(("breaking schema change WITHOUT a functor — REJECTED with a list",
                  out["status"] == "rejected"
                  and any("amount" in r for r in out["reasons"])))
        alive = http(8631, "/health")["ok"]
        R.append(("the organism SURVIVED the rejected mutation (old genome alive)", alive))

        # ---------- (b2) the same change WITH a functor — the log is migrated
        bal_before = http(8631, "/state/wallet/bob")["balance"]
        root.write_text(root.read_text() + """
migrations:
  rename_event_fields:
    ChargeRequested: {amount: sum}
    ChargeRefunded:  {amount: sum}
    BonusGranted:    {amount: sum}
""", encoding="utf-8")
        out = w.tick_watch()
        st = http(8631, "/state/wallet/bob")
        mig = out.get("migration", {})
        R.append((f"molt with schema change: log migrated ({mig.get('events_in')}"
                  f" events, backup present), balance preserved, downtime "
                  f"{out['downtime_s']:.1f}s",
                  out["status"] == "molted" and st["balance"] == bal_before
                  and mig.get("backup") and out["downtime_s"] < 3))
        ok_new = http(8631, "/event", {"id": "n1", "type": "ChargeRequested",
                                       "wallet": "bob", "sum": 25})
        R.append(("the new schema accepts events (sum instead of amount)",
                  ok_new["status"] == "applied"
                  and http(8631, "/state/wallet/bob")["balance"] == bal_before - 25))

        # ---------- (e) subtraction: replay did not inflate monitors/heat
        h = http(8631, "/health")
        R.append(("subtracting one's own actions: after molts heat==live traffic,"
                  " violations are not replayed",
                  h["counters"]["invariant_violations"] == 0
                  and h["heat"]["wallet"] <= 2))

        # ---------- (c) storm of violations -> quota -> REVOKE
        for i in range(5):      # overbook: room guard holds, reservation opens
            http(8631, "/event", {"id": f"ob{i}", "type": "BookingRequested",
                                  "room": "room101", "resv": f"r{i % 3 + 1}",
                                  "nights": 1})
        mon = w.tick_monitors()
        R.append(("storm of invariant violations: quota exceeded -> REVOKE, "
                  "rights lowered",
                  mon["status"] == "revoked" and w.rights == "observational"))
        led = (ws / "data" / "warden.jsonl").read_text()
        R.append(("REVOKE — an event in the ledger with a number and quota provenance",
                  '"kind": "revoke"' in led and "declared" in led))

        # ---------- (d) auto-molt driven by monitor data (rights re-granted)
        w.rights = "interventional"        # the operator restored rights after review
        h0 = http(8631, "/health")["heat"]
        t1 = time.perf_counter()
        for i in range(400):
            http(8631, "/event", {"id": f"hot{i}", "type": "ChargeRequested",
                                  "wallet": "alice", "sum": 1})
        dt = time.perf_counter() - t1
        h1 = http(8631, "/health")["heat"]
        out = w.tick_placer(dt, h0, h1,
                            t_cold_ns=measured(41000, "bench:interp"),
                            t_warm_ns=measured(6400, "bench:go"))
        ex = out["executed"]
        svc_ok = False
        if ex and ex[0]["build_ok"]:
            for _ in range(100):
                try:
                    svc_ok = http(ex[0]["port"], "/health")["ok"]
                    break
                except Exception:
                    time.sleep(0.05)
        R.append(("auto-molt driven by monitor data: wallet extracted, service alive, "
                  "molt_executed in ledger",
                  bool(ex) and svc_ok
                  and '"kind": "molt_executed"' in
                  (ws / "data" / "warden.jsonl").read_text()))
    finally:
        w.stop()

    print(f"\n=== EXAM F6 ({time.time() - t0:.1f} s, ws={ws}) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED (mechanisms; calendar week — a background criterion)"
          if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
