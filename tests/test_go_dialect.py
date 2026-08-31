# -*- coding: utf-8 -*-
"""go-stdlib dialect: byte-for-byte determinism, build, conformance certificate."""
import hashlib
import pathlib

import pytest

from onto.core import genome as G
from onto.dialects.go_stdlib import gates, skeleton

ROOT = pathlib.Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(gates.find_go() is None, reason="no go toolchain")


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_generation_deterministic(tmp_path):
    g = G.load(ROOT / "genomes" / "booking.yaml")
    d1, d2 = tmp_path / "a", tmp_path / "b"
    skeleton.generate(g, d1)
    skeleton.generate(g, d2)
    assert _sha(d1 / "main.go") == _sha(d2 / "main.go")


def test_build_and_conformance(tmp_path):
    g = G.load(ROOT / "genomes" / "booking.yaml")
    out = skeleton.generate(g, tmp_path / "org")
    ok, msg = gates.build(out)
    assert ok, msg
    cert = gates.certificate(ROOT / "exams" / "conformance_expr.jsonl", tmp_path / "conf")
    assert cert["printer_conformance"] == "green", cert
