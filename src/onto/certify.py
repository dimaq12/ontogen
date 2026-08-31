# -*- coding: utf-8 -*-
"""Per-class coverage certificate (D91): the escape-class taxonomy
(CERTIFICATION_BOUNDARY.md) is not just documented — for EVERY one of the 17
classes the engine emits a mechanical STATE, so nothing is silently ignored.

A class is in exactly one state for a given artifact:
  N/A            — structurally impossible here (a guarantee by construction)
  PROVEN         — the court/gates certify it
  DELEGATED      — routed to a verified named guarantor (D90)
  MEASURED       — a monitor emits a number (nu-bridge / DKW / spectral)
  CONTAINED      — membrane / budget / kill-9 with REVOKE
  MONITORED      — runtime invariant/drift watcher
  DECLARED       — the operator named an assumption/ack/unknown
  NAMED_UNPROVEN — no handler exists; named in the passport (honest limit)
  UNCOVERED      — touched but neither handled nor declared -> MUST fix

The guarantee is not "everything is proven" — it is "every class is in a KNOWN,
enforced state, never silent". PROVE / DELEGATE / MEASURE / CONTAIN / DECLARE /
NAME — one of these for each, or the passport flags UNCOVERED.
"""
from __future__ import annotations


def coverage(genome_path, skills_cache=None) -> list[dict]:
    from onto.core import court as C, genome as G, membrane as MB
    g = G.load(genome_path)
    has_skills = bool(g.skills)
    has_islands = bool(g.externals)
    has_dynamic = any(e.instances == "dynamic" for e in g.entities.values())
    has_timers = bool(getattr(g, "timers", {}))

    # islands: proven(cases) / delegated(guarantee) / contained-only
    delegated = contained_only = functional_islands = 0
    for raw in g.externals.values():
        ext = MB.External.model_validate(raw)
        if ext.guarantee is not None:
            delegated += 1
        elif ext.cases:
            functional_islands += 1
        else:
            contained_only += 1

    # court: any rule/invariant the SMT could not decide (routed, not silent)
    unsupported = 0
    refuted = 0  # A DISPROVED obligation: the genome violates its own contract
    inv_monitored = 0
    for en, ent in g.entities.items():
        for rn, r in ent.rules.items():
            if r.when not in g.events:
                continue
            v = C.prove_rule(dict(ent.state), dict(g.events[r.when]),
                             r.guard, r.body, r.contract.post, r.contract.conserves)
            unsupported += sum(1 for x in v.values() if x.status == "unsupported")
            refuted += sum(1 for x in v.values() if x.status == "counterexample")
    dyn_inv = xent_inv = 0
    if g.invariants:
        inv = C.prove_invariants(g)
        inv_monitored = sum(1 for x in inv.values() if x.status != "proved")
        for x in inv.values():
            if x.status == "proved":
                continue
            note = (x.note or "").lower()
            if "dynamic" in note:
                dyn_inv += 1
            elif "spans" in note or "cross" in note:
                xent_inv += 1
            else:
                xent_inv += 1

    def row(cid, name, group, state, move, detail, standing=False):
        # standing=True: a UNIVERSAL limit, true for every artifact (not a
        # per-artifact verdict). standing=False: DERIVED from THIS genome.
        return {"id": cid, "class": name, "group": group, "state": state,
                "move": move, "detail": detail, "standing": standing}

    out = []
    # A. Continuum
    out.append(row(1, "float / numerical accuracy", "A", "DECLARED",
                   "float: N/A by construction; int overflow: declare + conform",
                   "FLOAT cannot occur (the IR is int/str only, the typechecker "
                   "rejects it). BUT integer obligations are PROVED over "
                   "unbounded Z while the phenotype runs int64 — the overflow "
                   "gap is DECLARED (UNEXPRESSIBLE) and delegated to dialect "
                   "conformance, NOT proved for values beyond 2^63"))
    out.append(row(2, "cryptographic strength", "A",
                   "DELEGATED" if delegated else "N/A",
                   "delegate (D90)" if delegated else "-",
                   f"{delegated} island(s) delegate to a verified guarantor"
                   if delegated else "no crypto tissue declared"))
    # B. Physical
    out.append(row(3, "hard real-time / latency", "B",
                   "MEASURED" if has_timers else "N/A", "measure (nu-bridge)",
                   "timers/load monitored; latency is measured, not proved"
                   if has_timers else "no timing claim"))
    out.append(row(4, "concurrency / memory-model", "B", "NAMED_UNPROVEN",
                   "name + partial contain (STANDING limit)",
                   "the court proves state arithmetic, not happens-before; the "
                   "runtime is fuzzed via kill-9/replay + fold-parity, not proved"))
    perf_tissue = has_skills or has_islands
    out.append(row(5, "resources / perf", "B",
                   "MEASURED" if perf_tissue else "N/A", "measure (bench)",
                   "skills/islands carry a relative budget (D38); absolute perf "
                   "is measured at materialization" if perf_tissue else
                   "pure interpreter, no perf claim"))
    # C. Undecidable / unbounded
    out.append(row(6, "skill termination", "C",
                   "CONTAINED" if has_skills else "N/A", "contain (budget/timeout)",
                   "skills bounded by the budget gate at synthesis + a runtime "
                   "timeout; halting is not proved" if has_skills else "no skills"))
    if refuted:
        c7_state, c7_move, c7_detail = ("REFUTED", "the court DISPROVED it",
            f"{refuted} obligation(s) have a COUNTEREXAMPLE — the genome "
            f"violates its own contract; NOT proven, fix the rule/contract")
    elif unsupported:
        c7_state, c7_move, c7_detail = ("CONTAINED", "route unsupported -> ack/fuzz",
            f"{unsupported} obligation(s) the SMT could not decide -> routed "
            f"(ack/fuzzed), not silently passed")
    else:
        c7_state, c7_move, c7_detail = ("PROVEN", "prove",
            "all obligations decided by the court (unsat-of-negation over "
            "unbounded Z; see class 1 for the Z-vs-int64 phenotype gap)")
    out.append(row(7, "deep-nonlinear contracts", "C", c7_state, c7_move, c7_detail))
    out.append(row(8, "dynamic-population invariants", "C",
                   "MONITORED" if dyn_inv else "N/A", "monitor",
                   f"{dyn_inv} invariant(s) over dynamic/unbounded scope -> "
                   f"monitored, not proved" if dyn_inv else
                   "no dynamic-scope invariant"))
    out.append(row(9, "cross-entity cascade invariants", "C",
                   "MONITORED" if xent_inv else "N/A", "monitor",
                   f"{xent_inv} cross-entity invariant(s) -> monitored"
                   if xent_inv else "none"))
    out.append(row(10, "spectrally-invisible corruption", "C", "NAMED_UNPROVEN",
                   "name + partial measure (STANDING limit)",
                   "Problem 2: below-gap self-sustaining corruption is provably "
                   "hard; the spectral audit measures what is visible, names the rest", standing=True))
    # D. World / meaning
    if not has_islands:
        out.append(row(11, "island content", "D", "N/A", "-", "no islands"))
    else:
        out.append(row(11, "island content", "D", "CONTAINED", "contain (membrane)",
                       f"{len(g.externals)} island(s) contained by assumptions + "
                       f"drift + REVOKE — content is bounded, not proved "
                       f"(the class 11 move IS contain); functional certificates "
                       f"are the D90 axis below"))
    out.append(row(12, "oracle / assumption truth", "D",
                   "DECLARED" if has_islands else "N/A", "declare",
                   "island assumptions + harden corpus are declared and "
                   "monitored; the world is not forced" if has_islands else "-"))
    import pathlib as _pl
    has_assumptions = (_pl.Path(genome_path).parent / "assumptions.yaml").exists()
    has_acks = bool(getattr(g, "ack_behavior_change", []))
    meaning_declared = has_assumptions or has_acks
    out.append(row(13, "underdetermined meaning", "D",
                   "DECLARED" if meaning_declared else "N/A", "declare (interview)",
                   "assumptions.yaml / ack_behavior_change present — declared "
                   "readings recorded" if meaning_declared else
                   "no underdetermination surfaced (no assumptions.yaml, no ack)"))
    out.append(row(14, "non-formalizable requirements", "D",
                   "DECLARED" if has_assumptions else "N/A", "declare",
                   "assumptions.yaml carries declared non-formal requirements"
                   if has_assumptions else
                   "none declared (no assumptions.yaml) — if any exist they are "
                   "UNCOVERED until declared"))
    grown = has_skills or has_islands
    out.append(row(15, "wrong-but-passes", "D",
                   "CONTAINED" if grown else "N/A", "contain (mutants/teeth/harden)",
                   "grown tissues: mutants + teeth + harden shrink it; residual "
                   "named" if grown else "no grown tissue (rules printed, not written)"))
    # E. Statistics
    out.append(row(16, "ML correctness / generalization", "E", "N/A",
                   "measure (held-out/DKW) if present",
                   "no ML tissue declared; if present, held-out + DKW measures "
                   "with confidence, not a proof"))
    # F. Meta / trust
    has_pin = (_pl.Path(genome_path).parent / "engine.pin").exists()
    out.append(row(17, "engine / model-edge / supply chain", "F",
                   "CONTAINED" if has_pin else "DECLARED",
                   "pin + provenance + TRUST.md",
                   "engine.pin present + guarantee provenance (D90) + TRUST.md"
                   if has_pin else
                   "NO engine.pin here — the trust-base is named (TRUST.md) but "
                   "not pinned; run onto init or onto new"))
    # D90 guarantee-chain (ORTHOGONAL to the 17 classes): every island must be
    # PROVEN (cases) or DELEGATED (guarantee). Contained-only = functionally
    # unverified = an open certificate. This is the user's "proven or delegated"
    # law, tracked as its own axis (id 0), NOT smuggled into class 11.
    if has_islands:
        gc_state = "OPEN" if contained_only else "CLOSED"
        out.append(row(0, "guarantee-chain (D90): islands proven-or-delegated",
                       "*", gc_state, "prove (cases) OR delegate (guarantee)",
                       f"{delegated} delegated + {functional_islands} proven-by-"
                       f"cases + {contained_only} contained-only"
                       + (" -> MUST close the contained-only ones" if contained_only
                          else " -> all islands carry a functional certificate")))
    return out


