# onto — a living compiler of ontologies

A program is stored not as code, but as a **genome**: entities, rules with
executable bodies, contracts, invariants. Code is the phenotype: printed into
dialects (Go, Python), proven by the court (SMT), living under a warden, and
regrown from scratch. A change in behavior without confirmation is a question with an
executable counterexample, not a silent merge.

```bash
uv tool install ontogen                # -> global `onto`
onto validate genomes/hotel.yaml       # typecheck the genome
onto court    genomes/hotel.yaml       # SMT court: contracts proven, mutants distinguished
onto serve    genomes/hotel.yaml --port 8090 --data ./data [--store sqlite]
onto warden   genomes/hotel.yaml ...   # daemon: watch -> gates -> molt -> monitors
onto materialize genomes/hotel.yaml --dialect go-stdlib   # print the phenotype
onto mcp      genomes/hotel.yaml       # a mouth for the LLM (propose = the only write)
```

## Models: bring your own (any OpenAI-compatible provider)

Configure providers and per-task model ladders in `.onto/config.toml` —
OpenRouter, OpenAI, Groq, Together, DeepSeek, a local Ollama/vLLM, anything
OpenAI-compatible. Name a known provider and give only a key (base_url is a
preset); reference models as `provider:model` or bare. Keys come from
`${ENV}` or `@keyfile`, never hardcoded. `onto models` shows the registry.

```toml
[default]
provider = "openrouter"
[provider.openrouter]
api_key = "${OPENROUTER_API_KEY}"
[provider.local]
base_url = "http://localhost:11434/v1"   # Ollama
api_key = "ollama"
[ladders]
skills = ["qwen/qwen3-coder", "qwen/qwen3-coder-plus"]
nl     = ["anthropic/claude-sonnet-4.5", "local:qwen2.5-coder"]
```

## Quickstart (zero machine)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # 1. uv (brings its own Python)
uv tool install ontogen                           # 2. the engine, isolated
onto init                                         # 3. couple this project + harness
#    -> .onto/ + genome/ + MCP registration + edit-guard hook + skill
onto court genome/genome.yaml                     # prove (ALL PROVED)
onto serve genome/genome.yaml --data .onto/data   # live organism from second zero
```

The harness (Claude Code) sees the MCP server immediately; it changes
behavior only through `propose` (checkers + SMT court + semantic diff), and
a hook blocks any direct edit of the genome or the printed phenotype.
Dialect toolchains (e.g. Go/JVM) are pulled lazily, only at `materialize`.

## Status: 1.3.0 — the U1-U8 constitution is closed, IR v1.0 is frozen (D72)

## End-to-end scenario (IDEAL, works)
A natural-language product description -> `nlfront` builds a genome+acceptance -> the COURT proves
-> the organism lives (warden timers, /admin, /list, /q?params, webhooks)
-> any language is grown by the model (`growdialect`). Exams: exams/fnl.py,
exams/fideal.py, exams/fgrow.py.

## Where to look
| you need | read |
|---|---|
| HOW any software is developed under this model | **`docs/design/MODEL.md`** — the method's constitution |
| to run an organism (features, operation) | `docs/OPERATOR.md` + `onto explain <root> <entity>` |
| engine development | `CLAUDE.md` -> `docs/log/PLAN.md` -> `docs/log/JOURNAL.md` |
| architecture and decisions | `docs/design/SPEC.md`, `docs/log/DECISIONS.md` (D1–D87) |
| what we don't do and why | `docs/design/NOT.md`, `docs/design/SCARS.md` (v0 scars), `docs/design/UNEXPRESSIBLE.md` |
| visual diagram | `docs/anatomy.html` |

## What the exams have proven (exams/, all green)
the organism lives via an interpreter without code generation; one judge is green on
interpreter+Go+Python; contracts are proven (COURT), 21/21 mutants
distinguished, an equivalent mutant recognized; gene composition (payments in three
domains byte-for-byte); metabolism by measured heat with failure-with-arithmetic;
warden: molt in 0.3s, migration of 30k live events by functor, REVOKE of rights;
live CEGIS with an SLM (~$0.001/skill); a membrane for others' organisms (drift ->
trust revocation); 25k ev/s ingest, p99 1.8ms, kill -9 -> start from snapshot
0.01s; jsonl|sqlite store with a byte-identical fold. Running the whole battery:
`tools/check.sh`.

Status: the engine is built and delivered exam by exam (see `docs/log/PLAN.md`); open —
calendar operation and the external operator (F7).
