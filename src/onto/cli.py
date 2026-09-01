# -*- coding: utf-8 -*-
"""CLI `onto` (D22). Commands: version | lint | fix | serve | judge |
conformance | validate | materialize | harden | attest | court | replay |
explain | new | init | models | schema | watch | mcp | growisland | warden |
unit | help."""
from __future__ import annotations

import pathlib
import sys

from onto import __version__
from onto.core import ir
from onto import lint as lint_mod


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    cmd = args[0] if args else "help"
    if cmd == "version":
        print(f"onto {__version__} (hub v{ir.HUB_VERSION})")
        return 0
    if cmd == "lint":
        return lint_mod.main(args[1:])
    if cmd == "serve":
        import argparse
        ap = argparse.ArgumentParser(prog="onto serve")
        ap.add_argument("genome"); ap.add_argument("--data", default="./data")
        ap.add_argument("--port", type=int, default=8090)
        ap.add_argument("--skills-cache", default="")
        ap.add_argument("--snapshot-every", type=int, default=0)
        ap.add_argument("--store", default=None, choices=["jsonl", "sqlite"])
        ap.add_argument("--ports", default="",
                        help="ports.yaml — declare transports (D88); "
                             "default is a single HTTP port")
        ns = ap.parse_args(args[1:])
        from onto.core import genome as genome_mod
        from onto.core.organism import Organism
        from onto.core.serve import make_server
        try:
            g = genome_mod.load(ns.genome)
        except genome_mod.GenomeError as e:
            print(str(e), file=sys.stderr)
            return 2
        org = Organism(g, ns.data, store=ns.store)
        org.snapshot_every = ns.snapshot_every
        pin_p = pathlib.Path(ns.genome).parent / "engine.pin"   # D74
        if pin_p.exists():
            import json as _json
            pin = _json.loads(pin_p.read_text())
            from onto.core import ir as ir_mod
            if (pin.get("version") != __version__
                    or pin.get("ir_fingerprint") != ir_mod.FROZEN_V1_FINGERPRINT):
                org.ledger.record("engine_pin_mismatch", {
                    "pinned": pin, "running": __version__,
                    "hint": "engine upgrade must be a MOLT: rerun all gates, "
                            "then update engine.pin (D74)"})
                print(f"WARNING: engine {__version__} != pinned "
                      f"{pin.get('version')} — upgrade is a molt, not a "
                      f"silent merge (ledger: engine_pin_mismatch)",
                      file=sys.stderr)
        import threading as _th
        import time as _time
        base = str(pathlib.Path(ns.genome).parent)
        if ns.ports:
            # D88: many transports over ONE fold, each a projection.
            from onto.ports import http as _hp  # noqa: F401 - register kinds
            from onto.ports import queue as _qp  # noqa: F401
            from onto.ports.base import Bus, load_ports, start_ports
            cfg = load_ports(ns.ports)
            for c in cfg:                       # inject shared runtime config
                if c.get("kind") == "http" and c.get("direction", "in") in ("in", "both"):
                    c.setdefault("genome_base", base)
                    c.setdefault("skills_cache", ns.skills_cache or None)
            bus = Bus()
            lock = _th.Lock()
            try:
                ports = start_ports(org, cfg, bus, lock)
            except ValueError as e:
                print(str(e), file=sys.stderr)
                return 2
            print(f"onto serve: genome '{g.name}' with {len(ports)} port(s): "
                  + ", ".join(f"{p.name}[{p.cfg['kind']}/{p.direction}]"
                              for p in ports))
            try:
                while True:
                    _time.sleep(1)
            except KeyboardInterrupt:
                for p in ports:
                    p.stop()
                bus.stop()
            return 0
        srv = make_server(org, port=ns.port,
                          skills_cache=ns.skills_cache or None,
                          genome_base=base)
        print(f"onto serve: genome '{g.name}' (reference interpreter) on :{ns.port}, data={ns.data}")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        return 0
    if cmd == "judge":
        from onto import judge as judge_mod
        return judge_mod.main(args[1:])
    if cmd == "conformance":
        from onto.core import conformance as conf
        sub = args[1] if len(args) > 1 else "check"
        path = args[2] if len(args) > 2 else "exams/conformance_expr.jsonl"
        if sub == "gen":
            corpus = conf.gen_corpus()
            conf.write_corpus(path, corpus)
            print(f"conformance: wrote {len(corpus)} cases -> {path}")
            return 0
        fails = conf.check_corpus(path)
        for f in fails[:20]:
            print(f, file=sys.stderr)
        print(f"conformance: {'PASS' if not fails else f'{len(fails)} FAIL'}")
        return 0 if not fails else 1
    if cmd == "validate":
        from onto.core import genome as genome_mod
        try:
            g = genome_mod.load(args[1])
        except genome_mod.GenomeError as e:
            print(str(e), file=sys.stderr)
            return 2
        nrules = sum(len(e.rules) for e in g.entities.values())
        print(f"genome '{g.name}': OK ({len(g.entities)} entities, {nrules} rules, "
              f"{len(g.invariants)} invariants, {len(g.queries)} queries)")
        return 0
    if cmd == "materialize":
        import argparse
        ap = argparse.ArgumentParser(prog="onto materialize")
        ap.add_argument("genome"); ap.add_argument("--dialect", default="go-stdlib")
        ap.add_argument("--out", default="")
        ap.add_argument("--skills-cache", default="")   # U7: printing bodies (python)
        ap.add_argument("--ports", default="")          # D97: transport spec (ports.yaml)
        ap.add_argument("--channel", default="")        # D97: sugar for a single in-driver
        ns = ap.parse_args(args[1:])
        from onto.core import genome as genome_mod
        from onto.dialects import registry
        try:
            d = registry.get(ns.dialect)
        except KeyError as e:
            print(e.args[0], file=sys.stderr)
            return 2
        try:
            g = genome_mod.load(ns.genome)
        except genome_mod.GenomeError as e:
            print(str(e), file=sys.stderr)
            return 2
        outdir = pathlib.Path(ns.out) if ns.out else pathlib.Path("build") / g.name
        # D97: the transport spec selects the door (functor). ports.yaml, or the
        # --channel sugar for a single in-driver; None -> the dialect's default.
        channels = None
        if ns.ports:
            import yaml as _yaml
            channels = (_yaml.safe_load(open(ns.ports)) or {}).get("channels")
        elif ns.channel:
            channels = [{"driver": ns.channel, "direction": "in", "codec": "json"}]
        import inspect as _inspect
        _gen = d["skeleton"].generate
        if channels is not None and "channels" in _inspect.signature(_gen).parameters:
            _gen(g, outdir, skills_cache=ns.skills_cache or None, channels=channels)
        else:
            if channels is not None:
                print(f"note: dialect '{ns.dialect}' has no channel axis yet — "
                      f"using its default door", file=sys.stderr)
            _gen(g, outdir, skills_cache=ns.skills_cache or None)
        ok, msg = d["gates"].build(outdir)
        owned = pathlib.Path(".onto/owned.json")            # P2: protect phenotype
        if owned.exists():
            import json as _json
            man = _json.loads(owned.read_text())
            import os as _os
            rel = _os.path.relpath(str(outdir), ".").replace(_os.sep, "/")
            glob = rel.rstrip("/") + "/**"
            if glob not in man.get("protected", []):
                man.setdefault("protected", []).append(glob)
                owned.write_text(_json.dumps(man, indent=2) + "\n")
        print(f"materialize[{ns.dialect}]: {outdir} -> build {'OK' if ok else 'FAIL: ' + msg}")
        return 0 if ok else 1
    if cmd == "harden":
        import argparse
        import json as _json
        ap = argparse.ArgumentParser(prog="onto harden")
        ap.add_argument("genome"); ap.add_argument("--skill", required=True)
        ap.add_argument("--case", required=True, help="JSON of the escape input")
        ap.add_argument("--expect", required=True,
                        help="JSON of the correct output (incident oracle)")
        ap.add_argument("--data", default="", help="organism data (ledger)")
        ns = ap.parse_args(args[1:])
        gp = pathlib.Path(ns.genome)
        rd = gp.parent / "regressions"
        rd.mkdir(exist_ok=True)
        rec = {"case": _json.loads(ns.case), "expect": _json.loads(ns.expect)}
        with (rd / f"{ns.skill}.jsonl").open("a", encoding="utf-8") as f:
            f.write(_json.dumps(rec, ensure_ascii=False) + "\n")
        if ns.data:
            from onto.core.organism import Ledger
            Ledger(pathlib.Path(ns.data) / "ledger.jsonl").record(
                "escape", {"skill": ns.skill, "case": rec["case"],
                           "hardened_into": str(rd / f"{ns.skill}.jsonl")})
        print(f"harden: escape of skill '{ns.skill}' -> regression corpus "
              f"{rd / (ns.skill + '.jsonl')} (bodies that fail the corpus "
              f"lose their certificate)")
        return 0
    if cmd == "certify":
        import argparse
        ap = argparse.ArgumentParser(prog="onto certify")
        ap.add_argument("genome"); ap.add_argument("--skills-cache", default="")
        ns = ap.parse_args(args[1:])
        from onto import certify as _ct
        rows = _ct.coverage(ns.genome, ns.skills_cache or None)
        print(_ct.render(rows))
        return 0 if _ct.is_green(rows) else 1
    if cmd == "attest":
        import argparse
        ap = argparse.ArgumentParser(prog="onto attest")
        ap.add_argument("genome"); ap.add_argument("--skills-cache", default="")
        ap.add_argument("--out", default="")
        ns = ap.parse_args(args[1:])
        from onto import attest as AT
        try:
            a = AT.build_attest(ns.genome, ns.skills_cache or None)
        except Exception as e:
            print(str(e), file=sys.stderr)
            return 2
        md = AT.render_md(a)
        print(md, end="")
        out = pathlib.Path(ns.out) if ns.out else pathlib.Path(ns.genome).parent
        (out / "attest.json").write_text(
            __import__("json").dumps(a, ensure_ascii=False, indent=1),
            encoding="utf-8")
        (out / "attest.md").write_text(md, encoding="utf-8")
        return 1 if a["proved"]["obligations_failed"] else 0
    if cmd == "court":
        from onto.core import court, genome as genome_mod, mutants
        try:
            g = genome_mod.load(args[1])
        except genome_mod.GenomeError as e:
            print(str(e), file=sys.stderr)
            return 2
        bad = 0
        for en, ent in g.entities.items():
            rules_spec = [(rn, r.guard, r.body, r.contract.post,
                           dict(g.events[r.when]))
                          for rn, r in ent.rules.items()
                          if r.when in g.events]
            ev = court.prove_entity(dict(ent.state), dict(ent.init),
                                    rules_spec, g.events)
            tag = ("ENTITY-INDUCTIVE (post rejection impossible)"
                   if ev.status == "proved" else
                   f"{ev.status.upper()}: {ev.note or ''}")
            print(f"{en} [entity induction]: {tag}")
            bad += ev.status == "counterexample"
            for rn, r in ent.rules.items():
                verdicts = court.prove_rule(dict(ent.state), dict(g.events[r.when]),
                                            r.guard, r.body, r.contract.post,
                                            r.contract.conserves)
                for kind, v in verdicts.items():
                    tag = v.status.upper() if v.status != "proved" else "PROVED"
                    print(f"{en}.{rn}.{kind}: {tag}"
                          + (f" model={v.model}" if v.model else ""))
                    bad += v.status == "counterexample"
                muts = mutants.generate(r.guard, r.body)
                blind, equivalent = [], []
                for m in muts:
                    eq = court.prove_equiv(dict(ent.state), dict(g.events[r.when]),
                                           (r.guard, r.body), (m.guard, m.body))
                    if eq.status == "counterexample":
                        continue                     # distinguished by a counterexample
                    if eq.status == "proved":
                        equivalent.append(m.name)    # PROVABLY equivalent —
                        continue                     # a verdict, not blindness
                    pr = court.prove_rule(dict(ent.state), dict(g.events[r.when]),
                                          m.guard, m.body, r.contract.post,
                                          r.contract.conserves)
                    if any(x.status == "counterexample" for x in pr.values()):
                        continue
                    blind.append(m.name)             # solver unknown and the contract stays silent
                n_dist = len(muts) - len(blind) - len(equivalent)
                print(f"{en}.{rn}: mutants {n_dist}/{len(muts)} distinguished"
                      + (f"; EQUIVALENT (proved): {equivalent}" if equivalent else "")
                      + (f"; BLIND SPOTS: {blind}" if blind else ""))
                bad += len(blind)
        inv_v = court.prove_invariants(g)
        for iname, iv in inv_v.items():
            if iv.status == "proved":
                print(f"invariant {iname}: PROVED ({iv.note})")
            else:
                print(f"invariant {iname}: monitored — {iv.note}")
        # Move 1 (D85): property-strength gate — a gene whose properties are
        # toothless (a lazy `return []` oracle survives them) CANNOT be
        # distributed/installed. This is the anti-prompt-injection primitive
        # for the gene pool: foreign INTENT is text fed to your ribosome, but
        # foreign PROPERTIES must have teeth or your model can satisfy them
        # with a backdoor. Bodies never travel (D85); only contracts do.
        from onto.core import skills as _SK
        for sname, raw_sk in g.skills.items():
            teeth = _SK.gate_teeth(_SK.Skill.model_validate(raw_sk))
            if teeth:
                print(f"skill {sname}: TOOTHLESS PROPERTIES — {teeth[0]}")
                bad += 1
            else:
                print(f"skill {sname}: properties have teeth (lazy oracle fails)")
        nproved = sum(1 for v in inv_v.values() if v.status == "proved")
        print(f"court: {'ALL PROVED, mutants distinguished' if bad == 0 else f'{bad} problem(s)'}"
              + (f"; invariants {nproved}/{len(inv_v)} PROVED, rest monitored" if inv_v else ""))
        return 0 if bad == 0 else 1
    if cmd == "replay":
        # #10 (D83): time-machine debugger — replay the log up to event N and
        # inspect state. Read-only: runs into a scratch dir, the real log is
        # untouched. Answers "why did the balance diverge" better than a
        # breakpoint (state = fold of the log).
        import argparse
        import tempfile
        ap = argparse.ArgumentParser(prog="onto replay")
        ap.add_argument("genome"); ap.add_argument("--data", required=True)
        ap.add_argument("--until", default=None, help="stop after event with this id")
        ap.add_argument("--entity", default=None)
        ap.add_argument("--instance", default=None)
        ap.add_argument("--watch", default=None, help="query name to print at the stop")
        ns = ap.parse_args(args[1:])
        from onto.core import genome as genome_mod
        from onto.core.organism import Organism
        from onto.core.store import open_store
        g = genome_mod.load(ns.genome)
        src = open_store(pathlib.Path(ns.data))
        org = Organism(g, tempfile.mkdtemp(prefix="replay-"))
        org._replaying = True
        applied = found = torn = 0
        last = None
        for ev in src.read_from(0):
            if ev is None:
                torn += 1
                continue
            last = org.handle(ev)
            applied += 1
            if ns.until is not None and ev.get("id") == ns.until:
                found = True
                break
        org._replaying = False
        stop = (f"after event '{ns.until}'" if found else
                (f"'{ns.until}' NOT FOUND — replayed all" if ns.until else "end of log"))
        print(f"replay: {applied} events applied ({torn} torn), stop {stop}")
        if found and last is not None:
            print(f"  outcome of '{ns.until}': {last}")
        if ns.entity and ns.instance:
            st = org.state.get(ns.entity, {}).get(ns.instance)
            print(f"  state {ns.entity}/{ns.instance} = {st}")
        elif ns.entity:
            print(f"  instances of {ns.entity}: {sorted(org.state.get(ns.entity, {}))}")
        if ns.watch:
            try:
                print(f"  {ns.watch} = {org.query(ns.watch, {})}")
            except Exception as e:
                print(f"  watch '{ns.watch}': {e}")
        return 0
    if cmd == "explain":
        if len(args) < 3:
            print("usage: onto explain <root.yaml> <entity|module>", file=sys.stderr)
            return 2
        from onto.core import modules
        print(modules.explain(args[1], args[2]))
        return 0
    if cmd == "new":
        import argparse
        import shutil
        ap = argparse.ArgumentParser(prog="onto new")
        ap.add_argument("name")
        ap.add_argument("--template", default="starter",
                        choices=["starter", "hotel", "lago", "market"])
        ns = ap.parse_args(args[1:])
        # P3: templates ship as PACKAGE DATA (importlib.resources), so this
        # works from an installed wheel with no repo and no network.
        from importlib import resources
        dst = pathlib.Path(ns.name)
        dst.mkdir(parents=True, exist_ok=False)
        try:
            tpl = resources.files("onto") / "templates_gallery" / ns.template
            with resources.as_file(tpl) as tdir:
                for item in pathlib.Path(tdir).iterdir():
                    if item.is_dir():
                        shutil.copytree(item, dst / item.name)
                    else:
                        shutil.copy(item, dst / item.name)
        except (ModuleNotFoundError, FileNotFoundError):
            print(f"onto new: template '{ns.template}' not found in package",
                  file=sys.stderr)
            return 2
        (dst / "README.md").write_text(
            f"# {ns.name} (onto organism)\n\n"
            f"```bash\nonto validate genome.yaml\nonto court genome.yaml\n"
            f"onto serve genome.yaml --port 8090 --data ./data\n"
            f"# admin panel: http://127.0.0.1:8090/admin\n"
            f"onto judge flows.yaml http://127.0.0.1:8090\n"
            f"onto warden genome.yaml --data ./data --port 8090\n```\n",
            encoding="utf-8")
        from onto.core import ir as ir_mod
        (dst / "engine.pin").write_text(__import__("json").dumps(
            {"version": __version__,
             "ir_fingerprint": ir_mod.FROZEN_V1_FINGERPRINT}) + "\n",
            encoding="utf-8")
        print(f"onto new: organism '{ns.name}' from template {ns.template} — "
              f"see {dst / 'README.md'} (engine pin: engine.pin)")
        return 0
    if cmd == "init":
        import argparse
        ap = argparse.ArgumentParser(prog="onto init")
        ap.add_argument("root", nargs="?", default=".")
        ap.add_argument("--harness", default="claude",
                        choices=["claude", "none"])
        ap.add_argument("--force", action="store_true")
        ns = ap.parse_args(args[1:])
        from onto import scaffold
        r = scaffold.init(ns.root, harness=ns.harness, force=ns.force)
        for a in r["actions"]:
            print(f"  {a}")
        print(f"onto init: coupled '{r['root']}' (harness={r['harness']}).\n"
              "Next: put your key in .onto/config.toml, then\n"
              "  onto court genome/genome.yaml   # prove\n"
              "  onto serve genome/genome.yaml --data .onto/data  # live organism\n"
              "The MCP server + edit-guard hook are registered; the harness\n"
              "changes behavior only through `propose`.")
        return 0
    if cmd == "models":
        import argparse
        ap = argparse.ArgumentParser(prog="onto models")
        ap.add_argument("--config", default=".onto/config.toml")
        ns = ap.parse_args(args[1:])
        from onto.ribosome import Provider
        try:
            d = Provider(ns.config).describe()
        except Exception as e:
            print(f"onto models: {e}", file=sys.stderr)
            return 2
        print(f"default provider: {d['default']}")
        print("providers:")
        for n, pr in d["providers"].items():
            mark = "" if pr["key"] == "set" else "   <-- API KEY MISSING"
            print(f"  {n:12} {pr['base_url']}  [key: {pr['key']}]{mark}")
        print("ladders (per task; models are 'provider:model' or bare=default):")
        for t, lad in d["ladders"].items():
            print(f"  {t:8} {' -> '.join(lad)}")
        return 0
    if cmd == "schema":
        import argparse
        import json as _json
        ap = argparse.ArgumentParser(prog="onto schema")
        ap.add_argument("--out", default="")
        ns = ap.parse_args(args[1:])
        from onto.core.genome import Genome
        sch = _json.dumps(Genome.model_json_schema(), indent=2)
        if ns.out:
            pathlib.Path(ns.out).write_text(sch + "\n", encoding="utf-8")
            print(f"onto schema: wrote {ns.out} "
                  f"(add '# yaml-language-server: $schema={ns.out}' atop your genome)")
        else:
            print(sch)
        return 0
    if cmd == "watch":
        import argparse
        import time as _time
        ap = argparse.ArgumentParser(prog="onto watch")
        ap.add_argument("genome")
        ap.add_argument("--interval", type=float, default=0.5)
        ns = ap.parse_args(args[1:])
        from onto.core import genome as genome_mod
        gp = pathlib.Path(ns.genome)
        print(f"onto watch: {gp} (Ctrl-C to stop)", flush=True)
        last = None
        try:
            while True:
                m = gp.stat().st_mtime if gp.exists() else None
                if m != last:
                    last = m
                    try:
                        g = genome_mod.load(gp)
                        nr = sum(len(e.rules) for e in g.entities.values())
                        print(f"  OK  '{g.name}': {len(g.entities)} entities, "
                              f"{nr} rules, {len(g.invariants)} invariants",
                              flush=True)
                    except genome_mod.GenomeError as e:
                        print("  ERRORS:", flush=True)
                        for err in e.errors:
                            print(f"    - {err}", flush=True)
                    except Exception as e:  # noqa: BLE001
                        print(f"  ERROR: {e}", flush=True)
                _time.sleep(ns.interval)
        except KeyboardInterrupt:
            return 0
    if cmd == "mcp":
        from onto import mcp_server
        return mcp_server.main(args[1:])
    if cmd == "growisland":
        # D63 (IDEAL pearl 4): the island-adapter grows an SLM from the
        # external spec (intent+cases); the gate is acceptance against a live upstream.
        import argparse
        ap = argparse.ArgumentParser(prog="onto growisland")
        ap.add_argument("genome"); ap.add_argument("name")
        ap.add_argument("--config", default=".onto/config.toml")
        ns = ap.parse_args(args[1:])
        from onto import growisland as GI
        from onto.ribosome import Provider
        tele = GI.grow(ns.genome, ns.name, Provider(ns.config))
        if tele["island_manual"]:
            print(f"growisland: ladder exhausted — write islands/{ns.name} "
                  "by hand (legal fallback)", file=sys.stderr)
            return 3
        print(f"growisland: GREEN [{tele['model']}]"
              f"{' (cache)' if tele.get('cache') else ''}")
        return 0
    if cmd == "warden":
        import argparse
        ap = argparse.ArgumentParser(prog="onto warden")
        ap.add_argument("root"); ap.add_argument("--data", default="./data")
        ap.add_argument("--port", type=int, default=8090)
        ap.add_argument("--interval", type=float, default=2.0)
        ap.add_argument("--rights", default="observational")
        ns = ap.parse_args(args[1:])
        import time as _time
        from onto.core.warden import Warden
        w = Warden(ns.root, ns.data, ns.port, rights=ns.rights)
        w.start()
        print(f"onto warden: genome '{w.genome.name}' on :{ns.port}, "
              f"rights={ns.rights}, watching every {ns.interval}s")
        try:
            n = 0
            while True:
                _time.sleep(ns.interval)
                n += 1
                out = w.tick_watch()
                if out["status"] != "unchanged":
                    print(f"warden: {out['status']}"
                          + (f" ({out.get('reasons', [''])[0][:100]})"
                             if out["status"] == "rejected" else ""), flush=True)
                w.tick_monitors()
                w.tick_timers(_time.time())        # U2: time is a warden organ
                sp = w.tick_spectral()             # VII §2.5: immune audit
                for v in sp.get("verdicts", []):
                    print(f"warden: spectral verdict {v}", flush=True)
                if n % 15 == 0:
                    w.tick_assumptions()           # U12: holes of ignorance
        except KeyboardInterrupt:
            pass
        finally:
            w.stop()
        return 0
    if cmd == "unit":
        if len(args) < 2:
            print("usage: onto unit <root.yaml> [--data D] [--port P]",
                  file=sys.stderr)
            return 2
        root = pathlib.Path(args[1]).resolve()
        data = pathlib.Path(args[args.index("--data") + 1]
                            if "--data" in args else "./data").resolve()
        port = args[args.index("--port") + 1] if "--port" in args else "8090"
        import shutil as _sh
        onto_bin = _sh.which("onto") or "onto"
        print(f"""[Unit]
Description=onto organism '{root.stem}' (warden-supervised)
After=network.target

[Service]
ExecStart={onto_bin} warden {root} --data {data} --port {port}
Restart=on-failure
WorkingDirectory={root.parent}

[Install]
WantedBy=default.target""")
        return 0
    if cmd == "fix":
        if len(args) < 2:
            print("usage: onto fix <genome.yaml> — rewrite file at current version", file=sys.stderr)
            return 2
        p = pathlib.Path(args[1])
        import yaml
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        p.write_text(ir.fix_text(raw), encoding="utf-8")
        print(f"onto fix: {p} -> onto: {ir.HUB_VERSION}")
        return 0
    print("onto — living ontology compiler.\n"
          "Commands: version | lint | validate | serve | judge | court |\n"
          "  conformance | materialize | explain | fix | warden | unit |\n"
          "  new | init | models | schema | watch | attest | certify | harden | growisland | replay | mcp\n"
          "Surfaces of a served organism: /event /state /q /list /instances\n"
          "  /admin /ops /skill /ext /health /checkpoint")
    return 0 if cmd == "help" else 2


if __name__ == "__main__":
    raise SystemExit(main())
