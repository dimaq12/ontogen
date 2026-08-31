# -*- coding: utf-8 -*-
"""hub-IR: genome versions and converters (SPEC §8.3, D5).

Mechanism before need (PLAN F0): a file version `onto: N` + a chain of vN→hub
converters. For now hub = version 1, the only converter is the trivial v0→v1
(a file without an `onto` field is treated as v0). The hub-IR models themselves
are F1.
"""
from __future__ import annotations

import pathlib
from typing import Any, Callable

HUB_VERSION = 1

# ---------------------------------------------------------------- FREEZE
# D72: IR v1.0 is FROZEN (release 1.0.0). The fingerprint = sha256 of the
# canonical json schema of the genome models. The test tests/test_freeze.py fails
# on ANY change to the format; the legal path for a change: bump HUB_VERSION +
# a vN->vN+1 converter + rewriting the fingerprint IN A SINGLE COMMIT. Silent
# evolution of the format no longer exists.
FROZEN_V1_FINGERPRINT = "e831b15e14ad6e828aa6d56c6898c59bf76403797c696f2a3405a3b409dff98b"


def _strip_prose(node):
    """Recursively drop 'description'/'title' so the freeze guards STRUCTURE,
    not prose (D81). Editing or translating a docstring must NOT trip the freeze."""
    if isinstance(node, dict):
        return {k: _strip_prose(v) for k, v in node.items()
                if k not in ("description", "title")}
    if isinstance(node, list):
        return [_strip_prose(v) for v in node]
    return node


def schema_fingerprint() -> str:
    """Canonical fingerprint of the genome format (pydantic models -> json schema),
    STRUCTURE ONLY — description/title are stripped (D81), so the freeze reacts to
    a real format change (a field, a type, a constraint), never to prose edits."""
    import hashlib
    import json as _json
    from onto.core.genome import Genome
    schema = _strip_prose(Genome.model_json_schema())
    return hashlib.sha256(
        _json.dumps(schema, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

# Converter: a version-N dict -> a version-N+1 dict. Index = source version.
_CONVERTERS: dict[int, Callable[[dict], dict]] = {}


def converter(from_version: int):
    def reg(fn):
        assert from_version not in _CONVERTERS, f"converter v{from_version} already registered"
        _CONVERTERS[from_version] = fn
        return fn
    return reg


@converter(0)
def _v0_to_v1(raw: dict) -> dict:
    """v0 (files without an onto field) -> v1: set the version. Trivial — but
    the mechanism (the chain + fix) must exist from F0, not appear once it
    starts to hurt (SCARS S6)."""
    out = dict(raw)
    out["onto"] = 1
    return out


def to_hub(raw: dict, *, source: str = "<memory>") -> dict:
    """Data of any supported version -> hub. Errors are in English
    (D24: machine surfaces are EN), citing the source."""
    if not isinstance(raw, dict):
        raise ValueError(f"{source}: genome must be a mapping, got {type(raw).__name__}")
    version = raw.get("onto", 0)
    if not isinstance(version, int) or version < 0:
        raise ValueError(f"{source}: field 'onto' must be an integer >= 0, got {version!r}")
    if version > HUB_VERSION:
        raise ValueError(
            f"{source}: onto: {version} is newer than this engine (hub v{HUB_VERSION}) — upgrade the engine")
    while version < HUB_VERSION:
        if version not in _CONVERTERS:
            raise ValueError(f"{source}: no converter v{version}->v{version + 1}")
        raw = _CONVERTERS[version](raw)
        got = raw.get("onto", version + 1)
        version = got if isinstance(got, int) else version + 1
    return raw


def load(path: str | pathlib.Path) -> dict:
    """A genome file -> hub dict (typing of the hub-IR is F1)."""
    import yaml
    p = pathlib.Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    return to_hub(raw, source=str(p))


def fix_text(raw: dict) -> str:
    """`onto fix`: canonical serialization of the file in the current version
    (v1: YAML with onto as the first key). A full fix that preserves comments —
    later; the mechanism and the place for it are here."""
    import yaml
    hub = to_hub(raw)
    ordered: dict[str, Any] = {"onto": hub["onto"]}
    for k, v in hub.items():
        if k != "onto":
            ordered[k] = v
    return yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False)
