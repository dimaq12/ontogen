# PLAN v1: implementation phases (draft 1, 2026-08-20 — reassembled under SPEC §9–12)

Rules: one phase = one risk removed = one exam. The key difference from draft 0:
**interpreter-first** (SPEC §10) — the organism lives from F1 with no code
generation at all; dialects and the ribosome are connected as acceleration. This
makes the first slice thin (PREDICTIONS #2) and gives §9's definition of
correctness for free. From v0 we carry over as code: the cache mechanics, the
ledger, the migrate functors, propcheck (the embryo of Expr), the gate runner.
The method (wave → design → METRICS → commit; UNEXPRESSIBLE as the gate for IR
growth) — unchanged.

## F0 "Decisions and skeleton" — ✅ PASSED 2026-08-20
- Closed: D11 (YAML+onto:N), D12 (python-fastapi second), D22 (the name onto),
  D23 (Expr = a py-ast subset; the spike spikes/expr/ — the SMT court already
  demonstrated: post proven, mutant caught).
- Repo skeleton core/ dialects/ theory/ exams/ (uv, lock, pinned 3.13 — D14);
  CI linters (I1, provenance, ban on extra=allow); `onto: N` + hub + trivial
  migration.
- EXAM: the linters go red on planted violations.

## F1 "Living reference" — ✅ PASSED 2026-08-20 (exam 5/5, 0.5 s)
- Parser → hub-IR → typecheck → **reference interpreter** (Expr + rule
  assignments) + event log + replay. ZERO code generation, ZERO SLM.
- **Expr conformance-suite** (D17): a corpus (expression, input) → reference
  output, generated from the canonical interpreter — future embeddable dialect
  interpreters are certified by it (P12: laid down HERE).
- The judge (external, black box) drives the interpreted organism over HTTP.
- EXAM PASSED (exams/f1.py): the judge 5/5 flows over HTTP on the pure
  interpreter; kill -9 → replay byte-for-byte (including the dedup window); a
  smuggler-algorithm (204 nodes) rejected as "this is a skill"; the
  invariant-observer writes to the ledger. 21 pytest, a conformance corpus of
  240 cases committed. ZERO code generation and SLM — P2 held.

## F2 "The court and the first fabric" — ✅ PASSED 2026-08-20 (exam 9/9, 7.2 s)
- SMT encoding of contracts; court-gates: body ≡ reference, post/inv — proven;
  mutants as prover calibration; attestation verified: proved|fuzzed.
- CEGIS-ribosome: SLM ↔ solver counterexamples; the ladder by capability.
- The go-stdlib dialect as a plugin (the interface of SPEC §2.3): skeleton + an
  EMBEDDABLE Expr-interpreter (a green conformance-suite = the condition for the
  dialect's certificate) + JIT warm-up of hot rules (by pin so far, traffic —
  F5).
- **Interview with counterexamples** (§11) on an underdetermined contract.
- EXAM PASSED (exams/f2.py, 9/9): (a) all post PROVED, 21/21 mutants
  distinguished, no blind spots; (b) the interview printed a question on the
  scar-13 corner (booked=0) with two valid options, the guard-answer makes the
  candidates provably ≡; (c) the go-fabric: the judge 5/5 (THE SAME judge), kill
  -9 -> replay, conformance 240/240 (would have caught floor-div!), byte-for-byte
  generation, the warmed path ~29,000x (the full path with the JSON envelope
  9.4x).
- Deviation from the letter: a live SLM was not connected — D27 (printer = rung 0)
  made it unnecessary for rules; the CEGIS mechanics (counterexamples) are built
  and work in the court/interview; the SLM will appear with skills (F3+).

## F3 "The second language" — ✅ PASSED 2026-08-20 (exam 9/9, 1.8 s)
- python-fastapi (or rust) second; a dialect certificate.
- EXAM PASSED (exams/f3.py, 9/9): one genome → THREE substrates (reference
  interpreter, go, python), ONE judge 5/5 across all, state snapshots
  byte-identical, both dialect certificates 240/240, the git diff of the core
  from the F2 commit EMPTY — I1 proven in practice. The python printer =
  ast.unparse (D23's promise "the second language almost for free" came true: the
  dialect is ~450 lines against go's ~700).

## F4 "Composition and genes" — ✅ PASSED 2026-08-20 (exam 10/10, 2.9 s)
- import/exports/requires, parameterization by types; a gene as a unit of import
  (the gene pool §12.1 — the format, without a public registry).
- Defaults; explain O(k); the ≤ 1/3 metric.
- EXAM PASSED (exams/f4.py, 10/10): hotel = 3 genes (rooms+reservations+
  payments), shop reuses payments AS IS; the judge green on the interpreter AND
  go for both; printed wallet bodies byte-for-byte in two phenotypes (analogue of
  "the body cache moved over" under D27); the court proves the linked contracts;
  genome/phenotype = 0.19 (target <= 1/3); explain-slice 37%. "A fresh agent over
  the explain-slice" — honestly deferred to F7 (a measurement, not a mechanism).
  Bonus find: the court PROVED the equivalence of a mutant (D32).

## F5 "Metabolism" — ✅ PASSED 2026-08-20 (exam 8/8; mark restored 08-30 by commit 94a4095 — PLAN was lagging)
- Measuring traffic/prices; the Placer as a control loop; JIT by measured heat;
  eviction of the cooled-down; a molt proposal as an event.
- theory/ formulas + provenance classes in action; measured supplants declared.
- EXAM: (a) a shift in the load profile → the system ITSELF proposes spinning out
  the hot domain, molt by the rights ladder, bodies shared (cache); (b) a
  deliberately impossible demand → a refusal with arithmetic; (c) the METRICS
  table "formula → decisions" is non-empty.

## F6 "Life" — ✅ MECHANISMS PASSED 2026-08-20 (exam 9/9, 2.3 s); a calendar week/month — a background criterion
- Done: warden (watch -> checkers -> molt with log migration by a functor and a
  restart 0.3s -> monitors -> placer-tick with the rights ladder); migration =
  rewriting the log, the state is recomputed by replay (D35); subtracting one's
  own actions (D36); REVOKE by quota (provenance in the ledger); the warden
  survives broken mutations (D37).
- EXAM (mechanisms, exams/f6.py 9/9): a feature by genome only; a schema change
  without a functor rejected / with a functor migrated (backup, balance
  preserved); a storm -> REVOKE; auto-molt by heat under interventional.
- IN THE BACKGROUND until v1 is delivered (together with F7): a calendar
  week/month of real life; a live traffic seam monolith<->service; module
  versions (UNEXPRESSIBLE).

## F7 "Foreign hands" — ◐ FIRST POINT 2026-08-20 (a fresh agent: PASSED on the first try)
- Mini-F7: a fresh agent with no context, input only CLAUDE.md+repo; a freeze
  feature (event+field+rule+guard) via the genome; validate+court green on the
  FIRST try, a live test noop(guard) after the freeze, the shared gene shop not
  broken. Agent's estimate: 20-30 min for a human from scratch, ~5 for an
  experienced one.
- DX findings (closed/noted): there is NO operator doc (the /event format, the
  endpoints — reconstructed from exams) -> docs/OPERATOR.md written; --help is
  one-line (strengthen as needed); the default init=0 lived in a comment ->
  documented in OPERATOR.md.
- REMAINING for full delivery of F7: a human operator (not an agent) and/or a
  clean machine + the calendar life of F6.
- A fresh agent/external human at every exam; a separate final one: a
  non-author operator runs a feature+migration, metrics of time and of what was
  read.
- Without F7, v1 is not delivered.

## Wave "skills + live SLM" — ✅ PASSED 2026-08-20 (exam 5/5, 7.6 s; ~2.8k tokens)
- Skill-gene in IR (params/returns/types/intent/properties/budget/ladder);
  properties — Expr with a completeness tooth (gate_teeth: a lazy oracle is
  obliged to fall); two-phase ribosome: naive (property-fuzz) -> fast
  (equivalence + complexity budget D38); LIVE CEGIS: qwen3-coder red->GREEN by a
  counterexample on the 2nd attempt; the cache is semantic (D6) — a repeat with
  no network; usage telemetry. The harness lessons of the wave: type constructors
  in the sandbox (the model writes Order(...)), argument order = signature order,
  the falsity of the speed budget (D38).

## Wave "connective fabric" — ✅ PASSED 2026-08-20 (exam 8/8, 3.5 s)
- Court+semdiff in the FLOW of mutations (mutgate, D40): the warden and propose
  judge with the same gates; a behavior change without ack — an executable
  question, ack — a molt.
- A skill — an organ of the organism (D41): /skill/<name> from the certified
  cache.
- MCP-mouth (D42): genome_read/validate/court/explain/propose/ledger_tail.
- Warden daemon CLI (onto warden) + a systemd unit (onto unit); the uv tool
  install delivery verified (a global onto).
- Remaining from the fabric (honestly): printing skills into go, per-rule
  in-process JIT (D28), the live traffic seam — on real need.

## Wave "DIRT AND VOLUME" — ✅ PASSED 2026-08-20 (exam 8/8, 30 s; a v0-class stress battery)
- Built: the membrane (externals+islands+drift monitors on Expr, D43), snapshots
  with a hash certificate + tolerant replay (D44), ThreadingHTTPServer.
- Numbers: 200k events, ingest 27k ev/s (fsync); the snapshot cuts cold start
  x100 (0.05s vs 4.7s), the folds identical; a broken snapshot rejected by hash;
  a torn line survived; a storm of 10k retries repelled; 5 kinds of garbage
  classified; 8 threads — the money adds up to the penny; a LIVE /ext/convert
  through a flaky API (the v0 debt closed): drift caught, trust revoked
  (cert_valid=false); a big genome 20x8: the court 3s over 160 rules
  (18ms/rule — P6 doesn't bite yet), the organism 24k ev/s, go build OK.

## Wave "MEGADIRT" — ✅ PASSED 2026-08-20 (exam 12/12, 16 s)
- The market domain: 7 genes (payments — the THIRD reuse; commerce_events — a
  shared vocabulary, D46), 6 entities/17 rules/15 events, order and ticket state
  machines, 3 flaky integrations, a live SLM-skill allocate.
- Facts: the court on the mix ALL PROVED 0.4s; the fuzzy cancel contract
  uncovered by the interview, a conditional post distinguished it (D47); the
  fuzz-pool uncovered the fuzziness of allocate — the contract refined, the
  ribosome resynthesized (D45/D6); 30k lifecycle events 10k ev/s
  (fsync+invariants), a deterministic race caught by the observer; kill -9 ->
  0.01s from a snapshot; the gateway demoted (cert_valid=false), tracker/fraud
  within tolerances; the judge 4/4 under load; migration points->pts on live 30k:
  without a functor a refusal, with a functor 0.4s downtime, points to the point.

## Wave "RELEASE 0.1" — ✅ PASSED 2026-08-20 (exam 6/6; ALL CHECKS GREEN)
- EventStore (D48): the sqlite fabric (WAL) on par with jsonl — 26k ev/s, the
  judge 4/4 on a real DB, migration by a functor over the .db with a backup, the
  folds byte-identical; p99 under HTTP = 1.8ms (the UNEXPRESSIBLE debt closed).
- README.md, docs/OPERATOR.md, tools/check.sh (the CI entry: lint+tests+5 exams),
  version 0.1.0, tag v1-0.1.0.
- Rake of the day: sqlite thread-affinity against multi-threaded HTTP (a classic
  of real projects) and a zombie server on the port that masked the fix.

## LAGO campaign — ✅ v0 SLICE PASSED 2026-08-20 (exam 6/6, 29 s)
- Reference source: Lago (open-source usage-based billing); the semantics taken
  from their docs (lago/SPEC.md), the judge mirrors their API examples.
- Waves demanded by the domain: DYNAMIC INSTANCES (D51 — in all three fabrics),
  a body cap of 256 (D52).
- Facts: the court PROVED invoicing (including a counterexample -99 -> the
  induction lesson D53); the judge 6/6 on the interpreter AND go (lifecycle,
  transaction_id idempotency, invoice fee+charges-credits = 5454/2454¢, fresh
  periods, a dynamic second subscription, termination); the billing job through
  the warden; 200 dynamic subscriptions x 200 events — invoices 200/200 matched
  an independent model. The tail of expressibility — in UNEXPRESSIBLE
  (count_unique, per-customer wallet, invoice read-model, graduated).

## Wave POLICIES + LAGO slice v1 — ✅ PASSED 2026-08-20 (flago 6/6, policies 4/4)
- D54: Rule.emit — derived events from the post-state; a synchronous cascade, cap
  8; NOT logged (recomputation by replay = determinism for free); all three
  fabrics; a change of emission = a mutgate question (cascades are unprovable).
- Lago v1: a per-CUSTOMER wallet (as in the original) — the SAGA close_period ->
  ApplyCredits -> wallet -> CreditsApplied -> debit from due; the judge: a shared
  wallet over a customer's two subscriptions (5454 out of 6000, the remaining 98
  eaten by the second period), interp AND go; 200 subscriptions/40k events —
  saga-invoices and wallets 200/200 against an independent model.

## LAGO slice v2 — ✅ PASSED 2026-08-20 (flago 6/6; ALL CHECKS GREEN)
- D55 str-state (all fabrics + court); D56 the invoice registry — a dynamic
  entity via emission, a two-key saga fan-out; graduated — IfExp.
- The judge: /state/invoice/INV-1 {total 5454, due 2454, applied 3000},
  invoices_due 7258; volume: 200/200 invoices+registry+wallets against an
  independent model. The cascade in outcomes = a free saga trace.
- Hygiene: zombie organisms with an old schema masked the green twice — pkill
  (escaped) in check.sh; there too — the eternal rake of pkill-suicide.

## Wave "GROWING A DIALECT" — ✅ PASSED 2026-08-30 (fgrow 5/5)
- IDEAL jewel 5 demonstrated: a NEW LANGUAGE (Node.js) for hotel grown by a weak
  model on the 1st try — without a human, without a core edit (a git check in the
  exam); certification: the same judge 4/4 + fold parity over all instances +
  kill -9/replay. "Any language" — a property of the system (D58). Cost: ~$0.02.

## Wave "THE MODEL GROWS ISLANDS" — ✅ PASSED 2026-08-30 (fisland 7/7, 5.3 s)
- growisland.py (D63): the SLM writes an island-adapter from an external spec
  (intent+cases — the IR growth is additive); the gates: import-membrane ->
  ACCEPTANCE THROUGH A LIVE FLAKE (MonitoredAdapter: without retries the cases go
  red) -> attestation cert_valid; CEGIS; the cache = a certified artifact; the
  CLI `onto growisland`.
- FACT: the fx-adapter grown by qwen3-coder on the 1st TRY (8 requests to the
  mock for 6 cases — retries written), the gate teeth verified with plants
  (subprocess, an adapter without retries), REVOKE on total failure, a
  cache-repeat with no network.
- Find of the wave: the gates judged the wrong file (ext.island vs island_rel) —
  caught by the exam's tooth; a manual island stays a legal exception.
- All three IDEAL jewels demonstrated: (3) the product U1-U6, (4) islands, (5)
  dialects. ALL CHECKS GREEN.

## CARTE BLANCHE "THE IDEAL VERSION" — ✅ PASSED 2026-08-30 (fideal 10/10)
The end-to-end IDEAL cycle works in full: a natural-language description (meeting rooms,
with the phrase "collect on a schedule by itself") -> Sonnet builds the
genome+acceptance -> the COURT ALL PROVED -> the organism lives (the judge 4/4)
-> the timer ticks by itself (D59) -> /list+parametrics (D60), /admin from the
genome (D61), webhooks outward (D62) -> a node-organism grown by qwen -> onto new
(D65). Waves: A NL-front (D64), B time, C queries, D admin, E webhooks, F
packaging. The NL/ideal exams are networked — not part of CI (the cache makes
repeats free).

## Waves U3+U4 — ✅ PASSED 2026-08-30 (ftypes2 10/10, fauth 12/12)
U3 (D66): decimal/timestamp = representation on the membrane, the carrier int —
court/log/replay/dialects are blind to the forms; optional/list-state rejected as
primitives (NOT §34-36). U4 (D67): auth-gene — predicates on Expr, an IdP-island,
deny-by-default, ledger-provenance of refusals. Both exams in CI.

## Wave GENERATOR GROWTH — ✅ PASSED 2026-08-30 (fgengrow 4/4)
Jewel 5 built out to rung 2 (D68): the model wrote the node-dialect emitter
ITSELF, certified by multi-genome CEGIS (3 genomes), a fresh genome is printed
without the model. build/gen_node/emitgen.py — the artifact.

## Wave U8-CONSOLE — ✅ PASSED 2026-08-30 (fops 6/6); release 0.3.0
/ops: ledger+filters+attestations+checkpoint (D69). The remainder of the
constitution: U7 (skills in go-print/RPC), a web-interview with buttons, freezing
IR v1.0 (after U7), calendar life, F7 (foreign hands).

## Wave U7 + FREEZE — ✅ PASSED 2026-08-30 (fy7 7/7); RELEASE 1.0.0
U7 (D71): skills are printed into the python-fabric, go — RPC to the canon;
parity 0 divergences on fuzz. Freeze of IR v1.0 (D72): a schema fingerprint + the
test_freeze tooth. THE CONSTITUTION U1-U8 IS CLOSED IN FULL. The remainder
outside code: the web-interview (the CLI exists), calendar life, F7 (foreign
hands).

## THE MAIN EXAM — ✅ PASSED 2026-08-30 (fgauntlet 10/10)
"Any software product": 8/8 distant domains assembled and proven (D73), the
inexpressible rejected honestly. Observation for a future wave: 5/8 required
Opus — the cheatsheet can be further trained on the gauntlet's counterexamples so
that Sonnet converges more often (economics, not correctness).

## Wave D74 — ✅ PASSED 2026-08-30 (fparadigm 13/13, fcold 4/4)
All the solvable shortcomings of PARADIGM_LIMITS are removed by mechanisms:
attest (attestation+the weakest seam, 1+5+9), harden (hardening, 3), ignorance
(4), declared_loss (6), fcold (8), engine.pin (11). fparadigm in CI.

## EPIC "MATHEMATICS" (D75) — wave 1 ✅ PASSED 2026-08-31 (fmath 9/9, in CI)
Waves 1-5 ✅ (D75, D76): Part VII v2 (after the adversarial review —
math/REVIEW_1.md), P15 confirmed (4/5), the spectral step done (fspectral in CI,
a two-component detector), attest with DKW and hazard. The rest of the epic ✅
PASSED (D77): a spectral audit in the warden (faudit), in-situ VII.1'
(fcompose), library 5/5 (the judge rake fixed), the P16-mechanism computes
(N=133/200). The ν-BRIDGE ✅ (D78, fnu 7/7): the fuzz/prod gap closed by VII.2 +
ν-monitoring in the warden. The epic is open: P16-refit (N=133/200),
attest-composition of the end-to-end path, state-dependent transfer,
κ-attestation, open-3 (Γ-fabrics) untouched.

## PRODUCT FREEZE 1.1.0 — ✅ 2026-08-31 (D79, FREEZE_v1.md)
attest of end-to-end paths, complete OPERATOR/CLI, the warden ticks all organs,
calendar life launched (life/). What remains to be delivered: time (life),
telemetry (P16: 133/200), and the operator's hands (F7).

## Wave "SECOND EXTERNAL REVIEW" — ✅ PASSED 2026-08-31 (D80, test_review2.py 8/8 in CI)
All six holes in the heart confirmed by reproductions and removed (+3 class
findings): (1) floor-division semantics in the court (exact floor encoding +
divisor≠0 obligation; JS % boundary recorded in UNEXPRESSIBLE); (2) "proved" was
self-induction → entity induction by the Houdini algorithm, the gallery is now
entity-inductive and the passport distinguishes the two; (3) mutgate no longer
swallows unknown (I7); (4) full population reset on a broken snapshot + dynamic;
(5) the hash chain is actually verified (Ledger.verify + kind in hv=2); (6) attest
no longer lies about runtime-checked invariants. Methodology: P15 is reclassified
as in-sample efficiency; the held-out test (fheldout) shows fan-out generalizes,
two-sided accounting does not (an island).

## Wave "SHIPPED IN ENGLISH" — ✅ PASSED 2026-08-31 (D81, CI green)
All prose/comments/docstrings/printed strings/theory translated Russian→English
(parallel agents over disjoint file groups); phase/wave ID tokens transliterated
1:1 to Latin. The freeze was hardened so schema_fingerprint strips
description/title — the freeze guards STRUCTURE, so a docstring translation is not
a format change (fingerprint rebaselined). Runtime loads skills by name.phase and
islands by path, so translation touches only growth caches (network exams).

## Wave "P2 DELIVERY WIRING" — ✅ PASSED 2026-08-31 (D82, finit)
`onto init` (scaffold.py) couples a project to the engine+harness in one shot:
.onto/{cache,ledger,checkpoints,hooks} + genome starter + engine.pin +
config.toml.example + .gitignore; for the Claude harness — .mcp.json, a workflow
skill, a CLAUDE.md fragment, and the PreToolUse EDIT-GUARD HOOK that mechanically
blocks Edit/Write to onto-owned paths and routes the harness to `propose` (I4
turned into a rail). Ownership is explicit (.onto/owned.json). Closes the delivery
gap, not architecture.

## Wave "TIER A" — ✅ PASSED 2026-08-31 (D83, ftier_a 11/11 in CI)
Pre-release math dial-up, zero new mechanisms, no compromise with "proved": #5
invariants over one entity with fixed instances now PROVED inductively (passport
splits invariant proved|monitored; cross-entity/dynamic stay honestly monitored);
#8 the spectral organ gets hands — a tick_spectral verdict DEMOTES rights +
records a recalibrate_proposal (a formula that acts, NOT S3); #10 `onto replay
--until <event>` — read-only time-machine debugger into a scratch dir; #4
entity-court named the strong guarantee ("post rejection impossible from init").

## Wave "TIER B cheap pair" — ✅ PASSED 2026-08-31 (D84, fvariants 5/5 in CI)
#6 the interview now PROPOSES completion variants (interview.generate_variants),
each certified by the court (§11's promised A/B/don't-know); on the F2 booking case
it re-discovers 's.booked > 0' unaided; unresolved → the U12 "I don't know"
fallback. TRUST.md: honest execution-boundary page (what runs, who authored it,
skills are hygiene-not-sandbox, a foreign genome+cache runs untrusted code). Real
process isolation (rlimit+seccomp) and full LSP deferred to pre-gene-pool /
post-release.

## Wave "GENE POOL = DNA NOT PROTEINS + FREE IDE" — ✅ PASSED 2026-08-31 (D85, fgene 6/6 in CI)
Three moves that dissolve the seccomp/LSP tails instead of paying them: (1) a gene
distributes as CONTRACT ONLY — bodies never travel, the body regrows locally via
the local ribosome/gates/cache, so you never execute a stranger's Turing-complete
code (foreign intent is the residual injection vector → gate_teeth is the immune
check, a toothless gene is rejected by court); (2) local-body isolation re-scoped
to bounded POSIX capability-starvation, deferred to the pre-gene-pool wave; (3)
frozen IR = free IDE — `onto schema` dumps JSON Schema from pydantic + a modeline
(yaml-language-server gives autocomplete/diagnostics) and `onto watch` gives live
Expr diagnostics — zero tail, no LSP.

## Wave "MODEL REGISTRY" — ✅ PASSED 2026-08-31 (D86, fmodels 11/11 in CI)
A real provider/model registry in the ribosome (Claude-Code/Kilo-Code style): any
number of named OpenAI-compatible providers, base_url presets, models as
'provider:model' or bare, safe key resolution (${ENV}/$ENV/@file/literal),
per-task ladders that can mix providers (nl never falls back to a weak skills
ladder). New `onto models` inspects it (no network). Fully back-compatible with the
legacy single-provider form; all exams unchanged.

## Wave "SHIP P3+P4 PACKAGING" — ✅ PASSED 2026-08-31 (D87, fship 10/10)
P3: templates ship as PACKAGE DATA (src/onto/templates_gallery/{starter,hotel,lago,
market}), so `onto new` works from an installed wheel with NO repo and NO network;
the broken 'scooters' template dropped, default now 'starter', repo-path reads gone
from the runtime path. P4: exam fship builds the wheel → installs into a CLEAN venv
→ runs new/court/schema/serve/judge/attest offline with the repo stripped from the
env, plus a repo-hygiene gate; it caught a real regression on the first run
(deleted init/models/schema/watch blocks) and it was restored. Deferred: P5
(publish to a public index) — on real need.

## Second echelon (after F6): a public gene pool; mining the genome from legacy
(§12.2 — the return of v0-ARCHGEN's mode 1 as a product).

## Conscious risks without insurance
- The SMT encoding of aggregates/invariants may hit undecidability — the boundary
  is shifted by fuzz, but the attestation is honest (proved|fuzzed).
- The interpreter may turn out too slow even for the judge — then F2 is pulled
  in earlier; this does NOT cancel the interpreter as the reference.
- The dialect interface gets renegotiated at the third dialect (PREDICTIONS #3) —
  accepted, while dialects are ≤ 3.
