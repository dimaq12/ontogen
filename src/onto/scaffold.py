# -*- coding: utf-8 -*-
"""`onto init`: couple a project to the engine and the harness in one shot
(SHIP.md P2). Creates the onto-owned corner (.onto/ + genome/), pins the
engine, registers the MCP mouth for the harness, drops a CLAUDE.md fragment,
installs the workflow skill, and — the killer move — installs a PRE-EDIT
HOOK GUARD that turns invariant I4 ("the only write path is propose") into a
mechanical rail: the harness physically cannot hand-write a phenotype file.

Boundary is explicit (honest "any project"): onto OWNS genome/ + .onto/ +
materialized output; the rest of the repo is the human's. The hook enforces
that boundary, not a rule in someone's head.
"""
from __future__ import annotations

import json
import pathlib

from onto import __version__
from onto.core import ir

STARTER_GENOME = """# Your first genome. The genome is the source of truth; code is a proven,
# printed phenotype — you never hand-edit the phenotype (the hook guard
# blocks it). Change behavior by editing this file through `propose`, then
# `onto court` must stay ALL PROVED.
onto: 1
name: starter
retry_window: 64
events:
  Counted: {counter: str, by: int}
entities:
  counter:
    key: counter
    instances: dynamic
    state: {total: int}
    init: {total: 0}
    rules:
      count:
        when: Counted
        intent: add a positive amount to a counter
        guard: "ev.by > 0"
        body: |
          s.total = s.total + ev.by
        contract: {post: "s.total >= 0"}
queries:
  grand_total: "sum(c.total for c in counter)"
"""

STARTER_FLOWS = """# Acceptance flows (outside the genome): the judge runs them top-to-bottom
# on one organism. They are the executable spec of expected behavior.
flows:
  happy:
    - post:  {id: e1, type: Counted, counter: a, by: 5}
    - state: {entity: counter, instance: a, expect: {total: 5}}
    - post:  {id: e2, type: Counted, counter: a, by: 3}
    - state: {entity: counter, instance: a, expect: {total: 8}}
    - query: {name: grand_total, expect: 8}
  guard_rejects_nonpositive:
    - post:  {id: e3, type: Counted, counter: b, by: 0}
    - query: {name: grand_total, expect: 8}
"""

CLAUDE_FRAGMENT = """<!-- onto:begin (managed by `onto init`) -->
## This repo is onto-owned in its genome corner

In `genome/` you do NOT edit code and you do NOT edit the genome file by hand.
Behavior is defined by the **genome**; runnable code is a **proven, printed
phenotype**. The single write path is the `propose` MCP tool (it runs the
gates: checkers + SMT court + semantic diff). A red court returns a
counterexample — feed it back into the next `propose`. This is the loop:

    explain(target)  ->  propose(changes)  ->  court  ->  (red? counterexample -> propose)  ->  materialize

- Read with the `genome_read`, `validate`, `explain`, `court`, `ledger_tail` MCP tools.
- Never use Edit/Write on files under `genome/` or the materialized output —
  a hook blocks it and tells you to use `propose`.
- `onto attest` prints the guarantee passport (what is proven vs assumed).
<!-- onto:end -->
"""

SKILL_MD = """---
name: onto-workflow
description: How to change behavior in an onto-owned repo — propose into the genome, never hand-edit the phenotype.
---

# Working in an onto repo

The genome is the source of truth; code is printed and proven, never
hand-written. Follow this loop:

1. **Understand** — `explain(<entity>)` gives an O(k) slice: exactly what to
   read to change one entity/module, instead of the whole genome.
2. **Propose** — `propose({"path": "<new file content>"})` is THE ONLY WRITE
   PATH. It runs checkers + SMT court + semantic diff. Editing files under
   `genome/` directly is blocked by a hook — always go through `propose`.
3. **Prove** — a red court returns a concrete counterexample (inputs +
   divergence). Feed it into the next `propose`. Green = ALL PROVED.
4. **Materialize** — `onto materialize` prints the phenotype in the target
   dialect; `onto serve` runs the organism on the reference interpreter from
   second zero (no dialect toolchain needed).
5. **Attest** — `onto attest` prints the guarantee passport: what is proven,
   what is assumed (weakest seam named), what is monitored.

Intentional behavior changes that the contracts don't distinguish require
`ack_behavior_change: ["entity.rule"]` in the root genome; the gate quotes an
executable example of the divergence.
"""

HOOK_GUARD = '''#!/usr/bin/env python3
# onto edit-guard hook (installed by `onto init`). Turns invariant I4 into a
# mechanical rail: block direct Edit/Write to onto-owned files; the harness
# must use the `propose` MCP tool instead. Claude Code runs this on PreToolUse
# and reads the tool input as JSON on stdin; exit code 2 blocks the call and
# feeds stderr back to the model.
import fnmatch
import json
import os
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)                       # not our shape -> don't interfere

tool = data.get("tool_name", "")
if tool not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    sys.exit(0)

fp = (data.get("tool_input", {}) or {}).get("file_path", "")
if not fp:
    sys.exit(0)

root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
try:
    rel = os.path.relpath(fp, root)
except ValueError:
    rel = fp
rel = rel.replace(os.sep, "/")

owned_path = os.path.join(root, ".onto", "owned.json")
try:
    protected = json.load(open(owned_path)).get("protected", [])
except Exception:
    protected = ["genome/**"]

for pat in protected:
    if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.rstrip("/*") + "/*"):
        sys.stderr.write(
            f"BLOCKED by onto: '{rel}' is onto-owned (genome or materialized "
            f"phenotype). Do NOT hand-edit it. Change behavior through the "
            f"`propose` MCP tool (checkers + court + semantic diff); read with "
            f"`explain`/`genome_read`. This is invariant I4.\\n")
        sys.exit(2)
sys.exit(0)
'''


