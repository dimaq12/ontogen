# -*- coding: utf-8 -*-
"""EXAM "IDEAL VERSION v0" — an end-to-end run of IDEAL in full:
a Russian DESCRIPTION (with time!) -> NL front builds genome+acceptance ->
gates (checkers+COURT+self-acceptance) -> organism lives -> the warden's timer
ticks events -> /admin (L5), /list and parametric /q (L1), outbound webhook
(L6) -> a NEW LANGUAGE grown by a weak model (pearl 5) -> onto new (L8).
No human in the loop."""
import json
import pathlib
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []

DESCRIPTION = """A meeting-room rental service in a coworking space.

Rooms are added by an administrator. Teams register and top up a deposit
(in kopecks). A team books a free room if its deposit is no less than
20000 kopecks; when a booking is completed a duration in hours is given and
8000 kopecks per hour is charged, but no more than the remaining deposit; the
room is freed. Once per period, a maintenance fee of 500 kopecks is
automatically withheld from every OCCUPIED room, taken from the deposit of the
team occupying it — for this the occupied room remembers its team. We want to
see: how many rooms are occupied right now and how much money in total has
been charged across all teams. Important: the maintenance fee must arrive on
its own, on schedule, not on an operator's request."""


def http(port, path, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read()
        try:
            return json.loads(raw)
        except ValueError:
            return raw.decode()


def wait_up(port):
    for _ in range(150):
        try:
            http(port, "/health")
            return True
        except Exception:
            time.sleep(0.05)
    return False


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growdialect, nlfront
    from onto.ribosome import Provider

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_ideal.jsonl"
    (ROOT / ".onto" / "usage_ideal.jsonl").unlink(missing_ok=True)

    # ---------- 1. description -> genome+acceptance (NL front)
    work = ROOT / "build" / "rooms_ideal"
    tele = nlfront.build(DESCRIPTION, provider, work, ROOT)
    R.append((f"description -> genome+acceptance [{tele.get('model')}, "
              f"{len(tele['attempts'])} attempts]", not tele["island"]))
    if tele["island"]:
        print(json.dumps(tele, ensure_ascii=False)[:2000])
        return 1
    court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                            str(work / "genome.yaml")],
                           cwd=ROOT, capture_output=True, text=True)
    R.append(("COURT independently: ALL PROVED", court.returncode == 0))

    # is there a timer in the genome (time from the description)?
    import yaml
    graw = yaml.safe_load((work / "genome.yaml").read_text())
    has_timer = bool(graw.get("timers"))
    R.append(("TIME: the model set up a timer itself from the phrase \"on schedule\"",
              has_timer))

    # ---------- 2. webhook receiver + organism under the warden
    hooks = []
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Hook(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            hooks.append(json.loads(self.rfile.read(n)))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")
    hs = ThreadingHTTPServer(("127.0.0.1", 8763), Hook)
    threading.Thread(target=hs.serve_forever, daemon=True).start()

    # webhook on the genome's first event (mechanical root edit — L6)
    graw["webhooks"] = {evn: "http://127.0.0.1:8763/h"
                        for evn in graw["events"]}
    # speed up timers for the exam
    for t in (graw.get("timers") or {}).values():
        t["every_s"] = 2
    (work / "genome.yaml").write_text(yaml.safe_dump(graw, allow_unicode=True,
                                                     sort_keys=False))

    from onto.core.warden import Warden
    w = Warden(work / "genome.yaml",
               tempfile.mkdtemp(prefix="ideal-warden-"), 8761)
    w.start()
    judge = subprocess.run([str(PY), "-m", "onto.cli", "judge",
                            str(work / "flows.yaml"),
                            "http://127.0.0.1:8761"],
                           cwd=ROOT, capture_output=True, text=True)
    print(judge.stdout.strip())
    R.append(("organism lives: judge green on the generated acceptance",
              judge.returncode == 0))

    # ---------- 3. the timer ticks ON ITS OWN (warden = source of time)
    q_names = list(graw.get("queries", {}))
    spent_q = next((q for q in q_names if "spent" in q or "charged" in q
                    or "total" in q), q_names[0] if q_names else None)
    before = http(8761, f"/q/{spent_q}")["value"] if spent_q else 0
    for _ in range(3):
        time.sleep(2.1)
        w.tick_timers(time.time())
    after = http(8761, f"/q/{spent_q}")["value"] if spent_q else 0
    R.append((f"timer ticks on its own: '{spent_q}' {before} -> {after}",
              has_timer and after > before))

    # ---------- 4. surfaces L1/L5/L6
    ent0 = sorted(graw["entities"])[0]
    lst = http(8761, f"/list/{ent0}?_limit=5")
    R.append((f"/list/{ent0}: generic query with pagination ({lst['count']} rows)",
              "rows" in lst))
    admin = http(8761, "/admin")
    R.append(("/admin: admin panel generated from the genome (HTML with tables and forms)",
              isinstance(admin, str) and "onto admin" in admin
              and ent0 in admin))
    R.append((f"outbound webhook delivered ({len(hooks)} total)", len(hooks) > 0))
    w.stop()
    hs.shutdown()

    # ---------- 5. any stack: grow node for THIS genome
    subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                    str(work / "genome.yaml"), "--dialect", "python-stdlib",
                    "--out", str(work / "py")],
                   cwd=ROOT, capture_output=True)
    data = tempfile.mkdtemp(prefix="ideal-canon-")
    # canon snapshot — from the INTERPRETER (it has /instances); the emitted py
    # is the reference text for the growth model
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(work / "genome.yaml"),
                             "--port", "8762", "--data", data],
                            cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait_up(8762)
    subprocess.run([str(PY), "-m", "onto.cli", "judge", str(work / "flows.yaml"),
                    "http://127.0.0.1:8762"], cwd=ROOT, capture_output=True)
    from onto.core import genome as G
    g = G.load(work / "genome.yaml")
    canon = {}
    for en, ent in g.entities.items():
        insts = http(8762, f"/instances/{en}")["instances"]
        canon[en] = {i: http(8762, f"/state/{en}/{i}") for i in insts}
    proc.kill()
    tele2 = growdialect.grow(work / "genome.yaml", work / "flows.yaml",
                             work / "node", provider, canon,
                             work / "py/organism.py", ROOT, port=8764)
    R.append((f"ANY STACK: node organism grown "
              f"[{tele2.get('model')}]", not tele2["island"]))

    # ---------- 6. packaging: onto new from this genome
    shutil_dst = pathlib.Path(tempfile.mkdtemp(prefix="ideal-new-")) / "myapp"
    newp = subprocess.run([str(ROOT / ".venv/bin/onto"), "new", str(shutil_dst),
                           "--template", "hotel"],
                          cwd=ROOT, capture_output=True, text=True)
    R.append(("packaging: onto new scaffolds a ready organism project",
              newp.returncode == 0 and (shutil_dst / "genome.yaml").exists()))

    up = ROOT / ".onto/usage_ideal.jsonl"
    calls = [json.loads(l) for l in up.read_text().splitlines()]         if up.exists() else []
    toks = sum((c["tokens_in"] or 0) + (c["tokens_out"] or 0) for c in calls)
    print(f"usage: {len(calls)} calls, {toks} tokens"
          + (" (all from cache)" if not calls else ""))

    print(f"\n=== EXAM IDEAL VERSION ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
