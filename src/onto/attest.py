# -*- coding: utf-8 -*-
"""ATTESTATION OF GUARANTEES (U10, D74; PARADIGM_LIMITS §1+5+9).

A compiler that prints the phenotype but not an attestation of its guarantees
lies by omission. `onto attest` is a signable release artifact: WHAT is proved
(the court, rule by rule), WHAT is assumed (membranes, auth, ignorance), WHAT is
monitored, and WHERE THE WEAKEST SEAM lies (the system's guarantee = the min
across membranes — so let that min be visible and named). Plus provenance: the
genome hash, the engine version, and the fingerprint of the frozen IR."""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import random

from onto import __version__
from onto.core import court, genome as G, ir, membrane as MB


def build_attest(genome_path, skills_cache=None) -> dict:
    genome_path = pathlib.Path(genome_path)
    g = G.load(genome_path)
    raw = genome_path.read_bytes()

    # --- court: rule by rule + entity induction (D80)
    proofs, proved, failed = {}, 0, 0
    entity_induction = {}
    for en, ent in g.entities.items():
        rules_spec = [(rn, r.guard, r.body, r.contract.post,
                       dict(g.events[r.when]))
                      for rn, r in ent.rules.items() if r.when in g.events]
        ev_v = court.prove_entity(dict(ent.state), dict(ent.init),
                                  rules_spec, g.events)
        entity_induction[en] = (ev_v.status if ev_v.status != "proved"
                                else "entity-inductive")
        for rn, r in ent.rules.items():
            verdicts = court.prove_rule(dict(ent.state), dict(g.events[r.when]),
                                        r.guard, r.body, r.contract.post,
                                        r.contract.conserves)
            for kind, v in verdicts.items():
                proofs[f"{en}.{rn}.{kind}"] = v.status
                proved += v.status == "proved"
                failed += v.status == "counterexample"

    # --- seams: every membrane + the weakest one
    seams = {}
    for name, raw_ext in g.externals.items():
        ext = MB.External.model_validate(raw_ext)
        seams[name] = {"assumptions": len(ext.assumptions), "quota": ext.quota,
                       "growable": bool(ext.intent and ext.cases)}
    weakest = (min(seams, key=lambda n: (seams[n]["assumptions"],
                                         -seams[n]["quota"]))
               if seams else None)

    # --- skills: quantile DKW certificate (Part VII §3 / thm.8), not a checkbox
    skills = {}
    if g.skills:
        from onto.core import skills as SK
        cache = pathlib.Path(skills_cache) if skills_cache else None
        for name, raw_sk in g.skills.items():
            phase = next((ph for ph in ("fast", "naive") if cache
                          and (cache / f"{name}.{ph}.py").exists()), None)
            if not phase:
                skills[name] = {"phase": "NOT CERTIFIED"}
                continue
            sk = SK.Skill.model_validate(raw_sk)
            fn = SK.load_body((cache / f"{name}.{phase}.py").read_text(),
                              f"{phase}_{name}", sk.types)
            rnd, M, defects = random.Random(20260831), 200, 0
            for _ in range(M):
                case = SK.gen_case(sk, rnd)
                try:
                    defects += bool(SK.check_properties(
                        sk, case, SK.run_case(fn, sk, case)))
                except Exception:  # noqa: BLE001
                    defects += 1
            delta = 0.01
            q = max(0.0, round(1 - defects / M
                               - math.sqrt(math.log(2 / delta) / (2 * M)), 3))
            skills[name] = {"phase": phase, "quantile_cert":
                            {"eta": 0, "q": q, "delta": delta, "M": M}}

    inv_verdicts = court.prove_invariants(g)
    invariants = {n: ("proved" if v.status == "proved" else f"monitored:{v.note}")
                  for n, v in inv_verdicts.items()}
    n_rules = sum(len(e.rules) for e in g.entities.values())
    return {
        "genome": {"name": g.name, "sha256": hashlib.sha256(raw).hexdigest(),
                   "path": str(genome_path)},
        "engine": {"version": __version__, "hub": ir.HUB_VERSION,
                   "ir_fingerprint": ir.FROZEN_V1_FINGERPRINT},
        "proved": {"rules_total": n_rules, "obligations_proved": proved,
                   "obligations_failed": failed, "per_rule": proofs,
                   "entity_induction": entity_induction,
                   "NOTE": "per-rule proved = SELF-induction (post preserves "
                           "itself); the strong guarantee is entity_induction"},
        "assumed": {
            "seams": seams, "weakest_seam": weakest,
            "auth": ("deny-by-default" if g.auth else
                     "NONE — every event is open"),
            "skills": skills},
        "invariants": invariants,
        "monitored": {"drift_monitors": sum(s["assumptions"]
                                            for s in seams.values()),
                      "webhooks": len(g.webhooks), "timers": len(g.timers),
                      "invariants_monitored": sum(1 for v in invariants.values()
                                                  if v.startswith("monitored"))},
        "chains": _chains(g, proofs),
        "survival": _hazard_moves(g),
        "honest": {
            "island_content": "NOT PROVED — only contained "
                              "(assumptions+drift+revoke)",
            "coverage": f"{proved} proved obligations over {n_rules} rules; "
                        f"{len(seams)} islands OUTSIDE the court"},
    }


