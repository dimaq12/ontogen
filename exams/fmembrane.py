# -*- coding: utf-8 -*-
"""EXAM membrane containment (adversarial self-audit D93): REVOKE is a real
circuit-break, not a flag. Proves (offline, no SLM): (1) a persistently-
violating island gets its trust REVOKED and then subsequent calls are BLOCKED
(the island fn is NOT invoked — fail-fast 503); (2) a non-dict island return is
CONTAINED as a failure, never entering the organism unvalidated; (3) an island
exception is contained (502, no propagation)."""
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


class _Ledger:
    def __init__(self): self.lines = []
    def record(self, kind, payload): self.lines.append((kind, payload))


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core.membrane import External, MonitoredAdapter

    d = pathlib.Path(tempfile.mkdtemp())

    # island whose behaviour we control by a module global (call count)
    (d / "isl.py").write_text(
        "N = {'i': 0}\n"
        "def go(p):\n"
        "    N['i'] += 1\n"
        "    if p.get('mode') == 'raise':\n"
        "        raise RuntimeError('boom')\n"
        "    if p.get('mode') == 'garbage':\n"
        "        return 'not-a-dict'\n"
        "    return {'ok': 1, 'n': N['i']}\n")

    # --- 1. REVOKE blocks subsequent calls (fail-fast, island NOT invoked) ---
    ext = External(island="isl.py", provides="go",
                   assumptions=["error_rate_pct < 40"], quota=4)
    lg = _Ledger()
    a = MonitoredAdapter("fx", ext, d, lg)
    # drive failures until revoked
    codes = []
    for _ in range(30):
        code, _ = a.call({"mode": "raise"})
        codes.append(code)
        if not a.cert_valid:
            break
    R.append((f"persistent failure -> trust REVOKED: cert_valid={a.cert_valid}",
              not a.cert_valid))
    # capture the island's internal call count at revoke, then call again
    n_at_revoke = a._fn.__globals__["N"]["i"]
    code2, out2 = a.call({"mode": "ok"})  # a HEALTHY payload, but trust is gone
    n_after = a._fn.__globals__["N"]["i"]
    R.append((f"after REVOKE: call BLOCKED fail-fast (503) not 200: got {code2}",
              code2 == 503))
    R.append((f"after REVOKE: the island fn was NOT invoked (count {n_at_revoke} "
              f"-> {n_after}, unchanged)", n_after == n_at_revoke))
    R.append(("REVOKE recorded in the ledger + call_blocked_revoked logged",
              any(k == "revoke_external_trust" for k, _ in lg.lines)
              and any(k == "call_blocked_revoked" for k, _ in lg.lines)))

    # --- 2. non-dict return CONTAINED as failure (not passed through 200) ---
    ext2 = External(island="isl.py", provides="go",
                    assumptions=["error_rate_pct < 40"], quota=100)
    a2 = MonitoredAdapter("fx2", ext2, d, _Ledger())
    code_g, out_g = a2.call({"mode": "garbage"})
    R.append((f"non-dict island return -> CONTAINED as failure (502, dict error), "
              f"not a raw {type('x').__name__} at 200: code={code_g} "
              f"type={type(out_g).__name__}",
              code_g == 502 and isinstance(out_g, dict) and "error" in out_g))

    # --- 3. exception contained (502, no propagation) ---
    a3 = MonitoredAdapter("fx3", ext2, d, _Ledger())
    code_r, out_r = a3.call({"mode": "raise"})
    R.append((f"island exception -> contained (502, dict error, no propagation): "
              f"code={code_r}", code_r == 502 and isinstance(out_r, dict)
              and "error" in out_r))

    print(f"\n=== EXAM membrane containment ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
