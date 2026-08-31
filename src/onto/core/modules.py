# -*- coding: utf-8 -*-
"""Genome composition (F4, SPEC §2.1): a module = a gene, the root = linking.

Doctrine (D2): composition through interfaces, not inheritance — the root
STRUCTURALLY cannot override a foreign rule (the root has no entities);
extending a provider = a new version of it with a functor (F6).

Module (*.yaml): onto + module(name) + events(exports) + entities (without
instances — a deploy detail) + requires.events (STRUCTURAL subtyping: the
module is typechecked against ITS OWN interface — the subset of fields it
actually reads; the real event may carry more).

Root: onto + name + imports[paths] + bind{entity: instances} + retry_window +
cross-module invariants/queries. Linking -> a flat hub-Genome: the
organism/court/dialects know nothing about modules at all.
"""
from __future__ import annotations

import pathlib
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from onto.core import ir
from onto.core.genome import Entity, Genome, GenomeError


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Requires(_Strict):
    events: dict[str, dict[str, str]] = Field(default_factory=dict)


class Module(_Strict):
    onto: int
    module: str
    events: dict[str, dict[str, str]] = Field(default_factory=dict)   # exports
    entities: dict[str, Entity] = Field(default_factory=dict)
    requires: Requires = Field(default_factory=Requires)
    invariants: dict[str, str] = Field(default_factory=dict)
    queries: dict[str, str] = Field(default_factory=dict)


class Bind(_Strict):
    instances: list[str] | str          # a list or "dynamic" (D51)


class Root(_Strict):
    onto: int
    name: str
    imports: list[str]
    bind: dict[str, Bind] = Field(default_factory=dict)
    retry_window: int = 1024
    invariants: dict[str, str] = Field(default_factory=dict)
    queries: dict[str, str] = Field(default_factory=dict)
    # F6: the migration functor for breaking schema changes (migrate.Migrations);
    # lives in the NEW version of the root, covers every breaking change or refuses
    migrations: dict = Field(default_factory=dict)
    # fabric wave: the operator's ack for an INTENTIONAL change of a rule's behavior
    # (mutgate's semantic diff; format: ["entity.rule", ...])
    ack_behavior_change: list[str] = Field(default_factory=list)
    # MEGA-DIRT: integrations and skills — a deploy concern of the ROOT (which
    # foreign organisms and algorithmic cores this deployment needs)
    externals: dict = Field(default_factory=dict)
    skills: dict = Field(default_factory=dict)
    timers: dict = Field(default_factory=dict)     # U2: schedules (D59)
    webhooks: dict[str, str] = Field(default_factory=dict)   # U6 (D62)


def load_module(path: str | pathlib.Path) -> Module:
    raw = ir.load(path)
    try:
        return Module.model_validate(raw)
    except Exception as e:
        raise GenomeError([f"module {path}: schema: {e}"])


