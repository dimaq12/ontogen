# -*- coding: utf-8 -*-
"""Provenance of numbers (SPEC §5, D-series "math with a contract").

Classes: measured (monitor/bench: source + window) > declared (by hand, bootstrap)
> default (engine). Contamination rule: a formula's output is no cleaner than its
worst input. "From the theorem" is a checkable claim: Derived stores the formula and
its inputs, and CI recomputes them (tests/test_theory.py)."""
from __future__ import annotations

from dataclasses import dataclass, field

_RANK = {"measured": 0, "declared": 1, "default": 2}


@dataclass(frozen=True)
class V:
    """A number with a lineage."""
    value: float
    cls: str                       # measured | declared | default
    src: str                       # where from: monitor id / who set it / formula
    formula: str | None = None     # for derived: formula id from theory/
    inputs: tuple = field(default_factory=tuple)   # (name, V), for recomputation

    def __post_init__(self):
        if self.cls not in _RANK:
            raise ValueError(f"unknown provenance class '{self.cls}'")

    def show(self) -> str:
        tag = f"{self.cls}:{self.src}"
        if self.formula:
            ins = ", ".join(f"{n}={v.value:g}({v.cls})" for n, v in self.inputs)
            tag = f"{self.cls} via {self.formula}({ins})"
        return f"{self.value:g} [{tag}]"


def measured(value: float, src: str) -> V:
    return V(value, "measured", src)


def declared(value: float, who: str) -> V:
    return V(value, "declared", who)


def default(value: float, src: str = "engine") -> V:
    return V(value, "default", src)


def derived(value: float, formula: str, inputs: dict[str, V]) -> V:
    """Contamination: output class = the WORST class among the inputs."""
    worst = max((v.cls for v in inputs.values()), key=lambda c: _RANK[c],
                default="default")
    return V(value, worst, formula, formula=formula,
             inputs=tuple(sorted(inputs.items())))
