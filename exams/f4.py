# -*- coding: utf-8 -*-
"""EXAM F4 "Composition and genes": a domain of 3 genes; the payments gene
reused in TWO genomes (printed bodies byte-for-byte); judge green on the
interpreter AND go for both; the court proves the linked contracts; genome
tokens <= 1/3 of the phenotype; explain slice O(k)."""
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
R = []


def wait_up(port):
    for _ in range(100):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
            return True
        except Exception:
            time.sleep(0.05)
    return False


def run(args, **kw):
    return subprocess.run([str(PY), "-m", "onto.cli", *args], cwd=ROOT,
                          capture_output=True, text=True, **kw)


def main():
    t0 = time.time()
    procs = []
    try:
        # ---- judge on the interpreter: both roots
        for gname, flows, port in (("hotel", "hotel_flows", 8611),
                                   ("shop", "shop_flows", 8612)):
            procs.append(subprocess.Popen(
                [str(PY), "-m", "onto.cli", "serve",
                 str(ROOT / f"genomes/{gname}.yaml"),
                 "--data", tempfile.mkdtemp(prefix=f"f4-{gname}-"),
                 "--port", str(port)],
                cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            up = wait_up(port)
            j = run(["judge", str(ROOT / f"exams/{flows}.yaml"),
                     f"http://127.0.0.1:{port}"])
            print(f"{gname}(interp): {j.stdout.strip().splitlines()[-1]}")
            R.append((f"judge on the linked {gname} (interpreter)",
                      up and j.returncode == 0))

        # ---- go materialization of both roots + judge
        for gname, flows, port in (("hotel", "hotel_flows", 8613),
                                   ("shop", "shop_flows", 8614)):
            m = run(["materialize", str(ROOT / f"genomes/{gname}.yaml"),
                     "--dialect", "go-stdlib", "--out",
                     str(ROOT / f"build/{gname}_go")])
            ok_build = m.returncode == 0
            procs.append(subprocess.Popen(
                [str(ROOT / f"build/{gname}_go/organism"), "--port", str(port),
                 "--data", tempfile.mkdtemp(prefix=f"f4-{gname}-go-")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            up = wait_up(port)
            j = run(["judge", str(ROOT / f"exams/{flows}.yaml"),
                     f"http://127.0.0.1:{port}"])
            print(f"{gname}(go):     {j.stdout.strip().splitlines()[-1]}")
            R.append((f"judge on the linked {gname} (go)",
                      ok_build and up and j.returncode == 0))

        # ---- gene reuse: wallet bodies byte-for-byte in two phenotypes
        def wallet_funcs(path):
            src = (ROOT / path / "main.go").read_text()
            return sorted(re.findall(
                r"func (?:guard|rule|post|conserves)Wallet\w*\([^)]*\)[^{]*\{.*?\n\}",
                src, re.S))
        hw, sw = wallet_funcs("build/hotel_go"), wallet_funcs("build/shop_go")
        R.append(("payments gene: printed wallet bodies BYTE-FOR-BYTE in hotel and shop",
                  hw == sw and len(hw) >= 4))

        # ---- court on the linked genomes
        for gname in ("hotel", "shop"):
            c = run(["court", str(ROOT / f"genomes/{gname}.yaml")])
            R.append((f"court on the linked {gname}: PROVED, mutants distinguished",
                      c.returncode == 0 and "BLIND" not in c.stdout))

        # ---- metric: genome tokens <= 1/3 of the phenotype
        genome_tok = sum(len((ROOT / p).read_text()) // 4 for p in
                         ("genomes/hotel.yaml", "modules/rooms.yaml",
                          "modules/reservations.yaml", "modules/payments.yaml"))
        pheno_tok = len((ROOT / "build/hotel_go/main.go").read_text()) // 4
        ratio = genome_tok / pheno_tok
        print(f"tokens: genome {genome_tok} vs phenotype(go) {pheno_tok} "
              f"= {ratio:.2f}")
        R.append((f"genome <= 1/3 of the phenotype (actual {ratio:.2f})", ratio <= 1 / 3))

        # ---- explain slice O(k)
        e = run(["explain", str(ROOT / "genomes/hotel.yaml"), "wallet"])
        pct = int(e.stdout.rsplit("(", 1)[1].rstrip("%)\n"))
        R.append((f"explain slice wallet = {pct}% of the genome (<= 50%)",
                  e.returncode == 0 and pct <= 50))

        # ---- composition rejections go red (quick check via the pytest suite)
        p = subprocess.run([str(PY), "-m", "pytest", "-q",
                            "tests/test_modules.py"],
                           cwd=ROOT, capture_output=True, text=True)
        R.append(("composition rejections (requires/override/instances) go red",
                  p.returncode == 0))
    finally:
        for pr in procs:
            pr.kill()

    print(f"\n=== EXAM F4 ({time.time() - t0:.1f} s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok &= passed
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
