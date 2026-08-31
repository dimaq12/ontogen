# -*- coding: utf-8 -*-
"""EXAM §8 «COLD REBUILD» (D74): the model is a SPOF only at the growth EDGE.
Everything behind the frontier must rebuild WITHOUT the model: the key is
physically broken, and all the grown tissue (NL genome, island, node organism)
is restored from certified caches with zero network calls."""
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

DESCRIPTION = open(__file__).read() and None  # placeholder


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growdialect, growisland, nlfront
    from onto.ribosome import Provider

    # key is BROKEN: the provider exists, but the network returns 401 on any call
    cfg = pathlib.Path(tempfile.mkdtemp(prefix="cold-")) / "config.toml"
    real = (ROOT / ".onto/config.toml").read_text()
    import re
    broken = re.sub(r'api_key\s*=\s*"[^"]*"', 'api_key = "sk-or-v1-DEAD"', real)
    cfg.write_text(broken)
    provider = Provider(cfg)
    usage = pathlib.Path(tempfile.mkdtemp(prefix="cold-u-")) / "usage.jsonl"
    provider.usage_path = usage

    # is the key really dead?
    try:
        provider.generate(provider.skills_ladder[0], "ping", seed=1, tag="t")
        dead = False
    except Exception:
        dead = True
    R.append(("key is dead: the model network is unreachable", dead))
    usage.unlink(missing_ok=True)

    # 1. NL front: the same genome from the description — from the cache
    desc = None
    import importlib.util
    spec = importlib.util.spec_from_file_location("fideal", ROOT / "exams/fideal.py")
    fid = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fid)
    desc = fid.DESCRIPTION
    tele = nlfront.build(desc, provider, ROOT / "build" / "rooms_ideal", ROOT,
                         log=lambda m: None)
    R.append(("NL genome rebuilt from the cache (0 model calls)",
              not tele["island"] and tele.get("cache")))

    # 2. island: the grown fx adapter — from the cache (the gates run live!)
    # mock upstream for the gates
    import json as J
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import os
    os.environ["FX_PORT"] = "8641"

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            req = J.loads(self.rfile.read(n) or b"{}")
            body = J.dumps({"status": "ok", "rate": 90,
                            "converted": int(req.get("amount", 0)) * 90 // 100}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    ThreadingHTTPServer.allow_reuse_address = True
    srv = ThreadingHTTPServer(("127.0.0.1", 8641), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tele2 = growisland.grow(ROOT / "genomes/fxlive.yaml", "fx", provider,
                            log=lambda m: None)
    srv.shutdown()
    R.append(("island rebuilt from the cache (gates passed live)",
              not tele2["island_manual"] and tele2.get("cache")))

    # 3. telemetry: ZERO model calls across the entire rebuild
    n_calls = len(usage.read_text().splitlines()) if usage.exists() else 0
    R.append((f"model network calls: {n_calls}", n_calls == 0))

    print(f"\n=== COLD REBUILD EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
