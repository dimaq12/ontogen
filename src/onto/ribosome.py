# -*- coding: utf-8 -*-
"""The skills ribosome — a live SLM in a CEGIS loop (SPEC §9.2, D27: rules are
printed, the SLM writes only SKILLS).

The loop: prompt (contract + intent + COUNTEREXAMPLES from past attempts) -> SLM ->
gates (semantics fuzz / equivalence+budget) -> green: into the cache; red:
counterexample into the prompt (the best few-shot is about THIS body), K attempts ->
one rung up the ladder -> exhausted: an island (a valid outcome, ledger).

Cache (D6): the key = hash(the skill's canonical contract + phase + model) — NOT
the prompt text: improving the prompt does not burn the bodies. Telemetry: usage in JSONL.
The provider is a tissue: OpenAI-compatible HTTP (config .onto/config.toml).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
import tomllib
import urllib.request

from onto.core import skills as SK

ATTEMPTS_PER_MODEL = 3
DEFAULT_MAX_TOKENS = 2200


# ------------------------------------------------------------- provider

# Built-in base_url presets: name a known provider, give only the key.
# Any OpenAI-compatible endpoint works; unknown names just need base_url.
PROVIDER_PRESETS = {
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "together": "https://api.together.xyz/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "mistral": "https://api.mistral.ai/v1",
    "fireworks": "https://api.fireworks.ai/inference/v1",
    "xai": "https://api.x.ai/v1",
    "ollama": "http://localhost:11434/v1",
    "local": "http://localhost:8000/v1",     # vLLM/llama.cpp default
    "lmstudio": "http://localhost:1234/v1",
}
DEFAULT_LADDERS = {
    "skills": ["qwen/qwen3-coder", "qwen/qwen3-coder-plus"],
    "nl": ["anthropic/claude-sonnet-4.5", "anthropic/claude-opus-4.1"],
    "dialect": ["qwen/qwen3-coder", "qwen/qwen3-coder-plus"],
    "island": ["qwen/qwen3-coder", "qwen/qwen3-coder-plus"],
}


def _resolve_secret(v: str) -> str:
    """User-friendly key resolution: '${VAR}' or '$VAR' -> env; '@path' ->
    file contents; anything else -> literal. Never hardcode a key in config."""
    import os
    v = (v or "").strip()
    # An EXPLICIT reference that fails to resolve is a config error, not a
    # blank key: raise so the misconfig is loud, never silently unauthenticated.
    if v.startswith("${") and v.endswith("}"):
        name = v[2:-1]
        if name not in os.environ:
            raise RuntimeError(f"key references ${{{name}}} but that env var is "
                               f"not set (fix the env or the config)")
        return os.environ[name]
    if v.startswith("$"):
        name = v[1:]
        if name not in os.environ:
            raise RuntimeError(f"key references ${name} but that env var is not set")
        return os.environ[name]
    if v.startswith("@"):
        pth = pathlib.Path(v[1:]).expanduser()
        if not pth.exists():
            raise RuntimeError(f"key references @{v[1:]} but that file does not exist")
        return pth.read_text(encoding="utf-8").strip()
    return v  # literal (incl. "" = deliberately no key, e.g. ollama/local)


class Provider:
    """Model registry (D86): many named OpenAI-compatible providers, models
    referenced as 'provider:model' or bare (-> default provider), per-task
    ladders that can mix providers. Fully user-configurable; back-compatible
    with the single-[provider.openrouter] + [ribosome].skills_ladder form."""

    def __init__(self, cfg_path: str | pathlib.Path):
        cfg = tomllib.load(open(cfg_path, "rb"))
        self.providers: dict = {}
        for name, p in cfg.get("provider", {}).items():
            base = (p.get("base_url") or PROVIDER_PRESETS.get(name, "")).rstrip("/")
            key = _resolve_secret(p.get("api_key")
                                  or (f"${{{p['api_key_env']}}}"
                                      if p.get("api_key_env") else ""))
            self.providers[name] = {
                "base_url": base, "api_key": key,
                "headers": p.get("extra_headers", p.get("headers", {})),
                "body": p.get("extra_body", p.get("body", {}))}
        if not self.providers:
            raise RuntimeError(f"{cfg_path}: no [provider.<name>] configured")
        self.default_provider = (cfg.get("default", {}).get("provider")
                                 or ("openrouter" if "openrouter" in self.providers
                                     else next(iter(self.providers))))
        # ladders: [ladders] skills/nl/dialect/island; back-compat with
        # [ribosome].skills_ladder; else built-in defaults.
        self._ladders = dict(cfg.get("ladders", {}))
        legacy = cfg.get("ribosome", {}).get("skills_ladder")
        if legacy and "skills" not in self._ladders:
            self._ladders["skills"] = legacy
        # back-compat attributes (default provider)
        dp = self.providers[self.default_provider]
        self.base_url, self.api_key = dp["base_url"], dp["api_key"]
        self.extra_headers, self.extra_body = dp["headers"], dp["body"]
        self.usage_path: pathlib.Path | None = None

    @property
    def skills_ladder(self) -> list:
        return self.ladder("skills")

    def ladder(self, task: str) -> list:
        # explicit task ladder wins; growth tasks inherit a configured
        # 'skills' ladder (matches the legacy skills_ladder behavior);
        # 'nl' never falls back to skills (needs a strong model).
        if task in self._ladders:
            return self._ladders[task]
        if task != "nl" and "skills" in self._ladders:
            return self._ladders["skills"]
        return DEFAULT_LADDERS.get(task) or DEFAULT_LADDERS["skills"]

    def route(self, model_ref: str) -> tuple:
        """'provider:model' -> (provider_cfg, model); bare -> default provider.
        ':' is the separator ('/' stays inside OpenRouter model names)."""
        if ":" in model_ref:
            head, tail = model_ref.split(":", 1)
            if head in self.providers:
                return self.providers[head], tail
        return self.providers[self.default_provider], model_ref

    def describe(self) -> dict:
        """For `onto models`: providers (key present?), default, ladders."""
        return {
            "default": self.default_provider,
            "providers": {n: {"base_url": p["base_url"],
                              "key": "set" if p["api_key"] else "MISSING"}
                          for n, p in self.providers.items()},
            "ladders": {t: self.ladder(t)
                        for t in sorted(set(self._ladders) | set(DEFAULT_LADDERS))}}

    def generate(self, model: str, prompt: str, seed: int, tag: str,
                 max_tokens: int | None = None) -> str:
        prov, real_model = self.route(model)
        if not prov["base_url"]:
            raise RuntimeError(f"provider for '{model}' has no base_url")
        body = {"model": real_model, "temperature": 0, "seed": seed,
                "max_tokens": max_tokens or DEFAULT_MAX_TOKENS,
                "messages": [{"role": "user", "content": prompt}],
                **prov["body"]}
        headers = {"Content-Type": "application/json", **prov["headers"]}
        if prov["api_key"]:
            headers["Authorization"] = f"Bearer {prov['api_key']}"
        req = urllib.request.Request(prov["base_url"] + "/chat/completions",
                                     data=json.dumps(body).encode(),
                                     headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
        content = data["choices"][0]["message"]["content"]
        if self.usage_path:
            u = data.get("usage", {})
            with self.usage_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "tag": tag, "model": data.get("model", real_model),
                    "seed": seed, "tokens_in": u.get("prompt_tokens"),
                    "tokens_out": u.get("completion_tokens"),
                    "ms": int((time.time() - t0) * 1000)},
                    ensure_ascii=False) + "\n")
        if not content.strip():
            raise RuntimeError(f"provider returned empty content for {model}")
        return content


def strip_code(text: str) -> str:
    import re
    blocks = re.findall(r"```(?:python|js|javascript|go)?\s*\n(.*?)```", text, flags=re.S)
    return (blocks[0] if blocks else text).strip()


# ----------------------------------------------------------------- cache

def cache_key(sk: SK.Skill, phase: str, model: str) -> str:
    """A semantic key (D6): the canonical contract, NOT the prompt text."""
    contract = {"params": sk.params, "returns": sk.returns, "types": sk.types,
                "intent": sk.intent, "properties": sk.properties,
                "budget": sk.budget, "phase": phase, "model": model}
    return hashlib.sha256(
        json.dumps(contract, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:16]


# --------------------------------------------------------------- prompts

def prompt_naive(name: str, sk: SK.Skill, counterexamples: list[str]) -> str:
    types_txt = "\n".join(f"  {t}: fields {fields}"
                          for t, fields in sk.types.items())
    props = "\n".join(f"  - {p}" for p in sk.properties)
    cx = ("\nYour previous attempts FAILED these machine-checked "
          "counterexamples — fix exactly these:\n" + "\n".join(counterexamples)
          ) if counterexamples else ""
    args = ", ".join(sk.params)
    return f"""You write ONE pure Python function. No imports, no I/O, no prints.

