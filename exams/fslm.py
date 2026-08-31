# -*- coding: utf-8 -*-
"""EXAM "skills + a live SLM" (v0 concern #7 in the v1 world): qwen3-coder via
OpenRouter writes match_orders in two phases; gates — properties with a
completeness tooth, equivalence, a relative budget; CEGIS: counterexamples into
the prompt; a semantic cache (a repeat without the network); usage telemetry in
JSONL."""
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G, skills as SK
    from onto import ribosome as RB

    g = G.load(ROOT / "genomes/exchange.yaml")
    sk = SK.Skill.model_validate(g.skills["match_orders"])
    R.append(("property teeth: a lazy oracle fails the fuzz",
              SK.gate_teeth(sk) == []))

    provider = RB.Provider(ROOT / ".onto/config.toml")
    usage = ROOT / ".onto/usage.jsonl"
    usage.unlink(missing_ok=True)
    provider.usage_path = usage
    cache = ROOT / "cache_skills"

    tele = RB.synthesize("match_orders", sk, provider, cache)
    print(json.dumps(tele, ensure_ascii=False, indent=1))
    R.append(("phase A (naive): the SLM wrote the oracle, properties green",
              tele["phases"].get("naive", {}).get("model") is not None))
    b = tele.get("bench", {})
    R.append(("phase B (fast): equivalent to naive; complexity budget "
              f"t(4n)/t(n)={b.get('ratio', 0):.1f} <= {b.get('max_ratio', 0):g}",
              not tele["island"]))

    calls = [json.loads(l) for l in usage.read_text().splitlines()]
    toks = sum((c["tokens_in"] or 0) + (c["tokens_out"] or 0) for c in calls)
    print(f"usage: {len(calls)} calls, {toks} tokens total")
    R.append(("telemetry: usage.jsonl is non-empty (model/tokens/ms per call)",
              len(calls) >= 2 and all("model" in c and "ms" in c for c in calls)))

    # repeat: semantic cache -> zero network calls
    n_before = len(calls)
    tele2 = RB.synthesize("match_orders", sk, provider, cache)
    calls2 = [json.loads(l) for l in usage.read_text().splitlines()]
    R.append(("repeat: cache hits on both phases, zero new network calls",
              bool(tele2["phases"].get("naive", {}).get("cache")) and
              bool(tele2["phases"].get("fast", {}).get("cache")) and len(calls2) == n_before))

    print(f"\n=== EXAM: SLM ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
