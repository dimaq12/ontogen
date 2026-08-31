# -*- coding: utf-8 -*-
"""NL front (IDEAL, the backbone): a human-language DESCRIPTION -> genome +
acceptance flows. The model is part of the system (a ladder by capability),
not a human at the wheel.

CEGIS: gate rejections (validate/court/the judge's teeth) are returned to the
model verbatim. The human gets only interview questions, rendered as prose. A
cache keyed by the description hash = determinism through certification.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import yaml

from onto.ribosome import Provider, strip_code

ATTEMPTS_PER_MODEL = 8
NL_LADDER = ["anthropic/claude-sonnet-4.5", "anthropic/claude-opus-4.6"]

IR_CHEATSHEET = """
# GENOME FORMAT (onto v1) — complete cheat sheet
onto: 1
name: <snake_case>
retry_window: 64               # dedup window for event ids
events:                        # every event MUST carry the str key field of
  EventName: {key_field: str, amount: int}   # each entity that consumes it
entities:
  entity_name:                 # key field defaults to entity name;
    key: key_field             # override with `key:`
    instances: dynamic         # or fixed list [a, b]; dynamic = born on first event
    state: {field: int, ref: str}   # int | str only
    init: {field: 0}           # omitted fields default to 0 / ""
    rules:
      rule_name:
        when: EventName
        guard: "s.field >= 0 and ev.amount > 0"     # optional; False => no-op
        body: |
          s.field = s.field + ev.amount
        contract:
          post: "s.field >= 0"          # proved by SMT for ALL inputs —
                                        # include every fact the proof needs
                                        # (inductive: post is assumed on the
                                        # pre-state too)
          conserves: "s.a + s.b"        # optional invariant sum
        emit:                           # optional derived events (sagas)
          - event: OtherEvent
            when: "s.field > 0"         # optional condition (post-state)
            fields: {key_field: "ev.key_field", amount: "s.field"}
queries:                       # global aggregates over entity populations
  total: "sum(x.field for x in entity_name)"
  # parametric form (served as /q/name?param=value):
  user_spent: {params: {user: str}, expr: "sum(u.spent for u in user if u.user_id == p.user)"}
timers:                        # schedules executed by the supervisor
  hourly_fee:                  # per: — one event per LIVE instance, its key
    {every_s: 3600, event: FeeTick, per: scooter, fields: {amount: 100}}
webhooks:                      # outbound notifications after an event applies
  ViolationReported: "http://127.0.0.1:9000/hooks"
invariants:
  sane: "all(x.field >= 0 for x in entity_name)"
# Expression language: Python expression subset — comparisons, and/or/not,
# + - * // %, min/max/len, sum/all/any over generators, ternary
# `a if cond else b`. str supports ==/!= only. NO loops in bodies.
# Bodies: assignments `s.field = expr` and if/elif/else only.

