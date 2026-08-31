# UNIVERSAL MODEL OF DEVELOPMENT (onto)

The constitution of the method. It answers one question: **how ANY kind of
software is developed on these rails.** Everything below is not a wish but
working mechanisms (exams in exams/, decisions in DECISIONS.md).

---

## 1. Principle

A program is not code but a **genome**: entities, events, executable rules,
contracts. Code is the phenotype: it is printed, proven, and regrown. Development
is not writing code but **expressing meaning + court + life**:

```
intent -> genome (diff) -> GATES (checkers + COURT-prover + interview)
        -> the organism lives (interpreter from second zero)
        -> materialization by heat (go/python/...)
        -> warden: molt, migrations, monitors, revocation of rights
```

No one — neither human nor LLM — writes or edits the phenotype. The only write
path is propose (file/MCP) through the same gates.

## 2. The five layers of any product

| layer | what it is | who writes | guarantee |
|---|---|---|---|
| **CORE** | entities, events, rules, contracts, invariants, sagas (emissions) | human/LLM — via the genome | COURT: proven for all inputs; the interview catches underdetermination |
| **SKILLS** | algorithms (matching, allocation, pricing) | SLM in a CEGIS loop | property-fuzz with teeth + equivalence to the oracle + complexity budget |
| **ISLANDS** | dirt: foreign APIs, crypto, files, custom UI | human, behind a membrane | assumption-Expr -> drift monitors -> revocation of trust; errors don't drop the organism |
| **FABRICS** | languages/frameworks/stores (go, python, jsonl, sqlite) | dialect plugins | conformance corpus; the fold is byte-identical across fabrics |
| **SURFACES** | API, queries, admin panel, webhooks | printed from the genome | parity: one judge across all substrates |

Meaning lives only in the CORE layer. Everything else is replaceable.

## 3. The development cycle (an operator's day)

1. `onto explain <root> <entity>` — read a slice, not everything (O(k)).
2. Edit the genome (or propose via MCP from any LLM).
3. The gates automatically: typecheck -> conservativity (a breaking change —
   only with a migration functor) -> COURT (contracts proven; a counterexample =
   a refusal with a concrete input) -> semdiff (behavior changed under the same
   contracts = a QUESTION with an executable example; ack = the answer).
4. The warden molts in seconds: the log is migrated with a backup, the state is
   recomputed, old behavior cannot be smuggled through unproven.
5. Life: heat is measured; the Placer proposes spin-out/collapse with
   arithmetic; monitor quotas revoke rights; everything is a ledger event.

There is no hotfix: you edit the genome, the code regrows.

## 4. Roles of intelligence

- **Human**: meaning (genome), interview answers, islands, acceptance of
  proposals.
- **Large LLM**: the mouth of the genome (MCP propose) — sees the genome and the
  reports, not the code.
- **Cheap SLM**: skill bodies in the CEGIS loop (court counterexamples go into
  the prompt).
- **Court (SMT)**: proofs instead of tests where decidable; an honest attestation
  proved|fuzzed; mutants calibrate the judge itself.
- **No intelligence at runtime**: the organism is deterministic.

## 5. The physics of coverage (honest)

The model covers software that has STATE AND RULES — that is, almost all of it.
What changes is the share of the provable core:

| category | core from the genome | skills | islands |
|---|---|---|---|
| SaaS/accounting/billing/booking | ~85–90% | a little | payments, IdP |
| marketplace/fintech | ~70% | matching, scoring | gateways, KYC |
| games | economy/inventory/accounts | matchmaking | render, gameplay |
| ML products | orchestration, accounting, quotas | post-processing | model behind a membrane |
| OS/drivers/browsers | — not our kind of life — | | |

An island is not a defeat: it is behind a membrane, with assumptions and
revocation of trust.

## 6. What already works (exams green)

Executable genome; a court with proofs and equivalent mutants; interview with
counterexamples in the flow; three substrates with one judge; gene composition
(payments in 3 domains byte-for-byte); dynamic instances; str-state;
emissions/sagas with a trace in the response; metabolism by heat; warden with
migrations and REVOKE; CEGIS-ribosome (~$0.001/skill); membrane; jsonl+sqlite;
25k ev/s, p99 1.8ms; the Lago core as a real reference.

## 7. The "UNIVERSAL" roadmap (in descending order of pain)

- **U1 Queries/read-models**: parametrics, filters, pagination, projections —
  without these there is no real API. BLOCKED by nothing — the next wave.
- **U2 Time**: timers/schedules as a warden organ, not an external job.
- **U3 Type-2s** ✅ (D66): decimal, timestamp — representation on the membrane;
  optional/list-state rejected as primitives (NOT §34-35).
- **U4 Auth-gene** ✅ (D67): roles/predicates on our Expr; IdP — an island;
  deny-by-default.
- **U5 UI-dialect**: admin panel/CRUD are printed from the genome; custom UI —
  an island with a typed SDK generated from the genome.
- **U6 Outward**: webhooks from emissions, queues, the blob pattern.
- **U7 Skills in all fabrics** ✅ (D71): printing bodies into the python-fabric,
  RPC to the canon from go. Related: the dialect generator is grown by the model
  (D68) ✅.
- **U8 Packaging**: onto new <template>, an operator web console (ledger,
  interview questions with buttons, molt proposals), freezing IR v1.0, a
  template gallery (lago/hotel/market), a tutorial.
- **Cross-cutting**: calendar life, foreign hands — the only exams that cannot be
  passed from within.

The point "the model is visible in full": **U1+U2+U5** — a complete SaaS product
(API + time + admin panel) from the genome, zero handwritten code.

## 8. Guarantees and non-guarantees

We give: proven contracts; the impossibility of a silent behavior change;
surviving a change of language/framework/store; lossless migrations with a
backup; kill -9 is safe; full provenance of numbers; the ledger answers "why".
We do NOT give: correctness of underdetermined meaning (the interview only
uncovers it); correctness of islands (we only monitor them); performance beyond
the measured. IR v1.0 is frozen (D72).
The end-to-end formula of contribution (and the boundary of promises,
PARADIGM_LIMITS.md): the paradigm translates uncertainty from SILENT into
visible, measurable, and revocable — it drives it behind a membrane, declares it
an assumption, and puts a monitor with revocation on it.