def _merge_json(path: pathlib.Path, patch: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cur = {}
    if path.exists():
        try:
            cur = json.loads(path.read_text())
        except Exception:
            cur = {}
    # deep-ish merge for known nesting
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(cur.get(k), dict):
            cur[k] = {**cur[k], **v}
        else:
            cur[k] = v
    path.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")


def init(root: str | pathlib.Path = ".", harness: str = "claude",
         force: bool = False, log=print) -> dict:
    root = pathlib.Path(root).resolve()
    made = []

    def w(rel, content, *, execu=False):
        p = root / rel
        if p.exists() and not force:
            made.append(f"kept {rel} (exists)")
            return p
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        if execu:
            p.chmod(0o755)
        made.append(f"wrote {rel}")
        return p

    # 1. onto-owned corner
    for d in ("cache", "ledger", "checkpoints", "hooks"):
        (root / ".onto" / d).mkdir(parents=True, exist_ok=True)
    # 2. engine pin
    w(".onto/engine.pin", json.dumps(
        {"version": __version__,
         "ir_fingerprint": ir.FROZEN_V1_FINGERPRINT}) + "\n")
    # 3. provider config example (real key goes in .onto/config.toml, gitignored)
    w(".onto/config.toml.example",
      '# Register OpenAI-compatible providers; ref models as "provider:model"\n'
      '# or bare (-> default). Known names auto-get a base_url preset.\n'
      '[default]\nprovider = "openrouter"\n\n'
      '[provider.openrouter]\napi_key = "${OPENROUTER_API_KEY}"  # or @keyfile\n\n'
      '# [provider.local]\n# base_url = "http://localhost:11434/v1"\n'
      '# api_key = "ollama"\n\n'
      '[ladders]\nskills = ["qwen/qwen3-coder", "qwen/qwen3-coder-plus"]\n'
      'nl = ["anthropic/claude-sonnet-4.5", "anthropic/claude-opus-4.6"]\n')
    # 4. starter genome (+ schema modeline: free IDE via yaml-language-server)
    import json as _json
    from onto.core.genome import Genome as _G
    (root / ".onto" / "genome.schema.json").write_text(
        _json.dumps(_G.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    made.append("wrote .onto/genome.schema.json (free IDE via yaml-language-server)")
    modeline = "# yaml-language-server: $schema=../.onto/genome.schema.json\n"
    w("genome/genome.yaml", modeline + STARTER_GENOME)
    w("genome/flows.yaml", STARTER_FLOWS)
    # 5. ownership manifest (drives the hook)
    w(".onto/owned.json", json.dumps(
        {"protected": ["genome/**"],
         "note": "onto materialize --out DIR appends DIR here"}, indent=2) + "\n")
    # 6. gitignore for secrets/live state
    gi = root / ".gitignore"
    marker = "# onto (managed)"
    lines = gi.read_text().splitlines() if gi.exists() else []
    if marker not in lines:
        lines += [marker, ".onto/config.toml", ".onto/ledger/",
                  ".onto/checkpoints/", ".onto/cache/"]
        gi.write_text("\n".join(lines) + "\n", encoding="utf-8")
        made.append("updated .gitignore")

    # ---- harness batteries ----
    if harness == "claude":
        # 7. MCP registration — Claude Code reads .mcp.json at repo root
        _merge_json(root / ".mcp.json", {"mcpServers": {"onto": {
            "command": "onto", "args": ["mcp", "genome/genome.yaml"]}}})
        made.append("registered MCP server (.mcp.json)")
        # 8. hook guard script + settings
        w(".onto/hooks/guard_edit.py", HOOK_GUARD, execu=True)
        _merge_json(root / ".claude" / "settings.json", {"hooks": {
            "PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit",
                            "hooks": [{"type": "command",
                                       "command": "python3 .onto/hooks/guard_edit.py"}]}]}})
        made.append("installed edit-guard hook (.claude/settings.json)")
        # 9. workflow skill
        w(".claude/skills/onto-workflow/SKILL.md", SKILL_MD)
        # 10. CLAUDE.md fragment (append, marker-guarded)
        cm = root / "CLAUDE.md"
        body = cm.read_text() if cm.exists() else ""
        if "onto:begin" not in body:
            cm.write_text((body.rstrip() + "\n\n" if body else "") +
                          CLAUDE_FRAGMENT, encoding="utf-8")
            made.append("added CLAUDE.md fragment")
        else:
            made.append("kept CLAUDE.md fragment (present)")

    return {"root": str(root), "harness": harness, "actions": made}
