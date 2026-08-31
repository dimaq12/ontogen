# -*- coding: utf-8 -*-
"""EXAM gene-pool + free IDE (D85): three moves that dissolve seccomp/LSP into
the doctrine instead of paying eternal tails.
Move 1: a gene distributes as CONTRACT ONLY — bodies never travel, they
regrow locally; a gene with toothless properties can't be certified (court
teeth-gate) — the anti-prompt-injection primitive.
Move 3: frozen IR = free IDE — `onto schema` (JSON Schema from pydantic) +
modeline gives autocomplete via any yaml-language-server; `onto watch` gives
live Expr diagnostics. Zero tail."""
import json
import subprocess
import sys
import pathlib
import tempfile
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G, skills as SK

    # ---- Move 1: gene is BODY-FREE by construction
    sk_fields = set(SK.Skill.model_fields)
    R.append(("gene is CONTRACT-ONLY: Skill has no 'body' field (bodies "
              f"regrow locally): {sorted(sk_fields)}",
              "body" not in sk_fields
              and {"params", "returns", "properties", "intent"} <= sk_fields))

    # ---- Move 1: teeth-gate — toothed gene passes court, toothless fails
    ce = subprocess.run([str(PY), "-m", "onto.cli", "court",
                         str(ROOT / "genomes/exchange.yaml")],
                        cwd=ROOT, capture_output=True, text=True)
    R.append(("toothed gene: court green + 'properties have teeth'",
              ce.returncode == 0 and "have teeth" in ce.stdout))
    # forge a toothless variant (property a lazy `return []` survives)
    raw = yaml.safe_load((ROOT / "genomes/exchange.yaml").read_text())
    for sname, sk in raw["skills"].items():
        sk["properties"] = ["all(t.qty >= 0 for t in out)"]  # lazy [] satisfies
    tp = pathlib.Path(tempfile.mkdtemp()) / "toothless.yaml"
    tp.write_text(yaml.safe_dump(raw, allow_unicode=True))
    ct = subprocess.run([str(PY), "-m", "onto.cli", "court", str(tp)],
                        cwd=ROOT, capture_output=True, text=True)
    R.append(("toothless gene: court REJECTS (can't be distributed/installed)",
              ct.returncode != 0 and "TOOTHLESS" in ct.stdout))

    # ---- Move 3: onto schema = valid JSON Schema from the frozen IR
    sp = pathlib.Path(tempfile.mkdtemp()) / "genome.schema.json"
    subprocess.run([str(PY), "-m", "onto.cli", "schema", "--out", str(sp)],
                   cwd=ROOT, capture_output=True, text=True)
    sch = json.loads(sp.read_text())
    R.append(("onto schema: valid JSON Schema derived from pydantic (zero tail)",
              sch.get("type") == "object" and "properties" in sch
              and "entities" in sch["properties"]))

    # ---- Move 3: onto init writes schema + modeline (free IDE on scaffold)
    proj = pathlib.Path(tempfile.mkdtemp(prefix="gene-init-"))
    subprocess.run([str(PY), "-m", "onto.cli", "init", str(proj)],
                   cwd=ROOT, capture_output=True, text=True)
    gtext = (proj / "genome/genome.yaml").read_text()
    R.append(("onto init: schema file + modeline in genome (IDE works on "
              "scaffold)", (proj / ".onto/genome.schema.json").exists()
              and "yaml-language-server: $schema=" in gtext))

    # ---- Move 3: onto watch live-validates (terminal, no LSP)
    proc = subprocess.Popen([str(PY), "-m", "onto.cli", "watch",
                             str(proj / "genome/genome.yaml"),
                             "--interval", "0.2"],
                            cwd=ROOT, stdout=subprocess.PIPE, text=True)
    time.sleep(1.0)
    proc.terminate()
    out = proc.stdout.read()
    R.append(("onto watch: live validation prints OK for a valid genome",
              "OK" in out and "starter" in out))

    print(f"\n=== EXAM gene-pool + free IDE ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