# WORKED EXAMPLE — study it carefully (routing + provable clamped charge):
# events:
#   RideEnded: {user: str, scooter: str, minutes: int}   # BOTH key fields!
# entities:
#   user:
#     instances: dynamic
#     state: {balance: int, spent: int}
#     rules:
#       charge_ride:
#         when: RideEnded
#         guard: "ev.minutes > 0"
#         body: |
#           s.spent = s.spent + min(s.balance, ev.minutes * 500)
#           s.balance = s.balance - min(s.balance, ev.minutes * 500)
#         contract:
#           post: "s.balance >= 0 and s.spent >= 0"   # provable: min-clamp
#   scooter:
#     instances: dynamic
#     state: {rented: int}
#     rules:
#       free_up:
#         when: RideEnded
#         guard: "s.rented == 1"
#         body: |
#           s.rented = 0
#         contract: {post: "s.rented >= 0 and s.rented <= 1"}
# FAN-OUT PATTERN — ONE EVENT TOUCHES TWO+ INSTANCES OF THE SAME ENTITY
# (e.g. a match with winner AND loser). Routing delivers an event to ONE
# instance per entity (by its key field). Solution: a small ROUTER entity
# (dynamic, keyed by e.g. match_id) that accepts the event once
# (guard s.processed == 0) and emits one PER-PARTICIPANT event each:
#   emit:
#     - {event: WinResult,  fields: {player: "ev.winner", match_id: "ev.match_id"}}
#     - {event: LoseResult, fields: {player: "ev.loser",  match_id: "ev.match_id"}}
# Each participant then reacts to ITS event via its own key.
#
# TWO-SIDED ACCOUNTING — a rule like "reader may hold <= 3 books AND the
# book must have a free copy" spans two entities: keep SYMMETRIC counters
# on both (book.borrowed, reader.books_on_hand); the checking side guards
# and emits an approved event; the other side applies its own counter on
# that event. Same for returns (both counters go down).
#
# POINTER FIELDS — "remember who occupies it": a str state field holding
# the OTHER entity's key (occupied_by: str, "" = free). Release guards on
# equality if identity matters; set back to "" on free.
#
# MONEY TO ANOTHER PARTY — never mutate another entity directly; emit an
# event with a computed amount: fields: {owner: "ev.owner", amount: "ev.hours * 200"}.
#
# CRITICAL RULES OF THUMB:
# - declare EVERY event you reference in `events:` with ALL fields;
# - an event consumed by N entities carries N key fields (str);
# - clamp subtractions with min(...) so `>= 0` posts are provable;
# - for global totals DO NOT invent a stats entity — use `queries:` over
#   existing populations (e.g. "sum(u.spent for u in user)");
# - posts are inductive: they are assumed on the pre-state, so include every
#   non-negativity fact your arithmetic relies on.

# SAGA PATTERN — CROSS-ENTITY PRECONDITIONS (very common, e.g. "rent only if
# wallet balance >= X"): entity A cannot guard on entity B's state! Route the
# request through the entity that OWNS the precondition, and let it EMIT an
# approved event for the other entity:
# events:
#   RideStarted:  {user: str, scooter: str}     # request hits USER first
#   RideApproved: {scooter: str}                # derived, emitted by user
# entities:
#   user:
#     rules:
#       approve_ride:
#         when: RideStarted
#         guard: "s.balance >= 10000"           # the owner of the precondition
#         body: |
#           s.rides = s.rides + 1
#         contract: {post: "s.rides >= 0"}
#         emit:
#           - event: RideApproved
#             fields: {scooter: "ev.scooter"}
#   scooter:
#     rules:
#       mark_rented:
#         when: RideApproved                    # reacts ONLY to approval
#         guard: "s.status == 0"
#         body: |
#           s.status = 1
#         contract: {post: "s.status >= 0 and s.status <= 1"}
# If the guard fails, nothing is emitted — the other entity never changes.
"""

FLOWS_CHEATSHEET = """
# ACCEPTANCE FLOWS FORMAT (judge) — sequential scenarios
flows:
  scenario_name:
    - post:  {id: unique_tx_1, type: EventName, key_field: somekey, amount: 5}
    - state: {entity: entity_name, instance: somekey, expect: {field: 5}}
    - query: {name: total, expect: 5}
"""


def nl_prompt(description: str, counterexamples: list[str]) -> str:
    cx = ("\nYour previous attempt was REJECTED by machine gates — fix "
          "exactly these issues and output the corrected files:\n"
          + "\n".join(counterexamples)) if counterexamples else ""
    return f"""You are the front-end of a software factory. From a plain-language
product description you produce TWO artifacts:
1. a GENOME (the entire program as data: entities, events, executable rules,
   contracts that will be PROVED by an SMT solver);
2. ACCEPTANCE FLOWS (scenarios an external judge will run over HTTP).

{IR_CHEATSHEET}
{FLOWS_CHEATSHEET}

PRODUCT DESCRIPTION (source of truth; the customer wrote it):
---
{description}
---

Design rules:
- model money in integer cents; statuses as int phases (0,1,2...) guarded
  by state-machine guards; ids/references as str fields.
- every event carries the key field of EVERY entity that reacts to it.
- keep contracts PROVABLE: post conditions must hold inductively (assume
  post on pre-state + guard => post on post-state). Include non-negativity
  facts the arithmetic depends on.
