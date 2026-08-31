# -*- coding: utf-8 -*-
"""EXAM U4 «AUTH GENE» (D67): roles/predicates are bool-Exprs of the genome over
{principal, ev}; the IdP is an island behind the membrane; deny-by-default;
denials go into the ledger with provenance. Zero hand-written authorization
code on the operator's side."""
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
PORT = 8772
R = []


def post(payload, token=None):
    """-> (code, body)"""
    hdr = {"Content-Type": "application/json"}
    if token:
        hdr["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/event",
                                 data=json.dumps(payload).encode(), headers=hdr)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G

    # 1-2. validation: broken auth genomes are rejected with a reason
    import yaml
    raw = yaml.safe_load((ROOT / "genomes/authwallet.yaml").read_text())
    bad_dir = ROOT / "build"
    bad_dir.mkdir(exist_ok=True)
    b1 = dict(raw)
    b1["auth"] = {"idp": "ghost", "rules": {"Deposited": "principal.role == 'x'"}}
    (bad_dir / "bad_auth1.yaml").write_text(yaml.safe_dump(b1, allow_unicode=True))
    try:
        G.load(bad_dir / "bad_auth1.yaml")
        r1 = False
    except G.GenomeError as e:
        r1 = "auth.idp" in str(e)
    R.append(("auth.idp pointing at a nonexistent island -> rejected", r1))
    b2 = dict(raw)
    b2["auth"] = {"idp": "idp", "rules": {"Deposited": "principal.balance + 1"}}
    (bad_dir / "bad_auth2.yaml").write_text(yaml.safe_dump(b2, allow_unicode=True))
    try:
        G.load(bad_dir / "bad_auth2.yaml")
        r2 = False
    except G.GenomeError as e:
        r2 = "auth.rules.Deposited" in str(e)
    R.append(("malformed Expr in auth.rules -> rejected by the typechecker", r2))

    # --- live organism
    data = tempfile.mkdtemp(prefix="auth-")
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "serve",
                             str(ROOT / "genomes/authwallet.yaml"),
                             "--port", str(PORT), "--data", data],
                            cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health",
                                       timeout=2)
                break
            except Exception:
                time.sleep(0.05)

        # 3. no token -> 401
        c, b = post({"id": "a1", "type": "Deposited", "wallet": "bob", "amount": 100})
        R.append(("no token -> 401", c == 401))
        # 4. garbage token -> 401 (IdP island rejected it)
        c, b = post({"id": "a2", "type": "Deposited", "wallet": "bob",
                     "amount": 100}, token="garbage")
        R.append(("garbage token -> 401 (IdP island rejected it)", c == 401))
        # 5. bob -> own wallet: applied (predicate ev.wallet == principal.subject)
        c, b = post({"id": "a3", "type": "Deposited", "wallet": "bob",
                     "amount": 100}, token="tok-bob")
        R.append(("bob into HIS OWN wallet -> applied", c == 200
                  and b["status"] == "applied"))
        # 6. bob -> someone else's wallet: 403
        c, b = post({"id": "a4", "type": "Deposited", "wallet": "alice",
                     "amount": 100}, token="tok-bob")
        R.append(("bob into SOMEONE ELSE'S wallet -> 403 (genome predicate)", c == 403))
        # 7. admin -> anywhere: applied
        c, b = post({"id": "a5", "type": "Deposited", "wallet": "bob",
                     "amount": 50}, token="tok-alice-admin")
        R.append(("admin into any wallet -> applied", c == 200
                  and b["status"] == "applied"))
        # 8. AdminReset: role decides
        c1, _ = post({"id": "a6", "type": "AdminReset", "wallet": "bob"},
                     token="tok-bob")
        c2, b2 = post({"id": "a7", "type": "AdminReset", "wallet": "bob"},
                      token="tok-alice-admin")
        R.append(("AdminReset: user 403, admin applied",
                  c1 == 403 and c2 == 200 and b2["status"] == "applied"))
        # 9. deny-by-default: Noop with no rule -> 403 even for an admin
        c, b = post({"id": "a8", "type": "Noop", "wallet": "bob"},
                    token="tok-alice-admin")
        R.append(("deny-by-default: event with no rule -> 403 even for an admin",
                  c == 403 and "deny-by-default" in b.get("error", "")))
        # 10. state is honest: only allowed mutations were applied
        st = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{PORT}/state/wallet/bob", timeout=5).read())
        R.append((f"final bob.balance == 0 (reset after 100+50): {st['balance']}",
                  st["balance"] == 0))
        # 11. denials in the ledger with provenance
        led = [json.loads(l) for l in
               (pathlib.Path(data) / "ledger.jsonl").read_text().splitlines()]
        denies = [e for e in led if e["kind"] == "auth_denied"]
        R.append((f"ledger: {len(denies)} auth_denied with why/principal",
                  len(denies) >= 4 and all("why" in e for e in denies)))
        # 12. admin UI: the token field appeared (genome with auth)
        admin = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/admin",
                                       timeout=5).read().decode()
        R.append(("/admin: token field + Authorization in js",
                  'id=tok' in admin and "Authorization" in admin))
    finally:
        proc.kill()

    print(f"\n=== AUTH GENE EXAM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
