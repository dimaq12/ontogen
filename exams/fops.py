# -*- coding: utf-8 -*-
"""U8-CONSOLE EXAM (D69): /ops — operator console served from the organism:
ledger (proof journal) with a filter by kind, external attestations, heat,
checkpoint button. Zero hand-written UI; interview/molt are CLI, their traces
are visible."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
PORT = 8775
R = []


def http(path, payload=None, token=None, method=None):
    hdr = {"Content-Type": "application/json"}
    if token:
        hdr["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=hdr, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
    try:
        return json.loads(raw)
    except ValueError:
        return raw.decode()


def main():
    t0 = time.time()
    data = tempfile.mkdtemp(prefix="ops-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(ROOT / "genomes/authwallet.yaml"),
                             "--port", str(PORT), "--data", data],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                http("/health")
                break
            except Exception:
                time.sleep(0.05)
        # feed the journal: applied events + auth denials
        http("/event", {"id": "o1", "type": "Deposited", "wallet": "bob",
                        "amount": 100}, token="tok-bob")
        http("/event", {"id": "o2", "type": "Deposited", "wallet": "alice",
                        "amount": 5}, token="tok-bob")           # 403
        http("/event", {"id": "o3", "type": "Noop", "wallet": "b"},
             token="tok-bob")                                     # 403
        http("/event", {"id": "o4", "type": "Deposited", "wallet": "x",
                        "amount": 1}, token="garbage")            # 401

        page = http("/ops")
        R.append(("/ops: operator console served (ledger+checkpoint+attestations)",
                  isinstance(page, str) and "onto ops" in page
                  and "/ops/ledger" in page and "checkpoint" in page
                  and "externals" in page))
        led = http("/ops/ledger")
        R.append((f"/ops/ledger: journal is readable ({led['total']} entries)",
                  led["total"] >= 3))
        den = http("/ops/ledger?kind=auth_denied")
        R.append((f"filter kind=auth_denied: {len(den['entries'])} entries, "
                  "with why provenance",
                  len(den["entries"]) == 3
                  and all("why" in e for e in den["entries"])))
        lim = http("/ops/ledger?kind=auth_denied&_limit=2")
        R.append(("_limit=2: tail of the journal", len(lim["entries"]) == 2))
        ck = http("/checkpoint", method="POST")
        R.append(("checkpoint from the console works",
                  isinstance(ck, dict) and proc.poll() is None))
        # journal hash-chain intact (prev links)
        raw = [json.loads(l) for l in
               (pathlib.Path(data) / "ledger.jsonl").read_text().splitlines()]
        chain = all("prev" in e for e in raw)
        R.append((f"journal is a hash-chain ({len(raw)} entries, prev on all)",
                  chain and len(raw) >= 3))
    finally:
        proc.kill()

    print(f"\n=== OPERATOR CONSOLE EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
