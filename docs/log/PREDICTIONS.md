# PREDICTIONS: predicted scars of v1 (registered 2026-08-20, BEFORE the code)

A mirror of SCARS.md: there — what we stepped on in v0, here — what, by our
estimate, v1 will step on. Check at every phase; the fulfilled ones carry over to SCARS
of the next version marked "predicted." The unfulfilled ones — also data.

| No.  | prediction | where it shows up | early insurance |
|---|---|---|---|
| 1 | **Humans write the contracts** — v0 concern #3 is closed only by the interview mechanism (§11); if the interview generates too many/dumb questions, the operator will start answering "yes-yes-yes" without looking — underdetermination returns in a new form | F2 exam (c), F7 | metric: questions per feature; quality: share of questions that changed the contract |
| 2 | **F1 bloat**: the temptation to drag the dialect/ribosome into the first slice against NOT §26 | F1 | re-scoped: F1 = interpreter without code generation; review the F1 diff for "not a single file in dialects/" |
| 3 | **The dialect interface is wrong after #3**: the skeleton (concurrency, persistence, errors) will spread the dialects apart; "add a language = a catalog" will turn out to be "= a catalog + weeks + certification" | F3, third dialect | the interface is declared unstable until 3 dialects; a dialect certificate makes the cost visible |
| 4 | **Mixins — new islands**: manual labor moved into mixins/, someone has to write and update them for every (body kind × dialect) | F2–F3 | mixins ≤ body kinds (countable); CEGIS counterexamples partly replace examples |
| 5 | **The semantic hash is unstable**: AST normalization changes as the IR grows → cache-epoch after epoch → the v0 pain in a new coat | F2+ every IR growth | normalization is versioned separately from the IR; epoch-metric in the ledger |
| 6 | **The SMT boundary will turn out closer than one would like**: aggregates over collections/invariants over several entities will fall out of the decidable fragment, "proved" will degenerate into a rarity, everything will become "fuzzed" | F2 | the verified passport is honest; the metric of the proved share — in every METRICS; the Expr boundary moves deliberately |
| 7 | **The interpreter crept into a language**: rules will want let/loops/fancier branching — the reference will become "an Erlang of its own" | F1–F4 | a hard AST limit; anything more complex = a skill with an oracle; UNEXPRESSIBLE as a gate |
| 8 | **The judge drifts away from the genome**: flows outside the genome → nobody checks coverage | F1+ | a judge coverage checker (events/rules untouched by any flow — a warning) |
| 9 | **Metabolism = distributed systems at runtime**: JIT warm-up/eviction and layout changes on live traffic — new classes of races that didn't exist in the v0 "build" world | F5 | a rights ladder: auto-molt only within granted rights; the interpreter as an always-correct fallback |
| 10 | **No outsider ever showed up** | F7 | F7 is end-to-end and blocks delivery |
| 11 | **Python delivery will sting the external operator** (F7); mid-way the temptation "let's rewrite the engine in Rust" will arise and eat a month | F5–F7 | uv+lock from day one; a language revision is frozen by decision D14 until after F6 |
| 12 | **Embedded Expr interpreters will diverge in semantics** across dialects (N reference implementations) | F2–F3 | Expr conformance suite — in F1, a dialect without a green suite is not certified (D17) |
| 13 | **The cache in the organism-repo grows without limit** | F4+ | GC by reachability from the genome; cache size — a metric in the ledger |
| 14 | **Z3 is unpredictable in time on aggregates** — the court will start timing out | F2 | a timeout = honest degradation to fuzzed (passport); the share of timeouts — a metric |

## P15 [08-31] ✅ CONFIRMED [08-31]: 4/5 sonnet-green (was 0/5),
2 first-try (tickets, leaderboard); null ~10^-3 (computed post hoc —
honestly; library stayed an island: two-sided accounting under-counted).
FINAL [08-31]: library green in 3 tries after fixing the judge (blind
counterexamples — a gate bug, not a model weakness). P15 result: 5/5.
RECLASSIFIED by D80 (second external review): the "5/5" is in-sample
efficiency; the held-out test (fheldout, 2 unseen domains) shows fan-out
GENERALIZES (green on the 1st) but two-sided accounting does NOT (an island —
lessons transfer unevenly).
## P16 [08-31, Part VII §1.2] ◐ PENDING (N=133/200): informativeness of the loop at N≥200
Upon accumulating ≥200 growth attempts in telemetry, an A/B re-fit will give
LR>3.84 (β>0 significant) OR the negative confirms — then the CEGIS loop is
valuable only via counterexamples-into-cheatsheet, not into the prompt context.
Status: the mechanism computes; N=133 accumulated, the refit is preregistered
at N≥200 (D77/D78).
