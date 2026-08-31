# -*- coding: utf-8 -*-
"""onto's MCP mouth (the v0 EPIC §4 trust ladder, in the v1 world):

READ:  genome_read, validate, court, explain, ledger_tail
WRITE: propose — the ONLY write path (mutgate: checkers+court+semdiff)
The organism is run by the warden (a file watch picks up an accepted propose).

Run: onto mcp <root.yaml>   (stdio; for Claude Code: claude mcp add)."""
from __future__ import annotations

import json
import pathlib

_ROOT: pathlib.Path | None = None


def build_server(root_path: str | pathlib.Path):
    from mcp.server.mcpserver import MCPServer      # mcp==2.0 API (as in v0)

    global _ROOT
    _ROOT = pathlib.Path(root_path).resolve()
    mcp = MCPServer("onto")

    @mcp.tool(description="Read the root genome and its imported modules "
                          "(the ONLY source code of the system).")
    def genome_read() -> dict:
        from onto.core import ir
        out = {_ROOT.name: _ROOT.read_text(encoding="utf-8")}
        for rel in ir.load(_ROOT).get("imports", []):
            p = (_ROOT.parent / rel).resolve()
            out[rel] = p.read_text(encoding="utf-8")
        return out

    @mcp.tool(description="Validate the genome (typecheck all Expr/bodies).")
    def validate() -> dict:
        from onto.core import genome as G
        try:
            g = G.load(_ROOT)
            return {"ok": True, "entities": sorted(g.entities),
                    "rules": sum(len(e.rules) for e in g.entities.values())}
        except G.GenomeError as e:
            return {"ok": False, "reasons": e.errors}

    @mcp.tool(description="Prove contracts of every rule (SMT court) and "
                          "report mutant calibration.")
    def court() -> dict:
        from onto.core import court as C, genome as G
        g = G.load(_ROOT)
        out = {}
        for en, ent in g.entities.items():
            for rn, r in ent.rules.items():
                vs = C.prove_rule(dict(ent.state), dict(g.events[r.when]),
                                  r.guard, r.body, r.contract.post,
                                  r.contract.conserves)
                out[f"{en}.{rn}"] = {k: v.status for k, v in vs.items()}
        return out

    @mcp.tool(description="O(k) slice: what to read to change one entity/"
                          "module — instead of the whole genome.")
    def explain(target: str) -> str:
        from onto.core import modules
        return modules.explain(_ROOT, target)

    @mcp.tool(description="THE ONLY WRITE PATH: propose file changes "
                          "(rel_path -> new content). Gates: checkers + SMT "
                          "court + semantic-diff interview. Rejected with "
                          "reasons, or applied with .bak backups.")
    def propose(changes: dict[str, str]) -> dict:
        from onto.core.propose import propose as run
        return run(_ROOT, changes)

    @mcp.tool(description="Tail of the warden/organism ledger (JSONL).")
    def ledger_tail(data_dir: str, n: int = 10) -> list[dict]:
        out = []
        for name in ("warden.jsonl", "ledger.jsonl"):
            p = pathlib.Path(data_dir) / name
            if p.exists():
                lines = p.read_text(encoding="utf-8").splitlines()
                out += [json.loads(l) for l in lines[-n:] if l.strip()]
        return out[-n:]

    return mcp


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: onto mcp <root.yaml>")
        return 2
    build_server(argv[0]).run()          # stdio
    return 0
