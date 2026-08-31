# -*- coding: utf-8 -*-
"""Growing the dialect GENERATOR (pearl 5, step 2; D68).

growdialect (step 1) translates the phenotype PER-GENOME — it scales by model
calls. Here the model writes the EMITTER ITSELF: a python module with
  def emit(genome: dict) -> str        # the full organism.js for ANY genome
Homology: the template is our own printing emitter for python-stdlib
(skeleton.py) + a ready js phenotype from growdialect as a sample target.

The gate is a MULTI-GENOME CEGIS: the emitter is certified on a SET of genomes;
for each: emit -> node --check -> the same judge -> parity with the canon ->
kill -9/replay (we reuse growdialect.gates). The counterexample names the
genome. A green generator means new genomes are printed WITHOUT the model."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import tempfile
import time
import urllib.request

from onto import growdialect
from onto.ribosome import Provider, strip_code

ATTEMPTS_PER_MODEL = 4


def _http(base, path):
    with urllib.request.urlopen(base + path, timeout=10) as r:
        return json.loads(r.read())


def canon_snapshot(genome_path, flows_path, root, port) -> dict:
    """Run the judge against the INTERPRETER (the canon) and take a state snapshot."""
    py = root / ".venv" / "bin" / "python"
    data = tempfile.mkdtemp(prefix="gencanon-")
    proc = subprocess.Popen([str(py), "-m", "onto.cli", "serve",
                             str(genome_path), "--port", str(port),
                             "--data", data], cwd=root,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                _http(base, "/health")
                break
            except Exception:
                time.sleep(0.05)
        judge = subprocess.run([str(py), "-m", "onto.cli", "judge",
                                str(flows_path), base],
                               cwd=root, capture_output=True, text=True)
        if judge.returncode != 0:
            raise RuntimeError(f"canon judge red for {genome_path}: "
                               f"{judge.stdout[-400:]}")
        from onto.core import genome as G
        g = G.load(genome_path)
        snap = {}
        for en in g.entities:
            insts = _http(base, f"/instances/{en}")["instances"]
            snap[en] = {i: _http(base, f"/state/{en}/{i}") for i in insts}
        return snap
    finally:
        proc.kill()


def gen_prompt(ref_skeleton: str, sample_js: str,
               counterexamples: list[str]) -> str:
    cx = ("\nYour previous attempts FAILED these machine checks — fix "
          "exactly these:\n" + "\n".join(counterexamples)) if counterexamples else ""
    return f"""You write ONE Python module: a CODE GENERATOR that turns ANY genome (a dict)
into a complete Node.js server source. It must define exactly:

    def emit(genome: dict) -> str      # returns full organism.js text

The genome dict has: name, retry_window, events {{Type: {{field: "int"|"str"}}}},
entities {{name: {{key, instances: list|"dynamic", state {{field: type}},
init {{field: literal}}, rules {{rname: {{when, guard?, body, contract, emit: []}}}}}}}},
queries {{qname: "python-expr" | {{params, expr}}}}.

