# -*- coding: utf-8 -*-
"""EXAM U3 "TYPES-2" (D66): decimal/timestamp — representation at the membrane,
int semantics. The court judges the carrier (decidable), log/replay see only
the carrier, human forms are always accepted on input and returned via
?repr=human; optional/list-state as primitives are REJECTED (NOT §34-35)."""
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
PORT = 8771
R = []


def http(path, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}",
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G

    # 1. normalization: carrier int, representation map
    g = G.load(ROOT / "genomes/billing2.yaml")
    inv = g.entities["invoice"]
    R.append(("carrier: decimal/timestamp -> int, the court doesn't see types-2",
              inv.state["amount"] == "int" and inv.state["due"] == "int"
              and g.reprs["invoice.amount"] == "decimal"
              and g.reprs["Issued.due"] == "timestamp"))

    # 2. an unknown type is still rejected (float is contraband)
    import yaml
    raw = yaml.safe_load((ROOT / "genomes/billing2.yaml").read_text())
    raw["entities"]["invoice"]["state"]["amount"] = "float"
    bad = ROOT / "build" / "bad_types.yaml"
    bad.parent.mkdir(exist_ok=True)
    bad.write_text(yaml.safe_dump(raw, allow_unicode=True))
    try:
        G.load(bad)
        rejected = False
    except G.GenomeError as e:
        rejected = "float" in str(e)
    R.append(("float rejected with a clear reason", rejected))

    # 3. court independently: the decimal genome is provable (int theory)
    court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                            str(ROOT / "genomes/billing2.yaml")],
                           cwd=ROOT, capture_output=True, text=True)
    R.append(("COURT on types-2: ALL PROVED", court.returncode == 0))

    # --- live organism
    data = tempfile.mkdtemp(prefix="types2-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(ROOT / "genomes/billing2.yaml"),
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

        # 4. input in human forms: "123.45" + ISO
        out = http("/event", {"id": "e1", "type": "Issued", "invoice": "A-1",
                              "amount": "123.45",
                              "due": "2026-09-01T12:00:00Z"})
        st = http("/state/invoice/A-1")
        R.append(("input human: amount='123.45' -> carrier 12345, due -> unix",
                  out["status"] == "applied" and st["amount"] == 12345
                  and st["due"] == 1788264000))

        # 5. input as a raw carrier: int passes through as-is
        out = http("/event", {"id": "e2", "type": "Issued", "invoice": "A-2",
                              "amount": 678, "due": 1788264000})
        st2 = http("/state/invoice/A-2")
        R.append(("input raw: the int carrier passes without conversion",
                  out["status"] == "applied" and st2["amount"] == 678))

        # 6. output via ?repr=human
        h = http("/state/invoice/A-1?repr=human")
        R.append((f"output human: {h['amount']} / {h['due']}",
                  h["amount"] == "123.45"
                  and h["due"] == "2026-09-01T12:00:00Z"))

        # 7. /list with human rendering and a filter
        lst = http("/list/invoice?status=open&repr=human&_limit=10")
        R.append(("/list?repr=human: rows in human form",
                  lst["count"] == 2
                  and all(r["amount"] in ("123.45", "6.78") for r in lst["rows"])))

        # 8. malformed decimal -> 400 with a reason
        try:
            http("/event", {"id": "e3", "type": "Issued", "invoice": "A-3",
                            "amount": "12.3.4", "due": 0})
            code, err = 200, {}
        except urllib.error.HTTPError as e:
            code, err = e.code, json.loads(e.read())
        R.append(("malformed decimal '12.3.4' -> 400 with a reason",
                  code == 400 and "bad decimal" in err.get("error", "")))

        # 9. the write-ahead log stores ONLY the carrier (replay is blind to forms)
        lines = [json.loads(l) for l in
                 (pathlib.Path(data) / "events.jsonl").read_text().splitlines()]
        R.append(("log: only the int carrier (replay knows no representations)",
                  all(isinstance(e["amount"], int) and isinstance(e["due"], int)
                      for e in lines if e["type"] == "Issued")))

        # 10. the admin UI knows types-2 (placeholder hints in the forms)
        admin = urllib.request.urlopen(
            f"http://127.0.0.1:{PORT}/admin", timeout=5).read().decode()
        R.append(("/admin: forms with hints '12.34' and ISO",
                  'placeholder="12.34"' in admin
                  and 'placeholder="2026-01-01T00:00:00Z"' in admin))
    finally:
        proc.kill()

    print(f"\n=== EXAM: TYPES-2 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
