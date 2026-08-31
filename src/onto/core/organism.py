# -*- coding: utf-8 -*-
"""Organism — the reference interpreter of the genome (SPEC §10.1, F1).

Alive from second zero WITHOUT code generation: event -> dedup (contract window)
-> fan-out across entities (guard -> body -> contracts) -> observer invariants.
The truth is the event log (JSONL, write-ahead); replay = regenerating state;
the ledger (JSONL, hash chain, D16) is the journal of proofs and violations.

Semantics (D25): a violation of the entity's OWN contract (post/conserves) or an
execution error = the entity transition is REJECTED + a ledger entry: the genome
contradicts itself, and this is visible rather than silently committed.
Invariants (cross-entity) are observers: a violation is recorded, state is not
blocked (v0 semantics).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from collections import deque

from onto.core import expr as E
from onto.core.genome import Genome


class Ledger:
    """Append-only JSONL with a hash chain (D16). Machine fields are English."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.prev = "genesis"
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.prev = json.loads(line)["h"]
        else:
            path.parent.mkdir(parents=True, exist_ok=True)

    def verify(self) -> dict:
        """D80: the hash chain MUST be verified, otherwise it is decoration
        (NOT §12). Recompute the whole chain; report a break with its line number."""
        prev, n = "genesis", 0
        if not self.path.exists():
            return {"ok": True, "entries": 0}
        for i, line in enumerate(self.path.read_text(
                encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            e = json.loads(line)
            h = e.pop("h")
            kind = e.pop("kind")
            claimed_prev = e.pop("prev")
            hv = e.pop("hv", 1)
            body = ({"kind": kind, **e} if hv == 2 else dict(e))
            want = hashlib.sha256(
                (prev + json.dumps(body, sort_keys=True,
                                   ensure_ascii=False)).encode()
            ).hexdigest()[:16]
            if claimed_prev != prev or h != want:
                return {"ok": False, "entries": i + 1, "broken_at": i + 1}
            prev, n = h, n + 1
        return {"ok": True, "entries": n}

    def record(self, kind: str, payload: dict) -> None:
        # D80 hv=2: kind is PART of the hash (swapping the entry kind breaks the chain)
        entry = {"kind": kind, "prev": self.prev, "hv": 2, **payload}
        entry["h"] = hashlib.sha256(
            (self.prev + json.dumps({"kind": kind, **payload},
                                    sort_keys=True, ensure_ascii=False)).encode()
        ).hexdigest()[:16]
        self.prev = entry["h"]
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class Organism:
    def __init__(self, g: Genome, data_dir: str | pathlib.Path,
                 store: str | None = None):
        self.g = g
        self.data = pathlib.Path(data_dir)
        self.data.mkdir(parents=True, exist_ok=True)
        from onto.core.store import open_store
        self.store = open_store(self.data, store)
        self.ledger = Ledger(self.data / "ledger.jsonl")
        # state: entity -> instance -> dict of fields
        self.state: dict[str, dict[str, dict]] = {
            en: ({} if ent.instances == "dynamic"
                 else {inst: dict(ent.init) for inst in ent.instances})
            for en, ent in g.entities.items()
        }
        # dedup: the retry_window contract window (SCARS S12: don't "remember everything forever")
        self._seen_q: deque[str] = deque()
        self._seen: set[str] = set()
        self.counters = {"applied": 0, "dup": 0, "noop": 0, "rejected": 0,
                         "unknown_instance": 0, "invariant_violations": 0}
        # heat (F5): applied rules per entity — raw material for the Placer;
        # rate = the difference between /health snapshots over an interval (Measured)
        self.heat: dict[str, int] = {en: 0 for en in g.entities}
        # compiled ASTs (once)
        self._compiled: dict[tuple[str, str], dict] = {}
        for en, ent in g.entities.items():
            for rn, r in ent.rules.items():
                self._compiled[(en, rn)] = {
                    "guard": E.parse_expr(r.guard) if r.guard else None,
                    "body": E.parse_body(r.body),
                    "post": E.parse_expr(r.contract.post) if r.contract.post else None,
                    "conserves": E.parse_expr(r.contract.conserves) if r.contract.conserves else None,
                    "emit": [(em.event,
                              E.parse_expr(em.when) if em.when else None,
                              {f: E.parse_expr(src) for f, src in em.fields.items()})
                             for em in r.emit],
                }
        self._invariants = {n: E.parse_expr(src) for n, src in g.invariants.items()}
        self._queries = {}
        self._query_params: dict[str, dict] = {}
        for n, q in g.queries.items():
            if isinstance(q, str):
                self._queries[n] = E.parse_expr(q)
            else:
                self._queries[n] = E.parse_expr(q["expr"])
                self._query_params[n] = dict(q.get("params", {}))
        self._replaying = False
        self._emit_hook = None   # ports: out-port observes emitted events (push)
        self._log_lines = 0
        self.snapshot_every = 0          # 0 = off; enabled by the CLI/exam
        if self.store.count() > 0:
            self.replay()

    # ------------------------------------------------------------- events

    def _dedup_check(self, ev_id: str) -> bool:
        """True = a duplicate within the window. Otherwise registers the id, advancing the window."""
        if ev_id in self._seen:
            return True
        self._seen.add(ev_id)
        self._seen_q.append(ev_id)
        while len(self._seen_q) > self.g.retry_window:
            self._seen.discard(self._seen_q.popleft())
        return False

    def handle(self, event: dict) -> dict:
        """event: {"id": str, "type": str, ...fields}. Returns the outcome."""
        ev_id, ev_type = event.get("id"), event.get("type")
        if not isinstance(ev_id, str) or not ev_id:
            return {"status": "error", "reason": "event requires non-empty str 'id'"}
        if ev_type not in self.g.events:
            return {"status": "error", "reason": f"unknown event type '{ev_type}'"}
        fields = {k: v for k, v in event.items() if k not in ("id", "type")}
        missing = [f for f in self.g.events[ev_type] if f not in fields]
        if missing:
            return {"status": "error", "reason": f"missing event fields: {missing}"}

        if not self._replaying:
            self._append_log(event)     # write-ahead: the log is the truth
            self._log_lines += 1
            if self.snapshot_every and self._log_lines % self.snapshot_every == 0:
                self.checkpoint()

        if self._dedup_check(ev_id):
            if not self._replaying:
                self.counters["dup"] += 1
            return {"status": "dup", "id": ev_id}

        outcomes = {}
        self._dispatch(ev_type, fields, ev_id, outcomes, depth=0)
        self._check_invariants(ev_id)
        if not self._replaying:
            self.counters["applied"] += 1
            # ν-bridge (VII.2/D78): empirical load — the frequencies of the types
            self.counters.setdefault("by_type", {})
            self.counters["by_type"][ev_type] = \
                self.counters["by_type"].get(ev_type, 0) + 1
        return {"status": "applied", "id": ev_id, "outcomes": outcomes}

    MAX_CASCADE = 8      # D54: cap on the depth of the policy cascade

    def _dispatch(self, ev_type: str, fields: dict, ev_id: str,
                  outcomes: dict, depth: int) -> None:
        """Fan-out of the event across rules + a SYNCHRONOUS cascade of emissions (D54).
        Derived events are neither logged nor deduped (they are deterministic)."""
        if depth > self.MAX_CASCADE:
            if not self._replaying:
                self.ledger.record("cascade_overflow",
                                   {"event": ev_id, "type": ev_type})
            outcomes[f"cascade:{ev_type}"] = "overflow"
            return
        for en, ent in self.g.entities.items():
            for rn, r in ent.rules.items():
                if r.when != ev_type:
                    continue
                key = f"{en}.{rn}" if depth == 0 else f"{en}.{rn}@d{depth}"
                outcomes[key] = self._fire(en, rn, fields, ev_id, outcomes, depth)

    def _fire(self, en: str, rn: str, ev: dict, ev_id: str,
              outcomes: dict | None = None, depth: int = 0) -> str:
        c = self._compiled[(en, rn)]
        inst = ev.get(self.g.key_field(en))
        states = self.state[en]
        if inst not in states:
            if self.g.entities[en].instances == "dynamic" and \
                    isinstance(inst, str) and inst:
                states[inst] = dict(self.g.entities[en].init)   # birth (D51)
            else:
                if not self._replaying:
                    self.counters["unknown_instance"] += 1
                return f"unknown-instance:{inst}"
        s = states[inst]
        try:
            if c["guard"] is not None and not E.eval_expr(c["guard"], {"s": s, "ev": ev}):
                if not self._replaying:
                    self.counters["noop"] += 1
                return "noop(guard)"
            new = E.exec_body(c["body"], s, ev)
            if c["post"] is not None and not E.eval_expr(c["post"], {"s": new}):
                self._violation("contract_post", en, rn, inst, ev_id)
                return "rejected(post)"
            if c["conserves"] is not None and \
               E.eval_expr(c["conserves"], {"s": s}) != E.eval_expr(c["conserves"], {"s": new}):
                self._violation("contract_conserves", en, rn, inst, ev_id)
                return "rejected(conserves)"
        except E.EvalError as e:
            self._violation("eval_error", en, rn, inst, ev_id, str(e))
            return f"rejected(eval: {e})"
        states[inst] = new
        if not self._replaying:
            self.heat[en] += 1       # heat is about live traffic, not replay
        # ---- policies (D54): emission of derived events from the POST-state
        for k, (ev_name, when_tree, field_trees) in enumerate(c["emit"]):
            env = {"s": new, "ev": ev}
            try:
                if when_tree is not None and not E.eval_expr(when_tree, env):
                    continue
                child = {f: E.eval_expr(t, env) for f, t in field_trees.items()}
            except E.EvalError as e:
                self._violation("emit_error", en, rn, inst, ev_id, str(e))
                continue
            if outcomes is not None:
                self._dispatch(ev_name, child, f"{ev_id}:p{k}", outcomes,
                               depth + 1)
                if self._emit_hook is not None and not self._replaying:
                    self._emit_hook(ev_name, dict(child), f"{ev_id}:p{k}")
        return "applied"

    def _violation(self, kind: str, en: str, rn: str, inst: str, ev_id: str, msg: str = "") -> None:
        if self._replaying:      # subtracting the organism's own actions (F6):
            return               # replay counts as neither effort nor trouble
        self.counters["rejected"] += 1
        if True:
            self.ledger.record(kind, {"entity": en, "rule": rn, "instance": inst,
                                      "event": ev_id, "msg": msg})

    def _check_invariants(self, ev_id: str) -> None:
        env = self.lists_env()
        for name, tree in self._invariants.items():
            if not E.eval_expr(tree, env):
                if self._replaying:
                    continue
                self.counters["invariant_violations"] += 1
                if True:
                    self.ledger.record("invariant_violation", {"invariant": name, "event": ev_id})

    # ------------------------------------------------------------- reads

    def lists_env(self) -> dict:
        return {en: list(insts.values()) for en, insts in self.state.items()}

    def query(self, name: str, params: dict | None = None):
        if name not in self._queries:
            raise KeyError(f"unknown query '{name}'; available: {sorted(self._queries)}")
        env = self.lists_env()
        want = self._query_params.get(name, {})
        if want:
            got = params or {}
            missing = [p for p in want if p not in got]
            if missing:
                raise KeyError(f"query '{name}' needs params {missing}")
            env["p"] = {p: (int(got[p]) if t == "int" else str(got[p]))
                        for p, t in want.items()}
        return E.eval_expr(self._queries[name], env)

    def list_instances(self, entity: str, filters: dict, limit: int,
                       offset: int) -> list[dict]:
        """U1: a generic selection of an entity's "rows": equality filter on
        fields, sort by key, pagination. Without growing the IR."""
        if entity not in self.state:
            raise KeyError(f"unknown entity '{entity}'")
        fields = self.g.entities[entity].state
        out = []
        for inst in sorted(self.state[entity]):
            row = self.state[entity][inst]
            ok = True
            for f, v in filters.items():
                if f not in fields:
                    raise KeyError(f"unknown field '{f}' of '{entity}'")
                want = int(v) if fields[f] == "int" else str(v)
                if row[f] != want:
                    ok = False
                    break
            if ok:
                out.append({"_key": inst, **row})
        return out[offset:offset + limit]

    def snapshot(self) -> dict:
        return {en: {i: dict(s) for i, s in insts.items()}
                for en, insts in self.state.items()}

    # ------------------------------------------------------- log and replay

    def _append_log(self, event: dict) -> None:
        self.store.append(event)

    def replay(self) -> int:
        """Regeneration from the log. CORRUPTION wave: a torn line (kill -9 in
        the middle of a write) is skipped and honestly recorded — the organism
        lives on; a snapshot (if valid by hash) trims the start down to a tail
        of O(snapshot_every)."""
        self._replaying = True
        n = torn = 0
        start_line = self._load_checkpoint()
        try:
            for ev in self.store.read_from(start_line):
                if ev is None:
                    torn += 1
                    continue
                self.handle(ev)
                n += 1
        finally:
            self._replaying = False
        self._emit_hook = None   # ports: out-port observes emitted events (push)
        self._log_lines = start_line + n + torn
        self.ledger.record("replay", {"events": n, "from_line": start_line,
                                      "torn_lines": torn})
        return n

    # ------------------------------------------------------- snapshots (CORRUPTION)

    def _state_hash(self) -> str:
        return hashlib.sha256(json.dumps(
            self.snapshot(), sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:16]

    def checkpoint(self) -> dict:
        """A fold cache with an attestation: state+seen+log-line counter+HASH.
        The log remains the truth; a corrupt snapshot is rejected by hash."""
        cp = {"log_lines": self._log_lines, "state": self.snapshot(),
              "seen_q": list(self._seen_q), "counters": dict(self.counters),
              "heat": dict(self.heat)}
        cp["hash"] = self._state_hash()
        (self.data / "checkpoint.json").write_text(
            json.dumps(cp, ensure_ascii=False), encoding="utf-8")
        return {"log_lines": cp["log_lines"], "hash": cp["hash"]}

    def _load_checkpoint(self) -> int:
        p = self.data / "checkpoint.json"
        if not p.exists():
            return 0
        try:
            cp = json.loads(p.read_text(encoding="utf-8"))
            for en, insts in cp["state"].items():
                for inst, st in insts.items():
                    self.state[en][inst] = dict(st)
            if self._state_hash() != cp["hash"]:
                raise ValueError("checkpoint hash mismatch")
            self._seen_q = deque(cp["seen_q"])
            self._seen = set(cp["seen_q"])
            self.counters.update(cp.get("counters", {}))
            self.heat.update(cp.get("heat", {}))
            return int(cp["log_lines"])
        except Exception as e:  # noqa: BLE001 — a corrupt snapshot = a full replay
            for en, ent in self.g.entities.items():
                # D80: FULL reset of the population: dynamic — empty (replay
                # will give birth again); static — exactly the listed ones
                # (ghost instances from a corrupt snapshot are buried, they do
                # not survive the reset)
                self.state[en] = ({} if ent.instances == "dynamic" else
                                  {inst: dict(ent.init)
                                   for inst in ent.instances})
            self._seen_q.clear()
            self._seen.clear()
            self.ledger.record("checkpoint_rejected",
                               {"why": f"{type(e).__name__}: {str(e)[:120]}"})
            return 0