guard/body/post are a tiny Python subset: ints, strs, s.field, ev.field,
+ - * // %, comparisons, and/or/not, min(), max(). body is lines of
"s.field = <expr>". Global queries are "AGG(expr for v in entity if cond)"
with AGG in sum/len (len may be written len([...]) or with a generator).
You must TRANSLATE these expressions to JavaScript (s.field -> s.field etc;
// -> Math.floor(a/b); use parentheses liberally). Skip dict-valued queries
(params) — emit no /q route for them.

The generated organism.js must (stdlib only: http, fs, path):
- CLI: node organism.js --port <p> --data <dir>
- POST /event {{"id","type",...fields}}: unknown type -> {{"status":"error",...}}
  (HTTP 422); dup id within RETRY_WINDOW most recent ids -> {{"status":"dup","id"}};
  else append the event AS RECEIVED as one JSON line to <data>/events.jsonl
  (create dir; write BEFORE applying), apply matching rules, respond
  {{"status":"applied","id":..,"outcomes":{{"entity.rule":"applied"|"guarded"}}}}.
- Routing: a rule of entity E applies to the instance named by the event's
  value of E's key field (default key field name = entity name). Static
  instances: only listed ones exist (event for others -> outcome omitted).
  instances == "dynamic": instance is BORN on first event carrying its key,
  initialized from init/defaults (missing init -> 0 for int, "" for str).
- guard false -> outcome "guarded", state untouched. No guard -> apply.
- GET /state/<entity>/<inst> -> state JSON (404 if absent);
  GET /q/<name> -> {{"value": <int>}}; GET /health -> {{"ok":true}}.
- On startup: replay events.jsonl (tolerate a torn last line) applying the
  same logic WITHOUT re-appending; maintain the same dedup window.
- Integer arithmetic exactly like Python for // on ints (floor division).

Here is OUR OWN generator for the python dialect — copy its STRUCTURE
(iterate entities/events/rules, print code) but target JavaScript:
```python
{ref_skeleton}
```

And here is a hand-certified organism.js previously grown for one specific
genome — copy its RUNTIME SHAPE (server, log, dedup, replay):
```js
{sample_js}
```
{cx}
Output ONLY the complete Python module in one ```python fence. It is long —
make sure you FINISH it (no truncation)."""


def sanitize(code: str) -> str | None:
    try:
        compile(code, "<emitgen>", "exec")
    except SyntaxError as e:
        return f"- generator syntax error: {e}"
    if not re.search(r"^def emit\(", code, re.M):
        return "- must define top-level 'def emit(genome):'"
    return None


def certify(code: str, certs: list[tuple], out: pathlib.Path, root,
            base_port: int, snaps: dict) -> str | None:
    """Run the emitter across ALL certification genomes. None = green."""
    verdict = sanitize(code)
    if verdict:
        return verdict
    ns: dict = {}
    try:
        exec(compile(code, "<emitgen>", "exec"), ns)  # noqa: S102 — the gate is the judge
    except Exception as e:  # noqa: BLE001
        return f"- generator import failed: {type(e).__name__}: {e}"
    fn = ns["emit"]
    py = root / ".venv" / "bin" / "python"
    from onto.core import genome as G
    for k, (gp, fp) in enumerate(certs):
        g = G.load(gp)
        gname = g.name
        try:
            js_text = fn(g.model_dump())
        except Exception as e:  # noqa: BLE001
            return f"- [{gname}] emit() raised: {type(e).__name__}: {e}"
        if not isinstance(js_text, str) or len(js_text) < 200:
            return f"- [{gname}] emit() returned non-code ({type(js_text).__name__})"
        js = out / f"organism_{gname}.js"
        js.write_text(js_text, encoding="utf-8")
        bad = growdialect.gates(js, gp, fp, base_port + k, snaps[str(gp)],
                                py, root)
        if bad:
            return f"- [{gname}] {bad}"
    return None


def grow(certs: list[tuple], out_dir, provider: Provider, root,
         base_port: int = 8781, ladder: list[str] | None = None,
         log=print) -> dict:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    root = pathlib.Path(root)
    ref = (root / "src/onto/dialects/python_stdlib/skeleton.py").read_text(
        encoding="utf-8")
    sample = root / "build/rooms_ideal/node/organism.js"
    sample_js = sample.read_text(encoding="utf-8") if sample.exists() else ""
    snaps = {str(gp): canon_snapshot(gp, fp, root, base_port + 40 + i)
             for i, (gp, fp) in enumerate(certs)}
    ladder = ladder or (provider.skills_ladder + ["anthropic/claude-sonnet-4.5"])
    spec = ref + json.dumps([str(p) for p, _ in certs]) + "node-gen"
    key = hashlib.sha256(spec.encode()).hexdigest()[:16]
    tele: dict = {"island": False, "attempts": []}

    for model in ladder:
        ck = out / f"emitgen.{key}.{model.replace('/', '_')}.py"
        cxs: list[str] = []
        if ck.exists():
            code = ck.read_text(encoding="utf-8")
            if certify(code, certs, out, root, base_port, snaps) is None:
                (out / "emitgen.py").write_text(code, encoding="utf-8")
                log(f"  growgen: CACHE hit [{model}]")
                tele["model"], tele["cache"] = model, True
                return tele
        for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            raw = provider.generate(model, gen_prompt(ref, sample_js, cxs),
                                    seed=42,
                                    tag=f"growgen:node:{model}:{attempt}",
                                    max_tokens=16000)
            code = strip_code(raw)
            verdict = certify(code, certs, out, root, base_port, snaps)
            tele["attempts"].append({"model": model, "attempt": attempt,
                                     "verdict": (verdict or "GREEN")[:200]})
            if verdict is None:
                ck.write_text(code, encoding="utf-8")
                (out / "emitgen.py").write_text(code, encoding="utf-8")
                log(f"  growgen: GREEN [{model}] attempt {attempt} — "
                    f"generator certified on {len(certs)} genomes")
                tele["model"], tele["cache"] = model, False
                return tele
            cxs.append(verdict)
            log(f"  growgen: red [{model}] attempt {attempt}: {verdict[:150]}")
        log(f"  growgen: ladder step exhausted [{model}] -> escalate")
    tele["island"] = True
    return tele
