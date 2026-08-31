# SPEC v1: ontology compiler (draft 0, 2026-08-19)

Status: specification of the ideal world. Written BEFORE the code. Neighboring
documents: `NOT.md` (what we don't want — checkable), `SCARS.md` (what we
stepped on in v0). Legacy: the theory corpus (semantics) and v0 (archgen —
donor of ideas and scars, not of code).

## 0. One sentence

**A living ontology compiler: the genome is executable on its own (reference
interpreter); code is JIT-materialization of hot paths into any dialect
(language + framework); body correctness is proven where decidable, not chosen
by tests; contract underdetermination is turned into generated
counterexample-questions to the operator; architecture is a control loop over
measured traffic; the model is a swappable enzyme.** Not a scaffolder with an
LLM, and not a generator with a "build" stage.

Three basic shifts relative to v0 (not a "horizon" but a foundation):
1. **from testing to proof** (§9), 2. **from build-time to metabolism** (§10),
3. **from authoring contracts to interviewing with counterexamples** (§11).

## 1. Invariants (checked by CI, a violation = a bug)

| No.  | invariant | how it is checked |
|---|---|---|
| I1 | The core knows no languages | grep-linter over `core/` for language/extension names; `if dialect` is forbidden |
| I2 | Determinism: (genome, cache, version) → byte-for-byte | golden tests for every dialect |
| I3 | Full provenance with an honest class (derived/declared/default) | constant linter — over IR, not over text |
| I4 | Central dogma: writes to the genome only via `propose` with checkers | MCP/CLI have no other path |
| I5 | Unit of materialization = unit of contract | the ribosome cannot batch |
| I6 | The ribosome context is finite and hashable | cache key = hash(IR slice + mixins + model + seed) |
| I7 | Gates catch the undeclared | mandatory mutants from contracts + semantic diff |
| I8 | Ledger of everything | every generation/molt/refusal/model call |
| I9 | Islands are legal and measurable | island share — a metric of every exam |

## 2. Architecture: three floors

```
 genome modules (*.onto)  ──parse──►  IR (typed) + Expr-AST  ──emit──►  dialect
      │                              │                                 │
   imports/interfaces            checkers, Placer,                templates, gates,
   parameterization              constants, migrations            ribosome, mixins
```

### 2.1 Frontend: modular genome
- **Module** — a closed unit: `exports` (events, entities, queries, skills),
  `requires` (events/externals it awaits), `provides` (contracts). Modules are
  parameterized (key types, field names) — like generics.
- **Kinds of modules**: entity-module, channel-module, skill-gene (signature +
  properties + oracle + budget), level/invariant/view — superstructures *over*
  imported modules, external+island — the membrane.
- **Root genome** = list of imports + binding (`bind`) + demand spectrum +
  layout (pins). Contains no bodies, no flows, no per-event auth.
- **Defaults**: channels are inferred from consumers; keys — from entities;
  auth — a default policy with pointwise overrides; `post` is optional;
  scenarios/judge — outside the genome.
- **Composition is checked piecewise**: conservativity (theorem-6-like) —
  per-module; the body cache is carried between genomes when the contract
  matches.
- Target metric: genome tokens ≤ 1/3 of phenotype tokens on the same domain
  (v0: ≈0.75).

### 2.2 IR: typed core
- pydantic/dataclass models without `extra="allow"`; the core works only with IR.
- **One expression language** (`Expr`): types (int, dec, str, bool, enum, list,
  optional, time), aggregates (`sum/count/all/any/filter/first/min/max`),
  lambdas, implication. Used everywhere v0 had a string: `post`, `guard`,
  `conserves`, `invariant.predicate`, `view.select`, `property.check`,
  `assumption`. One grammar, one type-checker, N printers (one per dialect).
- **IR types → dialect types** — a table of the dialect, not of the core.
- Provenance is an attribute of an IR node (`class: derived|declared|default`,
  `formula`, `inputs`), not a comment in the text.

### 2.3 Backend: dialect = language + framework + gates + mixins
A dialect is a directory + a class with an interface. The core calls only the
interface.
```
dialect/<name>/
  dialect.yaml      # manifest: language, framework, version, targets (monolith|service|lib)
  types.yaml        # IR-type -> language type; naming (field/rule/entity/file)
  emit.py           # Expr-AST -> language string (printer); literals; imports
  templates/<target>/…
  ribosome.py       # prompt(rule, examples) / strip / assemble / allowed_imports
  gates.py          # build, lint, test, bench, mutate(contract)->mutant text
  skeleton.py       # import parser for the membrane (islands don't touch the core)
  migrate.py        # rename_in_body(body, renames) — carry bodies over by a functor
  mixins/           # MIXINS: a finite curated set of examples + manifest
```
- **Adding a language/framework = adding a directory.** Not a single core edit.
  Test of invariant I1: `go-stdlib`, `rust-axum`, `python-fastapi` from one
  genome, bodies byte-for-byte by contract (different text — the same meaning,
  verified by the same gates).
