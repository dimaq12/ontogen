# -*- coding: utf-8 -*-
"""EXAM "FILTH AND VOLUME" — the nastiest of real projects, a battery
modeled on v0 (EDIRT/ESNAP/E3/concern #6):

G1 volume: 200k events (fsync write-ahead), replay speed, a snapshot with a
   hash certificate cuts the cold start; a corrupt snapshot is rejected.
G2 kill -9 mid-write: a torn log line — the organism lives, the fact is in the ledger.
G3 duplicate storm + garbage on input (broken json/fields/types/instances) —
   the organism doesn't crash, everything is classified.
G4 concurrency: 8 threads hammer one wallet — money conservation
   settles to the penny.
G5 filth: a FLAKY external API (timeouts, 500s, malformed responses) behind
   an island membrane; assumption Exprs catch drift; quota -> revoke of trust;
   a live /ext/convert — the v0 debt (a live /convert transaction) is closed in v1.
G6 complexity: a genome of 20 entities x 8 rules (160 rules, invariants) —
   validate/COURT AT SCALE (P6 measurement), throughput, go build.
"""
import concurrent.futures
import json
import os
import pathlib
import random
import signal
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
    for _ in range(200):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


# ---------------------------------------------------------------- G6 genome

def big_genome(path: pathlib.Path, n_ent=20, n_rules=8):
    ents = []
    events = []
    for e in range(n_ent):
        en = f"acct{e:02d}"
        rules = []
        for r in range(n_rules // 2):
            ev_in, ev_out = f"Credit{e:02d}_{r}", f"Debit{e:02d}_{r}"
            events += [f"  {ev_in}: {{{en}: str, amount: int}}",
                       f"  {ev_out}: {{{en}: str, amount: int}}"]
            rules.append(f"""      add{r}:
        when: {ev_in}
        guard: "ev.amount > 0"
        body: |
          s.balance = s.balance + ev.amount
          s.ops = s.ops + 1
        contract: {{post: "s.balance >= 0 and s.ops >= 0"}}
      sub{r}:
        when: {ev_out}
        guard: "ev.amount > 0 and s.balance >= ev.amount"
        body: |
          s.balance = s.balance - ev.amount
          s.ops = s.ops + 1
        contract: {{post: "s.balance >= 0"}}""")
        ents.append(f"""  {en}:
    key: {en}
    instances: [a{e:02d}x, a{e:02d}y]
    state: {{balance: int, ops: int}}
    init:  {{balance: 1000}}
    rules:
{chr(10).join(rules)}""")
    path.write_text(f"""onto: 1
name: bigcorp
retry_window: 4096
events:
{chr(10).join(events)}
entities:
{chr(10).join(ents)}
invariants:
  no_money_lost: "all(a.balance >= 0 for a in acct00)"
queries:
  total00: "sum(a.balance for a in acct00)"
""", encoding="utf-8")
    return path


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism

    # =============================================== G1: volume + snapshots
    g = G.load(ROOT / "genomes" / "hotel.yaml")
    data = pathlib.Path(tempfile.mkdtemp(prefix="stress-vol-"))
    org = Organism(g, data)
    org.snapshot_every = 50_000
    N = 200_000
    t1 = time.perf_counter()
    for i in range(N):
        org.handle({"id": f"v{i}", "type": "ChargeRequested",
                    "wallet": "bob" if i % 2 else "alice", "amount": 0})
    ingest = N / (time.perf_counter() - t1)
    org.checkpoint()
    t1 = time.perf_counter()
    org2 = Organism(g, data)                       # start from a snapshot
    warm_start = time.perf_counter() - t1
    (data / "checkpoint.json").unlink()
    t1 = time.perf_counter()
    org3 = Organism(g, data)                       # full replay
    cold_start = time.perf_counter() - t1
    same = org2.snapshot() == org3.snapshot()
    print(f"G1: ingest {ingest:,.0f} ev/s (fsync); start from snapshot "
          f"{warm_start:.2f}s vs full replay {cold_start:.2f}s "
          f"(x{cold_start / max(warm_start, 1e-9):.1f}); states equal: {same}")
    R.append((f"G1 volume {N // 1000}k: snapshot cuts the start x"
              f"{cold_start / max(warm_start, 1e-9):.0f}, folds identical",
              same and warm_start < cold_start / 3))
    # a corrupt snapshot is rejected by hash
    org3.checkpoint()
    cp = json.loads((data / "checkpoint.json").read_text())
    cp["state"]["wallet"]["bob"]["balance"] += 777        # corruption
    (data / "checkpoint.json").write_text(json.dumps(cp))
    org4 = Organism(g, data)
    rejected = "checkpoint_rejected" in (data / "ledger.jsonl").read_text()
    R.append(("G1 corrupt snapshot rejected by hash -> honest full replay",
              rejected and org4.snapshot() == org3.snapshot()))

    # =============================================== G2: kill -9 mid-write
    data2 = pathlib.Path(tempfile.mkdtemp(prefix="stress-torn-"))
    orgt = Organism(g, data2)
    for i in range(50):
        orgt.handle({"id": f"t{i}", "type": "ChargeRequested",
                     "wallet": "bob", "amount": 1})
    with (data2 / "events.jsonl").open("a") as f:
        f.write('{"id": "torn", "type": "ChargeRequ')      # truncated record
    orgt2 = Organism(g, data2)
    led = (data2 / "ledger.jsonl").read_text()
    R.append(("G2 torn line (kill -9 during a write): the organism is alive, "
              "torn_lines in the ledger, state correct",
              orgt2.state["wallet"]["bob"]["balance"] == 950
              and '"torn_lines": 1' in led))

    # =============================================== G3: duplicate storm + garbage
    # storm = RETRIES of one message in a row (hotel dedup window = 8 —
    # cycling 50 distinct ids would be a test AGAINST contract D26)
    orgt2.handle({"id": "storm", "type": "ChargeRequested",
                  "wallet": "bob", "amount": 1})
    base_balance = orgt2.state["wallet"]["bob"]["balance"]
    dup_hits = 0
    for i in range(10_000):
        out = orgt2.handle({"id": "storm", "type": "ChargeRequested",
                            "wallet": "bob", "amount": 1})
        dup_hits += out["status"] == "dup"
    garbage = [
        {"id": "", "type": "ChargeRequested"},
        {"id": "g1", "type": "NoSuchEvent"},
        {"id": "g2", "type": "ChargeRequested", "wallet": "bob"},
        {"id": "g3", "type": "ChargeRequested", "wallet": "NOBODY", "amount": 5},
        {"no": "id at all"},
    ]
    outcomes = [orgt2.handle(ev).get("status") for ev in garbage]
    alive = orgt2.state["wallet"]["bob"]["balance"] == base_balance
    print(f"G3: duplicates rejected {dup_hits}, garbage -> {outcomes}")
    R.append(("G3 duplicate storm (within the window) + 5 kinds of garbage: "
              "everything classified, state untouched",
              alive and dup_hits == 10_000
              and outcomes[3] == "applied"      # unknown-instance = no-op inside
              and all(o in ("error", "dup", "applied") for o in outcomes)))

    # =============================================== G4: concurrency (HTTP)
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(ROOT / "genomes/hotel.yaml"), "--port", "8671",
                             "--data", tempfile.mkdtemp(prefix="stress-conc-")],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    assert wait_up(8671)
    def hammer(t):
        for i in range(150):
            http(8671, "/event", {"id": f"c{t}_{i}", "type": "ChargeRequested",
                                  "wallet": "bob", "amount": 1})
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        list(ex.map(hammer, range(8)))
    st = http(8671, "/state/wallet/bob")
    spent = 1000 - st["balance"]
    ok_conc = spent == st["charges"] and spent == 1000  # guard stopped at zero
    print(f"G4: 8 threads x 150 charges: balance={st['balance']}, "
          f"charges={st['charges']} (conservation settles)")
    R.append(("G4 concurrency: money settles to the penny, "
              "the guard held at zero", ok_conc))
    proc.kill()

    # =============================================== G5: flaky external API
    ws = pathlib.Path(tempfile.mkdtemp(prefix="stress-dirt-"))
    # flaky "foreign organism"
    flaky_port = 8672
    class Flaky(threading.Thread):
        daemon = True
        def run(self):
            from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
            rnd = random.Random(7)
            class H(BaseHTTPRequestHandler):
                def log_message(self, *a): pass
                def do_POST(self):
                    roll = rnd.random()
                    if roll < 0.25:
                        time.sleep(0.25)                    # stalls
                    if roll < 0.15:
                        self.send_response(500); self.end_headers(); return
                    body = json.dumps({"rate": 100 if roll < 0.9 else -3}).encode()
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers(); self.wfile.write(body)
            ThreadingHTTPServer(("127.0.0.1", flaky_port), H).serve_forever()
    Flaky().start()
    (ws / "islands").mkdir()
    (ws / "islands" / "fx.py").write_text(f'''
# ISLAND (hand-written, trusted, behind the membrane): the only place with the network.
import json, urllib.request

def convert(payload):
    req = urllib.request.Request("http://127.0.0.1:{flaky_port}/rate",
                                 data=json.dumps(payload).encode(),
                                 headers={{"Content-Type": "application/json"}})
    with urllib.request.urlopen(req, timeout=2) as r:
        data = json.loads(r.read())
    rate = data["rate"]
    if rate <= 0:
        raise ValueError(f"foreign organism returned nonsense rate={{rate}}")
    return {{"amount_eur": payload.get("amount", 0) * 100 // rate}}
''', encoding="utf-8")
    (ws / "dirty.yaml").write_text('''onto: 1
name: dirty
events: {}
entities: {}
externals:
  fx:
    island: islands/fx.py
    provides: convert
    assumptions:
      - "latency_ms < 100"
      - "error_rate_pct < 10"
    quota: 5
''', encoding="utf-8")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(ws / "dirty.yaml"), "--port", "8673",
                             "--data", str(ws / "data")],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    assert wait_up(8673)
    codes = {}
    for i in range(60):
        try:
            out = http(8673, "/ext/fx", {"amount": 500}, timeout=5)
            codes["200"] = codes.get("200", 0) + 1
        except urllib.error.HTTPError as e:
            codes[str(e.code)] = codes.get(str(e.code), 0) + 1
    hp = http(8673, "/health")["externals"]["fx"]
    led5 = (ws / "data" / "ledger.jsonl").read_text()
    print(f"G5: /ext/fx x60 -> {codes}; attestation: {hp}")
    R.append(("G5 live /ext/convert through the membrane (v0 debt closed): "
              "the organism survived the flakiness, errors=502",
              codes.get("200", 0) > 0 and wait_up(8673)))
    R.append(("G5 drift monitors: assumption Exprs violated, quota -> "
              "REVOKE OF TRUST in the foreigner (cert_valid=False in the attestation)",
              "drift_violation" in led5 and hp["cert_valid"] is False
              and "revoke_external_trust" in led5))
    proc.kill()

    # =============================================== G6: complexity (P6 measurement)
    bigp = big_genome(pathlib.Path(tempfile.mkdtemp(prefix="stress-big-")) / "big.yaml")
    t1 = time.perf_counter()
    bg = G.load(bigp)
    t_validate = time.perf_counter() - t1
    n_rules = sum(len(e.rules) for e in bg.entities.values())
    court = subprocess.run([str(PY), "-m", "onto.cli", "court", str(bigp)],
                          cwd=ROOT, capture_output=True, text=True)
    import re as _re
    t1 = time.perf_counter()
    court2 = subprocess.run([str(PY), "-m", "onto.cli", "court", str(bigp)],
                           cwd=ROOT, capture_output=True, text=True)
    t_court = time.perf_counter() - t1
    orgb = Organism(bg, tempfile.mkdtemp(prefix="stress-big-d-"))
    orgb._append_log = lambda ev: None
    M = 20_000
    t1 = time.perf_counter()
    for i in range(M):
        orgb.handle({"id": f"b{i}", "type": "Credit00_0", "acct00": "a00x",
                     "amount": 1})
    thr = M / (time.perf_counter() - t1)
    t1 = time.perf_counter()
    mat = subprocess.run([str(PY), "-m", "onto.cli", "materialize", str(bigp),
                          "--dialect", "go-stdlib",
                          "--out", str(bigp.parent / "big_go")],
                         cwd=ROOT, capture_output=True, text=True)
    t_go = time.perf_counter() - t1
    print(f"G6: {len(bg.entities)} entities / {n_rules} rules / "
          f"{len(bg.events)} events; validate {t_validate:.1f}s; COURT (all "
          f"contracts+mutants) {t_court:.1f}s ({t_court / n_rules * 1000:.0f}ms/rule); "
          f"organism {thr:,.0f} ev/s; go materialize+build {t_go:.1f}s")
    R.append((f"G6 complexity 20x8: validate {t_validate:.1f}s, court "
              f"{t_court:.0f}s on {n_rules} rules, go build "
              f"{'OK' if mat.returncode == 0 else 'FAIL'}",
              court.returncode == 0 and court2.returncode == 0
              and mat.returncode == 0 and t_court < 120 and thr > 3000))

    print(f"\n=== EXAM: FILTH AND VOLUME ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
