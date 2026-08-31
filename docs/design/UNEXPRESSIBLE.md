# UNEXPRESSIBLE: a diary of the inexpressible (the gate for IR growth — SPEC §8.1)

What did NOT fit into the genome/Expr and why. A new primitive is legal only via
an entry here with a proof that it is inexpressible by a pattern.

| date | what | F1 decision | next |
|---|---|---|---|
| 08-20 | division/remainder by zero | EvalError -> the transition is rejected + ledger (eval_error) | candidate: an explicit divisor contract (a guard hint from the checker) |
| 08-20 | per-channel dedup windows | retry_window — the GENOME level (D26) | F4: channels return with composition — the window becomes a channel contract |
| 08-20 | str in expressions | only ==/!= (routing keys) | concatenation/prefix — only if an inexpressible pattern appears |
| 08-20 | state fields other than int | state: int only | enum/str phases — at the first real genome where numeric flags lie |
| 08-20 | judge coverage checker (P8) | not implemented, coverage by eye | F2: a warning "an event/rule is untouched by any flow" |
| 08-20 | dialect int64 vs the mathematical int of the canon/court | int64 overflow is outside the court's model; conformance catches only small values | a field-range contract (min/max in state) -> the court gets bounds, the dialect gets a check |
| 08-20 | floor-semantics // and % | Go's truncated division -> helpers floorDiv/floorMod (caught by the conformance corpus); SMT div matches floor only when the divisor > 0 | court: a precondition of divisor positivity, otherwise the attestation is fuzzed |
| 08-20 | parameterizing a module by BEHAVIOR (a rule over a foreign event-parameter) | against D2: types/instances only; payments is made a closed genome with its OWN events | if two domains require linking a foreign event to a gene's body — a "bridge-rule" pattern in the root? record it at the first real case |
| 08-20 | module version + functor (extending a supplier) | F4 links by file path, there are no module versions | F6: a gene manifest (name+version+contract hash), migrating importers by a functor |
| 08-20 | printing skills into go/other dialects | the skill is judged and lives in the canon's language (D39); the go-phenotype so far calls it... in no way — skills are not connected to the organism | the "skill in the organism" wave: a rule calls a skill (rule -> skill call in Expr?) + printing the body into the dialect or RPC to the canon |
| 08-20 | skill sandbox as a security boundary | this is hygiene (no import/dunder), not a sandbox | if a foreign operator appears — judge in a separate process with rlimit |
| 08-20 | the seen-window in a snapshot | the snapshot carries seen_q (the window, not the whole history — S12 not reproduced) | ok as is |
| 08-20 | ~~p99 latency under HTTP load~~ CLOSED (RELEASE 0.1: p99=1.8ms, sqlite WAL) | — | — |
| 08-20 | assumptions over p95/quantiles | window statistics = max latency + error% (no quantiles) | add p95 to stats when a real SLA requires it |
| 08-20 | hints to the fuzz generator (unique_by, value pools) in a skill contract | D45 hardcoded the id/category heuristic | a field fuzz: {field: unique|pool[n]} in Skill — at the next skill with a different shape |
| 08-20 | "after transition X" in contracts (temporal post) | expressible via a conditional post (D47), but not obvious to the operator | a template/checker hint: "a conjunction with a pre-variable? suggest the conditional form" |
| 08-20 | ~~event emission by a rule~~ CLOSED (D54: Rule.emit, cascade, cap 8) | — | compensation BY AN INVARIANT (not by a rule) — a separate trigger, awaits a case |
| 08-20 | COUNT_UNIQUE (a set in state) | there are no set-states | a skill with snapshot semantics or a set-type state — at a real metric |
| 08-20 | ~~per-customer wallet~~ CLOSED (D54: saga close_period -> ApplyCredits -> wallet -> CreditsApplied) | — | — |
| 08-20 | ~~invoice as an object~~ CLOSED (D56: a dynamic entity via emission) | — | line items — at a real UI |
| 08-20 | ~~graduated~~ CLOSED (IfExp pattern); volume/percentage — the same trick | — | — |
| 08-20 | an invariant over the WHOLE population of dynamic instances = O(N) per event | L5: 1.5k ev/s over 200 subscriptions (money_conserved scans all of them) | incremental invariants (maintained sums) — at pain on a real volume |
| 08-20 | ~~subscription->customer link in a job event~~ CLOSED (D55) | — | — |
| 08-20 | court of cascades (equivalence through emissions) | prove_equiv — per-rule; a change of emit = always a question | symbolic composition of transitions along the emission chain — a research wave |

## 2026-08-30 · boundary revision: the data plane (the maintainer's concern)
"Byte blobs/pipelines are inexpressible" — NO LONGER accepted as an eternal
boundary: the class has mathematics (references + probes + hash idempotency), the
design is DATAPLANE.md (U9). What stays eternal is only the perception of
quality.

## 2026-08-31 · certification boundaries of grown dialects (D80)
The grown node-generator translates // as Math.floor (matching the canon), but
leaves % with JS semantics (the sign of the DIVIDEND; Python — the sign of the
divisor): organisms are certified BY THE GATES ON THEIR OWN GENOMES — a genome
with negative moduli must re-pass parity. The court with D80 computes exactly
like the canon (floor, divisor≠0 — an obligation).
