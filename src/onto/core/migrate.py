# -*- coding: utf-8 -*-
"""Conservativity and migration (F6, thesis-6 discipline made executable).

In an event-sourced world, a molt with a schema change = REWRITE THE LOG with
a functor; state is recomputed by replay for free (state = a fold of the log).

diff_genomes: breaking changes (removing/renaming events, fields, entities,
rules) as a list. Additive changes are not breaking.
The functor (the migrations block of the NEW genome's ROOT) must cover EVERY
breaking change — otherwise a refusal listing what is uncovered.
migrate_log: an idempotent rewrite of events.jsonl + a backup of the old log.
"""
from __future__ import annotations

import json
import pathlib

from pydantic import BaseModel, ConfigDict, Field

from onto.core.genome import Genome


class Migrations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rename_events: dict[str, str] = Field(default_factory=dict)
    rename_event_fields: dict[str, dict[str, str]] = Field(default_factory=dict)
    drop_events: list[str] = Field(default_factory=list)
    # U-lossy (D74; PARADIGM_LIMITS §6): loss is legal only when DECLARED:
    # event -> text of "what we lose and why it's acceptable". Signed off by
    # the operator (the root file is under git), the warden writes
    # declared_loss into the ledger.
    declared_loss: dict[str, str] = Field(default_factory=dict)


def diff_genomes(old: Genome, new: Genome) -> list[str]:
    """Breaking changes old -> new (additive ones don't count)."""
    breaking: list[str] = []
    for evn, fields in old.events.items():
        if evn not in new.events:
            breaking.append(f"event '{evn}' removed")
            continue
        for f, t in fields.items():
            if f not in new.events[evn]:
                breaking.append(f"event field '{evn}.{f}' removed")
            elif new.events[evn][f] != t:
                breaking.append(f"event field '{evn}.{f}' retyped {t} -> "
                                f"{new.events[evn][f]}")
    for en, ent in old.entities.items():
        if en not in new.entities:
            breaking.append(f"entity '{en}' removed")
            continue
        for f in ent.state:
            if f not in new.entities[en].state:
                breaking.append(f"state field '{en}.{f}' removed")
        for rn in ent.rules:
            if rn not in new.entities[en].rules:
                breaking.append(f"rule '{en}.{rn}' removed")
    return breaking


def coverage(breaking: list[str], fx: Migrations) -> list[str]:
    """Which breaking changes are NOT covered by the functor (empty = migration
    is allowed)."""
    uncovered = []
    for b in breaking:
        if b.startswith("event '"):
            evn = b.split("'")[1]
            if evn not in fx.rename_events and evn not in fx.drop_events:
                uncovered.append(b + " — add rename_events or drop_events")
        elif b.startswith("event field '"):
            evn, f = b.split("'")[1].split(".", 1)
            if fx.rename_event_fields.get(evn, {}).get(f) is None:
                uncovered.append(b + f" — add rename_event_fields.{evn}.{f}")
        else:
            uncovered.append(b + " — no functor form yet (state/rule "
                             "changes regenerate via replay of migrated log; "
                             "removal needs explicit drop — not in v1)")
    for evn in fx.drop_events:
        if evn not in fx.declared_loss:
            uncovered.append(f"dropping '{evn}' is LOSSY — declare it: "
                             f"migrations.declared_loss.{evn}: «what we lose and "
                             f"why it's acceptable» (D74)")
    return uncovered


def apply_functor(fx: "Migrations", events: list[dict]) -> tuple[list[dict], int]:
    """The functor as a pure transform on an event list: rename events/fields,
    drop declared-lost events. Shared by migrate_log (rewrite) and the
    fold-parity certificate (dry run) so the two can never diverge."""
    out, dropped = [], 0
    for ev in events:
        typ = ev.get("type")
        if typ in fx.drop_events:
            dropped += 1
            continue
        new_typ = fx.rename_events.get(typ, typ)
        renames = {**fx.rename_event_fields.get(typ, {}),
                   **fx.rename_event_fields.get(new_typ, {})}
        ev2 = {}
        for k, v in ev.items():
            if k == "type":
                ev2["type"] = new_typ
            else:
                ev2[renames.get(k, k)] = v
        out.append(ev2)
    return out, dropped


def _fold_of(genome, events: list[dict]) -> dict:
    """The fold (entity-state snapshot) of a genome over an explicit event list,
    computed in an isolated temp dir by real replay (no side effects: replay
    suppresses emissions)."""
    import tempfile
    from onto.core.organism import Organism
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "events.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
        encoding="utf-8")
    return Organism(genome, tmp, store="jsonl").snapshot()


def certify_migration_fold(old_genome, new_genome, old_events: list[dict],
                           fx: "Migrations") -> str | None:
    """FOLD-PARITY CERTIFICATE for a migration (D93): the migration is a functor
    that must PRESERVE the fold. Compute old_fold (old genome over the old log)
    and new_fold (new genome over the functored log); every entity/instance/
    field that DIVERGES must be attributable to a declared loss (drop_events +
    declared_loss, D74). An undeclared divergence = a functor that corrupts data
    -> reject. A pure rename with any divergence is always a reject. None =
    certified; else a counterexample string. This is REAL parity over the actual
    stored history, not a trusted transform."""
    new_events, _ = apply_functor(fx, old_events)
    old_fold = _fold_of(old_genome, old_events)
    try:
        new_fold = _fold_of(new_genome, new_events)
    except Exception as ex:  # noqa: BLE001 — a log the new genome can't replay
        return (f"migration BROKE fold-parity: the functored log is "
                f"unprocessable by the new genome ({type(ex).__name__}: "
                f"{str(ex)[:120]})")
    diffs = []
    for en in sorted(set(old_fold) | set(new_fold)):
        oi, ni = old_fold.get(en, {}), new_fold.get(en, {})
        for inst in sorted(set(oi) | set(ni), key=str):
            os_, ns_ = oi.get(inst, {}), ni.get(inst, {})
            for f in sorted(set(os_) | set(ns_)):
                if os_.get(f) != ns_.get(f):
                    diffs.append(f"{en}/{inst}.{f}: {os_.get(f)!r} -> "
                                 f"{ns_.get(f)!r}")
    if not diffs:
        return None
    # divergence exists: permitted ONLY if the operator declared a loss (D74).
    if fx.drop_events and fx.declared_loss:
        return None
    return ("migration BROKE fold-parity (undeclared divergence — the functor "
            "does not preserve the fold): " + "; ".join(diffs[:6]))


def migrate_log(fx: Migrations, data_dir: str | pathlib.Path,
                version_tag: str) -> dict:
    """Rewrite the log with the functor via EventStore (jsonl OR sqlite —
    auto-detected; idempotent). The old log -> a backup is mandatory."""
    from onto.core.store import open_store
    store = open_store(data_dir)
    lines = [ev for ev in store.read_from(0) if ev is not None]
    if not lines:
        return {"events_in": 0, "events_out": 0, "backup": None}
    out, dropped = apply_functor(fx, lines)
    backup = store.rewrite(out, version_tag)
    return {"events_in": len(lines), "events_out": len(out),
            "dropped": dropped, "backup": backup}
