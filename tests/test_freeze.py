# -*- coding: utf-8 -*-
"""FREEZE GUARD for IR v1.0 (D72): the genome format changes only via
a HUB_VERSION bump + a converter + a new fingerprint — in a single commit."""
from onto.core import ir


def test_ir_v1_frozen():
    fp = ir.schema_fingerprint()
    assert fp == ir.FROZEN_V1_FINGERPRINT, (
        "genome format CHANGED after the v1.0 freeze!\n"
        f"  frozen:  {ir.FROZEN_V1_FINGERPRINT}\n"
        f"  current: {fp}\n"
        "Legal path: bump HUB_VERSION, add a converter vN->vN+1, and update "
        "FROZEN_V1_FINGERPRINT — in the SAME commit (D72). Silent format "
        "evolution is forbidden.")


def test_gallery_loads_under_freeze():
    """The entire gallery of genomes lives in the frozen format."""
    import pathlib
    from onto.core import genome as G
    root = pathlib.Path(__file__).resolve().parents[1]
    for gp in sorted((root / "genomes").glob("*.yaml")):
        if gp.name == "skill_smuggler.yaml":
            continue           # deliberately broken genome (smuggling exam)
        G.load(gp)   # must not raise
