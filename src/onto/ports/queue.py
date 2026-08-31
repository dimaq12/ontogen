# -*- coding: utf-8 -*-
"""Queue port (D88): the ASYNC beast — genuinely asynchronous, dependency-free
(in-process Bus stands in for Kafka/MQTT; a real broker is a grown adapter
with the same send/subscribe interface).

- direction 'in':  a consumer subscribes to a topic; each message is decoded
  into a canonical event and fed to the fold. Async by construction.
- direction 'out': observes the organism's EMITTED events (push, D54); matching
  types are encoded and SENT with RETRIES (backoff). Delivery health is a
  membrane: repeated failure -> drift -> REVOKE (cert_valid=False) in the ledger.
"""
from __future__ import annotations

import time

from onto.ports.base import Port, register


@register("queue")
class QueuePort(Port):
    def __init__(self, cfg, org, bus, lock):
        super().__init__(cfg, org, bus, lock)
        self.topic = cfg.get("topic") or cfg.get("to") or f"{self.name}"
        self.on = cfg.get("on", ["*"])            # event types to publish (out)
        self.retries = int(cfg.get("retries", 3))
        self.backoff = float(cfg.get("backoff", 0.02))
        self.quota = int(cfg.get("quota", 5))     # failures before REVOKE
        self._fail_streak = 0
        # the beast driver: send(msg) may raise (broker down). Default = bus.
        self._send = lambda msg: self.bus.publish(self.topic, msg)
        # D89: a GROWN codec (decode/encode) can be plugged in by path.
        self._codec = None
        if cfg.get("codec"):
            import pathlib as _pl
            ns: dict = {}
            exec(compile(_pl.Path(cfg["codec"]).read_text(), "<codec>", "exec"), ns)  # noqa: S102
            self._codec = ns

    # ---- decode/encode: canonical event <-> wire message (identity for the
    # in-process bus; a real beast overrides these with its serialization) ----
    def decode(self, msg: dict) -> dict:
        return self._codec["decode"](msg) if self._codec else msg

    def encode(self, ev_name: str, fields: dict, ev_id: str) -> dict:
        if self._codec:
            return self._codec["encode"](ev_name, fields, ev_id)
        return {"id": ev_id, "type": ev_name, **fields}

    def start(self) -> None:
        if self.direction in ("in", "both"):
            self.bus.subscribe(self.topic, self._on_message)
        if self.direction in ("out", "both"):
            self._install_out_hook()

    def _on_message(self, msg: dict) -> None:
        try:
            event = self.decode(msg)
        except Exception:  # noqa: BLE001
            self.stats["failed"] += 1
            return
        self.deliver(event)                       # into the fold (locked)

    def _install_out_hook(self):
        prev = self.org._emit_hook

        def hook(ev_name, fields, ev_id):
            if prev is not None:
                prev(ev_name, fields, ev_id)      # chain multiple out-ports
            if self.on != ["*"] and ev_name not in self.on:
                return
            self._deliver_out(self.encode(ev_name, fields, ev_id))
        self.org._emit_hook = hook

    def _deliver_out(self, msg: dict) -> None:
        """SEND with retries; delivery is a membrane (drift -> REVOKE)."""
        for attempt in range(self.retries + 1):
            try:
                self._send(msg)
                self.stats["delivered"] += 1
                self._fail_streak = 0
                return
            except Exception:  # noqa: BLE001 — the beast is flaky
                self.stats["retries"] += 1
                if attempt < self.retries:
                    time.sleep(self.backoff * (attempt + 1))
        # all attempts failed
        self.stats["failed"] += 1
        self._fail_streak += 1
        if self._fail_streak > self.quota and self.cert_valid:
            self.org.ledger.record("port_trust_revoked", {
                "port": self.name, "port_kind": "queue",
                "why": f"{self._fail_streak} delivery failures > quota "
                       f"{self.quota}", "stats": dict(self.stats)})
            self.cert_valid = False

    def passport(self) -> dict:
        return {"cert_valid": self.cert_valid, **self.stats}
