# -*- coding: utf-8 -*-
"""EXAM "THE MODEL GROWS ISLANDS" (IDEAL pearl 4, D63): the fx island adapter
for fxlive is grown by an SLM without a human; the gates = acceptance through
a LIVE flaky upstream (retries are forced, not trusted), the membrane's drift
monitors judge the grown code the same as handwritten; REVOKE on total failure;
the cache = a certified artifact."""
import json
import os
import pathlib
import shutil
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def flaky_fx(port, mode):
    """Flaky converter: every 3rd request — 500, every 5th — slow.
    mode["dead"]=True -> 100% errors (total failure for REVOKE)."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    counter = {"n": 0}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            counter["n"] += 1
            n = counter["n"]
            if mode.get("dead") or n % 3 == 0:
                self.send_response(500)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if n % 5 == 0:
                time.sleep(0.15)
            ln = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(ln) or b"{}")
            body = json.dumps({"status": "ok", "rate": 90,
                               "converted": int(req.get("amount", 0)) * 90 // 100}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    ThreadingHTTPServer.allow_reuse_address = True
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, counter


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growisland
    from onto.core import genome as G, membrane as MB
    from onto.core.organism import Organism
    from onto.core.serve import make_server
    from onto.ribosome import Provider

    # working copy of the genome (the grown file doesn't litter genomes/)
    ws = pathlib.Path(tempfile.mkdtemp(prefix="fisland-"))
    shutil.copy(ROOT / "genomes/fxlive.yaml", ws / "fxlive.yaml")
    os.environ["FX_PORT"] = "8641"
    srv, counter = flaky_fx(8641, mode={})

    provider = Provider(ROOT / ".onto" / "config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_island.jsonl"

    # 1) GROWTH: the SLM writes the adapter, gates = acceptance through live flak
    tele = growisland.grow(ws / "fxlive.yaml", "fx", provider)
    grown = (ws / "islands/fx_adapter.py")
    R.append(("grown by the model: gates GREEN (flakiness survived via retries)",
              not tele["island_manual"] and grown.exists()))
    n_attempts = len(tele["attempts"])
    print(f"  telemetry: model={tele.get('model')}, attempts={n_attempts}, "
          f"requests to mock={counter['n']}")

    # 2) tooth of the sanitizing membrane: a forbidden import is rejected
    bad = "import subprocess\n\ndef convert(payload):\n    return {}\n"
    R.append(("import membrane: subprocess rejected",
              "forbidden imports" in (growisland.sanitize(bad, "convert") or "")))

    # 3) tooth of acceptance-through-flak: an adapter WITHOUT retries goes red on the cases
    g = G.load(ws / "fxlive.yaml")
    ext = MB.External.model_validate(g.externals["fx"])
    naive = (
        "import json, os, urllib.request\n\n"
        "def convert(payload):\n"
        "    port = os.environ.get('FX_PORT', '8641')\n"
        "    req = urllib.request.Request(f'http://127.0.0.1:{port}/rate',\n"
        "        data=json.dumps(payload).encode(),\n"
        "        headers={'Content-Type': 'application/json'})\n"
        "    with urllib.request.urlopen(req, timeout=1) as r:\n"
        "        d = json.loads(r.read())\n"
        "    return {'converted': d['converted'], 'rate': d['rate']}\n")
    verdict = growisland.gates(naive, "fx", ext, ws, "islands/fx_naive.py")
    R.append(("gate tooth: an adapter without retries rejected by live flakiness",
              verdict is not None and "case[" in (verdict or "")))

    # 4) the grown island mounted into the organism: /ext/fx works
    g2 = G.load(ws / "fxlive.yaml")
    org = Organism(g2, tempfile.mkdtemp(prefix="fisland-data-"))
    http_srv = make_server(org, port=8642, genome_base=str(ws))
    threading.Thread(target=http_srv.serve_forever, daemon=True).start()
    time.sleep(0.2)

    def call(path, payload=None):
        req = urllib.request.Request(f"http://127.0.0.1:8642{path}",
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())

    outs = [call("/ext/fx", {"from": "USD", "to": "EUR", "amount": a})
            for a in (100, 250, 33)]
    ok_live = (outs[0].get("converted") == 90 and outs[1].get("converted") == 225
               and outs[2].get("converted") == 29)
    hp = call("/health")["externals"]["fx"]
    R.append(("organism: /ext/fx through flakiness is correct, attestation cert_valid",
              ok_live and hp["cert_valid"]))

    # 5) total upstream failure -> drift -> REVOKE (trust in the external revoked)
    srv.shutdown(); srv.server_close()
    dead_srv, _ = flaky_fx(8641, mode={"dead": True})
    for _ in range(30):
        try:
            call("/ext/fx", {"from": "USD", "to": "EUR", "amount": 5})
        except Exception:  # noqa: BLE001 — a 502 is exactly the expected behavior
            pass
        hp = call("/health")["externals"]["fx"]
        if not hp["cert_valid"]:
            break
    R.append(("total failure: drift caught, trust revoked (REVOKE)",
              not hp["cert_valid"]))
    led_lines = org.ledger.path.read_text(encoding="utf-8").splitlines()
    revoked = [l for l in led_lines if '"revoke_external_trust"' in l]
    R.append(("REVOKE in the ledger with provenance", len(revoked) >= 1))

    # 6) cache = certified artifact: a repeat grow without the network
    dead_srv.shutdown(); dead_srv.server_close(); srv.server_close()
    srv2, counter2 = flaky_fx(8641, mode={})
    calls_before = provider.calls if hasattr(provider, "calls") else None
    grown.unlink()
    tele2 = growisland.grow(ws / "fxlive.yaml", "fx", provider)
    R.append(("cache: a repeat grow — CACHE hit, file restored",
              tele2.get("cache") is True and grown.exists()))
    srv2.shutdown(); srv2.server_close()

    print()
    ok = 0
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok += passed
    print(f"\nISLAND EXAM: {ok}/{len(R)} in {time.time()-t0:.1f} s")
    return 0 if ok == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
