# SCARS: what we stepped on in v0 (archgen, 12–19 August 2026)

This is the most valuable document of v1. Each scar is a fact from v0's code or
metrics, not an opinion. Format: **what happened → why → rule for v1**. The
references are to v0.

## 1. The language is wired into seven layers of the engine
- **Fact.** Go lives not in the templates but everywhere: `_gofield`/types in
  `transpile.py` (83 mentions), the DSL compilers print Go expressions directly
  (`_query_go_body`, `_inv_side_go`, `propcheck.py`), the ribosome prompt is a
  Go signature, `strip_code` cuts `package/import/fmt.`, the gates = `go
  vet/test`, `check_skeleton` parses a Go import, `carry_body` renames Go
  literals, `lint_orphans` walks over `gen_*.go`. The attempt at a second
  language (`rust-std`) produced `if dialect.startswith("rust")` in 6 places +
  228 lines of `rustdialect.py` with its own prompt and its own filters.
- **Why.** There was no IR core: dictionaries + Jinja + regex emitters. Parsing
  the DSL and printing to the language were fused into one function.
- **Rule.** The core knows not a single language. A dialect is an object with an
  interface (types, naming, emit(AST), templates, ribosome, gates, skeleton,
  migrate, mixins). Any `if lang` is forbidden in the core. Parse → AST → print
  by the dialect.

## 2. A DSL zoo on regex
- **Fact.** Seven mini-languages (invariants, `views.select`, guard,
  assumptions, skill signatures, propcheck, flows) — seven parsers, not a single
  grammar. A typo in one is silent prose, in another a checker error.
- **Rule.** One expression language with a grammar and types; everything that is
  now a string (`post`, `guard`, `predicate`, `select`, `check`) is an
  expression of this language. One grammar, one type-checker, N printers.

## 3. Constants "from a theorem" are actually from the genome
- **Fact.** `constants.derive`: `RefreshTicks = floor(eps/rate)`, the DKW quota
  — from `q0/delta/calib_M/window/eta_max/eps_frac`, set by hand in YAML;
  `DefectThreshold = 3η` — "series v0-v5"; the Placer: the floor
  `(⌈log₂N⌉+1)·1µs` will never refuse, `substrate = monolith if N<=64` is
  hardcoded. The provenance leads back to other hand-set numbers.
- **Rule.** Provenance stays mandatory, but honest: `derived` (from a formula
  over the measured), `declared` (set by a human), `default` (the engine). No
  declared value is called "from a theorem". A number the engine "derived" from
  a hand-set input is marked `derived-from-declared`.

## 4. Gates weaker than the word "gates"
- **Fact.** "Idempotency" tests the transpiler's dedup, not the body; "fuzzing"
  is a deterministic alternation of qty 1..7 on a single instance; `ruleFree` in
  booking yields `Available > Capacity` — the test doesn't see it; there is one
  mutant, Go text for `sku`, meaningless on other genomes; `lint_orphans` is a
  line-by-line heuristic. EMIG: two bodies with different semantics passed the
  same gates.
- **Rule.** The gates are part of the dialect, but their *content* comes from IR:
  real property-fuzz (rapid/proptest/hypothesis) with generators from the types;
  mutants generated from contracts (inverting a comparison, removing a clamp,
  doubling an increment); a semantic diff of the folded reference log on any
  body regeneration; the gates are obliged to catch at least one class of the
  *undeclared*.

## 5. The genome is no more compact than the code
- **Fact.** T4 (EBATTLE): genome 479 lines vs code 637; a fresh agent reads both
  in full; G is 1.5× dearer than D. `api.events` with auth on every event,
  channels with `carries/consumers`, flows inside the genome, a contract on
  every rule.
- **Rule.** IR is designed from defaults: everything derivable is derived
  (channels from consumers, default auth, `post` optional); flows/judge — outside
  the genome; `explain`/the genome map — a mandatory tool; IR's target metric:
  genome tokens ≤ 1/3 of phenotype tokens on the same domain.

