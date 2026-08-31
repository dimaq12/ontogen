# -*- coding: utf-8 -*-
"""Ports (D88): transport is a FUNCTOR on the I/O boundary, not part of the
brain (I1: the core knows no transports, just as it knows no languages).

One law generates every beast — HTTP, a queue, gRPC, Kafka, sync or async:

    the FOLD is the invariant; a port is a (decode, encode, driver) triple
    that must PRESERVE it. Certificate = fold-parity (the same gate that
    certifies dialects/migrations) + round-trip(encode∘decode).

Two observation channels, both already in the organism:
  - PULL  (state/query)         -> sync ports (HTTP/gRPC request-response)
  - PUSH  (emitted events, D54) -> async ports (queue/Kafka/MQTT)

Because the fold is the single source of truth, ONE organism exposes MANY
ports at once — each is a projection of the same fold, so they are mutually
consistent BY CONSTRUCTION. Untrusted delivery (drop/reorder/at-least-once)
is the membrane doctrine applied to the port: assumptions over delivery
stats -> drift -> REVOKE; duplicates are already neutralised by retry_window.

Ports are DECLARED next to the genome (ports.yaml), never in the frozen IR —
transport is a surface, not semantics.
"""
from __future__ import annotations

import queue as _queue
import threading
import time

PORT_KINDS: dict = {}


def register(kind: str):
    def deco(cls):
        PORT_KINDS[kind] = cls
        return cls
    return deco


class Bus:
    """A dependency-free in-process message broker (stands in for Kafka/MQTT
    in tests; a real broker is a grown adapter with the same interface).
    Topics -> subscriber callbacks; publish is asynchronous (a worker thread
    per subscriber), so async ports are genuinely async."""

    def __init__(self):
        self._subs: dict[str, list] = {}
        self._threads: list = []
        self._alive = True

    def subscribe(self, topic: str, fn) -> None:
        q: _queue.Queue = _queue.Queue()
        self._subs.setdefault(topic, []).append(q)

        def worker():
            while self._alive:
                try:
                    msg = q.get(timeout=0.1)
                except _queue.Empty:
                    continue
                try:
                    fn(msg)
                except Exception:  # noqa: BLE001 — a bad consumer never kills the bus
                    pass
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        self._threads.append(t)
        # attach the queue so publish can find it
        self._subs[topic][-1] = (q, fn)

    def publish(self, topic: str, msg) -> None:
        for q, _fn in self._subs.get(topic, []):
            q.put(msg)

    def stop(self) -> None:
        self._alive = False


class Port:
    """A transport binding over ONE organism. Kinds implement start()/stop()."""

    def __init__(self, cfg: dict, org, bus: Bus, lock):
        self.cfg = cfg
        self.name = cfg.get("name", cfg.get("kind"))
        self.org = org
        self.bus = bus
        self.lock = lock
        self.direction = cfg.get("direction", "in")
        # membrane stats for this port (delivery health)
        self.stats = {"delivered": 0, "failed": 0, "retries": 0}
        self.cert_valid = True

    def start(self) -> None:                      # pragma: no cover - abstract
        raise NotImplementedError

    def stop(self) -> None:
        pass

    # --- the organism-driving helpers every in-port shares (the fold) ---
    def deliver(self, event: dict) -> dict:
        """decode already done: feed a canonical event into the fold."""
        with self.lock:
            return self.org.handle(event)


def load_ports(path) -> list:
    import pathlib
    import yaml
    p = pathlib.Path(path)
    if not p.exists():
        return []
    doc = yaml.safe_load(p.read_text()) or {}
    return doc.get("ports", [])


def start_ports(org, ports_cfg: list, bus: Bus, lock) -> list:
    started = []
    for cfg in ports_cfg:
        kind = cfg["kind"]
        if kind not in PORT_KINDS:
            raise ValueError(f"unknown port kind '{kind}' "
                             f"(have: {sorted(PORT_KINDS)})")
        port = PORT_KINDS[kind](cfg, org, bus, lock)
        port.start()
        started.append(port)
    return started


def fold_parity(genome_path, flows_path, drive_a, drive_b, root) -> str | None:
    """THE PORT LAW-GATE (D88): drive the SAME genome+flows through two
    different port drivers; the fold (state snapshot after flows) MUST be
    byte-identical. None = certified; else a counterexample string.
    drive_x(events) -> the organism's full state dict after applying them."""
    import yaml
    flows = yaml.safe_load(open(flows_path))["flows"]
    events = []
    for _fname, steps in flows.items():
        for st in steps:
            if "post" in st:
                events.append(st["post"])
    fold_a = drive_a(events)
    fold_b = drive_b(events)
    if fold_a != fold_b:
        # find first divergence for a useful counterexample
        for en in sorted(set(fold_a) | set(fold_b)):
            if fold_a.get(en) != fold_b.get(en):
                return (f"fold parity BROKEN at entity '{en}': "
                        f"portA={fold_a.get(en)} portB={fold_b.get(en)}")
        return "fold parity BROKEN (structural)"
    return None
