# -*- coding: utf-8 -*-
"""Measuring the pure WARMED path (guard+body+post) — what the JIT materializes;
the HTTP/JSON envelope is shared by both tiers and is excluded from the tier comparison."""
from __future__ import annotations

from onto.core.genome import Genome
from onto.dialects.go_stdlib.emit import goname


def rule_bench_go(g: Genome) -> str:
    """Go code inside runBench(): benchmarking the first rule with a guard and post."""
    for en, ent in g.entities.items():
        for rn, r in ent.rules.items():
            if not (r.guard and r.contract.post):
                continue
            fn = goname(en) + goname(rn)
            ev_lits = ", ".join(
                f"{goname(f)}: " + ('"x"' if t == "str" else "1")
                for f, t in sorted(g.events[r.when].items()))
            init = ", ".join(f"{goname(f)}: " + (f'"{ent.init[f]}"' if ent.state[f] == "str" else str(ent.init[f])) for f in sorted(ent.state))
            int_fields = [f for f in sorted(ent.state) if ent.state[f] == "int"]
            f0 = goname(int_fields[0]) if int_fields else None
            lines = [
                f"\tsRule := {goname(en)}State{{{init}}}",
                f"\tevRule := Ev{r.when}{{{ev_lits}}}",
                "\tconst M = 20000000",
                "\tvar acc int64",
                "\tstart2 := time.Now()",
                "\tfor i := 0; i < M; i++ {",
                f"\t\tif guard{fn}(sRule, evRule) {{",
                f"\t\t\tnext := rule{fn}(sRule, evRule)",
                f"\t\t\tif post{fn}(next) {{",
                (f"\t\t\t\tacc += next.{f0}" if f0 else "\t\t\t\tacc++") + "",
                "\t\t\t}",
                "\t\t}",
                "\t}",
                "\tel2 := time.Since(start2)",
                f'\tfmt.Printf("bench rule-path ({en}.{rn}): '
                '%.1f ns/op (acc=%d)\\n", float64(el2.Nanoseconds())/M, acc)',
            ]
            return "\n".join(lines) + "\n"
    return ""