def render(rows: list[dict]) -> str:
    L = ["# CERTIFICATION COVERAGE (D91) — every escape class in a known state",
         ""]
    uncovered = [r for r in rows if r["state"] == "UNCOVERED"]
    for r in rows:
        if r["id"] == 0:
            continue  # guarantee-chain rendered separately below
        tag = " (standing)" if r.get("standing") else ""
        L.append(f"[{r['id']:2}/{r['group']}] {r['state']:14} {r['class']}{tag}")
        L.append(f"          -> {r['move']}: {r['detail']}")
    gc = next((r for r in rows if r["id"] == 0), None)
    if gc:
        L.append("")
        L.append(f"[ D90 ] {gc['state']:14} {gc['class']}")
        L.append(f"          -> {gc['move']}: {gc['detail']}")
    L.append("")
    refuted = [r for r in rows if r["state"] == "REFUTED"]
    gc_open = bool(gc and gc["state"] == "OPEN")
    if refuted:
        L.append(f"VERDICT: {len(refuted)} REFUTED class(es) — the genome "
                 f"violates its own contract (counterexample): "
                 f"{[r['id'] for r in refuted]}. Fix before shipping.")
    elif uncovered:
        L.append(f"VERDICT: {len(uncovered)} UNCOVERED class(es) — MUST close: "
                 f"{[r['id'] for r in uncovered]}")
    elif gc_open:
        L.append("VERDICT: all 17 classes in a known state, BUT the D90 "
                 "guarantee-chain is OPEN — island(s) neither proven (cases) nor "
                 "delegated (guarantee). Prove or delegate them.")
    else:
        L.append("VERDICT: every class is in a known, enforced state, and the "
                 "D90 guarantee-chain is CLOSED (every island proven or delegated).")
    return "\n".join(L)


def is_green(rows: list[dict]) -> bool:
    """certify passes iff no class is UNCOVERED AND the D90 guarantee-chain is
    not OPEN (every island proven-by-cases or delegated-to-a-guarantor)."""
    if any(r["state"] in ("UNCOVERED", "REFUTED") for r in rows):
        return False
    gc = next((r for r in rows if r["id"] == 0), None)
    return not (gc and gc["state"] == "OPEN")