def _chains(g, proofs: dict) -> dict:
    """End-to-end paths (VII.1'/D79): event -> rules -> emissions (cascade,
    cap 8) -> webhook. A rule with a PROVED post = a deterministic step
    (q=1); a fully PROVED chain == the court proved every step. A webhook is
    fire-and-forget: delivery is NOT certified (stated honestly in the attestation)."""
    ev_rules = {}
    for en, ent in g.entities.items():
        for rn, r in ent.rules.items():
            ev_rules.setdefault(r.when, []).append((en, rn, r))
    out = {}
    for ev0 in g.events:
        steps, frontier, seen = [], [ev0], set()
        for _ in range(8):
            nxt = []
            for ev in frontier:
                for en, rn, r in ev_rules.get(ev, []):
                    if (en, rn) in seen:
                        continue
                    seen.add((en, rn))
                    proved = all(v == "proved" for k, v in proofs.items()
                                 if k.startswith(f"{en}.{rn}."))
                    has_obl = any(k.startswith(f"{en}.{rn}.")
                                  for k in proofs)
                    steps.append({"rule": f"{en}.{rn}",
                                  "proved": proved and has_obl})
                    nxt += [em.event for em in r.emit]
            if not nxt:
                break
            frontier = nxt
        if not steps:
            continue
        hooked = [e for e in ([ev0] + [em.event
                  for _, _, r in ev_rules.get(ev0, []) for em in r.emit])
                  if e in g.webhooks]
        out[ev0] = {"steps": steps,
                    "proved_end_to_end": all(st["proved"] for st in steps),
                    "webhook": ("fire-and-forget (delivery NOT certified)"
                                if hooked else None)}
    return out


def _hazard_moves(g) -> dict:
    """Part VI slide 6'.2: hazard moves — for each bad set S, a declared
    move with a lower bound h; worst-case recovery time 1/h.
    h=1 is a deterministic move; moves with h<1 require measurement (§2.2 VII)."""
    moves = {}
    if g.externals:
        moves["island_storm"] = {
            "move": "REVOKE trust (membrane quota)", "h": 1.0,
            "worst_recovery_steps": 1.0,
            "assumes": "drift monitors see the storm (declared assumptions)"}
    moves["bad_molt"] = {
        "move": "rollback from pre-molt backup (warden)", "h": 1.0,
        "worst_recovery_steps": 1.0, "assumes": "backup alive (membrane)"}
    moves["crash_loop"] = {
        "move": "warden restart + replay", "h": None,
        "worst_recovery_steps": None,
        "assumes": "MEASURE h per deployment (Part VII §2.2) — not claimed"}
    return moves


def render_md(a: dict) -> str:
    L = [f"# ATTESTATION OF GUARANTEES · {a['genome']['name']}",
         f"genome sha256:{a['genome']['sha256'][:16]}… · engine "
         f"{a['engine']['version']} · IR v{a['engine']['hub']} "
         f"(frozen {a['engine']['ir_fingerprint'][:12]}…)", "",
         "## PROVED (court, inductively)",
         f"- obligations: {a['proved']['obligations_proved']} PROVED, "
         f"{a['proved']['obligations_failed']} FAILED "
         f"(rules: {a['proved']['rules_total']}; per-rule = self-induction)"]
    L += [f"  - {k}: {v}" for k, v in a["proved"]["per_rule"].items()]
    L += [f"- induction of entity {en}: {v}"
          for en, v in a["proved"]["entity_induction"].items()]
    L += ["", "## ASSUMED (membranes and open surfaces)",
          f"- auth: {a['assumed']['auth']}"]
    for n, s in a["assumed"]["seams"].items():
        mark = "  ← WEAKEST SEAM" if n == a["assumed"]["weakest_seam"] else ""
        L.append(f"- island '{n}': {s['assumptions']} assumptions, "
                 f"quota {s['quota']}{mark}")
    for n, sc in a["assumed"]["skills"].items():
        if isinstance(sc, dict) and "quantile_cert" in sc:
            c = sc["quantile_cert"]
            L.append(f"- skill '{n}': {sc['phase']} · DKW (η={c['eta']}, "
                     f"q≥{c['q']}, δ={c['delta']}, M={c['M']})")
        else:
            L.append(f"- skill '{n}': {sc.get('phase', sc) if isinstance(sc, dict) else sc}")
    L += ["", "## MONITORED",
          f"- {a['monitored']['drift_monitors']} drift monitors, "
          f"{a['monitored']['timers']} timers, "
          f"{a['monitored']['webhooks']} webhooks", "",
          "", "## END-TO-END PATHS (VII.1': composition of steps)"]
    for ev, ch in a.get("chains", {}).items():
        mark = "PROVED end-to-end" if ch["proved_end_to_end"] else \
            "has UNproven steps"
        wh = f" · webhook: {ch['webhook']}" if ch["webhook"] else ""
        L.append(f"- {ev} -> {' -> '.join(st['rule'] for st in ch['steps'])}"
                 f" · {mark}{wh}")
    L += ["", "## SURVIVAL (hazard moves, Part VI slide 6'.2)"]
    for sname, m in a["survival"].items():
        hh = "h=1 (deterministic)" if m["h"] == 1.0 else "h NOT MEASURED"
        L.append(f"- {sname}: {m['move']} · {hh} · assumption: {m['assumes']}")
    L += ["",
          "## HONEST", f"- {a['honest']['island_content']}",
          f"- {a['honest']['coverage']}"]
    return "\n".join(L) + "\n"
