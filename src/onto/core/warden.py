# -*- coding: utf-8 -*-
"""Warden — the supervision daemon (F6): watch the genome -> checkers/
conservativity -> molt (log migration by functor + restart, downtime in
seconds) -> monitors (quotas -> REVOKE rights) -> Placer loop (F5) with a
rights ladder.

Rights: observational — proposals to the ledger only; interventional —
auto-execution of the Placer's molt proposals. A REVOKE on the violation
quota demotes interventional -> observational in the same tick. The lifecycle
is driven by ticks (the exam/CLI call tick*) — determinism."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

from onto.core import genome as G
from onto.core import ir, migrate
from onto.core.organism import Ledger
from onto.theory.provenance import V, declared, measured


class Warden:
    def __init__(self, root_path, data_dir, port: int,
                 rights: str = "observational",
                 quota_inv_violations: V | None = None):
        self.root_path = pathlib.Path(root_path)
        self.data = pathlib.Path(data_dir)
        self.data.mkdir(parents=True, exist_ok=True)
        self.port = port
        self.rights = rights
        self.quota = quota_inv_violations or declared(3.0, "operator: quota/window")
        self.ledger = Ledger(self.data / "warden.jsonl")
        self.proc: subprocess.Popen | None = None
        self.genome: G.Genome | None = None
        self._hash = ""
        self._last_inv = 0
        self._warm: set[str] = set()
        self.svc_procs: list[subprocess.Popen] = []

    # ------------------------------------------------------------ process

    def _hash_tree(self) -> str:
        """Hash of the root + all imported modules (F4 composition)."""
        h = hashlib.sha256(self.root_path.read_bytes())
        raw = ir.load(self.root_path)
        for rel in raw.get("imports", []):
            mp = (self.root_path.parent / rel).resolve()
            if mp.exists():
                h.update(mp.read_bytes())
        return h.hexdigest()

    def _http(self, path: str):
        with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}{path}", timeout=5) as r:
            return json.loads(r.read())

    def _wait_up(self, timeout_s: float = 10.0) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            try:
                self._http("/health")
                return True
            except Exception:
                time.sleep(0.05)
        return False

    def start(self) -> None:
        self.genome = G.load(self.root_path)
        self._hash = self._hash_tree()
        py = sys.executable
        self.proc = subprocess.Popen(
            [py, "-m", "onto.cli", "serve", str(self.root_path),
             "--data", str(self.data), "--port", str(self.port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        assert self._wait_up(), "organism did not start"
        self.ledger.record("start", {"genome": self.genome.name,
                                     "rights": self.rights})

    def stop(self) -> None:
        if self.proc:
            self.proc.kill()
            self.proc.wait()
            self.proc = None
        for p in self.svc_procs:
            p.kill()

    # -------------------------------------------------------------- molt

    def tick_watch(self) -> dict:
        """Did the genome change? checkers -> (functor?) -> molt with restart."""
        h = self._hash_tree()
        if h == self._hash:
            return {"status": "unchanged"}
        try:
            new_g = G.load(self.root_path)
        except G.GenomeError as e:
            self.ledger.record("reject_mutation", {"reasons": e.errors[:10]})
            self._hash = h          # don't twitch on the same broken file
            return {"status": "rejected", "reasons": e.errors}
        except Exception as e:      # broken YAML etc.: the organism LIVES on
            reasons = [f"{type(e).__name__}: {str(e)[:200]}"]
            self.ledger.record("reject_mutation", {"reasons": reasons})
            self._hash = h
            return {"status": "rejected", "reasons": reasons}

        raw_root = ir.load(self.root_path)
        # UNIFIED mutation gates (mutgate): conservativity + COURT + semdiff —
        # the same as propose (one judgment path, two mouths)
        from onto.core import mutgate
        reasons = mutgate.judge_mutation(self.genome, new_g, raw_root)
        if reasons:
            self.ledger.record("reject_mutation", {"reasons": reasons[:10]})
            self._hash = h
            return {"status": "rejected", "reasons": reasons}
        breaking = migrate.diff_genomes(self.genome, new_g)
        fx = migrate.Migrations.model_validate(raw_root.get("migrations", {}))

        t0 = time.time()
        self.stop()
        stats = {}
        if breaking:
            stats = migrate.migrate_log(fx, self.data,
                                        f"v{int(time.time()) % 100000}")
            if fx.drop_events:                    # D74: loss is visible
                self.ledger.record('declared_loss', {
                    'events': fx.drop_events,
                    'declarations': fx.declared_loss,
                    'dropped': stats.get('dropped', 0)})
        self.genome = new_g
        self._hash = h
        py = sys.executable
        self.proc = subprocess.Popen(
            [py, "-m", "onto.cli", "serve", str(self.root_path),
             "--data", str(self.data), "--port", str(self.port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        up = self._wait_up()
        downtime = time.time() - t0
        self.ledger.record("molt", {"breaking": breaking, "migration": stats,
                                    "downtime_s": round(downtime, 2)})
        return {"status": "molted", "breaking": breaking,
                "migration": stats, "downtime_s": downtime, "up": up}

    # ------------------------------------------------------------- timers

    def tick_timers(self, now_s: float) -> list[str]:
        """U2 (D59): genome schedules -> events. The Warden is the time source
        (the organism is deterministic and has no clock). id = timer:<name>:<epoch>
        — dedup makes the tick idempotent across a warden restart."""
        fired = []
        if not hasattr(self, "_timer_last"):
            self._timer_last: dict[str, int] = {}
        for tn, t in (self.genome.timers or {}).items():
            epoch = int(now_s // t["every_s"])
            if self._timer_last.get(tn) == epoch:
                continue
            self._timer_last[tn] = epoch
            base = {"type": t["event"], **t.get("fields", {})}
            targets = [None]
            if t.get("per"):
                targets = self._instances(t["per"])   # live instances (/instances)
            for tgt in targets:
                ev = dict(base)
                ev["id"] = f"timer:{tn}:{epoch}" + (f":{tgt}" if tgt else "")
                if tgt is not None:
                    ev[self.genome.key_field(t["per"])] = tgt
                try:
                    import json as _json
                    import urllib.request as _rq
                    req = _rq.Request(
                        f"http://127.0.0.1:{self.port}/event",
                        data=_json.dumps(ev).encode(),
                        headers={"Content-Type": "application/json"})
                    _rq.urlopen(req, timeout=10)
                    fired.append(ev["id"])
                except Exception:  # noqa: BLE001 — organism restarting etc.
                    pass
        if fired:
            self.ledger.record("timer_fired", {"events": fired[:20],
                                               "count": len(fired)})
        return fired

    def _instances(self, entity: str) -> list[str]:
        try:
            snap = self._http(f"/instances/{entity}")
            return snap.get("instances", [])
        except Exception:  # noqa: BLE001
            return []

    # ------------------------------------------------------------ monitors

    def tick_spectral(self, window: int = 150) -> dict:
        """Spectral audit (Part VII §2.5): sliding windows of observables; the
        threshold is calibrated from the FIRST (healthy) window — not by hand.
        Verdicts spectral_drift / variance_freeze -> ledger. All conditional
        on ν."""
        from onto.core import genome as G
        from onto.core import spectral as SP
        if not hasattr(self, "_spec_buf"):
            self._spec_buf, self._spec_cal = [], None
            self._spec_g = G.load(self.root_path)
        g = self._spec_g
        x = []
        try:
            for en in sorted(g.entities):
                ent = g.entities[en]
                insts = self._http(f"/instances/{en}")["instances"]
                if ent.instances == "dynamic":
                    x.append(len(insts))
                else:
                    for inst in insts:
                        st = self._http(f"/state/{en}/{inst}")
                        for f in sorted(ent.state):
                            if ent.state[f] == "int":
                                x.append(st[f])
        except Exception:  # noqa: BLE001 — organism busy: skip the tick
            return {"skipped": True}
        self._spec_buf.append(x)
        try:                                    # ν-bridge (VII.2): load snapshot
            bt = self._http("/health")["counters"].get("by_type", {})
        except Exception:  # noqa: BLE001
            bt = {}
        if not hasattr(self, "_nu_hist"):
            self._nu_hist = []
        self._nu_hist.append(dict(bt))
        out = {"points": len(self._spec_buf), "verdicts": []}

        def _nu_window(a, b):
            """Empirical ν over [a,b): the delta of type counters."""
            first = self._nu_hist[a] if a < len(self._nu_hist) else {}
            last = self._nu_hist[min(b, len(self._nu_hist)) - 1]
            d = {t: last.get(t, 0) - first.get(t, 0) for t in last}
            tot = sum(v for v in d.values() if v > 0)
            return {t: v / tot for t, v in d.items() if v > 0} if tot else {}

        if self._spec_cal is None and len(self._spec_buf) >= window:
            self._spec_cal = SP.calibrate(self._spec_buf[:window])
            nu_ref = _nu_window(0, window)
            self._spec_cal["nu"] = nu_ref
            # ν-drift threshold — FROM the spread of the healthy window's
            # sub-windows (not by hand)
            def _tv(a, b):
                ks = set(a) | set(b)
                return 0.5 * sum(abs(a.get(t, 0.0) - b.get(t, 0.0)) for t in ks)
            halves = [_nu_window(0, window // 2),
                      _nu_window(window // 2, window)]
            self._spec_cal["nu_tol"] = round(
                max(0.05, 3 * max(_tv(h, nu_ref) for h in halves)), 3)
            mk = SP.markov_test(self._spec_buf[:window])
            self.ledger.record("spectral_calibrated",
                               {**self._spec_cal, "markov": mk})
            out["calibrated"] = self._spec_cal
        elif (self._spec_cal is not None
              and len(self._spec_buf) % (window // 2) == 0):
            # ν-drift: TV(ν̂_window, ν_certificate) — the certificate is
            # CONDITIONAL on ν; a load shift is declared BEFORE the thresholds
            # go stale silently
            nu_now = _nu_window(len(self._nu_hist) - window, len(self._nu_hist))
            nu_ref = self._spec_cal.get("nu", {})
            if nu_ref and nu_now:
                keys = set(nu_ref) | set(nu_now)
                tv = 0.5 * sum(abs(nu_ref.get(t, 0.0) - nu_now.get(t, 0.0))
                               for t in keys)
                if tv > self._spec_cal.get("nu_tol", 0.15):
                    self.ledger.record("nu_drift", {
                        "tv": round(tv, 3), "nu_certified": nu_ref,
                        "nu_now": nu_now,
                        "hint": "spectral certificate is conditional on nu "
                                "(VII.2) — recalibrate"})
            verdicts = SP.audit(self._spec_buf[-window:], self._spec_cal)
            for v in verdicts:
                kind = v.pop("kind")
                self.ledger.record(kind, v)
                # #8 (D83): the spectral organ gets HANDS — a verdict is a
                # decision, not a note (NOT S3: a formula must act or it is
                # decoration). Corruption -> demote to observational + propose
                # recalibration; the loop stops trusting a drifted model.
                if self.rights == "interventional":
                    self.rights = "observational"
                    self.ledger.record("revoke", {
                        "why": f"spectral {kind} {v}",
                        "rights": "interventional -> observational"})
                self.ledger.record("recalibrate_proposal", {
                    "why": kind, "detail": v,
                    "action": "restart warden to open a fresh healthy "
                              "calibration window"})
            out["verdicts"] = verdicts
        return out

    def tick_assumptions(self) -> dict:
        """U12 (D74): declared holes of ignorance (assumptions.yaml next to the
        genome) — watch-Expr over live populations; a hit in the
        underdetermination region = a ledger record (visible, measurable,
        revocable)."""
        import yaml
        from onto.core import expr as E
        ap = pathlib.Path(self.root_path).parent / "assumptions.yaml"
        out = {"checked": 0, "hits": []}
        if not ap.exists():
            return out
        doc = yaml.safe_load(ap.read_text()) or {}
        for name, a in (doc.get("assumptions") or {}).items():
            if a.get("status") != "declared":
                continue
            out["checked"] += 1
            env = {}
            try:
                for en in self._entities():
                    insts = self._http(f"/instances/{en}")["instances"]
                    env[en] = [self._http(f"/state/{en}/{i}") for i in insts]
                hit = bool(E.eval_expr(E.parse_expr(a["watch"]), env))
            except Exception:  # noqa: BLE001 — organism busy: skip the tick
                continue
            if hit:
                out["hits"].append(name)
                self.ledger.record("assumption_hit", {
                    "assumption": name, "rule": f"{a['entity']}.{a['rule']}",
                    "watch": a["watch"],
                    "question": a.get("question", "")[:200]})
        return out

    def _entities(self):
        from onto.core import genome as G
        return list(G.load(self.root_path).entities)

    def tick_monitors(self) -> dict:
        """Quota of invariant violations in the window -> REVOKE (rights
        demotion)."""
        health = self._http("/health")
        inv = health["counters"]["invariant_violations"]
        delta = inv - self._last_inv
        self._last_inv = inv
        if delta > self.quota.value:
            old_rights = self.rights
            self.rights = "observational"
            self.ledger.record("revoke", {
                "why": f"invariant violations {delta} > quota "
                       f"{self.quota.value:g} [{self.quota.cls}] in window",
                "rights": f"{old_rights} -> {self.rights}"})
            return {"status": "revoked", "delta": delta}
        return {"status": "ok", "delta": delta}

    # ------------------------------------------------------- placer loop

    def tick_placer(self, dt_s: float, heat_before: dict, heat_after: dict,
                    t_cold_ns: V, t_warm_ns: V) -> dict:
        from onto.core import placer
        rates = {en: measured((heat_after[en] - heat_before[en]) / dt_s,
                              f"heat:{self.genome.name}")
                 for en in heat_after}
        plan = placer.tick(rates, t_cold_ns=t_cold_ns, t_warm_ns=t_warm_ns,
                           warm_set=self._warm)
        executed = []
        for p in plan.proposals:
            self.ledger.record(p["kind"], p)
            if p["kind"] == "molt_proposal" and self.rights == "interventional":
                executed.append(self._execute_molt(p["entity"]))
        return {"plan": plan, "executed": executed}

    def _execute_molt(self, entity: str) -> dict:
        """Auto-extraction of a gene (interventional rights): split ->
        materialization -> service start. The dialect comes from the registry
        (the first certified one)."""
        from onto.core import placer
        svc_root = placer.split_hot_root(
            self.root_path, [entity], self.data / f"{entity}_svc.yaml")
        py = sys.executable
        out = self.data / f"{entity}_svc_build"
        m = subprocess.run([py, "-m", "onto.cli", "materialize", str(svc_root),
                            "--dialect", "go-stdlib", "--out", str(out)],
                           capture_output=True, text=True)
        svc_port = self.port + 100
        proc = subprocess.Popen([str(out / "organism"), "--port", str(svc_port),
                                 "--data", str(self.data / f"{entity}_svc_data")],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.svc_procs.append(proc)
        self._warm.add(entity)
        self.ledger.record("molt_executed", {
            "entity": entity, "svc_root": str(svc_root), "port": svc_port,
            "rights": self.rights, "build_ok": m.returncode == 0})
        return {"entity": entity, "port": svc_port, "build_ok": m.returncode == 0}