- **Mixins** (`mixins/`): `manifest.yaml` describes the `kind` (rule_body,
  handler, repo, skill_naive, skill_fast…), the selection conditions
  (`uses: [sort]`, `has: guard`), and the file itself. Each example *passes the
  gates of its kind* when the dialect is built; the mixin hash is in the
  ribosome cache key. The prompt gets 1–3 examples selected by the rule's
  features — a finite subset, not a repository. A custom framework = a dialect
  with mixins and its own gates; no MCP over a codebase.
- **The dialect's gates** execute, the **content of the gates** comes from IR;
  for the decidable fragment — a court with proofs (§9: body ≡ reference,
  post/inv), fuzzing (rapid/proptest/hypothesis by dialect) — for the rest;
  mutants calibrate the prover; a bench — for skills.

## 3. The ribosome
- Rule/skill bodies are the only thing the model writes; pure functions,
  context O(k): signature + intent + contract + 1–3 mixins.
- The provider is the fabric (local/cloud); the ladder — by measured capability
  on a class of tasks (ledger telemetry), not by size.
- Cache is content-addressed; per-rule; descent down the ladder to the cheapest.
- The CEGIS loop (§9.2): solver counterexamples go into the prompt; escalation —
  when the counterexamples do not converge.
- Two-phase skill (oracle → fast under budget) — as in v0; for rules the oracle
  role is played by the reference interpreter (§10.1) — "two-phase" becomes
  universal.
- A model refusal is not a failure: an island with a record; a verdict about a
  model requires "the harness is certified" (oracle validated by machine, budget
  from the oracle, provider checked for integrity).

## 4. Placer and theory — honestly
- The Placer computes a layout by prices (currencies: latency, freshness, wire,
  capacity, failure independence) and **can refuse with arithmetic**. If the
  decision is a human pin, it is signed as such.
- `theory/` — a catalog of formulas with applicability conditions (lemma 1 TTL,
  DKW quota, HTN floor, γ-compression…); an IR node references a formula
  identifier; the code does not cite theorems in prose.
- Everything theory cannot yet give quantitatively is marked `declared`. The
  list of "where theory actually decides" is a project metric, not a slogan.

## 5. Life: molt, migrations, ledger, warden
- As in v0 (carried over): a migration functor that carries bodies over,
  snapshots with a hash certificate, `propose` as the only write, ledger of
  everything.
- Dedup with a channel window (`retry_window`), declared in the contract.
- Warden: watch → checkers → molt → migration → restart; the monitors subtract
  their own actions; certificate dead → rights revoked.

