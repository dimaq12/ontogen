# -*- coding: utf-8 -*-
"""EXAM 'onto init' (SHIP.md P2): one-shot coupling of a fresh project to the
engine + harness. Verifies: scaffold created, engine pinned, MCP registered,
CLAUDE.md fragment + skill installed, and — the killer move — the edit-guard
HOOK actually BLOCKS a direct Edit to an onto-owned file while letting a
non-owned file through. Then court on the starter genome is GREEN, and
materialize registers its output as protected."""
import json
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def main():
    t0 = time.time()
    proj = pathlib.Path(tempfile.mkdtemp(prefix="onto-init-"))

    # 1. onto init in a fresh dir
    out = subprocess.run([str(PY), "-m", "onto.cli", "init", str(proj)],
                         cwd=ROOT, capture_output=True, text=True)
    R.append(("onto init runs clean", out.returncode == 0))

    # 2. scaffold present
    must = [".onto/engine.pin", ".onto/owned.json", ".onto/hooks/guard_edit.py",
            "genome/genome.yaml", "genome/flows.yaml", ".mcp.json",
            ".claude/settings.json", ".claude/skills/onto-workflow/SKILL.md",
            "CLAUDE.md"]
    missing = [m for m in must if not (proj / m).exists()]
    R.append((f"scaffold complete ({len(must)-len(missing)}/{len(must)})",
              not missing))

    # 3. engine pinned to this build
    pin = json.loads((proj / ".onto/engine.pin").read_text())
    from onto import __version__
    from onto.core import ir
    R.append(("engine pinned (version + IR fingerprint)",
              pin["version"] == __version__
              and pin["ir_fingerprint"] == ir.FROZEN_V1_FINGERPRINT))

    # 4. MCP registered for the harness
    mcp = json.loads((proj / ".mcp.json").read_text())
    R.append(("MCP server registered (onto mcp genome/genome.yaml)",
              mcp["mcpServers"]["onto"]["command"] == "onto"
              and mcp["mcpServers"]["onto"]["args"] == ["mcp", "genome/genome.yaml"]))

    # 5. hook registered in settings
    st = json.loads((proj / ".claude/settings.json").read_text())
    pre = st["hooks"]["PreToolUse"][0]
    R.append(("edit-guard hook registered (PreToolUse Edit|Write)",
              "Edit" in pre["matcher"] and "guard_edit.py" in pre["hooks"][0]["command"]))

    # 6. HOOK BLOCKS a direct edit to an onto-owned file (genome/)
    def run_hook(file_path, tool="Edit"):
        payload = json.dumps({"tool_name": tool,
                              "tool_input": {"file_path": file_path}})
        return subprocess.run(
            [str(PY), str(proj / ".onto/hooks/guard_edit.py")],
            input=payload, capture_output=True, text=True,
            env={"CLAUDE_PROJECT_DIR": str(proj), "PATH": "/usr/bin:/bin"})

    blocked = run_hook(str(proj / "genome/genome.yaml"))
    R.append((f"hook BLOCKS direct edit of genome (exit {blocked.returncode}, "
              f"says propose)", blocked.returncode == 2
              and "propose" in blocked.stderr))
    # 7. hook ALLOWS a non-owned file (human's code)
    allowed = run_hook(str(proj / "src/app.py"))
    R.append(("hook ALLOWS edit of non-owned file (human's corner)",
              allowed.returncode == 0))

    # 8. court on the starter genome is GREEN
    court = subprocess.run([str(PY), "-m", "onto.cli", "court",
                            str(proj / "genome/genome.yaml")],
                           cwd=ROOT, capture_output=True, text=True)
    R.append(("starter genome: court ALL PROVED (entity-inductive)",
              court.returncode == 0 and "ENTITY-INDUCTIVE" in court.stdout))

    # 9. materialize registers its output as protected, then hook blocks it
    mout = proj / "build_py"
    subprocess.run([str(PY), "-m", "onto.cli", "materialize",
                    str(proj / "genome/genome.yaml"), "--dialect",
                    "python-stdlib", "--out", str(mout)],
                   cwd=proj, capture_output=True, text=True)
    man = json.loads((proj / ".onto/owned.json").read_text())
    prot = any("build_py" in p for p in man["protected"])
    blocked2 = run_hook(str(mout / "organism.py"))
    R.append(("materialized phenotype auto-protected + hook blocks its edit",
              prot and blocked2.returncode == 2))

    print(f"\n=== EXAM onto init ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
