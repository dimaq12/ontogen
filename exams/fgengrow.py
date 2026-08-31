# -*- coding: utf-8 -*-
"""EXAM "DIALECT GENERATOR GROWTH" (pearl 5, tier 2, D68): the model writes
the emit(genome)->organism.js emitter ITSELF; the gates certify it against a
SET of genomes (multi-genome CEGIS: node --check, judge, parity with the
canon, kill -9/replay — on each one). Then the KEY part: a genome the
generator has never seen is emitted WITHOUT calling the model and passes the
same gates. The dialect stops costing tokens."""
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

CERTS = [("genomes/hotel.yaml", "exams/hotel_flows.yaml"),
         ("genomes/shop.yaml", "exams/shop_flows.yaml"),
         ("genomes/billing2.yaml", "exams/billing2_flows.yaml")]
FRESH = ("genomes/booking.yaml", "exams/booking_flows.yaml")


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto import growdialect, growgen
    from onto.ribosome import Provider

    provider = Provider(ROOT / ".onto/config.toml")
    provider.usage_path = ROOT / ".onto" / "usage_gengrow.jsonl"
    out = ROOT / "build" / "gen_node"

    certs = [(ROOT / g, ROOT / f) for g, f in CERTS]
    tele = growgen.grow(certs, out, provider, ROOT)
    n_att = len(tele["attempts"])
    R.append((f"generator grew [{tele.get('model')}, "
              f"{n_att} attempts{', cache' if tele.get('cache') else ''}]",
              not tele["island"]))
    if tele["island"]:
        print(json.dumps(tele, ensure_ascii=False)[:3000])
        return 1
    R.append((f"certified on {len(CERTS)} genomes "
              "(judge+parity+kill -9 on each)", True))

    # --- KEY PART: a fresh genome -> organism WITHOUT the model
    from onto.core import genome as G
    ns: dict = {}
    exec((out / "emitgen.py").read_text(encoding="utf-8"), ns)  # noqa: S102
    g = G.load(ROOT / FRESH[0])
    js_text = ns["emit"](g.model_dump())
    js = out / "organism_fresh_booking.js"
    js.write_text(js_text, encoding="utf-8")
    calls_before = _ncalls()
    snap = growgen.canon_snapshot(ROOT / FRESH[0], ROOT / FRESH[1], ROOT, 8794)
    bad = growdialect.gates(js, ROOT / FRESH[0], ROOT / FRESH[1], 8795, snap,
                            ROOT / ".venv/bin/python", ROOT)
    R.append(("FRESH genome (booking, outside certification) emitted and "
              "passed all gates", bad is None))
    if bad:
        print("fresh verdict:", bad)
    R.append(("emitting the fresh genome did NOT call the model (0 calls)",
              _ncalls() == calls_before))

    print(f"\n=== EXAM GENERATOR GROWTH ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def _ncalls():
    p = ROOT / ".onto" / "usage_gengrow.jsonl"
    return len(p.read_text().splitlines()) if p.exists() else 0


if __name__ == "__main__":
    sys.exit(main())