Types (objects with attributes; constructors like Order(id, price, qty, ts) or Order(id=..., ...) are available):
{types_txt}
Construct output items as plain dicts: {{"bid": ..., "ask": ..., "price": ..., "qty": ...}} matching fields of {sk.returns}.

Implement EXACTLY:
def naive_{name}({args}):

Semantics: {sk.intent}

Correctness first; a simple O(n*m) approach is fine. Machine-checked
properties your output MUST satisfy on every input:
{props}
{cx}
Output ONLY the Python code of this single function in a ```python fence."""


def prompt_fast(name: str, sk: SK.Skill, naive_code: str,
                counterexamples: list[str]) -> str:
    cx = ("\nYour previous attempts FAILED these machine-checked "
          "counterexamples — fix exactly these:\n" + "\n".join(counterexamples)
          ) if counterexamples else ""
    args = ", ".join(sk.params)
    return f"""You write ONE pure Python function. No imports, no I/O.

This REFERENCE implementation is correct but slow:
```python
{naive_code}
```

Implement EXACTLY (same output, byte-for-byte equal trade lists on any input):
def fast_{name}({args}):

It must scale near-linearithmically: time at n={sk.budget.get('n', 600) * sk.budget.get('growth', 4)}
must be <= {sk.budget.get('max_ratio', 8)}x the time at n={sk.budget.get('n', 600)}
(quadratic nested scans fail this). Use sorting + two pointers / indexes.
Output items are plain dicts like the reference.
{cx}
Output ONLY the Python code of this single function in a ```python fence."""


# ------------------------------------------------------------ CEGIS loop

def _short_cx(cx: dict) -> str:
    case = {k: v[:4] for k, v in cx["case"].items()}
    if cx.get("error"):
        return f"- input {json.dumps(case)} -> raised {cx['error'][:120]}"
    return (f"- input {json.dumps(case)} -> your output "
            f"{json.dumps(cx.get('out', cx.get('fast'))[:4])} violated: "
            f"{'; '.join(cx.get('violated', ['equivalence with reference']))[:220]}")


def synthesize(name: str, sk: SK.Skill, provider: Provider,
               cache_dir: str | pathlib.Path, log=print,
               regressions_dir=None) -> dict:
    """Two-phase skill synthesis. Returns telemetry + code. An island is a
    valid outcome (island=True), not an exception."""
    cache = pathlib.Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    ladder = sk.ladder or provider.skills_ladder
    tele: dict = {"skill": name, "phases": {}, "island": False}

    def phase(phase_name: str, fname: str, make_prompt, gates) -> str | None:
        ck = None
        for model in ladder:
            ck = cache / f"{cache_key(sk, phase_name, model)}.py"
            if ck.exists():
                code = ck.read_text(encoding="utf-8")
                if gates(code) is None:
                    (cache / f"{name}.{phase_name}.py").write_text(
                        code, encoding="utf-8")
                    log(f"  {phase_name}: CACHE hit [{model}]")
                    tele["phases"][phase_name] = {"model": model, "attempts": 0,
                                                  "cache": True}
                    return code
            cxs: list[str] = []
            for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
                raw = provider.generate(model, make_prompt(cxs), seed=42,
                                        tag=f"{name}:{phase_name}:{model}:{attempt}")
                code = strip_code(raw)
                verdict = gates(code)
                if verdict is None:
                    ck.write_text(code, encoding="utf-8")
                    # a named artifact for the organism (readable, committed)
                    (cache / f"{name}.{phase_name}.py").write_text(
                        code, encoding="utf-8")
                    log(f"  {phase_name}: GREEN [{model}] attempt {attempt}")
                    tele["phases"][phase_name] = {"model": model,
                                                  "attempts": attempt,
                                                  "cache": False}
                    return code
                cxs.append(verdict)
                log(f"  {phase_name}: red [{model}] attempt {attempt}: "
                    f"{verdict[:110]}")
            log(f"  {phase_name}: ladder step exhausted [{model}] -> escalate")
        tele["phases"][phase_name] = {"model": None, "attempts": None}
        return None

    # --- phase A: naive (correctness by properties)
    def gates_naive(code: str) -> str | None:
        try:
            fn = SK.load_body(code, f"naive_{name}", sk.types)
        except Exception as e:
            return f"- your code failed to load: {type(e).__name__}: {str(e)[:150]}"
        cx = SK.gate_semantics(sk, fn)
        if cx is None:
            reg = SK.gate_regressions(sk, fn, regressions_dir / f"{name}.jsonl") \
                if regressions_dir else None
            cx = {"case": None, "violated": reg} if reg else None
        return None if cx is None else _short_cx(cx)

    naive_code = phase("naive", f"naive_{name}",
                       lambda cxs: prompt_naive(name, sk, cxs), gates_naive)
    if naive_code is None:
        tele["island"] = True
        tele["why"] = "phase A (naive) exhausted the ladder"
        return tele
    naive_fn = SK.load_body(naive_code, f"naive_{name}", sk.types)

    # --- phase B: fast (equivalence + budget)
    def gates_fast(code: str) -> str | None:
        try:
            fn = SK.load_body(code, f"fast_{name}", sk.types)
        except Exception as e:
            return f"- your code failed to load: {type(e).__name__}: {str(e)[:150]}"
        cx = SK.gate_equivalence(sk, naive_fn, fn)
        if cx is not None:
            return _short_cx({"case": cx["case"], "fast": cx["fast"],
                              "violated": ["equivalence with reference"]})
        b = SK.gate_budget(sk, naive_fn, fn)
        tele["bench"] = b
        if not b["ok"]:
            return (f"- complexity too high: t({b['growth']}n)/t(n) = "
                    f"{b['ratio']:.1f} > allowed {b['max_ratio']:g} "
                    f"(looks super-linearithmic; avoid nested scans)")
        return None

    fast_code = phase("fast", f"fast_{name}",
                      lambda cxs: prompt_fast(name, sk, naive_code, cxs),
                      gates_fast)
    if fast_code is None:
        tele["island"] = True
        tele["why"] = "phase B (fast) exhausted the ladder — naive stands in"
    return tele
