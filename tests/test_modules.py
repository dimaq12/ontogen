# -*- coding: utf-8 -*-
"""Composition F4: linking, interfaces, refusals, defaults, explain."""
import pathlib
import textwrap

import pytest

from onto.core import genome as G
from onto.core.genome import GenomeError

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_link_hotel_and_shop():
    hotel = G.load(ROOT / "genomes" / "hotel.yaml")
    shop = G.load(ROOT / "genomes" / "shop.yaml")
    assert set(hotel.entities) == {"room", "reservation", "wallet"}
    assert set(shop.entities) == {"sku", "wallet"}
    # init default F4: charges not set in the gene -> 0
    assert hotel.entities["wallet"].init == {"balance": 1000, "charges": 0, "frozen": 0}


def test_module_alone_not_runnable():
    with pytest.raises(GenomeError, match="not[ \\n]+runnable|not\\s+runnable"):
        G.load(ROOT / "modules" / "payments.yaml")


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_unmet_requires_is_refused(tmp_path):
    root = _write(tmp_path, "bad.yaml", f"""
        onto: 1
        name: bad
        imports: [{(ROOT / 'modules' / 'reservations.yaml').as_posix()!r}]
        bind:
          reservation: {{instances: [r1]}}
    """)
    with pytest.raises(GenomeError, match="requires event 'BookingRequested'"):
        G.load(root)


def test_root_cannot_override_rules(tmp_path):
    """Composition, not inheritance (D2): the root structurally has no entities."""
    root = _write(tmp_path, "bad2.yaml", f"""
        onto: 1
        name: bad2
        imports: [{(ROOT / 'modules' / 'payments.yaml').as_posix()!r}]
        bind:
          wallet: {{instances: [w1]}}
        entities:
          wallet:
            state: {{balance: int}}
            rules: {{}}
    """)
    with pytest.raises(GenomeError, match="schema"):
        G.load(root)


def test_unbound_instances_refused(tmp_path):
    root = _write(tmp_path, "bad3.yaml", f"""
        onto: 1
        name: bad3
        imports: [{(ROOT / 'modules' / 'payments.yaml').as_posix()!r}]
    """)
    with pytest.raises(GenomeError, match="no instances"):
        G.load(root)


def test_explain_slice_is_small():
    from onto.core import modules
    out = modules.explain(ROOT / "genomes" / "hotel.yaml", "wallet")
    assert "module 'payments'" in out and "root binding" in out
    pct = int(out.rsplit("(", 1)[1].rstrip("%)\n"))
    assert pct <= 50, f"slice is {pct}% of genome — not O(k)"
