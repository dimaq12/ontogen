# -*- coding: utf-8 -*-
"""EXAM F0 (PLAN): the linters MUST go red on planted violations —
we check the linter itself, then use it on the real engine code."""
import pathlib
import textwrap

from onto import lint

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "onto"


def _plant(tmp_path, rel, text):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_i1_go_in_core_is_red(tmp_path):
    p = _plant(tmp_path, "onto/core/bad.py", '''
        def emit(): return "rules.go"  # printing Go straight from the core
    ''')
    vs = lint.check_file(p, is_core=True)
    assert vs and "Go in core" in vs[0].text


def test_i1_if_dialect_is_red(tmp_path):
    p = _plant(tmp_path, "onto/core/bad2.py", '''
        def f(dialect):
            if dialect == "rust":
                pass
    ''')
    assert any("branching on dialect" in v.text for v in lint.check_file(p, is_core=True))


def test_extra_allow_is_red_everywhere(tmp_path):
    p = _plant(tmp_path, "onto/anything.py", '''
        model_config = ConfigDict(extra="allow")
    ''')
    assert any("extra" in v.text for v in lint.check_file(p, is_core=False))


def test_machine_path_is_red(tmp_path):
    p = _plant(tmp_path, "onto/anything2.py", '''
        GO = "/tmp/claude-1000/scratchpad/go/bin/go"
    ''')
    assert any("machine-specific path" in v.text for v in lint.check_file(p, is_core=False))


def test_clean_file_is_green(tmp_path):
    p = _plant(tmp_path, "onto/core/ok.py", '''
        def to_hub(raw: dict) -> dict:
            return dict(raw)
    ''')
    assert lint.check_file(p, is_core=True) == []


def test_engine_source_is_clean():
    """With the same tool — real code: the engine must pass its own linters."""
    assert lint.check_tree(SRC) == []
