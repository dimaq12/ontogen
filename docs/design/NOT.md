# NOT: what we do NOT want (v1 anti-spec)

Each item is a refusal that is checked by review or CI. If an item is violated,
it is a v1 bug, even if it "works". The numbering references the scars
(SCARS.md).

## Core
1. **The core knows not a single programming language.** Neither `Go`, nor
   `Rust`, nor filenames like `*.go` in `core/`. A grep over the core for a
   language name = a review error. (S1)
2. **Not a single `if dialect == …` / `if lang` in the core.** A dialect is
   polymorphism, not branching. (S1)
3. **Not a single DSL string parsed by regex.** Every expression goes through
   one grammar and one type-checker. (S2)
4. **The core does not work with genome dictionaries.** Only the typed IR.
   `extra="allow"` is forbidden. (S6)
5. **No Jinja logic.** A template prints the context; the core makes the
   decisions. Conditions more complex than `if has_x` in a template are a smell.

## Genome
6. **We don't want a monolithic 500-line YAML.** The genome is a composition of
   modules with interfaces; the root file is a list of imports and a layout.
   (S5, S6)
7. **We don't want to declare what is derivable.** Channels from consumers,
   default auth, keys from entities — defaults are mandatory. (S5)
8. **We don't want flows/test scenarios inside the genome.** The judge is a
   separate artifact, shared by any arms of a comparison. (S5)
9. **We don't want "a level is mandatory".** All superstructures (levels,
   invariants, views) are optional and live as modules over other modules. (S6)
10. **We don't want brands in the genome.** `postgres`, `axum`, `gin` — only in
    the layout/materialization, never in contracts. (EPIC §5, kept)

## Numbers and theory
11. **We don't want "from a theorem" where a number is set by hand.** Provenance
    with an honest class: derived / declared / default / derived-from-declared.
    (S3)
12. **We don't want a decorative Placer.** A placer that never refuses and
    decides by a hardcoded threshold is not a Placer but a constant. Either it
    computes from prices, or it is honestly called a "pin". (S3, S8)
13. **We don't want references to theorems in code comments if the formula is
    not applied literally.** A reference to theory = formula + applicability
    conditions in one place (the `theory/` catalog); the code references an
    identifier.

## Ribosome and gates
14. **We don't want a large LLM as an executor.** Bodies are written by a cheap
    model with context O(k); the large LLM is only the mouth of the genome.
    Exception — an explicitly marked fallback with a ledger record.
15. **We don't want a prompt without mixins or a mixin without a certificate.**
    An example that did not pass the gates of its kind does not get into the
    prompt. (S14)
16. **We don't want MCP/RAG "over the whole codebase".** The ribosome context is
    a finite, enumerable, hashable subset. If the subset has grown to
    "everything", the dialect is designed wrong. (S14)
17. **We don't want gates that check only the declared.** At least one class of
    the undeclared (mutants from contracts, semantic diff of the fold, inferred
    candidate invariants) is mandatory. (S4, S13)
18. **We don't want batches.** Unit of materialization = unit of contract. (S11)
19. **We don't want a ladder by size.** Only by measured capability. (S10)
20. **We don't want verdicts about a model with an uncertified harness.** (S9)

## Process
21. **We don't want diary comments in the code.** History lives in git/DESIGN.
    (S7)
22. **We don't want exams where both arms are the engine's author.** (S15)
23. **We don't want "passed" without a fresh agent or an external human.** (S15)
24. **We don't want uncommitted waves.** A wave = a commit with METRICS. (S7)
25. **We don't want the dogma of "100% generation".** Islands are legal,
    measurable, under a membrane; their share is a metric, not a sin. (v0
    doctrine DIRT, kept)
26. **We don't want to build everything a second time before the first organism
    lives.** v1 begins with a LIVING interpreted organism (F1: parser →
    typecheck → reference interpreter → judge) — without code generation, not
    with a full IR.
27. **We don't want a "deploy" stage.** There is a genome version and a degree of
    warm-up; rollback = reverting the genome + regeneration. (SPEC §10)
28. **We don't want a "proved" that is actually fuzzed.** A body's attestation
    carries the honest verified class; substituting the class is a gate bug.
    (SPEC §9)
29. **We don't want interview spam.** A question to the operator is generated
    only with an executable counterexample and ready-made contract-addition
    options; the quality metric is the share of questions that changed the
    genome. (SPEC §11)
30. **We don't want state in the engine's git.** Ledger/cache/checkpoints live
    in the organism repo; the ledger is JSONL, no binaries in git;
    __pycache__/build — in .gitignore. (ST3)
31. **We don't want machine-specific paths in the code.** Toolchains — the
    dialect manifest + `onto doctor`. (ST2)
32. **We don't want determinism that depends on the provider.** Determinism =
    cache + gates; the provider fills the misses with an integrity check. (ST6)
33. **We don't want a single repository for the compiler and the organism.**
    (ST5)
34. **We don't want optional/null as a type primitive.** "May be absent" = a
    presence flag (a bool field) or the ""-sentinel for str — it is already
    expressible, and the court stays on the decidable int/str theory. Precedent:
    a state machine = a pattern, not a primitive (v0 wave 3). (U3/D66)
35. **We don't want lists in state.** A list = the POPULATION of a dynamic entity
    (instances: dynamic) — with a key, rules, and a court on every element; the
    theory of arrays in SMT is not bought. (U3/D66)
36. **We don't want decimal/timestamp in the semantics.** Type-2s are a
    REPRESENTATION on the HTTP membrane (D66): the carrier is int everywhere
    (minor units / unix-seconds), the log and replay know only the carrier;
    human forms — always on input, on output via ?repr=human. Float in money is
    contraband forever. (U3)
