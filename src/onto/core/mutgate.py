# -*- coding: utf-8 -*-
"""Mutation gates — SHARED by warden (file watch) and propose (MCP/CLI):
one judgment path, two mouths (otherwise the gates drift apart — a v0 scar).

Order: conservativeness/functor (migrate) -> COURT (every contract of the new
genome is proven; a counterexample = rejection) -> SEMANTIC DIFF (a rule whose
behavior changed under the same contracts = an interview question §11: rejected
with an executable example until the operator confirms ack_behavior_change).
"""
from __future__ import annotations

from onto.core import court, expr as E, migrate
from onto.core.genome import Genome


def judge_mutation(old_g: Genome, new_g: Genome, raw_root: dict) -> list[str]:
    """Reasons for rejection (empty = the mutation is accepted)."""
    reasons: list[str] = []

    # 1) conservativeness: breaking changes are covered by a functor
    breaking = migrate.diff_genomes(old_g, new_g)
    if breaking:
        fx = migrate.Migrations.model_validate(raw_root.get("migrations", {}))
        reasons += migrate.coverage(breaking, fx)

    # 2) court: the contracts of the new genome are proven
    for en, ent in new_g.entities.items():
        for rn, r in ent.rules.items():
            vs = court.prove_rule(dict(ent.state), dict(new_g.events[r.when]),
                                  r.guard, r.body, r.contract.post,
                                  r.contract.conserves)
            for kind, v in vs.items():
                if v.status == "counterexample":
                    reasons.append(
                        f"court: {en}.{rn}.{kind} DISPROVED, counterexample "
                        f"{v.model} — fix the body or weaken the contract "
                        f"explicitly")

    # 3) semantic diff: behavior changed under the same contracts
    acks = set(raw_root.get("ack_behavior_change", []))
    for en, ent in new_g.entities.items():
        old_ent = old_g.entities.get(en)
        if old_ent is None:
            continue
        for rn, r in ent.rules.items():
            orr = old_ent.rules.get(rn)
            if orr is None or (orr.guard == r.guard and orr.body == r.body
                               and orr.emit == r.emit):
                continue
            if (orr.guard, orr.body) == (r.guard, r.body) and orr.emit != r.emit:
                if f"{en}.{rn}" not in acks:
                    reasons.append(
                        f"policy change in {en}.{rn}: emission differs and "
                        f"cascade equivalence is not provable yet — if "
                        f"intended, add ack_behavior_change: [\"{en}.{rn}\"]")
                continue
            if r.when not in old_g.events or r.when not in new_g.events:
                continue
            if f"{en}.{rn}" in acks:
                continue
            ev_t = dict(new_g.events[r.when])
            if dict(old_g.events[r.when]) != ev_t:
                continue        # the event schema changed — already covered by step 1
            eq = court.prove_equiv(dict(ent.state), ev_t,
                                   (orr.guard, orr.body), (r.guard, r.body))
            if eq.status == "proved":
                continue        # provably equivalent (a refactor) — ok
            if eq.status != "counterexample":
                # D80: solver unknown/unsupported — the court did NOT certify
                # equivalence; a silent pass = a violation of I7.
                reasons.append(
                    f"equivalence of {en}.{rn} NOT certified (solver: "
                    f"{eq.status}) — court cannot vouch for this change; "
                    f"if intended, add ack_behavior_change: [\"{en}.{rn}\"]")
                continue
            s_vals = {f: eq.model.get(f"s.{f}", 0) for f in ent.state}
            ev_vals = {f: eq.model.get(f"ev.{f}", 0 if t == "int" else "x")
                       for f, t in ev_t.items()}
            old_out = _run(orr.guard, orr.body, s_vals, ev_vals)
            new_out = _run(r.guard, r.body, s_vals, ev_vals)
            reasons.append(
                f"behavior change in {en}.{rn} (contracts do not distinguish "
                f"it): on input s={s_vals} ev={ev_vals} old yields {old_out}, "
                f"new yields {new_out}. If intended, add "
                f"ack_behavior_change: [\"{en}.{rn}\"] to the root genome")
    return reasons


def _run(guard: str | None, body: str, s: dict, ev: dict) -> dict:
    if guard and not E.eval_expr(E.parse_expr(guard), {"s": s, "ev": ev}):
        return dict(s)
    return E.exec_body(E.parse_body(body), s, ev)
