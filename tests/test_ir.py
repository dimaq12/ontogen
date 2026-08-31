# -*- coding: utf-8 -*-
"""hub versions: a v0 file (without onto) is converted; newer than the engine — refused;
onto fix canonicalizes. Mechanism before need (F0)."""
import pytest

from onto.core import ir


def test_v0_migrates_to_hub():
    hub = ir.to_hub({"name": "shop"})
    assert hub["onto"] == ir.HUB_VERSION and hub["name"] == "shop"


def test_current_version_passthrough():
    raw = {"onto": 1, "name": "shop"}
    assert ir.to_hub(raw) == raw


def test_future_version_refused():
    with pytest.raises(ValueError, match="newer than this engine"):
        ir.to_hub({"onto": 99})


def test_fix_puts_onto_first():
    text = ir.fix_text({"name": "shop"})
    assert text.splitlines()[0] == f"onto: {ir.HUB_VERSION}"