- flows must cover: the happy path, one guard rejection, and idempotency is
  automatic (same event id twice) — do not test it explicitly.
- flows use ONLY events/entities/queries you defined, with correct fields.
- flows MUST NOT depend on wall-clock or schedules: the judge runs WITHOUT
  the scheduler. To cover a timer's behavior, POST the timer's event
  explicitly in a flow (a timer is just a scheduled sender of that event).
- guard EVERY event that carries an amount with `ev.amount > 0` (negative
  amounts break `>= 0` proofs).
- before writing each flow `expect`, recompute the arithmetic step by step
  through every rule (including emitted saga events and clamps) — most
  failures are your own expected values being wrong, not the genome.
- CRITICAL: ALL flows run SEQUENTIALLY on ONE organism — state and global
  queries ACCUMULATE across flows. Use fresh instance keys in every flow,
  and compute global query expectations CUMULATIVELY (including effects of
  all previous flows), or check global queries only in the first flow.
{cx}
Output EXACTLY two fenced blocks, first the genome then the flows:
```yaml
# genome
...
```
```yaml
# flows
...
```"""


def _two_yaml_blocks(text: str) -> tuple[str, str]:
    import re
    blocks = re.findall(r"```(?:yaml)?\s*\n(.*?)```", text, flags=re.S)
    if len(blocks) < 2:
        raise ValueError(f"expected two yaml blocks, got {len(blocks)}")
    return blocks[0], blocks[1]


def gates(genome_text: str, flows_text: str, workdir: pathlib.Path,
          root: pathlib.Path) -> tuple[str | None, list]:
    """None = green. Returns (counterexample, interview_questions[])."""
    from onto.core import court, genome as G

    try:
        raw = yaml.safe_load(genome_text)
        flows = yaml.safe_load(flows_text)
    except Exception as e:  # noqa: BLE001
        return f"- YAML parse error: {str(e)[:300]}", []
    if not isinstance(flows, dict) or "flows" not in flows:
        return "- flows file must have a top-level `flows:` mapping", []

    gpath = workdir / "genome.yaml"
    gpath.write_text(genome_text, encoding="utf-8")
    try:
        g = G.load(gpath)
    except G.GenomeError as e:
        return "- genome rejected by checkers:\n" + "\n".join(
            f"  {x}" for x in e.errors[:8]), []
    except Exception as e:  # noqa: BLE001
        return f"- genome load error: {type(e).__name__}: {str(e)[:200]}", []

    # court: contracts are proved
    for en, ent in g.entities.items():
        for rn, r in ent.rules.items():
            vs = court.prove_rule(dict(ent.state), dict(g.events[r.when]),
                                  r.guard, r.body, r.contract.post,
                                  r.contract.conserves)
            for kind, v in vs.items():
                if v.status == "counterexample":
                    return (f"- SMT court DISPROVED {en}.{rn}.{kind}; "
                            f"counterexample {v.model}. Fix the body or state "
                            f"the missing inductive fact in post.", [])

    # flows: static field check against the genome
    for fname, steps in flows["flows"].items():
        if not isinstance(steps, list):
            return f"- flow '{fname}' must be a list of steps", []
        for i, st in enumerate(steps):
            if "post" in st:
                p = st["post"]
                evt = p.get("type")
                if evt not in g.events:
                    return (f"- flow '{fname}' step {i}: unknown event "
                            f"'{evt}' (events: {sorted(g.events)})"), []
                missing = [f for f in g.events[evt]
                           if f not in p and f not in ("id", "type")]
                if missing:
                    return (f"- flow '{fname}' step {i}: event '{evt}' "
                            f"missing fields {missing}"), []
            elif "state" in st:
                en = st["state"].get("entity")
                if en not in g.entities:
                    return (f"- flow '{fname}' step {i}: unknown entity "
                            f"'{en}'"), []
                bad = [k for k in st["state"].get("expect", {})
                       if k not in g.entities[en].state]
                if bad:
                    return (f"- flow '{fname}' step {i}: entity '{en}' has no "
                            f"state fields {bad}"), []
            elif "query" in st:
                qn = st["query"].get("name")
                if qn not in g.queries:
                    return (f"- flow '{fname}' step {i}: unknown query "
                            f"'{qn}' (queries: {sorted(g.queries)})"), []

    # dynamic acceptance: organism + judge
    import subprocess
    import tempfile
    import time
    import urllib.request
    fpath = workdir / "flows.yaml"
    fpath.write_text(flows_text, encoding="utf-8")
    py = root / ".venv" / "bin" / "python"
    port = 8741
    proc = subprocess.Popen(
        [str(py), "-m", "onto.cli", "serve", str(gpath),
         "--data", tempfile.mkdtemp(prefix="nlfront-"), "--port", str(port)],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        up = False
        for _ in range(100):
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/health", timeout=2)
                up = True
                break
            except Exception:
                time.sleep(0.05)
        if not up:
            return "- organism did not start (internal)", []
        judge = subprocess.run(
            [str(py), "-m", "onto.cli", "judge", str(fpath),
             f"http://127.0.0.1:{port}"],
            cwd=root, capture_output=True, text=True)
        if judge.returncode != 0:
            red = [l for l in judge.stdout.splitlines()
                   if "RED" in l or "step" in l]
            if not red:                     # the judge CRASHED (did not judge) — trace
                red = ["judge crashed: " + l for l in
                       judge.stderr.splitlines()[-3:]]   # into the counterexample (D77)
            hint = ("\n  HINT: flows run SEQUENTIALLY on ONE organism — "
                    "global queries accumulate across flows; recompute "
                    "expectations cumulatively or use fresh keys."
                    if any("q/" in l for l in red) else "")
            return ("- your own acceptance flows FAIL on the built system "
                    "(genome and flows disagree — decide which is right and "
                    "fix it):\n" + "\n".join("  " + l for l in red[:8])
                    + hint), []
    finally:
        proc.kill()
    return None, []


def build(description: str, provider: Provider, workdir,
          root, ladder: list[str] | None = None, log=print) -> dict:
    workdir = pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(description.encode()).hexdigest()[:16]
    tele: dict = {"attempts": [], "island": False, "key": key}
    cache = workdir / f"cache_{key}"
    cache.mkdir(exist_ok=True)

    for model in (ladder or provider.ladder("nl")):
        ck_g = cache / f"{model.replace('/', '_')}.genome.yaml"
        ck_f = cache / f"{model.replace('/', '_')}.flows.yaml"
        cxs: list[str] = []
        if ck_g.exists() and ck_f.exists():
            v, _ = gates(ck_g.read_text(encoding="utf-8"),
                         ck_f.read_text(encoding="utf-8"), workdir, root)
            if v is None:
                log(f"  nlfront: CACHE hit [{model}]")
                tele.update(model=model, cache=True)
                return tele
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            raw = provider.generate(model, nl_prompt(description, cxs),
                                    seed=42,
                                    tag=f"nl:{model}:{attempt}",
                                    max_tokens=8000)
            try:
                genome_text, flows_text = _two_yaml_blocks(raw)
            except ValueError as e:
                cxs.append(f"- output format: {e}")
                tele["attempts"].append({"model": model, "attempt": attempt,
                                         "verdict": str(e)[:120]})
                continue
            verdict, _ = gates(genome_text, flows_text, workdir, root)
            tele["attempts"].append({"model": model, "attempt": attempt,
                                     "verdict": (verdict or "GREEN")[:160]})
            if verdict is None:
                ck_g.write_text(genome_text, encoding="utf-8")
                ck_f.write_text(flows_text, encoding="utf-8")
                (workdir / "genome.yaml").write_text(genome_text,
                                                     encoding="utf-8")
                (workdir / "flows.yaml").write_text(flows_text,
                                                    encoding="utf-8")
                log(f"  nlfront: GREEN [{model}] attempt {attempt}")
                tele.update(model=model, cache=False)
                return tele
            cxs.append(verdict)
            log(f"  nlfront: red [{model}] attempt {attempt}: "
                f"{verdict.splitlines()[0][:110]}")
        log(f"  nlfront: ladder step exhausted [{model}] -> escalate")
    tele["island"] = True
    return tele
