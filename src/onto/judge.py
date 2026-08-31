# -*- coding: utf-8 -*-
"""The judge is an external black box (NOT §8: scenarios live OUTSIDE the genome).
The same one for the interpreter, for any dialects (F3), and for any comparison arms.

Format of the flows file (YAML):
flows:
  <name>:
    - post:  {id: e1, type: BookingRequested, room: room101, ...}
    - state: {entity: room, instance: room101, expect: {booked: 1}}
    - query: {name: total_booked, expect: 1}
"""
from __future__ import annotations

import json
import urllib.request


def _http(url: str, payload: dict | None = None) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def run_flow(base: str, steps: list[dict]) -> list[str]:
    """Returns a list of failures (empty = the flow is green)."""
    fails: list[str] = []
    for i, step in enumerate(steps):
        if "post" in step:
            out = _http(base + "/event", step["post"])
            if out.get("status") not in ("applied", "dup"):
                fails.append(f"step {i}: post -> {out}")
        elif "state" in step:
            sp = step["state"]
            from urllib.parse import quote
            got = _http(f"{base}/state/{quote(str(sp['entity']))}/"
                        f"{quote(str(sp['instance']))}")
            for k, v in sp["expect"].items():
                if got.get(k) != v:
                    fails.append(f"step {i}: {sp['entity']}/{sp['instance']}.{k} = "
                                 f"{got.get(k)}, expected {v}")
        elif "query" in step:
            qp = step["query"]
            got = _http(f"{base}/q/{qp['name']}")
            if got.get("value") != qp["expect"]:
                fails.append(f"step {i}: q/{qp['name']} = {got.get('value')}, "
                             f"expected {qp['expect']}")
        else:
            fails.append(f"step {i}: unknown step {sorted(step)}")
    return fails


def main(argv: list[str]) -> int:
    import sys
    import yaml
    if len(argv) < 2:
        print("usage: onto judge <flows.yaml> <base_url>", file=sys.stderr)
        return 2
    flows = yaml.safe_load(open(argv[0], encoding="utf-8"))["flows"]
    base = argv[1].rstrip("/")
    green = 0
    for name, steps in flows.items():
        fails = run_flow(base, steps)
        ok = not fails
        green += ok
        print(f"flow {name}: {'GREEN' if ok else 'RED'}")
        for f in fails:
            print("  " + f)
    print(f"judge: {green}/{len(flows)} green")
    return 0 if green == len(flows) else 1