def link(root_path: str | pathlib.Path) -> Genome:
    """Root + modules -> a flat Genome. Errors as a list (D24, English)."""
    root_path = pathlib.Path(root_path)
    raw = ir.load(root_path)
    try:
        root = Root.model_validate(raw)
    except Exception as e:
        raise GenomeError([f"root {root_path}: schema: {e}"])

    errs: list[str] = []
    modules: list[tuple[pathlib.Path, Module]] = []
    for rel in root.imports:
        mp = (root_path.parent / rel).resolve()
        if not mp.exists():
            errs.append(f"import not found: {rel}")
            continue
        modules.append((mp, load_module(mp)))
    if errs:
        raise GenomeError(errs)

    # exports: events; a duplicate name = a conflict (not a silent merge)
    events: dict[str, dict[str, str]] = {}
    exporter: dict[str, str] = {}
    for mp, m in modules:
        for evn, fields in m.events.items():
            if evn in events:
                errs.append(f"event '{evn}' exported by both "
                            f"'{exporter[evn]}' and '{m.module}'")
                continue
            events[evn] = dict(fields)
            exporter[evn] = m.module

    # requires: structural subtyping (needed fields ⊆ exported ones)
    for mp, m in modules:
        for evn, need in m.requires.events.items():
            if evn not in events:
                errs.append(
                    f"module '{m.module}' requires event '{evn}' which no "
                    f"imported module exports (exported: {sorted(events)})")
                continue
            have = events[evn]
            for f, t in need.items():
                if f not in have:
                    errs.append(f"module '{m.module}' requires {evn}.{f}, "
                                f"but exporter '{exporter[evn]}' provides "
                                f"fields {sorted(have)}")
                elif have[f] != t:
                    errs.append(f"module '{m.module}' requires {evn}.{f}: {t}, "
                                f"exporter provides {have[f]}")

    # entities: merge without collisions; instances — from the root's bind
    entities: dict[str, Entity] = {}
    owner: dict[str, str] = {}
    for mp, m in modules:
        for en, ent in m.entities.items():
            if en in entities:
                errs.append(f"entity '{en}' defined by both "
                            f"'{owner[en]}' and '{m.module}'")
                continue
            ent2 = ent.model_copy(deep=True)
            if en in root.bind:
                if ent2.instances:
                    errs.append(f"entity '{en}': module fixes instances AND "
                                f"root binds them — pick one")
                b = root.bind[en].instances
                ent2.instances = b if isinstance(b, str) else list(b)
            if not ent2.instances:
                errs.append(f"entity '{en}': no instances (add root "
                            f"bind.{en}.instances)")
            entities[en] = ent2
            owner[en] = m.module
    for en in root.bind:
        if en not in entities:
            errs.append(f"root binds unknown entity '{en}' "
                        f"(known: {sorted(entities)})")
    if errs:
        raise GenomeError(errs)

    # invariants/queries: module-level + root-level (cross-module)
    invariants: dict[str, str] = {}
    queries: dict[str, str] = {}
    for _, m in modules:
        for n, src in m.invariants.items():
            invariants[f"{m.module}_{n}"] = src
        for n, src in m.queries.items():
            queries.setdefault(n, src)
    invariants.update(root.invariants)
    queries.update(root.queries)

    g = Genome(onto=ir.HUB_VERSION, name=root.name, events=events,
               entities=entities, invariants=invariants, queries=queries,
               retry_window=root.retry_window,
               externals=dict(root.externals), skills=dict(root.skills),
               timers=dict(root.timers), webhooks=dict(root.webhooks))
    from onto.core.genome import fill_defaults, normalize_types2, validate
    normalize_types2(g)
    fill_defaults(g)
    verrs = validate(g)
    if verrs:
        raise GenomeError([f"(linked) {e}" for e in verrs])
    return g


def is_root(raw: dict) -> bool:
    return "imports" in raw


def is_module(raw: dict) -> bool:
    return "module" in raw


# --------------------------------------------------------------- explain

def explain(root_path: str | pathlib.Path, target: str) -> str:
    """An O(k) slice for a feature around the entity/module `target`: WHAT to
    read to add a rule/event — instead of reading the whole genome (S5)."""
    root_path = pathlib.Path(root_path)
    raw = ir.load(root_path)
    root = Root.model_validate(raw)
    lines: list[str] = []
    total_tokens = _tok(root_path.read_text(encoding="utf-8"))
    slice_tokens = 0
    found = None
    for rel in root.imports:
        mp = (root_path.parent / rel).resolve()
        m = load_module(mp)
        total_tokens += _tok(mp.read_text(encoding="utf-8"))
        if target == m.module or target in m.entities:
            found = (mp, m)
    if found is None:
        names = [load_module((root_path.parent / r).resolve()).module
                 for r in root.imports]
        return f"explain: '{target}' not found (modules: {names})"
    mp, m = found
    src = mp.read_text(encoding="utf-8")
    slice_tokens += _tok(src)
    lines.append(f"# SLICE for '{target}' — read THIS, not the whole genome")
    lines.append(f"## module '{m.module}' ({mp.name}):\n{src}")
    binds = {en: root.bind[en].instances for en in m.entities if en in root.bind}
    bind_txt = f"bind: {binds}  retry_window: {root.retry_window}"
    slice_tokens += _tok(bind_txt)
    lines.append(f"## root binding ({root_path.name}):\n{bind_txt}")
    iface = {evn: f for evn, f in m.requires.events.items()}
    if iface:
        lines.append(f"## requires (satisfied by imports): {iface}")
    lines.append(f"\n# slice: ~{slice_tokens} tokens vs whole genome "
                 f"~{total_tokens} tokens ({100 * slice_tokens // max(total_tokens, 1)}%)")
    return "\n".join(lines)


def _tok(text: str) -> int:
    return len(text) // 4
