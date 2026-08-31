# TRUST.md — what the engine executes, who wrote it, and where the boundary is

Honesty page (PARADIGM_LIMITS §1: prove *containment*, not *content*). If you
run a genome, this is what actually executes on your machine and how far the
guarantees reach.

## What runs, and who authored it

| Tissue | Author | What it is | Gate BEFORE it runs |
|---|---|---|---|
| Rule bodies (Expr) | you (the genome) | a decidable subset of Python | SMT court proves the contracts |
| Skill bodies | an SLM (qwen/…) | Turing-complete Python (algorithms) | property-fuzz + budget + certified cache |
| Islands | you OR an SLM | trusted Python, the only place with network/IO | acceptance cases through the live upstream; drift monitors + REVOKE |
| Dialect phenotype | the printer (no LLM) | Go/JS/Python source | conformance judge + parity + kill -9/replay |

The genome and the printed phenotype are **data you can read**. Skill bodies
and islands are **code that executes**.

## The boundary — stated plainly

- **Skills** run in-process with an AST filter (no import/global/nonlocal, no
  dunder access) and a cleaned `__builtins__`. This is **hygiene, not a
  sandbox**: it stops accidental capability reach, not a determined attacker,
  and it does NOT bound CPU or memory (a skill can loop forever).
- **Islands** run with **no restriction** — they are the trusted corner (they
  need real network/IO by design). The membrane monitors their *behavior*
  (latency, error rate, drift → REVOKE), not their *code*: an island can do
  anything a Python process can.
- Therefore: **running a foreign genome with a foreign skill cache or foreign
  islands executes untrusted code with your privileges.** Today the assumed
  model is *you author your own genomes*; the cache in your repo is yours.

## What IS guaranteed vs what is NOT

- Guaranteed: rule contracts are **proved**; behavioral drift of islands is
  **monitored and revocable**; the printed phenotype is **certified** against
  the reference; determinism behind the growth edge is **cache-replayable**
  (fcold). See `onto attest` for the per-genome passport.
- NOT guaranteed: that skill/island **code** is safe to execute from an
  untrusted source. There is no process isolation, no rlimit, no syscall
  filter yet. Real isolation (subprocess + rlimit + seccomp) is a planned
  wave, needed before a public gene pool exists (SHIP.md; PLAN Tier B).

## The gene pool distributes DNA, not proteins (D85)

A gene is distributed as **contract only** — signatures, properties, intent,
cases, budgets. **Bodies never travel.** A body regrows locally: your own
ribosome synthesizes it against the received contract, through your own gates,
into your own cache. Organisms exchange DNA; each ribosome makes its own
proteins on the spot. So **you never execute a stranger's Turing-complete
code** — there is nothing foreign to sandbox. This dissolves most of the boundary
above structurally, not with a syscall filter.

Residual risk, named honestly: foreign **intent** is text fed to your model —
a prompt-injection vector (intent that talks your ribosome into a backdoor
which passes weak properties). Mitigation, in-spirit: `onto court` runs a
**property-strength gate** (`gate_teeth`) — a gene whose properties a lazy
`return []` oracle can satisfy is REJECTED, so it cannot be installed. Strong
properties are the immune check; a gene without teeth does not enter the pool.

Still-planned (pre-gene-pool wave, replaces seccomp — POSIX, no eternal tail):
capability starvation for locally-grown bodies — subprocess with empty env,
closed fds, `resource.rlimit` (CPU/RSS), plus a determinism double-execution
gate. This is a bounded POSIX mechanism, not a rotating syscall profile.

## Practical rule until then

Treat a genome+cache from someone else like `curl | sh`: read it, or run it
only in a throwaway container. Your own genomes are as safe as your own repo.
