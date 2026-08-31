# -*- coding: utf-8 -*-
"""Conformance suite: the corpus is generated deterministically and self-checks;
the committed corpus (exams/) must match the canon (D17/P12)."""
import pathlib

from onto.core import conformance as C

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "exams" / "conformance_expr.jsonl"


def test_gen_deterministic():
    assert C.gen_corpus() == C.gen_corpus()


def test_committed_corpus_matches_canon():
    assert CORPUS.exists(), "run: onto conformance gen exams/conformance_expr.jsonl"
    assert C.check_corpus(CORPUS) == []
