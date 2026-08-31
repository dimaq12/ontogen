# -*- coding: utf-8 -*-
"""python-stdlib dialect: determinism, build, conformance certificate."""
import hashlib
import pathlib

from onto.core import genome as G
from onto.dialects.python_stdlib import gates, skeleton

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_generation_deterministic(tmp_path):
    g = G.load(ROOT / "genomes" / "booking.yaml")
    d1, d2 = tmp_path / "a", tmp_path / "b"
    skeleton.generate(g, d1)
    skeleton.generate(g, d2)
    assert hashlib.sha256((d1 / "organism.py").read_bytes()).digest() == \
        hashlib.sha256((d2 / "organism.py").read_bytes()).digest()


def test_build_and_conformance(tmp_path):
    g = G.load(ROOT / "genomes" / "booking.yaml")
    out = skeleton.generate(g, tmp_path / "org")
    ok, msg = gates.build(out)
    assert ok, msg
    cert = gates.certificate(ROOT / "exams" / "conformance_expr.jsonl", tmp_path / "conf")
    assert cert["printer_conformance"] == "green", cert


def test_registry_has_both():
    from onto.dialects import registry
    assert registry.names() == ["go-stdlib", "python-stdlib"]
