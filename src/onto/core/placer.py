# -*- coding: utf-8 -*-
"""Placer — the metabolism control loop (SPEC §10.3, F5).

F5 granularity is DEPLOYABLE (splitting off a hot gene as a separate organism);
per-rule in-process hot-swap awaits an embeddable interpreter (D28).

Input: measured heat (events/s per entity), measured tier prices
(t_cold/t_warm from benchmarks), declared demand. Output: a PLAN with the
decisions of the theory/ formulas (each one a row of the METRICS table
"formula -> decision"), molt proposals as ledger events, refusals with the
arithmetic. Rights (the ladder): the Placer PROPOSES; the operator/warden
executes, within the granted rights."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

from onto.core.genome import GenomeError
from onto.theory import formulas as F
from onto.theory.provenance import V, declared, default


@dataclass
class Plan:
    warm: list[str] = field(default_factory=list)       # entities to warm up
    evict: list[str] = field(default_factory=list)      # to evict
    refusals: list[str] = field(default_factory=list)   # demand unreachable
    proposals: list[dict] = field(default_factory=list) # molt events (ledger)
    metrics: list[str] = field(default_factory=list)    # "formula -> decision"


def tick(rates: dict[str, V], *, t_cold_ns: V, t_warm_ns: V,
         demand: dict[str, V] | None = None,
         floor_warm_ms: V | None = None,
         warm_set: set[str] = frozenset(),
         horizon_s: V | None = None,
         build_cost_s: V | None = None,
         evict_below_per_s: V | None = None,
         window_s: V | None = None) -> Plan:
    """One tick of the loop. rates: entity -> V(events/s, measured)."""
    horizon_s = horizon_s or declared(3600.0, "operator: 1h horizon")
    build_cost_s = build_cost_s or declared(5.0, "operator: materialize ~5s")
    evict_below_per_s = evict_below_per_s or default(1.0)
    window_s = window_s or default(10.0)
    plan = Plan()

    for en, rate in sorted(rates.items()):
        if en in warm_set:
            d = F.evict_idle(rate, evict_below_per_s, window_s)
            plan.metrics.append(f"[{en}] " + d.row())
            if d.verdict.startswith("EVICT"):
                plan.evict.append(en)
                plan.proposals.append({
                    "kind": "evict_proposal", "entity": en,
                    "why": d.row(), "rights": "proposal-only"})
        else:
            d = F.warm_gain(rate, t_cold_ns, t_warm_ns, horizon_s, build_cost_s)
            plan.metrics.append(f"[{en}] " + d.row())
            if d.verdict.startswith("WARM"):
                plan.warm.append(en)
                plan.proposals.append({
                    "kind": "molt_proposal", "entity": en,
                    "why": d.row(), "gain": d.value.show(),
                    "rights": "proposal-only"})

    for target, t_max in sorted((demand or {}).items()):
        if floor_warm_ms is None:
            plan.refusals.append(f"'{target}': cannot judge demand — floor "
                                 f"not measured yet")
            continue
        d = F.latency_floor(t_max, floor_warm_ms)
        plan.metrics.append(f"[{target}] " + d.row())
        if d.verdict.startswith("REFUSE"):
            plan.refusals.append(f"'{target}': {d.verdict}")
    return plan


# ------------------------------------------------- molt: split the root by gene

def split_hot_root(root_path: str | pathlib.Path, hot_entities: list[str],
                   out_path: str | pathlib.Path) -> pathlib.Path:
    """Split off the hot entities: a new ROOT from the same genes (closure over
    requires). Bodies are not rewritten — the same gene => byte-for-byte
    emission (proven by the F4 exam). Cross-module invariants of the original
    root that reference entities not taken along are honestly NOT carried over
    (this is noted)."""
    from onto.core import ir, modules as M
    root_path = pathlib.Path(root_path)
    raw = ir.load(root_path)
    root = M.Root.model_validate(raw)
    loaded = []
    for rel in root.imports:
        mp = (root_path.parent / rel).resolve()
        loaded.append((rel, mp, M.load_module(mp)))

    keep: list[tuple[str, pathlib.Path, M.Module]] = [
        (rel, mp, m) for rel, mp, m in loaded
        if set(m.entities) & set(hot_entities)]
    if not keep:
        raise GenomeError([f"no imported module owns entities {hot_entities}"])
    # closure: pull in the exporters of the required events
    changed = True
    while changed:
        changed = False
        need = {evn for _, _, m in keep for evn in m.requires.events}
        have = {evn for _, _, m in keep for evn in m.events}
        for rel, mp, m in loaded:
            if (rel, mp, m) not in keep and set(m.events) & (need - have):
                keep.append((rel, mp, m))
                changed = True

    kept_entities = {en for _, _, m in keep for en in m.entities}
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    new_root = {
        "onto": raw["onto"],
        "name": f"{root.name}_{'_'.join(sorted(hot_entities))}_svc",
        "imports": [str(pathlib.Path(mp).resolve().relative_to(
            out_path.parent.resolve())) if _is_rel(mp, out_path.parent)
            else str(mp) for _, mp, _ in keep],
        "retry_window": root.retry_window,
        "bind": {en: {"instances": (root.bind[en].instances
                                     if isinstance(root.bind[en].instances, str)
                                     else list(root.bind[en].instances))}
                 for en in sorted(kept_entities) if en in root.bind},
    }
    out_path.write_text(yaml.safe_dump(new_root, allow_unicode=True,
                                       sort_keys=False), encoding="utf-8")
    return out_path


def _is_rel(p: pathlib.Path, base: pathlib.Path) -> bool:
    try:
        pathlib.Path(p).resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False
