# -*- coding: utf-8 -*-
"""EXAM model registry (D86): easy, broad, user-friendly provider/model config
in the ribosome (Claude-Code/Kilo-style). Many OpenAI-compatible providers,
models as 'provider:model' or bare, per-task ladders that mix providers,
env/file key resolution, base_url presets. No network — pure routing/config."""
import os
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []

RICH = '''
[default]
provider = "groq"

[provider.openrouter]
api_key = "${TEST_OR_KEY}"

[provider.groq]
api_key = "@KEYFILE"

[provider.local]
base_url = "http://localhost:11434/v1"
api_key = "ollama"

[ladders]
skills = ["llama-3.3-70b", "openrouter:qwen/qwen3-coder"]
nl = ["openrouter:anthropic/claude-sonnet-4.5", "local:qwen2.5-coder"]
'''


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.ribosome import Provider, PROVIDER_PRESETS

    d = pathlib.Path(tempfile.mkdtemp(prefix="models-"))
    kf = d / "key.txt"
    kf.write_text("gsk-secret-key\n")
    cfg = d / "config.toml"
    cfg.write_text(RICH.replace("@KEYFILE", f"@{kf}"))
    os.environ["TEST_OR_KEY"] = "sk-or-env-key"
    p = Provider(cfg)

    # 1. preset base_url (groq named -> auto URL, only key given)
    R.append((f"preset base_url from provider name: groq -> "
              f"{p.providers['groq']['base_url']}",
              p.providers["groq"]["base_url"] == PROVIDER_PRESETS["groq"]))
    # 2. env-var key resolution ${VAR}
    R.append(("key from ${ENV}: openrouter key resolved from env",
              p.providers["openrouter"]["api_key"] == "sk-or-env-key"))
    # 3. key from @file
    R.append(("key from @file: groq key read from keyfile",
              p.providers["groq"]["api_key"] == "gsk-secret-key"))
    # 4. local provider, explicit base_url, no preset needed
    R.append(("local/self-hosted provider (explicit base_url)",
              p.providers["local"]["base_url"] == "http://localhost:11434/v1"))
    # 5. default provider honored
    R.append(("default provider = groq (bare model routes there)",
              p.default_provider == "groq"))

    # 6. routing: 'provider:model' splits; bare -> default; '/' stays in model
    prov_or, m1 = p.route("openrouter:qwen/qwen3-coder")
    R.append(("route 'openrouter:qwen/qwen3-coder' -> openrouter + full model",
              prov_or["base_url"] == PROVIDER_PRESETS["openrouter"]
              and m1 == "qwen/qwen3-coder"))
    prov_b, m2 = p.route("llama-3.3-70b")
    R.append(("route bare 'llama-3.3-70b' -> default provider (groq)",
              prov_b["base_url"] == PROVIDER_PRESETS["groq"]
              and m2 == "llama-3.3-70b"))
    prov_l, m3 = p.route("local:qwen2.5-coder")
    R.append(("route 'local:qwen2.5-coder' -> local server",
              prov_l["base_url"] == "http://localhost:11434/v1"
              and m3 == "qwen2.5-coder"))

    # 7. per-task ladders, can mix providers
    R.append((f"per-task ladders mix providers: nl={p.ladder('nl')}",
              p.ladder("nl") == ["openrouter:anthropic/claude-sonnet-4.5",
                                 "local:qwen2.5-coder"]))
    # 8. nl never falls back to skills; dialect inherits skills
    cfg2 = d / "c2.toml"
    cfg2.write_text('[provider.openrouter]\napi_key="x"\n'
                    '[ladders]\nskills=["a","b"]\n')
    p2 = Provider(cfg2)
    R.append(("unconfigured 'dialect' inherits configured skills; 'nl' uses "
              "strong default",
              p2.ladder("dialect") == ["a", "b"]
              and p2.ladder("nl")[0].startswith("anthropic/")))

    # 9. BACK-COMPAT: the real repo config still loads and works
    real = Provider(ROOT / ".onto/config.toml")
    R.append(("back-compat: legacy [provider.openrouter]+[ribosome] config "
              "loads, skills_ladder intact",
              real.default_provider == "openrouter"
              and len(real.skills_ladder) >= 1))

    print(f"\n=== EXAM model registry ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
