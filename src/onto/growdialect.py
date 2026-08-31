# -*- coding: utf-8 -*-
"""Growing a dialect (IDEAL §3, pearl 5): a new language WITHOUT touching the core.

v0 form: an SLM translates the CANONICAL phenotype (python-stdlib, the canon
language) into the target language per-genome. The oracle is the canonical
organism; the gates:
  1) syntax (node --check);
  2) THE SAME judge (flows) against the live process;
  3) parity: the state snapshot after flows == the canonical one;
  4) kill -9 -> replay from the log (the same events.jsonl format).
CEGIS: gate failures (which flow, which step, what it answered) go into the prompt.
Cache keyed by hash (genome+reference+language+model) — determinism through
certification, not through the model's own determinism (as with skills). An
island outcome is legal.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import time
import urllib.request

from onto.ribosome import Provider, strip_code

ATTEMPTS_PER_MODEL = 4


def _http(base, path, payload=None, timeout=10):
    req = urllib.request.Request(base + path,
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def grow_prompt(genome_yaml: str, ref_py: str, flows_yaml: str,
                counterexamples: list[str]) -> str:
    cx = ("\nYour previous attempts FAILED these machine checks — fix "
          "exactly these:\n" + "\n".join(counterexamples)) if counterexamples else ""
    return f"""You translate a reference server into Node.js (stdlib only: http, fs).
Write ONE complete file organism.js. No npm deps, no comments needed.

The GENOME (source of truth for semantics):
```yaml
{genome_yaml}
```

The REFERENCE implementation (Python; your Node.js server must behave
byte-for-byte identically at the HTTP level and produce the same states):
```python
{ref_py}
```

Requirements:
- CLI: node organism.js --port <p> --data <dir>
- Endpoints exactly as the reference: POST /event, GET /state/<entity>/<key>,
  GET /q/<name>, GET /health (same JSON field names and value types).
- Event log: append each accepted event as one JSON line to
  <data>/events.jsonl (create dir), replay it on startup (same dedup window
  semantics as the reference: RETRY_WINDOW most recent ids).
- Dynamic entities are born on first event with their key (copy the
  reference init defaults).
- Integer arithmetic only where the reference uses ints.

These acceptance flows will be run by an external judge (each post's effects
then checked via /state and /q):
```yaml
{flows_yaml}
```
{cx}
The file is long — make sure you FINISH it (no truncation).\nOutput ONLY the complete Node.js code in one ```js fence."""


def gates(js_path: pathlib.Path, genome_path: pathlib.Path,
          flows_path: pathlib.Path, port: int, canon_snapshot: dict,
          py: pathlib.Path, root: pathlib.Path) -> str | None:
    """None = green, otherwise a counterexample string for CEGIS."""
    chk = subprocess.run(["node", "--check", str(js_path)],
                         capture_output=True, text=True)
    if chk.returncode != 0:
        return f"- node --check failed: {chk.stderr.strip()[:300]}"
    import tempfile
    data = tempfile.mkdtemp(prefix="grow-js-")
    proc = subprocess.Popen(["node", str(js_path), "--port", str(port),
                             "--data", data],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"
    try:
        up = False
        for _ in range(60):
            try:
                _http(base, "/health", timeout=2)
                up = True
                break
            except Exception:
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
        if not up:
            err = (proc.stderr.read() or b"").decode()[:300] if proc.poll() is not None else "no /health"
            return f"- server did not start: {err}"
        judge = subprocess.run(
            [str(py), "-m", "onto.cli", "judge", str(flows_path), base],
            cwd=root, capture_output=True, text=True)
        if judge.returncode != 0:
            red = [l for l in judge.stdout.splitlines() if "RED" in l or "step" in l]
            return "- judge failed:\n" + "\n".join("  " + l for l in red[:6])
        # parity of the folds against the canon
        for en, insts in canon_snapshot.items():
            for inst, want in insts.items():
                got = _http(base, f"/state/{en}/{inst}")
                if got != want:
                    return (f"- state parity: /state/{en}/{inst} -> "
                            f"{json.dumps(got)} but canon has {json.dumps(want)}")
        # kill -9 -> replay
        import os
        import signal
        os.kill(proc.pid, signal.SIGKILL)
        proc.wait()
        proc2 = subprocess.Popen(["node", str(js_path), "--port", str(port),
                                  "--data", data],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        try:
            up = False
            for _ in range(60):
                try:
                    _http(base, "/health", timeout=2)
                    up = True
                    break
                except Exception:
                    time.sleep(0.1)
            if not up:
                return "- after kill -9 restart: server did not come back"
            for en, insts in canon_snapshot.items():
                for inst, want in insts.items():
                    got = _http(base, f"/state/{en}/{inst}")
                    if got != want:
                        return (f"- replay after kill -9 diverged: "
                                f"/state/{en}/{inst} -> {json.dumps(got)}, "
                                f"expected {json.dumps(want)}")
        finally:
            proc2.kill()
    finally:
        if proc.poll() is None:
            proc.kill()
    return None


def grow(genome_path, flows_path, out_dir, provider: Provider,
         canon_snapshot: dict, ref_py_path, root, port: int = 8721,
         log=print) -> dict:
    genome_yaml = pathlib.Path(genome_path).read_text(encoding="utf-8")
    flows_yaml = pathlib.Path(flows_path).read_text(encoding="utf-8")
    ref_py = pathlib.Path(ref_py_path).read_text(encoding="utf-8")
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    py = root / ".venv" / "bin" / "python"
    tele: dict = {"island": False, "attempts": []}
    key = hashlib.sha256((genome_yaml + ref_py + "node").encode()).hexdigest()[:16]

    for model in provider.ladder("dialect"):
        ck = out / f"organism.{key}.{model.replace('/', '_')}.js"
        cxs: list[str] = []
        if ck.exists():
            js = out / "organism.js"
            js.write_text(ck.read_text(encoding="utf-8"), encoding="utf-8")
            if gates(js, genome_path, flows_path, port, canon_snapshot,
                     py, root) is None:
                log(f"  grow: CACHE hit [{model}]")
                tele["model"], tele["cache"] = model, True
                return tele
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            raw = provider.generate(model,
                                    grow_prompt(genome_yaml, ref_py,
                                                flows_yaml, cxs),
                                    seed=42, tag=f"grow:node:{model}:{attempt}",
                                    max_tokens=12000)
            code = strip_code(raw)
            js = out / "organism.js"
            js.write_text(code, encoding="utf-8")
            verdict = gates(js, genome_path, flows_path, port,
                            canon_snapshot, py, root)
            tele["attempts"].append({"model": model, "attempt": attempt,
                                     "verdict": (verdict or "GREEN")[:160]})
            if verdict is None:
                ck.write_text(code, encoding="utf-8")
                log(f"  grow: GREEN [{model}] attempt {attempt}")
                tele["model"], tele["cache"] = model, False
                return tele
            cxs.append(verdict)
            log(f"  grow: red [{model}] attempt {attempt}: {verdict[:120]}")
        log(f"  grow: ladder step exhausted [{model}] -> escalate")
    tele["island"] = True
    return tele
