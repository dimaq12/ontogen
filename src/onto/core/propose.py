# -*- coding: utf-8 -*-
"""propose — the ONLY programmatic path for writing the genome (the v0 central
dogma in the API, now in v1): file changes -> copy the tree -> load/validate
-> mutgate (conservativeness + COURT + semantic diff) -> green: write with .bak.

The same gates as warden.tick_watch (mutgate) — one judgment path."""
from __future__ import annotations

import pathlib
import shutil
import tempfile

from onto.core import genome as G, ir, mutgate


def propose(root_path: str | pathlib.Path, changes: dict[str, str]) -> dict:
    """changes: path RELATIVE to the root directory -> new file contents.
    Returns {"accepted": bool, "reasons": [...], "backups": [...]}"""
    root_path = pathlib.Path(root_path).resolve()
    base = root_path.parent
    for rel in changes:
        target = (base / rel).resolve()
        if not str(target).startswith(str(base)):
            return {"accepted": False,
                    "reasons": [f"path escapes genome dir: {rel}"]}

    old_g = G.load(root_path)
    raw_old_names = {root_path.name}

    # copy the tree -> apply the changes -> judge
    with tempfile.TemporaryDirectory(prefix="onto-propose-") as td:
        tmp = pathlib.Path(td)
        shutil.copytree(base, tmp / "tree")
        tree = tmp / "tree"
        for rel, content in changes.items():
            p = tree / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        try:
            new_g = G.load(tree / root_path.name)
            raw_root = ir.load(tree / root_path.name)
        except G.GenomeError as e:
            return {"accepted": False, "reasons": e.errors}
        except Exception as e:  # noqa: BLE001 — corrupt YAML, etc.
            return {"accepted": False,
                    "reasons": [f"{type(e).__name__}: {str(e)[:200]}"]}
        reasons = mutgate.judge_mutation(old_g, new_g, raw_root)
        if reasons:
            return {"accepted": False, "reasons": reasons}

    backups = []
    for rel, content in changes.items():
        p = base / rel
        if p.exists():
            bak = p.with_suffix(p.suffix + ".bak")
            bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            backups.append(str(bak))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return {"accepted": True, "reasons": [],
            "backups": backups, "genome": new_g.name}
