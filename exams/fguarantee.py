# -*- coding: utf-8 -*-
"""EXAM guarantee chain (D90): every part of the code is PROVEN here or
DELEGATED to a NAMED external guarantor — nothing is left uncertified. An
island that leans on a vetted library declares a guarantor; the membrane
verifies (provenance) it is really the pinned one at load (integrity, not a
security audit — the guarantor's OWN audit is the guarantee); a mismatch
REVOKES. The attest passport prints the full chain and FLAGS any uncovered
part (contained-only)."""
import json
import pathlib
import sys
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import membrane as MB

    # an island that DELEGATES cryptographic work to the platform OpenSSL via
    # the stdlib `ssl` module (a real, externally-audited guarantor).
    d = pathlib.Path(tempfile.mkdtemp(prefix="guar-"))
    (d / "island.py").write_text(
        "import ssl\n"
        "def fingerprint(payload):\n"
        "    return {'ok': True, 'backend': ssl.OPENSSL_VERSION[:7]}\n")

    class Led:
        def __init__(self): self.rows = []
        def record(self, k, p): self.rows.append((k, p))

    # 1. valid delegation -> verified at load, guarantee recorded
    ext_ok = MB.External(
        island="island.py", provides="fingerprint",
        assumptions=["error_rate_pct < 50"],
        guarantee=MB.Guarantee(by="openssl", ref="platform OpenSSL (its own audit)",
                               module="ssl", attr="OPENSSL_VERSION", expect="OpenSSL"))
    led = Led()
    ad = MB.MonitoredAdapter("crypto", ext_ok, d, led)
    kinds = [k for k, _ in led.rows]
    R.append((f"DELEGATION verified at load: guarantor present + version "
              f"({ad.guarantee_detail})",
              ad.cert_valid and "guarantee_verified" in kinds
              and "OpenSSL" in (ad.guarantee_detail or "")))

    # 2. TAMPERED guarantee (wrong expected guarantor version) -> UNMET -> refuse
    ext_bad = MB.External(
        island="island.py", provides="fingerprint",
        assumptions=["error_rate_pct < 50"],
        guarantee=MB.Guarantee(by="openssl", ref="x",
                               module="ssl", attr="OPENSSL_VERSION",
                               expect="BoringSSL-9.9"))   # not what's installed
    led2 = Led()
    refused = False
    try:
        MB.MonitoredAdapter("crypto", ext_bad, d, led2)
    except ValueError:
        refused = True
    R.append(("TAMPER: wrong pinned guarantor -> guarantee UNMET, island "
              "REFUSES to load + ledger guarantee_unmet",
              refused and "guarantee_unmet" in [k for k, _ in led2.rows]))

    # 3. missing guarantor module -> UNMET
    ext_missing = MB.External(
        island="island.py", provides="fingerprint",
        assumptions=["error_rate_pct < 50"],
        guarantee=MB.Guarantee(by="ghost", ref="x", module="no_such_lib_xyz"))
    refused2 = False
    try:
        MB.MonitoredAdapter("crypto", ext_missing, d, Led())
    except ValueError:
        refused2 = True
    R.append(("missing guarantor module -> UNMET (can't claim a borrowed "
              "guarantee that isn't installed)", refused2))

    # 4. attest passport: the chain classifies EVERY part; uncovered flagged
    from onto import attest as AT
    # a genome with a DELEGATED island, a FUNCTIONAL island (cases), and a
    # CONTAINED-ONLY island (neither) — the passport must tell them apart.
    (d / "isl2.py").write_text("def go(p): return {'v': 1}\n")
    G = {"onto": 1, "name": "gtest", "retry_window": 8,
         "events": {"Ping": {"k": "str"}},
         "entities": {"k": {"key": "k", "instances": ["a"], "state": {"n": "int"},
                            "init": {"n": 0}, "rules": {"p": {"when": "Ping",
                            "body": "s.n = s.n + 1\n", "contract": {"post": "s.n >= 0"}}}}},
         "queries": {},
         "externals": {
             "delegated": {"island": "island.py", "provides": "fingerprint",
                           "assumptions": ["error_rate_pct < 50"],
                           "guarantee": {"by": "openssl", "ref": "platform OpenSSL",
                                         "module": "ssl", "attr": "OPENSSL_VERSION",
                                         "expect": "OpenSSL"}},
             "functional": {"island": "isl2.py", "provides": "go",
                            "assumptions": ["error_rate_pct < 50"],
                            "cases": [{"payload": {}, "expect": {"v": 1}}]},
             "bare": {"island": "isl2.py", "provides": "go",
                      "assumptions": ["error_rate_pct < 50"]}}}
    gp = d / "g.yaml"
    gp.write_text(yaml.safe_dump(G, sort_keys=False))
    a = AT.build_attest(gp)
    chain = a["guarantee_chain"]
    R.append((f"passport chain classifies every part: delegated="
              f"{chain['island:delegated'][:18]}, functional="
              f"{chain['island:functional'][:18]}, bare="
              f"{chain['island:bare'][:14]}",
              chain["island:delegated"].startswith("DELEGATED")
              and chain["island:functional"].startswith("functional")
              and chain["island:bare"].startswith("CONTAINED ONLY")))
    R.append((f"passport FLAGS the uncovered part (bare island) and only it: "
              f"{a['uncovered']}",
              a["uncovered"] == ["island:bare"]))

    print(f"\n=== EXAM guarantee chain ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