## 6. IR — dictionaries with `extra="allow"`
- **Fact.** pydantic only validates the input, the engine walks over dicts; the
  sections are flat top-level dictionaries linked by name-strings through the
  whole file; `levels` is de facto mandatory; there is no `include/use/extends`;
  `shared_events` from EPIC is not implemented.
- **Rule.** The typed IR is the only thing the core works with. A genome module
  is a closed unit with an explicit interface (exports/requires).

## 7. Code as a changelog
- **Fact.** Diary comments of 10–20 lines inside `ir.py`, `ribosome.py`, the
  templates ("agreed with the template-agent by READING its header"); a
  hardcoded scratchpad path in `gates.py`; 31 commits + a huge uncommitted tail.
- **Rule.** History lives in git and in DESIGN/METRICS, not in the code. A
  comment explains "why it's so", not "who agreed and when". A commit for every
  wave.

## 8. Monolith-centricity and dead services
- **Fact.** The `services` target is legacy under `sku`; `place_workspace`
  respects the pins and nothing else; the hybrid (EPIC's main thesis) does not
  exist in any exam.
- **Rule.** Materialization is a property of an edge/deployable, computed by the
  Placer; the first v1 exam on architecture is one genome, two layouts, bodies
  byte-for-byte shared.

## 9. The harness lied instead of the model (wave 5)
- **Fact.** The first verdict "the SLM doesn't write the algorithm" was an
  artifact: the oracle contradicted the intent, property tests were not
  generated, `equivalence: exact` to an unvalidated oracle; plus Cloudflare lost
  characters, a token limit cut the bodies, the budget was unreachable even by
  the reference.
- **Rule.** Before judging the model — judge the harness: the oracle is validated
  by machine, budgets carry provenance from a reference implementation, providers
  are checked for response integrity. A negative verdict about a model requires
  "the harness is certified" in the report.

## 10. A ladder by size, not by capability
- **Fact.** 7b-coder handled matching, 14b/32b general did not.
- **Rule.** The ladder is ranked by measured capability on a class of tasks
  (ledger telemetry), not by parameter count.

## 11. The ribosome batch hid the failure of one rule
- **Fact.** One hard rule sank a batch of 6; "0/6" was misleading — fixed by
  per-rule materialization.
- **Rule.** Unit of materialization = unit of contract. Always.

## 12. Dedup that "remembers all ids forever"
- **Fact.** A seen-map O(history): in a snapshot of 150k events, 4.6 MB is the
  seen-map.
- **Rule.** at_least_once is paid for by a window (`retry_window`) declared in
  the channel contract; past the window, the same id is not a duplicate by
  contract.

## 13. Contracts underdetermine, and nobody complains
- **Fact.** `room` does not declare `available <= capacity`; the T0 spec was
  contradictory, G "didn't notice" — the contract is not declared, the test is
  not generated.
- **Rule.** The engine is obliged to *suspect*: typical invariants are inferred
  from the shape of the state (bounds, conservation) and proposed as candidates;
  the gates report "covered/not covered" for the state fields.

## 14. Provenance of terms exists, provenance of examples does not
- **Fact.** The rule prompt is a single f-string, with no slot for examples;
  with a custom framework the ribosome is blind.
- **Rule.** Mixins are part of the dialect, a finite curated set; each example
  passes the gates of its kind, and the mixin hash enters the cache key.

## 15. Both arms of the exam are one author
- **Fact.** T0–T3 were written by the engine's builder; the author's knowledge
  was passed off as a property of the genome. Not a single external view in a
  week.
- **Rule.** An exam counts as passed only with a fresh agent/human; an "external
  user" is a milestone, not a wish.

## What was RIGHT in v0 and is carried over unchanged
- The cut: deterministic skeleton / tiny pure bodies from the SLM / gates.
- Content-addressed cache, determinism, ledger, a single write path
  (`propose_mutation`), provenance as a discipline.
- Two-phase ribosome for skills (oracle → fast under budget).
- The method: concern → wave → measurement → honest negative; UNEXPRESSIBLE.
- Migrations by a functor with body carry-over; snapshots with a hash
  certificate.
