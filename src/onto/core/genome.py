# -*- coding: utf-8 -*-
"""Typed hub-IR of the genome (F1). No extra=allow (NOT §4): an unknown
field = a load error, not a silent tag-along (scar S6).

F1 subset of the IR: entities (rule bodies IN THE GENOME — reference semantics §10),
events, invariants/queries (Expr over lists of entities), retry_window — the
genome dedup contract (UNEXPRESSIBLE: per-channel windows return with F4
composition). Validation = a full typecheck of every Expr/body at load time.
"""
from __future__ import annotations

import pathlib
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from onto.core import expr as E
from onto.core import ir


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Contract(_Strict):
    post: Optional[str] = None        # Expr over s (after the body)
    conserves: Optional[str] = None   # int-Expr over s: value before == after


class Emit(_Strict):
    """POLICY wave (D54): a derived event after a rule is applied. Fields are
    Expr over the POST-state s and ev; NOT written to the log (recomputed by
    replay — deterministic by construction); id = <parent>:p<n>; the cascade is
    synchronous, depth capped at MAX_CASCADE."""
    event: str
    fields: dict[str, str]            # event field -> Expr
    when: Optional[str] = None        # emission condition (bool-Expr), None = always


class Rule(_Strict):
    when: str                         # event type
    body: str                         # body: reference semantics (Expr statements)
    guard: Optional[str] = None       # pre-condition over s and ev; False => no-op
    intent: Optional[str] = None      # prose for humans and (F2) the ribosome
    contract: Contract = Field(default_factory=Contract)
    emit: list[Emit] = Field(default_factory=list)   # policies (D54)


class Entity(_Strict):
    # F4: modules have no instances (a deploy detail, bound at the root); a flat
    # genome's must be non-empty — checked by validate().
    # Wave LAGO: instances: "dynamic" — an instance is BORN by the first event
    # carrying its key (init = zygote); real products don't know their clients
    # at deploy time (D51).
    instances: list[str] | str = Field(default_factory=list)
    state: dict[str, str]             # field -> "int" | "str" (D55: LAGO v2)
    init: dict[str, int | str] = Field(default_factory=dict)  # omitted = 0/"" (F4/D55)
    rules: dict[str, Rule]
    key: Optional[str] = None         # event field for routing (default: entity name)


class Genome(_Strict):
    onto: int
    name: str
    events: dict[str, dict[str, str]]           # type -> field -> "int"|"str"
    entities: dict[str, Entity]
    # skills (SLM wave): algorithmic cores with semantic+budget contracts
    skills: dict = Field(default_factory=dict)
    # membrane (CORRUPTION wave): foreign organisms behind islands with Expr assumptions
    externals: dict = Field(default_factory=dict)
    invariants: dict[str, str] = Field(default_factory=dict)   # name -> bool-Expr
    # queries (U1/D60): str = global aggregate; dict = PARAMETRIC:
    # {params: {name: int|str}, expr: "... p.name ..."}
    queries: dict[str, str | dict] = Field(default_factory=dict)
    retry_window: int = 1024          # dedup contract: an id older than the window is not a duplicate
    # TIME wave (U2/D59): timers — schedules executed by the warden:
    # name -> {every_s: N, event: Type, fields: {field: literal-value},
    #         per: entity?}  (per: an event for EACH live instance, the key
    # field is substituted automatically)
    timers: dict = Field(default_factory=dict)
    # U6 (D62): outbound webhooks: event type -> url (sent AFTER application,
    # fire-and-forget; errors — counter+ledger, the organism doesn't wait)
    webhooks: dict[str, str] = Field(default_factory=dict)
    # U3 (D66): representation map for type-2s (DERIVED, filled by load):
    # "entity.field"|"Event.field" -> "decimal"|"timestamp". After
    # normalization state/events hold the CARRIER (int) — court/printers/dialects
    # don't see type-2s; the representation lives only on the HTTP membrane.
    reprs: dict[str, str] = Field(default_factory=dict)
    # U4 (D67): auth gene. {idp: <external name>, rules: {Event|"*": bool-Expr
    # over {principal.role, principal.subject, ev.*}}}. The IdP is an ISLAND
    # behind the membrane (drift monitors judge it too). Deny-by-default: an event
    # without a rule (and without "*") — 403. MUTATIONS are protected (POST /event).
    auth: dict = Field(default_factory=dict)

    # -------- derived (not serialized)
    def key_field(self, ent_name: str) -> str:
        return self.entities[ent_name].key or ent_name

    def lists_env_types(self) -> dict:
        """Type environment for invariants/queries: entity -> list of states."""
        return {en: E.TList(dict(ent.state)) for en, ent in self.entities.items()}


