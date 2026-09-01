# -*- coding: utf-8 -*-
"""EXAM channel axis (D97, Wave 1 / rust): the CHANNEL is a functor SELECTED FROM
SPEC, not a hardcoded door. One genome + one brain, FOUR real channels (file,
stdio, tcp, http) chosen by --channel; each is compiled by rustc and driven
through its ACTUAL transport, and every one produces a BYTE-IDENTICAL fold to
the interpreter. That is the certificate: fold-parity across channels proves the
door is a fold-preserving functor, and that the brain is genome-printed (same
across all doors). Skips cleanly if rustc is absent."""
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

WAL = """onto: 1
name: wal
retry_window: 8
events: {Deposit: {w: str, amt: int}}
entities:
  w: {key: w, instances: [bob, alice], state: {bal: int}, init: {bal: 0},
      rules: {dep: {when: Deposit, guard: "ev.amt > 0",
                    body: "s.bal = s.bal + ev.amt\\n", contract: {post: "s.bal >= 0"}}}}
queries: {}
"""
EVENTS = [{"id": "e1", "type": "Deposit", "w": "bob", "amt": 100},
          {"id": "e2", "type": "Deposit", "w": "bob", "amt": 50},
          {"id": "e3", "type": "Deposit", "w": "alice", "amt": 30},
          {"id": "e4", "type": "Deposit", "w": "bob", "amt": -5},    # guard blocks
          {"id": "e2", "type": "Deposit", "w": "bob", "amt": 999}]   # dedup


def interp_fold(genome_path):
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import genome as G
    from onto.core.organism import Organism
    org = Organism(G.load(genome_path), pathlib.Path(tempfile.mkdtemp()))
    for e in EVENTS:
        org.handle(e)
    return json.dumps({en: {i: dict(s) for i, s in insts.items()}
                       for en, insts in org.snapshot().items()},
                      separators=(",", ":"), sort_keys=True)


# each dialect: (registry name, toolchain-probe, run-argv builder from outdir)
def _run_prefix(dialect, wd):
    wd = pathlib.Path(wd)
    if dialect in ("rust-stdlib", "go-stdlib"):
        return [str(wd / "organism")]
    if dialect == "python-stdlib":
        return [sys.executable, str(wd / "organism.py")]
    if dialect == "kotlin-stdlib":
        import os as _os
        from onto.dialects.kotlin_stdlib import gates as KG
        jh = KG.find_java_home()
        return [f"{jh}/bin/java", "-jar", str(wd / "organism.jar")]
    raise RuntimeError(f"no run prefix for {dialect}")


def _toolchain_ok(dialect):
    if dialect == "rust-stdlib":
        return shutil.which("rustc") is not None
    if dialect == "go-stdlib":
        from onto.dialects.go_stdlib.gates import find_go
        return find_go() is not None
    if dialect == "python-stdlib":
        return True
    if dialect == "kotlin-stdlib":
        from onto.dialects.kotlin_stdlib.gates import available
        return available()[0]
    return False


def build(genome_path, dialect, channel, wd):
    from onto.core import genome as G
    from onto.dialects import registry
    reg = registry.get(dialect)
    reg["skeleton"].generate(G.load(genome_path), pathlib.Path(wd),
                             channels=[{"driver": channel, "direction": "in",
                                        "codec": "json"}])
    ok, msg = reg["gates"].build(pathlib.Path(wd))
    if not ok:
        raise RuntimeError(f"build {dialect}/{channel}: {msg}")
    return _run_prefix(dialect, wd)


def wait_port(port, t=5.0):
    end = time.time() + t
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.3).close()
            return True
        except OSError:
            time.sleep(0.05)
    return False


def drive_file(pref, wd):
    evf = pathlib.Path(wd) / "ev.jsonl"
    evf.write_text("\n".join(json.dumps(e) for e in EVENTS) + "\n")
    r = subprocess.run(pref + [str(evf)], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def drive_stdio(pref, wd):
    inp = "\n".join(json.dumps(e) for e in EVENTS) + "\n"
    r = subprocess.run(pref, input=inp, capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def drive_http(pref, wd, port):
    import urllib.request
    p = subprocess.Popen(pref + ["--port", str(port)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_port(port):
            return "server-did-not-start"
        for e in EVENTS:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/event",
                                         data=json.dumps(e).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5).read()
        return urllib.request.urlopen(f"http://127.0.0.1:{port}/dump",
                                      timeout=5).read().decode().strip()
    finally:
        p.terminate(); p.wait()


def drive_tcp(pref, wd, port):
    p = subprocess.Popen(pref + ["--port", str(port)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_port(port):
            return "server-did-not-start"
        s = socket.create_connection(("127.0.0.1", port), timeout=3)
        payload = "".join(json.dumps(e) + "\n" for e in EVENTS) + "?dump\n"
        s.sendall(payload.encode())
        s.shutdown(socket.SHUT_WR)
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
        s.close()
        # the last non-empty reply line is the ?dump response
        lines = [l for l in buf.decode().splitlines() if l.strip()]
        return lines[-1] if lines else ""
    finally:
        p.terminate(); p.wait()


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    if shutil.which("rustc") is None:
        print("=== EXAM channel axis: SKIPPED (no rustc) ===\nVERDICT: SKIPPED")
        return 0

    gp = pathlib.Path(tempfile.mkdtemp()) / "wal.yaml"
    gp.write_text(WAL)
    want = interp_fold(gp)

    DIALECTS = ["rust-stdlib", "go-stdlib", "python-stdlib", "kotlin-stdlib"]
    base = 8651
    drivers = [("file", drive_file, False), ("stdio", drive_stdio, False),
               ("http", drive_http, True), ("tcp", drive_tcp, True)]
    for dialect in DIALECTS:
        if not _toolchain_ok(dialect):
            R.append((f"[{dialect}] SKIPPED (no toolchain on this host)", None))
            continue
        # not every dialect has the channel axis yet (Waves 2-4)
        import inspect as _inspect
        from onto.dialects import registry as _reg
        if "channels" not in _inspect.signature(_reg.get(dialect)["skeleton"].generate).parameters:
            R.append((f"[{dialect}] no channel axis yet (pending its wave)", None))
            continue
        for name, driver, needs_port in drivers:
            wd = tempfile.mkdtemp(prefix=f"ch-{dialect[:2]}-{name}-")
            base += 1
            try:
                pref = build(gp, dialect, name, wd)
                got = driver(pref, wd, base) if needs_port else driver(pref, wd)
                ok = got == want
                R.append((f"[{dialect}] channel '{name}': compiled + driven through "
                          f"the REAL transport -> fold byte-identical"
                          + ("" if ok else f"  (got {got!r} want {want!r})"), ok))
            except Exception as e:  # noqa: BLE001
                R.append((f"[{dialect}] channel '{name}': {type(e).__name__}: "
                          f"{str(e)[:120]}", False))

    print(f"\n=== EXAM channel axis / rust (D97) ({time.time()-t0:.1f}s) ===")
    print(f"  interpreter fold: {want}")
    ok = True
    for name, passed in R:
        tag = "SKIP" if passed is None else ("PASS" if passed else "FAIL")
        print(f"  {tag}  {name}")
        if passed is False:
            ok = False
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