## 6. Method and exams
- Each wave — concern → design → measurement → METRICS + commit.
- Exams with two arms; passing — only with a fresh agent/human.
- UNEXPRESSIBLE is kept from day one.
- **First vertical slice of v1** (NOT §26, reassembled under §10): parser →
  typecheck → **reference interpreter** → judge. The genome LIVES without a
  single dialect, ribosome, or code generation — the organism exists from day
  one, materialization is connected later as an acceleration. This is radically
  thinner than the slice "IR+dialect+gates+ribosome at once" (see PREDICTIONS
  #2).

## 7. Open questions (to resolve before code)
1. Genome format: YAML with imports or an own text language (`.onto`) with a
   grammar? (YAML drags in v0's `setdefault` disease; an own language means a
   parser.)
2. How far do module "generics" go: parameterization by types or by names only?
3. Where is the boundary "gates from IR" vs "gates of the dialect" for fuzzers
   of different languages — a single generator specification?
4. What to carry over from v0 as code (cache, ledger, migrate, propcheck as the
   seed of Expr) and what to rewrite from scratch (transpile, checkers,
   ribosome prompts)?
5. First second dialect: rust-std (already has a v0 draft) or python-fastapi
   (cheaper for checking I1)?

## 8. Evolution of the lexicon itself (decision, 2026-08-20)

The genome language is also an ontology, and it is obliged to molt by theorem 6.
v0 froze itself: a section per wave, `setdefault` chains, a cache keyed by prompt
text ("byte-for-byte"), `levels` — eternal legacy. Three laws of v1:

1. **The core is minimal, growth is by patterns.** A new capability must first
   try to express itself as a pattern in the core (lesson of ESM: state machine
   = guard, 0 primitives). A new primitive is legal only with a UNEXPRESSIBLE
   entry proving inexpressibility. UNEXPRESSIBLE = the gate for IR growth.
   Core: types, events, entities, rules, contracts, modules. Levels/views/
   invariants — modules over the core, not syntax.
2. **Do not own a lexicon you can avoid owning.** The expression language is
   borrowed (candidate: CEL; alternative: a Starlark subset) — we maintain only
   the allowed subset and the printers to dialects. Structure is data + a
   versioned schema, not an own format.
3. **Hub-and-spoke versioning** (precedent: k8s apiVersion, Rust editions, go
   fix). A genome file carries `onto: N`; in memory — one internal hub-IR; on
   input, converters vN→hub; `onto fix` automatically rewrites genomes to the
   new version; the old one is read for K releases and dies. Dialects and
   checkers see only the hub.
4. **Cache by semantics, not by text.** Key = hash(normal form of the rule
   slice's AST + dialect + mixin hash + model + seed). Improving the prompt does
   not break the cache; a deliberate change of semantics = an explicit
   cache-epoch in the ledger. (Scar: v0 could not improve a prompt without
   losing all bodies.)

Self-application test: an engine that cannot migrate its own language has no
right to promise migration of others' schemas. The versioning mechanism is
introduced in phase 1 with a trivial migration — mechanism before need.


## 9. Proofs instead of samples (base mechanism)

Expr is deliberately not Turing-complete — and this is a prize to be claimed:
rules are tiny pure functions over integers/enums, and their contracts (post,
conserves, guard, invariants) lie in the decidable fragment.

1. **Court-gates.** For the decidable fragment the gates PROVE (SMT/Z3):
   `body ≡ reference` and `post/inv hold` — theorems, not samples. Fuzzing
   remains only where proof does not reach (skills, islands, dialect specifics)
   — and this is honestly marked in the body's attestation:
   `verified: proved | fuzzed | trusted-island`.
2. **CEGIS-ribosome.** The loop: the SLM proposes a body → the solver looks for
   a counterexample → the counterexample (concrete inputs + divergence) goes
   into the prompt → the next attempt. Escalation up the ladder — only when
   counterexamples do not converge. A counterexample is the best possible
   few-shot: it is about THIS rule.
3. **Mutants remain** as calibration of the prover itself (a mutant the solver
   could not tell from the reference = a hole in the SMT encoding of the
   contract).

Requirement for the design of Expr (affects the F0 spike): the semantics must
have a direct SMT encoding (linear integer arithmetic + bounded arrays/sums);
anything that breaks it goes into skills.

## 10. Metabolism instead of build (base mechanism)

"Code is a cache of the genome" — literally:

1. **The organism starts as an interpreter.** Reference semantics (Expr + rule
   assignments) is executable from second zero: slowly, but correct by
   definition. The judge is green BEFORE the first line of generated code. The
   interpreter is two-tier (D17/STACK.md): the canonical one — in the engine; an
   embeddable one — in the generic runtime of every dialect (path eviction
   happens WITHIN the organism's process); correspondence — the Expr
   conformance-suite.
2. **Materialization = JIT.** Ribosome + dialect warm up the hot paths shown by
   MEASURED traffic (or a human pin): a rule body, a handler, a whole
   deployable. The cold honestly stays interpreted; the cooled-down may be
   evicted. The phenotype is a warmed cache with an attestation.
3. **The Placer is a control loop, not a stage.** Prices and demand are measured
   continuously; the layout is recomputed; a molt proposal (spin a service out,
   collapse it back) is a monitoring event, and the decision is by the rights
   ladder (automatic within the granted rights, a human above them).
4. **Deploy disappears as a concept.** There is a genome version and a degree of
   warm-up. Rollback = reverting the genome + regeneration (the cache makes this
   take seconds).

Consequence for the plan: interpreter — F1, code generation — F2+. Consequence
for the gates: §9.1 "body ≡ reference" — the definition of correctness, given
for free.

## 11. Interview with counterexamples (base mechanism; closes v0 concern #3)

An underdetermined contract is not a silent hole but a generator of questions:

1. **Underdetermination detector.** Two candidate bodies (or a body and its
   mutant) pass all declared contracts but are not equivalent → the solver
   SYNTHESIZES an input on which they diverge (u* = argmax of divergence, the v4
   ONTORUNTIME mechanic aimed at the genome).
2. **The question to the operator is an executable example,** not an
   abstraction: "room is full, a free one arrived: available becomes 2 at
   capacity 1 — is that allowed?" The answer options = ready-made contract
   additions (clamp / refuse / invariant).
3. **The answer extends the genome** via propose (the usual checkers), and the
   question is never asked again (the ledger remembers).
4. The same mechanism works when regenerating bodies (the semantic diff of §9
   found a divergence from old behavior → question: intentional?) and when
   mining contracts from legacy (see §12).

The operator stops writing invariants blindly — the system interviews him.
Metric: the share of contract lines in the genome born from interview answers
(expectation: over time > half).

## 12. Gene pool and mining (second echelon of the base)

1. **Gene pool.** A gene = contract + oracle + properties + budget, versioned AS
   A CONTRACT; certified bodies by dialect are the cache with it. A second
   project imports the gene and gets bodies for free (or grows them for its own
   types). The registry is the same content-addressed cache, raised to an
   exchange artifact.
2. **Mining the genome from legacy** (return of mode 1 from ARCHGEN.md v0):
   legacy code + traffic → candidate entities/rules/invariants with
   observational-level certificates → the interview (§11) brings them up to a
   genome. The demand spectrum is MEASURED from traffic, not declared.
3. Both points are built AFTER one organism has lived through a cycle (F6), but
   the IR must not forbid them from day one (a gene is a separate import unit
   already in the F4 composition).
