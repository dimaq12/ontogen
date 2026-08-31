# STACK: technology, deployment, delivery (2026-08-20)

Same methodology: ideal world → v0 scars → decisions → refusals → predictions.

## Ideal world
- The operator installs the engine with ONE command, and it works a year later:
  `uv tool install ontogen==X`. Updating the engine does not silently break the
  organism.
- The organism is the user's SEPARATE repository (genome + .archgen/{cache,
  ledger, checkpoints} + islands); the engine is a pinned version in the genome
  (like terraform required_version). Changing the engine version = an explicit
  molt.
- Determinism lives in the cache and the gates, NOT in the provider: two cold
  runs on different machines give byte-for-byte (the cache is committed); the
  provider fills only the misses, with a response integrity check.
- Phenotype: one process = one deployable; the skeleton — zero mandatory
  dependencies; the build is offline after the first fetch; a systemd unit is
  generated. A backup of the organism = a copy of the data dir (event log +
  snapshot) + the genome.
- The ledger is read by eye and by diff; nothing in the repo depends on a
  specific machine's paths.

## v0 scars (stack) — all with evidence in the repo
| No.  | scar | evidence |
|---|---|---|
| ST1 | the engine did not own its environment: a foreign venv, a random Python 3.14 | a stale sibling `.venv`, a sys.prefix warning, cpython-314.pyc |
| ST2 | a hardcoded machine path | `gates.py:_SCRATCH=/tmp/claude-…/scratchpad/go`; find_go across 4 places |
| ST3 | state in the engine's git | `.archgen/ledger.db` (a binary!) and `__pycache__/*.pyc` are tracked and "modified" in every status; build/ is not cleaned |
| ST4 | phenotype network dependencies = a blocker | modernc.org/sqlite doesn't fetch offline → the wave collapsed to memory (UNEXPRESSIBLE) |
| ST5 | one repository for everything | engine + genomes + build + cache + ledger mixed together; no boundary "compiler" vs "user's project" |
| ST6 | determinism by provider — an illusion | the seed wanders across upstreams, Novita empty content, Cloudflare corrupts code (concern #12) |
| ST7 | there is no delivery | entry = git clone + knowing the right venv and paths; the barrier — only the author |

## Decisions (entered in DECISIONS D14–D21)
- **D14 Engine: Python 3.13 + uv** (pyproject + uv.lock, pinned toolchain; its
  own .venv in the engine repo). Why not Rust/Go: iteration speed with
  LLM-sessions, z3-solver, mcp-sdk, lark — all first-class in Python; v0's rake
  was not the language but environment hygiene. A revision is legal after F6 on
  metrics (cycle time, delivery pain) — NOT earlier (see P11).
- **D15 Two repository archetypes.** The engine repo (this one) and the
  organism-workspace. The organism pins `engine: ">=1.2,<2"` in the root genome;
  the engine version is written into every ledger record. Exam: the organism
  builds on a clean machine from its repo + `uv tool install`.
- **D16 Ledger = append-only JSONL** with a hash chain (diffable, greppable);
  SQLite — a derived local index, rebuildable from JSONL, outside git. The body
  cache (text files) — committed to the organism repo; GC by reachability from
  the genome.
- **D17 The interpreter is two-tier** (surfaced by the delivery question):
  metabolism (§10) requires an evicted path to be executed by the interpreter IN
  THE SAME process as the warmed bodies — meaning an embeddable Expr-interpreter
  is part of the generic runtime of EVERY dialect. The canonical interpreter
  lives in the engine (the truth for courts and the F1-organism). Tier
  correspondence — the shared **Expr conformance-suite** (like the WASM spec
  tests): a dialect without a green suite is not certified. The suite is laid
  down in F1 (no later!), see P12.
- **D18 Toolchains are declared, not guessed**: the dialect manifest carries the
  requirements (go>=1.23, …); `onto doctor` checks and hints; hardcoded paths
  are forbidden (NOT §31).
- **D19 Phenotype dependencies**: the skeleton — zero mandatory; a dialect
  dependency must be vendorable; the build is offline after the first fetch.
- **D20 SLM providers**: local (5090/ollama) — the anchor of determinism; the
  cloud — an accelerator with a response integrity check; determinism = cache +
  gates. CI-exam: a double cold run, the cache diff is empty.
- **D21 Delivery**: the engine — `uv tool install` by git tag; the organism — a
  generated systemd unit on the deployable; docker/k8s — not before an external
  operator's request (F7). MCP stdio — the interface for the LLM, as in v0.

## What we consciously do NOT change relative to v0
Go-stdlib as the first dialect (experience + a single binary + easy to embed the
interpreter); YAML/text as the genome carrier until the F0 spike; SQLite as the
index; MCP as the mouth. Phenotype technology is still a fabric: a decision of
the Placer/dialect, not of the engine.