class GenomeError(ValueError):
    """Load rejection: a list of reasons, in English (D24)."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("genome rejected:\n" + "\n".join(f"  - {e}" for e in errors))


# --------- U3 (D66): type-2s = a membrane representation, int semantics.
# decimal — minor units (scale 2), timestamp — unix seconds UTC.
# optional/list-state are REJECTED as PRIMITIVES (NOT §34-35): optional =
# a flag/"" sentinel, a list = the population of a dynamic entity.
TYPES2 = {"decimal": "int", "timestamp": "int"}
_DEC_RE = None


def normalize_types2(g: "Genome") -> None:
    """Build the representation map and reduce field types to the carrier."""
    for en, ent in g.entities.items():
        for f, t in list(ent.state.items()):
            if t in TYPES2:
                g.reprs[f"{en}.{f}"] = t
                ent.state[f] = TYPES2[t]
    for evn, fields in g.events.items():
        for f, t in list(fields.items()):
            if t in TYPES2:
                g.reprs[f"{evn}.{f}"] = t
                fields[f] = TYPES2[t]


def parse_repr(r: str, v) -> int:
    """Human string -> carrier. int passes through as-is (the raw API is the truth)."""
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    s = str(v).strip()
    if r == "decimal":
        import re as _re
        if not _re.fullmatch(r"[+-]?\d+(\.\d{1,2})?", s):
            raise ValueError(f"bad decimal '{s}' (want '12.34' or minor-units int)")
        neg = s.startswith("-")
        s = s.lstrip("+-")
        whole, _, frac = s.partition(".")
        n = int(whole) * 100 + int((frac + "00")[:2] or 0)
        return -n if neg else n
    if r == "timestamp":
        import datetime
        try:
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"bad timestamp '{s}' (want ISO-8601 or unix int)")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    raise ValueError(f"unknown repr '{r}'")


def human_repr(r: str, v: int):
    """Carrier -> human string (surfaces with ?repr=human)."""
    if r == "decimal":
        sign = "-" if v < 0 else ""
        a = abs(v)
        return f"{sign}{a // 100}.{a % 100:02d}"
    if r == "timestamp":
        import datetime
        return datetime.datetime.fromtimestamp(
            v, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return v


def coerce_event_in(g: "Genome", event: dict) -> tuple[dict, str | None]:
    """Inbound HTTP membrane: human forms of type-2 fields -> carrier. The log
    stores ONLY the carrier — replay knows nothing about representations."""
    if not g.reprs:
        return event, None
    evn = event.get("type", "")
    out = dict(event)
    for f in g.events.get(evn, {}):
        r = g.reprs.get(f"{evn}.{f}")
        if r and f in out:
            try:
                out[f] = parse_repr(r, out[f])
            except ValueError as e:
                return event, f"field '{f}': {e}"
    return out, None


def render_state(g: "Genome", en: str, st: dict) -> dict:
    """Output surface (?repr=human): state with type-2s in human form."""
    return {f: (human_repr(g.reprs[f"{en}.{f}"], v)
                if f"{en}.{f}" in g.reprs else v) for f, v in st.items()}


def validate(g: Genome) -> list[str]:
    """Full typecheck of the genome. Returns a list of errors (empty = clean)."""
    errs: list[str] = []
    for en, ent in g.entities.items():
        for f, t in ent.state.items():
            if t not in ("int", "str"):
                errs.append(f"{en}.state.{f}: state fields are 'int'|'str' "
                            f"(or types-2 'decimal'|'timestamp'), got '{t}'")
            iv = ent.init.get(f)
            if iv is not None and (
                    (t == "int" and not isinstance(iv, int)) or
                    (t == "str" and not isinstance(iv, str))):
                errs.append(f"{en}.init.{f}: must be {t}, got {type(iv).__name__}")
        if isinstance(ent.instances, str) and ent.instances != "dynamic":
            errs.append(f"{en}: instances must be a list or 'dynamic'")
        if not ent.instances:
            errs.append(f"{en}: no instances (list or 'dynamic')")
        key = g.key_field(en)
        for rn, r in ent.rules.items():
            where = f"{en}.{rn}"
            if r.when not in g.events:
                errs.append(f"{where}: unknown event '{r.when}'")
                continue
            ev_t = g.events[r.when]
            if key not in ev_t or ev_t[key] != "str":
                errs.append(f"{where}: event '{r.when}' must carry str key field "
                            f"'{key}' to route to entity '{en}'")
            env = {"s": dict(ent.state), "ev": dict(ev_t)}
            try:
                if r.guard:
                    t = E.typecheck_expr(E.parse_expr(r.guard), env)
                    if t != "bool":
                        errs.append(f"{where}.guard: must be bool, got {t}")
                body = E.parse_body(r.body)
                E.typecheck_body(body, dict(ent.state), dict(ev_t))
                if r.contract.post:
                    t = E.typecheck_expr(E.parse_expr(r.contract.post), {"s": dict(ent.state)})
                    if t != "bool":
                        errs.append(f"{where}.contract.post: must be bool, got {t}")
                if r.contract.conserves:
                    t = E.typecheck_expr(E.parse_expr(r.contract.conserves), {"s": dict(ent.state)})
                    if t != "int":
                        errs.append(f"{where}.contract.conserves: must be int, got {t}")
            except E.ExprError as e:
                errs.append(f"{where}: {e}")
            for j, em in enumerate(r.emit):
                ewhere = f"{where}.emit[{j}]"
                if em.event not in g.events:
                    errs.append(f"{ewhere}: unknown event '{em.event}'")
                    continue
                need = g.events[em.event]
                missing = [f for f in need if f not in em.fields]
                extra = [f for f in em.fields if f not in need]
                if missing:
                    errs.append(f"{ewhere}: missing fields {missing}")
                if extra:
                    errs.append(f"{ewhere}: unknown fields {extra}")
                env2 = {"s": dict(ent.state), "ev": dict(ev_t)}
                try:
                    if em.when:
                        t2 = E.typecheck_expr(E.parse_expr(em.when), env2)
                        if t2 != "bool":
                            errs.append(f"{ewhere}.when: must be bool, got {t2}")
                    for f, src in em.fields.items():
                        if f in need:
                            t2 = E.typecheck_expr(E.parse_expr(src), env2)
                            if t2 != need[f]:
                                errs.append(f"{ewhere}.{f}: must be {need[f]}, "
                                            f"got {t2}")
                except E.ExprError as e:
                    errs.append(f"{ewhere}: {e}")
    lists_env = g.lists_env_types()
    for name, src in g.invariants.items():
        try:
            t = E.typecheck_expr(E.parse_expr(src), lists_env)
            if t != "bool":
                errs.append(f"invariant {name}: must be bool, got {t}")
        except E.ExprError as e:
            errs.append(f"invariant {name}: {e}")
    for name, q in g.queries.items():
        try:
            if isinstance(q, str):
                E.typecheck_expr(E.parse_expr(q), lists_env)
            else:
                params = q.get("params", {})
                bad = [p for p, t in params.items() if t not in ("int", "str")]
                if bad:
                    errs.append(f"query {name}: params must be int|str: {bad}")
                    continue
                env_q = dict(lists_env)
                env_q["p"] = dict(params)
                E.typecheck_expr(E.parse_expr(q["expr"]), env_q)
        except E.ExprError as e:
            errs.append(f"query {name}: {e}")
        except KeyError:
            errs.append(f"query {name}: dict form needs {{params, expr}}")
    if g.retry_window < 1:
        errs.append("retry_window must be >= 1")
    for tn, t in g.timers.items():
        if not isinstance(t, dict) or "event" not in t or "every_s" not in t:
            errs.append(f"timer {tn}: needs {{every_s, event, fields?, per?}}")
            continue
        if t["event"] not in g.events:
            errs.append(f"timer {tn}: unknown event '{t['event']}'")
            continue
        per = t.get("per")
        if per is not None and per not in g.entities:
            errs.append(f"timer {tn}: unknown entity '{per}' in per:")
        need = dict(g.events[t["event"]])
        if per is not None:
            need.pop(g.key_field(per), None)   # the warden supplies the key
        missing = [f for f in need if f not in t.get("fields", {})]
        if missing:
            errs.append(f"timer {tn}: missing literal fields {missing}")
    if g.externals:
        # the membrane is validated without a base directory here (the island
        # file is checked by serve at mount time); Expr assumptions — now
        from onto.core import membrane as MB
        for name, raw_ext in g.externals.items():
            try:
                ext = MB.External.model_validate(raw_ext)
            except Exception as e:
                errs.append(f"external {name}: schema: {e}")
                continue
            for i, a in enumerate(ext.assumptions):
                try:
                    t = E.typecheck_expr(E.parse_expr(a),
                                         {"latency_ms": "int",
                                          "error_rate_pct": "int",
                                          "calls": "int"})
                    if t != "bool":
                        errs.append(f"external {name}.assumptions[{i}]: must be bool")
                except E.ExprError as e:
                    errs.append(f"external {name}.assumptions[{i}]: {e}")
            if not ext.assumptions:
                errs.append(f"external {name}: no assumptions — blind trust "
                            f"in a foreign organism is contraband")
    if g.skills:
        from onto.core import skills as SK
        for sname, raw_sk in g.skills.items():
            try:
                sk = SK.Skill.model_validate(raw_sk)
            except Exception as e:
                errs.append(f"skill {sname}: schema: {e}")
                continue
            errs.extend(SK.validate_skill(sname, sk))
    if g.auth:
        idp = g.auth.get("idp")
        if not idp or idp not in g.externals:
            errs.append(f"auth.idp: must name an external island "
                        f"(have: {sorted(g.externals)})")
        principal_t = {"role": "str", "subject": "str"}
        rules = g.auth.get("rules", {})
        if not isinstance(rules, dict) or not rules:
            errs.append("auth.rules: need {Event|'*': bool-Expr} (deny-by-default "
                        "without a rule)")
        else:
            for evn, src in rules.items():
                if evn != "*" and evn not in g.events:
                    errs.append(f"auth.rules.{evn}: unknown event")
                    continue
                env = {"principal": dict(principal_t)}
                if evn != "*":
                    env["ev"] = dict(g.events[evn])
                try:
                    t = E.typecheck_expr(E.parse_expr(src), env)
                    if t != "bool":
                        errs.append(f"auth.rules.{evn}: must be bool, got {t}")
                except E.ExprError as e:
                    errs.append(f"auth.rules.{evn}: {e}")
        extra = set(g.auth) - {"idp", "rules"}
        if extra:
            errs.append(f"auth: unknown keys {sorted(extra)}")
    return errs


def fill_defaults(g: Genome) -> None:
    """F4/D55 defaults: an unset init field = 0 (int) | "" (str)."""
    for ent in g.entities.values():
        for f, t in ent.state.items():
            ent.init.setdefault(f, "" if t == "str" else 0)


def load(path: str | pathlib.Path) -> Genome:
    """File -> hub version -> typed Genome -> typecheck. A root with
    imports is linked (core/modules); a module on its own is not runnable."""
    raw = ir.load(path)
    if "imports" in raw:
        from onto.core import modules
        return modules.link(path)
    if "module" in raw:
        raise GenomeError([
            f"{path}: this is a MODULE ('{raw['module']}') — modules are not "
            f"runnable alone; import it from a root genome"])
    try:
        g = Genome.model_validate(raw)
    except Exception as e:  # pydantic reports the fields itself
        raise GenomeError([f"schema: {e}"])
    normalize_types2(g)
    fill_defaults(g)
    errs = validate(g)
    if errs:
        raise GenomeError(errs)
    return g
