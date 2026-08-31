# -*- coding: utf-8 -*-
"""Interview by counterexamples (SPEC §11): contract underdetermination ->
an executable question to the operator with ready-made completion variants.

F2 mechanics:
  1. detect(): both candidates pass the court under their DECLARED contracts,
     yet prove_equiv finds a diverging input (u*, v4 mechanics) -> Question.
  2. Question carries a concrete input, both outcomes and patch variants
     (guard/post); a variant is valid only if it RESOLVES the question:
     after applying it at least one candidate is eliminated (the court or the
     equivalence becomes proven).
  3. The answer = a genome patch via the ordinary propose flow (outside this
     module).
Hygiene NOT §29: without an executable counterexample no question is asked.
Variant generation (D84): templates enumerated from the
counterexample, each CERTIFIED by the court; unresolved -> the U12
'I don't know' path is the honest fallback.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from onto.core import court, expr as E


@dataclass
class Patch:
    kind: str      # "guard" | "post"
    src: str       # Expr string

    def describe(self) -> str:
        return f"add {self.kind}: \"{self.src}\""


@dataclass
class Question:
    rule: str
    input_example: dict          # court counterexample: concrete s and ev
    outcome_a: dict
    outcome_b: dict
    variants: list[Patch] = field(default_factory=list)

    def render(self) -> str:
        lines = [f"UNDERDETERMINED CONTRACT for rule '{self.rule}':",
                 f"  on input {self.input_example}",
                 f"  candidate A yields {self.outcome_a}",
                 f"  candidate B yields {self.outcome_b}",
                 "  both satisfy every declared contract. Which is intended?"]
        for i, v in enumerate(self.variants):
            lines.append(f"  [{i}] {v.describe()}")
        return "\n".join(lines)


def _concrete_run(guard_src, body_src, s_vals: dict, ev_vals: dict,
                  state_types: dict) -> dict:
    """Run a candidate through the canonical interpreter on a concrete input."""
    if guard_src and not E.eval_expr(E.parse_expr(guard_src), {"s": s_vals, "ev": ev_vals}):
        return dict(s_vals)
    return E.exec_body(E.parse_body(body_src), s_vals, ev_vals)


def _split_model(model: dict, state_types: dict, ev_types: dict) -> tuple[dict, dict]:
    s_vals = {f: model.get(f"s.{f}", 0) for f in state_types}
    ev_vals = {}
    for f, t in ev_types.items():
        v = model.get(f"ev.{f}", 0 if t == "int" else "x")
        if t == "str" and not isinstance(v, str):
            v = str(v)
        if isinstance(v, str):
            v = v.strip('"')
        ev_vals[f] = v
    return s_vals, ev_vals


def _passes_court(state_types, ev_types, guard_src, body_src,
                  post_src, conserves_src) -> bool:
    verdicts = court.prove_rule(state_types, ev_types, guard_src, body_src,
                                post_src, conserves_src)
    return all(v.status == "proved" for v in verdicts.values())


def detect(rule_name: str, state_types: dict, ev_types: dict,
           cand_a: tuple[str | None, str], cand_b: tuple[str | None, str],
           post_src: str | None, conserves_src: str | None = None,
           variants: list[Patch] | None = None) -> Question | None:
    """None = the contracts determine the behavior (a candidate was eliminated
    or they are ≡)."""
    a_ok = _passes_court(state_types, ev_types, *cand_a, post_src, conserves_src)
    b_ok = _passes_court(state_types, ev_types, *cand_b, post_src, conserves_src)
    if not (a_ok and b_ok):
        return None                      # the court itself distinguished them — no question needed
    v = court.prove_equiv(state_types, ev_types, cand_a, cand_b)
    if v.status != "counterexample":
        return None                      # equivalent (or unknown) — no question
    s_vals, ev_vals = _split_model(v.model, state_types, ev_types)
    q = Question(
        rule=rule_name,
        input_example={"s": s_vals, "ev": ev_vals},
        outcome_a=_concrete_run(*cand_a, s_vals, ev_vals, state_types),
        outcome_b=_concrete_run(*cand_b, s_vals, ev_vals, state_types),
    )
    if variants is None:
        # AUTO-GENERATE (D84): system proposes court-certified variants
        q.variants = generate_variants(
            state_types, ev_types, cand_a, cand_b, post_src, conserves_src,
            s_vals, ev_vals, q.outcome_a, q.outcome_b)
    else:
        for p in variants:
            if _variant_resolves(p, state_types, ev_types, cand_a, cand_b,
                                 post_src, conserves_src):
                q.variants.append(p)
    return q


def generate_variants(state_types: dict, ev_types: dict,
                      cand_a, cand_b, post_src, conserves_src,
                      s_vals: dict, ev_vals: dict, outcome_a: dict,
                      outcome_b: dict, cap: int = 4) -> list:
    """#6 (D84): the interview now GENERATES the completion variants instead
    of only checking hand-written ones (SPEC §11 promised A/B/don't-know).
    Templates are enumerated from the counterexample; the COURT certifies
    each (via _variant_resolves) — intelligence in the gate, enumeration
    cheap. Unresolved -> the U12 'I don't know' path stays the honest
    fallback. Returns up to `cap` court-certified resolving patches."""
    ints_s = [f for f, t in state_types.items() if t == "int"]
    ints_ev = [f for f, t in ev_types.items() if t == "int"]
    cands: list[Patch] = []

    # --- GUARD templates: exclude the divergence region (make bodies ≡).
    # Sign conditions on each int field (the F2 lesson: `s.booked > 0`).
    for f in ints_ev:
        cands += [Patch("guard", f"ev.{f} > 0"), Patch("guard", f"ev.{f} >= 0")]
    for f in ints_s:
        cands += [Patch("guard", f"s.{f} > 0"), Patch("guard", f"s.{f} >= 0")]
    # Orderings between an event amount and a state field (spend/withdraw).
    for a in ints_ev:
        for b in ints_s:
            cands += [Patch("guard", f"ev.{a} <= s.{b}"),
                      Patch("guard", f"s.{b} >= ev.{a}")]

    # --- POST templates: one candidate satisfies, the other violates.
    # Non-negativity and bounds from the diverging outcomes.
    for f in ints_s:
        va, vb = outcome_a.get(f), outcome_b.get(f)
        cands.append(Patch("post", f"s.{f} >= 0"))
        if isinstance(va, int) and isinstance(vb, int) and va != vb:
            mid = (min(va, vb) + max(va, vb)) // 2
            cands += [Patch("post", f"s.{f} >= {max(va, vb)}"),
                      Patch("post", f"s.{f} <= {min(va, vb)}"),
                      Patch("post", f"s.{f} > {mid}")]
        for g in ints_s:
            if g != f:
                cands.append(Patch("post", f"s.{f} <= s.{g}"))

    seen, out = set(), []
    for p in cands:
        key = (p.kind, p.src)
        if key in seen:
            continue
        seen.add(key)
        try:
            if _variant_resolves(p, state_types, ev_types, cand_a, cand_b,
                                 post_src, conserves_src):
                out.append(p)
                if len(out) >= cap:
                    break
        except Exception:  # noqa: BLE001 — a bad template never breaks the menu
            continue
    return out


def _variant_resolves(p: Patch, state_types, ev_types, cand_a, cand_b,
                      post_src, conserves_src) -> bool:
    """A patch resolves the question if, after it, the candidates are
    distinguishable by the court or become provably equivalent."""
    if p.kind == "post":
        new_post = p.src if not post_src else f"({post_src}) and ({p.src})"
        a_ok = _passes_court(state_types, ev_types, *cand_a, new_post, conserves_src)
        b_ok = _passes_court(state_types, ev_types, *cand_b, new_post, conserves_src)
        return a_ok != b_ok or (not a_ok and not b_ok)
    if p.kind == "guard":
        ga = (p.src, cand_a[1])
        gb = (p.src, cand_b[1])
        return court.prove_equiv(state_types, ev_types, ga, gb).status == "proved"
    return False


def apply_patch(genome_raw: dict, entity: str, rule: str, p: Patch) -> dict:
    """Operator answer -> a genome diff (hub-version dict; the write goes
    through the ordinary propose/checkers outside this module)."""
    import copy
    g2 = copy.deepcopy(genome_raw)
    r = g2["entities"][entity]["rules"][rule]
    if p.kind == "guard":
        r["guard"] = p.src
    elif p.kind == "post":
        c = r.setdefault("contract", {})
        c["post"] = p.src if not c.get("post") else f"({c['post']}) and ({p.src})"
    return g2


# --------- U12 (D74; PARADIGM_LIMITS §4): interview WITHOUT an oracle.
# "Counterexample -> question to the operator" assumes someone at least
# knows the answer. In reality often nobody does. Not-knowing is not a
# blocker but a STATE: a third legal interview outcome — "I don't know" —
# turns the question into a TYPED HOLE: an assumption + a watch-Expr; the
# organism lives under the declared assumption, the warden records hits on
# the region of uncertainty into the ledger, and the answer (when the world
# answers) retracts the hole. These are islands applied to KNOWLEDGE. The
# file sits next to the genome (like flows): the frozen IR is not touched.

def declare_unknown(assumptions_path, name: str, entity: str, rule: str,
                    question_text: str, watch_expr: str,
                    lists_env: dict) -> None:
    """Record not-knowing. watch_expr is a bool-Expr over populations (env as
    for invariants): "the region of uncertainty is reachable/hit"."""
    import pathlib
    import yaml
    from onto.core import expr as E
    t = E.typecheck_expr(E.parse_expr(watch_expr), dict(lists_env))
    if t != "bool":
        raise E.ExprError(f"watch must be bool, got {t}")
    p = pathlib.Path(assumptions_path)
    doc = yaml.safe_load(p.read_text()) if p.exists() else {}
    doc = doc or {}
    doc.setdefault("assumptions", {})[name] = {
        "entity": entity, "rule": rule, "question": question_text,
        "watch": watch_expr, "status": "declared"}
    p.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
                 encoding="utf-8")


def resolve_unknown(assumptions_path, name: str) -> bool:
    """The world answered: the hole is retracted (the record stays, with
    status resolved)."""
    import pathlib
    import yaml
    p = pathlib.Path(assumptions_path)
    doc = yaml.safe_load(p.read_text()) if p.exists() else {}
    a = (doc or {}).get("assumptions", {}).get(name)
    if not a:
        return False
    a["status"] = "resolved"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
                 encoding="utf-8")
    return True
