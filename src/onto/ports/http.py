# -*- coding: utf-8 -*-
"""HTTP ports (D88): the REFERENCE sync/pull beast (request-response) and the
'web' async-out beast WITH RETRIES.

- direction 'in': reuses the reference HTTP runtime (serve.make_server) —
  POST /event, GET /state,/q (pull observation). This IS the canonical port;
  every other beast is certified fold-equal (structural snapshot equality
  after decode, not raw bytes) to its fold.
- direction 'out': on an emitted event -> POST to a URL with retries+backoff
  (generalises U6 webhooks into a first-class, membrane-monitored out-port).
"""
from __future__ import annotations

import json
import threading
import time
import urllib.request

from onto.ports.base import Port, register


@register("http")
class HttpPort(Port):
    def __init__(self, cfg, org, bus, lock):
        super().__init__(cfg, org, bus, lock)
        self.bind = cfg.get("bind", "127.0.0.1:8090")
        self.url = cfg.get("to")                  # out: target URL
        self.on = cfg.get("on", ["*"])
        self.retries = int(cfg.get("retries", 3))
        self.backoff = float(cfg.get("backoff", 0.05))
        self.quota = int(cfg.get("quota", 5))
        self._fail_streak = 0
        self._srv = None

    def start(self) -> None:
        if self.direction in ("in", "both"):
            self._start_in()
        if self.direction in ("out", "both"):
            self._install_out_hook()

    def _start_in(self) -> None:
        from onto.core.serve import make_server
        host, _, port = self.bind.partition(":")
        skills = self.cfg.get("skills_cache")
        base = self.cfg.get("genome_base")
        self._srv = make_server(self.org, host=host or "127.0.0.1",
                                port=int(port or 8090),
                                skills_cache=skills, genome_base=base)
        threading.Thread(target=self._srv.serve_forever, daemon=True).start()

    def _install_out_hook(self) -> None:
        prev = self.org._emit_hook

        def hook(ev_name, fields, ev_id):
            if prev is not None:
                prev(ev_name, fields, ev_id)
            if self.on != ["*"] and ev_name not in self.on:
                return
            self._deliver_out({"id": ev_id, "type": ev_name, **fields})
        self.org._emit_hook = hook

    def _deliver_out(self, msg: dict) -> None:
        if not self.cert_valid:              # D95: REVOKE actually gates delivery
            self.stats["dropped_revoked"] = self.stats.get("dropped_revoked", 0) + 1
            return                           # stop hammering a sink we no longer trust
        for attempt in range(self.retries + 1):
            try:
                req = urllib.request.Request(
                    self.url, data=json.dumps(msg).encode(),
                    headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
                self.stats["delivered"] += 1
                self._fail_streak = 0
                return
            except Exception:  # noqa: BLE001
                self.stats["retries"] += 1
                if attempt < self.retries:
                    time.sleep(self.backoff * (attempt + 1))
        self.stats["failed"] += 1
        self._fail_streak += 1
        if self._fail_streak > self.quota and self.cert_valid:
            self.org.ledger.record("port_trust_revoked", {
                "port": self.name, "port_kind": "http", "url": self.url,
                "why": f"{self._fail_streak} POST failures > quota {self.quota}"})
            self.cert_valid = False

    def stop(self) -> None:
        if self._srv is not None:
            self._srv.shutdown()

    def passport(self) -> dict:
        return {"cert_valid": self.cert_valid, **self.stats}
