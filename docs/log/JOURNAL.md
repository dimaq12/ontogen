# JOURNAL: session diary (new entries ON TOP)

## 2026-08-31 · SHIP P3+P4: packaging + legacy cleanup (fship 10/10)
- Templates became package data (self-contained gallery under src/onto/),
  so `onto new` works from an installed wheel offline — the real P3 gap
  (repo-path template reads) closed. Dropped the broken 'scooters' template
  (its source was gitignored build/), default is now 'starter'.
- fship builds the wheel, installs into a clean venv, runs the whole
  new->court->serve->judge->attest chain with the repo stripped from the
  env — the 'zero machine' claim mechanized. It caught a real regression
  on the first run (the onto-new rewrite had silently deleted init/models/
  schema/watch); restored and re-verified. Good exam.
- Cleanup scan: no dead modules, no orphan genomes; kept the validation
  corpus. Repo-hygiene gate in fship guards against keys/pyc/artifacts.

## 2026-08-31 · model registry in the ribosome (fmodels 11/11)
- Widened the single-hardcoded-openrouter Provider into a real registry:
  many named OpenAI-compatible providers, base_url presets, models as
  'provider:model' or bare, per-task ladders that mix providers, env/file
  key resolution, and `onto models` to inspect it. Claude-Code/Kilo-style
  user-friendliness, zero new dependency (still stdlib http).
- Kept full back-compat: the real config and every network exam load
  unchanged; ladder() falls back so a legacy skills_ladder still drives
  growth. nl never inherits a weak skills ladder.

## 2026-08-31 · gene pool = DNA not proteins + free IDE (fgene 6/6)
- Validated a second agent's three moves against the code and shipped the
  cheap in-spirit two-and-a-half: the gene-pool DESIGN LOCK (bodies never
  travel — the Skill model is already body-free, so this is a protocol
  decision + a teeth-gate, not new machinery), and the FREE IDE (onto
  schema from the frozen pydantic + modeline + onto watch — zero tail).
- The reframe is the win: seccomp's whole threat model dissolves because
  foreign Turing-complete code never arrives — you receive a contract and
  your own ribosome grows the body under your own gates. The eternal
  cross-platform syscall tail evaporates; what remains (local-body
  capability starvation) is bounded POSIX, deferred to pre-gene-pool.
- Anti-prompt-injection is in-spirit: gate_teeth (already built for a v0
  lesson) becomes the gene-install immune check — a toothless gene is
  rejected by court. Locked in DECISIONS before anyone gets used to
  shipping caches with genes (the agent's sharpest point).
- Free IDE for ~0.6d vs LSP 3-4d+tail: onto schema is one pydantic line;
  the frozen IR (D72) makes the schema un-rottable.

## 2026-08-31 · Tier B cheap pair: interview generates variants + TRUST.md (fvariants 5/5)
- Budgeted Tier B against the code, shipped only the two cheap in-spirit
  items: #6 (interview auto-variants) and TRUST.md. Deferred seccomp and
  full LSP as post-release (adoption/security, permanent tails).
- #6 is the second-strongest wow after entity-court: the system re-found
  the F2 lesson guard 's.booked > 0' by itself, and every variant it offers
  is court-certified to resolve — half the machinery (_variant_resolves)
  was already there; only the template menu was missing.
- TRUST.md states the execution boundary plainly (skills = hygiene not
  sandbox; islands unrestricted) — closes the honesty gap the second agent
  flagged, without pretending the sandbox exists.

## 2026-08-31 · Tier A: pre-release math dial-up (ftier_a 11/11)
- Validated a second agent's proposal set against the code, then built the
  4 that survived: #5 invariants proved (fixed-instance conserves-class),
  #8 spectral organ gets hands (verdict -> rights demotion), #10 replay
  time machine, #4 entity-court headline. No new mechanisms — pure dial-up
  of existing math.
- Honest wins: invariant proof correctly REFUSES money_sane (refund adds
  unbounded ev.amount -> real counterexample) and keeps it monitored, so
  the passport never lies; a fixed-instance solvent invariant proves.
- Caught the agent overselling z3 guard-synthesis (#6) — deferred with a
  note rather than shipping a half-truth.
- Updated test_review2 invariant-honesty guard to the finer proved|monitored
  split (D80 -> D83).

## 2026-08-31 · the second external review: six holes in the heart — all confirmed and removed (D80)
- The heaviest and most valuable review of the project: the court issued a green
  passport that was not earned (euclidean vs floor; self-induction instead of
  reachability; unknown swallowed). All six — reproduced, fixed, closed by 8 guards
  in CI.
- Entity induction (Houdini) PAID OFF immediately: it found a real hole in the live
  lago (ev.total<0 passed the guard) — the new court catches the class "untrusted
  input refutes the post", the old one stayed silent.
- My class-level side findings around the review: division by zero, kind outside
  the ledger hash (found WHILE writing the verify fix), a ghost for static, the
  js % in the grown generator.
- The methodology was accepted without haggling: P15 reclassified as in-sample;
  held-out delivered the subtle truth — fan-out generalizes, two-sided does not.
- Lesson of the day: "ALL PROVED" are the most dangerous words in the project;
  every new guarantee must name WHAT exactly was proved.

## 2026-08-31 · FREEZE 1.1.0: everything finishable was finished (D79)
- attest: end-to-end paths — the passport now speaks of CHAINS (the leaderboard
  cascade: MatchPlayed -> route -> win+lose · PROVED end-to-end).
- OPERATOR.md tripled: all surfaces, a 3-a.m. runbook, harden, not-knowing. CLI
  help lists everything. The warden CLI ticks all organs — before, only
  watch+monitors (timers/spectrum/holes would not spin in production — caught in
  the freeze preparation, not after).
- CALENDAR LIFE STARTED: life/ — a meeting-room organism (NL-grown) under a full
  warden, a pulse ~20 s, nohup. The exam is passed by time.
- FREEZE_v1.md: an inventory of guarantees/non-guarantees/a one-command check.
- Gotcha of the day: a foreground sleep is cut by the harness (144) — check statuses
  with a separate command.

## 2026-08-31 · the ν-bridge (fnu 7/7): the review v2 frontier closed in one go
- The retraction was re-checked by a run (not on faith): all figures confirmed;
  two corrections (R² with a 70% margin, λ post-selection).
- The most beautiful identity of the day: the organism kernel is LINEAR in load —
  and this is not a postulate but a MEASUREMENT (0.020). Hence VII.2: the operator
  shift ≤ TV(ν',ν), per-event certificates transfer by domination, the spectrum —
  honestly without oaths (the pseudospectrum is the right language, κ is not
  attested).
- Load became a MEMBRANE ASSUMPTION: ν̂ in the certificate, a threshold from
  subwindows (I caught myself at 0.15 by hand — redid it), nu_drift into the ledger.
  The same trust pattern for the third time: islands -> knowledge -> load.
- Gotcha-lesson: a manual threshold in the detector is the same smuggling as a
  float in money. Discipline: thresholds only from calibration.

## 2026-08-31 · the remainder of the MATHEMATICS epic (faudit 5/5, fcompose 4/4, library 5/5)
- The spectral audit became an ORGAN: warden.tick_spectral with a calibrated (not
  manual) threshold, vocabulary selection and a Markov test. Health is silent,
  corruption and freeze go into the ledger. The THEORY_BRIDGE parking is lifted:
  the organism's operator is defined, measured, and works in the production loop.
- fcompose: VII.1' verified BY THE ENGINE — conditions (i)-(ii) satisfied by a live
  saga, the Fréchet bound reached by live data (0.742=0.742).
- BEST FINDING OF THE DAY: library "beyond Sonnet" turned out to be a JUDGE bug
  (a crash on 'War and Peace' -> an empty counterexample -> blind CEGIS, 16
  attempts). Fixing URL quoting + the trace into the verdict -> green in 3. The
  thesis of Part VII is reinforced: convergence = f(cheatsheet, quality of
  counterexamples). Blind gates are indistinguishable from an inexpressible task.
- P15 final score: 5/5. The P16 mechanism is alive (N=133/200).

## 2026-08-31 · the MATHEMATICS epic, waves M2-M5 (P15 ✅, fspectral 5/5, review)
- P15 CONFIRMED: gauntlet lessons transferred p0 — 4/5 former opus tasks are now
  sonnet-green, two on the FIRST attempt in 20 seconds. The nul ~10^-3. The
  cheatsheet again beat escalation. library is an honest remainder.
- fspectral: the spectral detector works on a live booking — λ 0.874 -> 0.996 under
  metastable corruption. The first run refuted the naive design (a freeze is not a
  slow mode!) -> the detector is two-component: spectrum + variance. The exam again
  taught the theory.
- An adversarial review of Part VII (a subagent) — a demolition at corpus level:
  11 blows, almost all accepted. The best moment: the reviewer demanded live
  telemetry instead of constants — the parser immediately found a lost
  impossible-series. The constants in the exam LIED; they are gone now.
- Part VII v2: VII.1' with conditions (i)-(iii), Norm 1 instead of a pseudo-
  Proposition, "calibration of the pipeline" instead of "verification of lemmas",
  §5 "Response to the review" in the corpus style.

## 2026-08-31 · MATHEMATICS EPIC, wave 1: Part VII (fmath 9/9)
- The first block of theory born from PRACTICE: v1/math/PART_VII.md + the exam
  fmath in CI — theory obliged to agree with measurement.
- THE MAIN EVENT — the exam REFUTED the draft theory: β̂=0, the gauntlet data does
  not distinguish memoryless from an informative loop. The theory was fixed, not
  the exam (v0's precedent "the gates caught the wrong algorithm" — now the gates
  caught the wrong THEOREM). P16 schedules a refit.
- For the first time: Part VI's lemmas computed on a live organism.handle() — a
  swamp with a reset move; the design itself gave a lesson: without reset the
  uniform hazard is zero, reset ≡ REVOKE/molt-rollback — the survival theory and
  the D74 queue closed on an executable example.
- VII.1 — a small honest passport-composition theorem: attest will be able to print
  an end-to-end path certificate. DKW gave the skill a quantile passport (q≥0.906)
  instead of a boolean checkmark.
- The telemetry thinks about the future: usage_*.jsonl accumulates by itself, N
  grows.

## 2026-08-30 · the paradigm's shortcomings -> MECHANISMS (fparadigm 13/13, fcold 4/4)
- Lesson of the day from the maintainer: "shortcomings must be REMOVED, not described." All
  six solvable ones — built in code in one go (D74).
- The pearl of the wave — attest: the guarantee passport as the compiler's output.
  The weakest seam is named; the thinness of the proved core stopped being hidden.
- Hardening is beautiful in its mechanics: the escape corpus judges not only new
  bodies but also the ALREADY certified cache at mount time — an incident revokes a
  certificate retroactively.
- Not-knowing: "I don't know" became a legal operator answer — the hole lives in
  assumptions.yaml next to the genome (the frozen IR untouched), the warden writes
  hits, the answer revokes it.
- fcold: model-independence past the frontier is now VERIFIABLE (a dead key, 0
  calls). genomes/.grown became a permanent cache in the repo.
- Gotcha: eval_expr expects dict populations, not SimpleNamespace (I step on this
  the 2nd time — now recorded).

## 2026-08-30 · THE MAIN EXAM: any product — PASSED (fgauntlet 10/10)
- The claim "any software product" was tested by the gauntlet: 8 domains, maximally
  different in mechanics (sagas, escalations, freezes, clamps, overwrite from an
  event, three-sided settlements). ALL assembled from a natural-language description and
  PROVED by an independent court. 268k tokens for 8 products.
- The ladder is not decoration: Sonnet did 3/8 by itself, Opus finished 5/8 after an
  honest exhaustion. Warehouse converged on the 2nd attempt (15 s) — where the
  mechanics fit the cheatsheet, the product costs pennies.
- THE BOUNDARY IS HONEST: video hosting with transcoding (blobs, background
  pipelines) -> an island, refusal. A system that converges on anything is lying;
  ours says "this is not my world."
- Lesson into the PLAN: the gauntlet's counterexamples = future fodder for the
  cheatsheet (economics).

## 2026-08-30 · U7 + the IR freeze = 1.0.0 (fy7 7/7)
- U7 (D71): skills are now in all tissues — python prints certified bodies from the
  ribosome cache (no re-synthesis), go proxies to the canon (ONTO_SKILL_CANON),
  without the canon — an honest 501. Fuzz parity: 0/90.
- A side catch: printing failed on a clean core (exchange: events {}) — the bench
  block required an event. A guard; clean cores print.
- THE FREEZE (D72): the genome format got a mechanical guard — the fingerprint of
  the json schema in ir.py + test_freeze. A format change without a hub bump and a
  converter now does NOT pass CI. This is the promise of stability from MODEL §8.
- The U1-U8 constitution is closed entirely. Version 1.0.0.
- Run gotcha: a stale __pycache__ masked an edit to a constant — cleanup.

## 2026-08-30 · the U8 console + release 0.3.0 (fops 6/6)
- /ops (D69): the operator console is printed from the organism like /admin — the
  ledger with filters and provenance, external passports (REVOKE visible to the
  eye), heat, checkpoint. 6/6 on the first run.
- The result of the day's marathon: U3 (types-2), U4 (auth), GROWTH of the dialect
  GENERATOR (D68), the U8 console. Constitution: U1-U6, U8 ✅; U7 and the IR freeze
  — a conscious remainder (D70).

## 2026-08-30 · GROWTH of the dialect GENERATOR — PASSED (fgengrow 4/4)
- Rung 2 of pearl 5 (D68): not a per-genome translation, but the model itself writes
  emit(genome)->organism.js. The gates — multi-genome CEGIS on 3 genomes,
  growdialect's gates reused entirely.
- THE LADDER SHOWED ITS TEETH: qwen3-coder (4 attempts) and -plus (4) — red (a
  meta-task: python that prints js, with an Expr translator); Sonnet — GREEN on the
  3rd. The counterexamples led: generator syntax -> emit() raised -> node --check on
  a concrete genome.
- THE MAIN BIRD: booking (outside the certification set) was printed in 0 model
  calls and passed judge+parity+kill -9. A new language = a one-time cost of growth,
  after that printing is free — like go-stdlib, but grown.
- Homology worked: the samples = our python emitter + the js of rung 1.

## 2026-08-30 · waves U3+U4: types-2 and the auth gene (ftypes2 10/10, fauth 12/12)
- U3 in ~an hour WITHOUT extending Expr/court: types-2 = representation on the HTTP
  membrane (D66). The int carrier everywhere; the write-ahead log stores only the
  carrier -> replay is blind to forms. The input is richer (both forms always), the
  output is stable (?repr=human optional) — a conservative extension, not one
  existing exam flinched.
- optional/list-state — NOT built, and that is a decision: patterns are stronger
  (NOT §34-35), the precedent "a state machine = a pattern" from v0.
- U4: authorization as a gene (D67) — predicates in the same Expr, with the same
  typecheck; the IdP is an ordinary island (the membrane monitors it too). fauth
  12/12 on the FIRST run — the machinery (Expr, membrane, ledger) already carried
  everything needed.
- ftypes2+fauth added to CI (local, <1 s each).

## 2026-08-30 · carte blanche "the ideal version" — PASSED (fideal 10/10)
- Waves A-E in one go: NL front (nlfront.py, D64), timers (D59), parametric queries
  + /list (D60), /admin from the genome (D61), webhooks (D62), onto new (D65). Plus
  D63 (the island-growing spec appeared in the membrane).
- THE MAIN LESSON of the NL front: convergence is determined by the CHEATSHEET, not
  by model strength — Sonnet and Opus failed on the same UNSPOKEN contracts of the
  testbench (a saga for cross-entity preconditions; the sequence of flows on one
  organism; timers outside the judge; a guard on amount). Each lesson written into
  the cheatsheet -> a "rental service" is built on the 1st attempt in ~4k tokens.
  The cheatsheet = the admixtures of the NL front.
- Run gotchas: a zombie on the port (the third time — now an assert on startup),
  the warden's dirty data (duplicates strangled the judge), a webhook on the
  alphabetically-first event, telemetry with a full cache.
- fideal 10/10: description->court->organism->time->surfaces->webhook->grown node->
  packaging. ALL CHECKS GREEN. Version 0.2.0.

## 2026-08-30 · session 2, the wave "THE MODEL GROWS THE ISLANDS" — PASSED (fisland 7/7)
- Document hygiene at the start: D59–D62 (U1/U2/U5/U6) lived only in code —
  reconstructed into DECISIONS; F5 in PLAN marked passed (it lagged behind commit
  94a4095).
- D63: External += intent/cases (additive); growisland.py — a CEGIS loop modeled on
  growdialect; gates: the import membrane (whitelist) -> acceptance through a LIVE
  flaky upstream via MonitoredAdapter (retries are forced by the gates, not trusted)
  -> the cert_valid passport. CLI `onto growisland`, docs/OPERATOR.md §islands.
- FACT: the fx adapter was grown by qwen3-coder on the 1st attempt (all 6 cases
  through the flake "every 3rd is a 500"); the planted guards (subprocess, naive
  without retries) are red; REVOKE on a total refusal; a cache-repeat without the
  network.
- A gate bug caught by its own guard: MonitoredAdapter judged ext.island rather than
  the recorded island_rel — the naive "passed" because it judged a grown neighbor.
  A lesson for the pile: "the gates must judge exactly the candidate's artifact."
- Testbench gotchas: a zombie onto on 8641 (SCARS classic), shutdown() without
  server_close() holds the port.
- IDEAL result: all three pearls demonstrated. Next on the map: growth of the
  dialect generator (a second language), the F7 human, calendar life.
- ALL CHECKS GREEN.

## 2026-08-30 · session 1, the wave "GROWING A DIALECT" — PASSED (fgrow 5/5)
- IDEAL fixed (after the user's clarification: NL->genome — to capable models;
  pearls 3/4/5 — to weak ones + rails). The OpenRouter key updated.
- growdialect.py: the SLM translates the canonical python phenotype into node
  per-genome; a 4-rung gate (--check / judge / parity / kill -9); CEGIS; the cache =
  a certified artifact.
- THE FIRST RUN: 5 reds in a row — ALL because of the testbench: max_tokens=2200
  clipped organism.js (the THIRD coming of the v0 scar "the limit clipped the
  bodies"); after max_tokens=12000 + js fences — GREEN ON THE FIRST ATTEMPT for
  qwen3-coder: judge 4/4, parity of all instances, replay after kill -9.
- The exam line "ZERO edits to the core and dialects" — by a git check.
- Conclusion for IDEAL: the gates are strong enough that "any language" is a system
  property; the next step of pearl 5 — a second language (rust/php?) by the same
  mechanism + growth of the GENERATOR (a dialect plugin), not per-genome.
- ALL CHECKS GREEN.

## 2026-08-20 · session 1, MODEL.md — the constitution of the universal model (D57)
- The user's goal fixed: a fully packaged system for developing ANY software.
  MODEL.md: 5 layers (core/skills/islands/tissues/surfaces), the operator cycle, the
  roles of intelligence (human-meaning, LLM-mouth, SLM-CEGIS, court, zero
  intelligence at runtime), the honest physics of coverage by software category, the
  UNIVERSAL U1-U8 program, guarantees/non-guarantees.
- README/CLAUDE reference it. Next wave on the map: U1 "Queries and read models"
  (unblocks a real API), then U2 (time), U5 (admin panel) — the point "a full SaaS
  from a genome without hand-written code."

## 2026-08-20 · session 1, LAGO slice v2 — PASSED (flago 6/6; ALL CHECKS GREEN)
- D55 str state: IR (int|str, default ""), go/py tissues (types, literals), the court
  already handled z3.String; rulebench works around str fields.
- D56 the invoice registry: invoice — a dynamic entity, BORN BY AN EMISSION; the
  two-key fan-out CreditsApplied (a subscription AND an invoice from one event —
  fan-out was capable since F1, needed for the first time). The cascade reads in
  outcomes as a trace: close_period -> invoice.issue@d1 + customer.apply@d1 ->
  credits_applied@d2 + invoice.apply@d2.
- Graduated (100 at 2¢, then 1¢) — IfExp; the L5 model mirrors it, 200/200.
- Court: invoice.apply — yet another provably equivalent mutant.
- Gotchas: zombie servers with the old schema (422) twice; a pkill suicide in a
  heredoc (the pattern killed the parent) — patterns escaped, a clean call.
- Campaign remainder: COUNT_UNIQUE, line items, the TIME wave (period timers instead
  of an external job).

## 2026-08-20 · session 1, the POLICY wave + LAGO v1 — PASSED
- D54 (the last major IR primitive): Rule.emit; the key decision — derived events are
  NOT in the log (the log = the external world, the cascade is recomputed by replay:
  determinism and restart idempotency by construction); a synchronous cascade with a
  cap of 8 (overflow into the ledger); a full typecheck of emissions; all three
  tissues taught (go: dispatch(depth), float64 conversion of fields; py: dispatch +
  a local alias s=nxt).
- mutgate: a change of emission is unprovable (cascades) -> always a question with
  ack.
- Lago v1: a per-customer wallet through a saga of three events; the judge 6/6 on
  both substrates (incl. a wallet shared by two subscriptions: 6000 - 5454 = 98, the
  second period eats it up); volume 200/200 against an independent model (~1.5k ev/s —
  an O(N) invariant, noted earlier).
- Gotchas of the hour: a schema shift in BillingPeriodClosed knocked down old flows
  (fixing the judge's expectations under genome evolution is a normal price); my own
  flow broke the counter of active subscriptions (3, not 2).
- tests/test_policies.py 4/4; ALL CHECKS GREEN. UNEXPRESSIBLE: closed "emission" and
  "per-customer wallet"; new ones: str state (a subscription doesn't remember its
  customer), the court of cascades.

## 2026-08-20 · session 1, the LAGO campaign: slice v0 — PASSED (exam 6/6, 29 s)
- The reference candidate approved by the user: Lago. The semantics were lifted from
  the docs (metric aggregations, usage events with transaction_id idempotency =
  literally our dedup, rate_amount wallets, plans/charges) -> lago/SPEC.md with a map
  of correspondences and a live list of expressiveness blocks.
- Wave D51 "dynamic instances" (the main universal block of real products):
  instances: dynamic in all three tissues; bind is not needed.
- Body cap 64->256 (D52): honest invoicing arithmetic, 145 nodes; the boundary with
  skills is structural. The smuggler exam inflated to 413 nodes.
- Court lesson (D53): the counterexample period_conn_max=-99 — an inductive post must
  carry the hypotheses it uses; after the addition, ALL PROVED.
- Exam: the Lago-semantics judge 6/6 on interp AND go; the billing job through the
  warden; 200 subscriptions/40k events — invoices 200/200 against an independent
  model; noted: an O(N) invariant over the population gives 1.5k ev/s (in
  UNEXPRESSIBLE: incremental invariants).
- flago added to tools/check.sh. ALL CHECKS GREEN.

## 2026-08-20 · session 1, the wave "RELEASE 0.1" — PASSED (6/6; ALL CHECKS GREEN)
- core/store.py (D48): EventStore jsonl|sqlite; the organism/migrations/snapshots over
  the abstraction; sqlite WAL 26k ev/s, the judge 4/4 on .db, a migration of 30k by a
  functor with a .db backup, fold parity byte-for-byte; p99=1.8ms.
- Gotchas: sqlite thread-affinity (check_same_thread + lock — a classic); a zombie
  process on the port masked the fix; the historical check "diff of the core up to
  HEAD" broke CI retroactively -> pin by range (D49).
- Readiness: README (an entry for all three audiences), tools/check.sh — a single CI
  entry point (lint+tests+f1/f3/f4/f8/frelease), version 0.1.0, tag v1-0.1.0. ALL
  CHECKS GREEN.
- What stays OUTSIDE the code (on principle): calendar operation, the human
  operator/pure machine (F7), and on demand: JIT in-process (D28), the live seam,
  printing skills into go, sagas/event emission (an UNEXPRESSIBLE candidate).

## 2026-08-20 · session 1, the wave "MEGA-DIRT" — PASSED (exam 12/12, 16 s)
- Domain market: 7 genes with a MIX (a shared vocabulary commerce_events — D46; stock
  and orders REQUIRE their own subsets of fields of one event; payments reused a third
  time), state machines, a racy cross-invariant by design, 3 integrations with
  different failure profiles, an SLM skill allocate.
- The linker caught a double export of an event live (before the vocabulary) — the
  refusal worked.
- FOUR findings of the wave (all about fuzziness, as the exam asked):
  1) an inductive post is blind to "after X" — a conditional form is needed (D47);
  2) fuzz with unique categories = sleeping guards (D45) — a toothless fuzzer accepted
     allocate with a contract silent about warehouse duplicates;
  3) refining the contract = a new semantic cache key = re-synthesis (D6 worked as
     intended);
  4) a sed on a field name snagged state — conservativeness honestly rejected it (the
     neighboring-meaning D35 confirmed by chance).
- Numbers: 30k events at 10k ev/s; kill -9 -> 0.01s; migration of a live 30k — 0.4s
  downtime, penny for penny; the gateway demoted at 20% errors/slowdowns, tracker
  (12%) and fraud (2%) — within tolerances; the judge 4/4 under load.
- pytest 63/63, lint CLEAN.

## 2026-08-20 · session 1, the wave "DIRT AND VOLUME" — PASSED (exam 8/8, 30 s)
- Built: core/membrane.py (D43: island+assumptions-Expr+monitors+trust revocation; a
  live /ext/<name> — the "live wiring of /convert", an unpaid debt of v0, paid in v1);
  snapshots with a hash certificate and tolerant replay (D44); serve became
  multithreaded.
- v0-class stress: G1 volume (x100 start with a snapshot, a broken snapshot rejected),
  G2 kill -9 mid-write (torn_lines), G3 a storm of retries + garbage, G4 concurrency
  (penny for penny, the guard held zero), G5 a flaky foreign organism (25% slowdown,
  15% 500s, crooked values) — drift caught, trust REVOKE, G6 complexity 20
  entities/160 rules — the court 18ms/rule.
- Exam gotcha (mine): I ran a "duplicate storm" with 50 different ids at a window of 8
  — a test against my own contract D26; a storm = retries of ONE message.
- P6 (the SMT boundary) does not bite on 160 simple rules; rich invariants are still
  ahead. pytest 63/63, lint CLEAN.

## 2026-08-20 · session 1, mini-F7 "other hands" — THE FIRST POINT (passed by a fresh agent)
- A fresh agent (zero context, input = CLAUDE.md) added a freeze feature to the
  payments gene: 1 file, +9/-2, validate+court ALL PROVED ON THE FIRST ATTEMPT, a live
  test: freeze -> charge = noop(guard), the balance untouched; as a bonus checked shop
  (the shared gene is alive). Explicitly praised: explain ("exactly the slice"), the
  honest outcomes in the /event response, the court "nothing had to be fixed".
- DX holes (all concrete): the POST /event format is documented nowhere
  (reconstructed from exams), --help is one-line, the default init=0 lives in a
  comment referencing F4. -> Wrote docs/OPERATOR.md (one scroll: endpoints, the event
  format, the feature path), CLAUDE.md branches the operator there.
- Comparison with v0-T4 (scar S15): there a fresh agent was MORE EXPENSIVE and learned
  the doctrine from the checkers; here the first attempt is green because the meaning
  is in the genome + the court proves instead of the operator. P1 (interview spam) did
  not come true: no questions were needed at all. P10 partially closed (the agent —
  yes, the human/pure machine — ahead).

## 2026-08-20 · session 1, the wave "connective tissue" — PASSED (8/8)
- mutgate (D40): a single mutation gate for the warden AND propose —
  conservativeness -> court (DISPROVED = refusal with a counterexample) -> semdiff
  (behavior changed under the same contracts = a question with an executable input;
  ack_behavior_change in the root = the operator's answer). The interview is EMBEDDED
  in the flow of life.
- Skill organ (D41): organism/serve mounts /skill/<name> from named cache artifacts
  (<skill>.fast.py); exchange responds with the certified fast body over HTTP.
- propose (core/propose.py): a copy of the tree -> gates -> a write with a .bak; the
  MCP mouth (mcp==2.0 MCPServer, as in v0) — 6 tools; onto mcp <root>.
- onto warden — a daemon (an interval loop, it picked up a mutation in the exam by
  itself); onto unit — systemd; uv tool install from /tmp — the global onto works.
- Exam trap: a "crooked" post balance>=999999 turned out to be inductively PROVABLE
  (the precondition carries it) — the court is right, the test corrected to
  balance<=100.
- Outside the wave (on demand): printing skills into go, JIT in-process (D28), the
  live seam.
- pytest 63/63, lint CLEAN. Next: mini-F7 with a fresh agent.

## 2026-08-20 · session 1, the wave "skills + live SLM" — PASSED (5/5, live network)
- core/skills.py: the Skill gene, properties-Expr (limit 400 nodes), the fuzz gate
  (gate_semantics -> counterexample), GUARDS (gate_teeth: return [] must fall — the
  lesson of v0-wave 5 encoded), equivalence, the complexity budget (D38).
- ribosome.py: the OpenRouter provider (config .onto/, the key from v0, SiliconFlow
  order / Cloudflare ignore), the CEGIS loop (counterexamples into the prompt, the
  ladder qwen3-coder -> plus), cache by CONTRACT (D6 — not by prompt text), an island
  = a valid outcome, usage.jsonl.
- LIVE run: naive red (the model called Order(...) — a testbench defect, gave type
  constructors into the sandbox) -> GREEN attempt 2 BY THE COUNTEREXAMPLE; fast GREEN
  attempt 1; t(4n)/t(n)=4.3<=8; a repeat — cache, 0 network; the cost of the wave ~2.8k
  tokens (~$0.001). The first unplayed organ played.
- Testbench lessons (all three — "judge the testbench before the model"): argument
  order = the signature (not sorted); type constructors; the speed budget vs an
  efficient naive -> complexity (D38).
- pytest 58/58, lint CLEAN. Remaining from PLAN: F7 "Other hands" (I cannot pass it
  myself) + the background criteria of F6; the next waves to choose from: a skill in
  the organism, printing skills into dialects, the warden daemon as CLI, demand in the
  IR.

## 2026-08-20 · session 1, F6 "Life" — MECHANISMS PASSED (exam 9/9, 2.3 s)
- core/migrate.py (D35): diff_genomes -> breaking; the Migrations functor; coverage
  (each breaking is covered or refusal); migrate_log is idempotent, with a backup;
  state = a fold of the log => state migration is free.
- core/warden.py (D37): watch by the hash of the root+modules; a molt with a restart
  (0.3s); survives broken YAML (reject, the organism is alive); monitors: a quota
  (declared, provenance in the ledger) -> REVOKE of rights in the same tick; the
  placer tick: proposal-only vs auto-molt (interventional) — the auto-eviction of
  wallet was executed, the service is alive, molt_executed in the ledger.
- Organism (D36): subtracting one's own actions — replay does not touch
  counters/heat/ledger; after two molts invariant_violations==0.
- Exam gotcha: an edit to the YAML "at the end of the file" broke the module — which is
  exactly why the warden must survive broken mutations (it catches any load errors).
- IN THE BACKGROUND: calendar week/month; the live seam of traffic; module versions.
- pytest 53/53, lint CLEAN. Remaining: F7 "Other hands" + the wave "skills+SLM".

## 2026-08-20 · session 1, F4 "Composition and genes" — PASSED (exam 10/10)
- core/modules.py: a module-gene (exports/requires with structural subtyping, without
  instances), the root (imports+bind+cross-invariants), linking into a flat
  hub-Genome — the organism/court/dialects DID NOT CHANGE (composition is a pure
  frontend). Overriding another's rule is structurally impossible (D2/D31).
- Defaults: init partial (a skip = 0), instances — only in the root's bind.
- explain: the slice for a feature around an entity = module + bind lines = 37% of the
  genome.
- Genes: rooms, reservations (requires without its own events), payments, stock; the
  roots hotel (3 genes) and shop (stock+payments) — payments reused without a single
  edit, the printed wallet bodies byte-for-byte in both go phenotypes.
- Exam: the judges 4/4 and 3/3 green on the interpreter and go for both domains; the
  court PROVED on the linked ones; genome/phenotype 0.19 (<= 1/3, in v0 it was ~0.75);
  composition refusals go red (tests).
- FINDING (D32): the court proved the EQUIVALENCE of the mutant flip qty>0->qty>=0
  (the body is neutral at qty=0) — the CLI now distinguishes "EQUIVALENT (proved)" /
  "BLIND (unknown)"; the v0 fuzzer silently missed such cases.
- UNEXPRESSIBLE: parametrization by behavior (rejected, D2), module versions with a
  functor — F6. PREDICTIONS: P5 (semantic hash) not touched yet — there is no SLM
  cache yet; P7 holds.
- Next: the wave "skills + live SLM" (a two-phase ribosome, CEGIS with the network)
  or F5 "Metabolism". pytest 41/41, lint CLEAN.

## 2026-08-20 · session 1, F3 "Second language" — PASSED (exam 9/9, 1.8 s)
- The python-stdlib dialect (D29: NOT fastapi — supersedes D12, the risk of F3 is I1,
  and D19 requires zero dependencies): the printer = ast.unparse LITERALLY (the
  dialect language = the canon language), the skeleton — dataclasses + http.server,
  full parity (log/dedup/D25/endpoints).
- The dialect registry (D30): data instead of an if-chain; the CLI materialize through
  the registry. The dialect interface {generate, build, certificate} withstood the
  second language without negotiation — P3 has NOT yet come true (a third dialect will
  show).
- Exam: three substrates from one genome, one judge 5/5 on all, snapshots
  byte-identical, conformance 240/240 both, git diff of src/onto/core with F2 empty.
- PREDICTIONS: P3 ◐ (the interface is alive after #2), P12 ◐ (python: native semantics
  closed the question of an embedded interpreter for this dialect; go — F5).
- Next: F4 "Composition and genes" (import/exports, parametrization, a gene as a unit
  of import, explain O(k), a genome metric ≤ 1/3) — or the wave "skills+live SLM" (the
  only thing the ribosome lacks for a full cycle).

## 2026-08-20 · session 1, F2 "The court and the first tissue" — PASSED (exam 9/9)
- THE COURT (core/court.py): symbolic execution of bodies -> z3; the full transition
  guard?body:s; prove_rule (inductive post/conserves) + prove_equiv with a
  counterexample; timeout 10s -> unsupported/fuzzed (P14). Mutants (core/mutants.py): 5
  classes of AST transformations; booking: 21/21 distinguished.
- THE INTERVIEW (core/interview.py): detect (both passed the court + not ≡ -> a
  question with a concrete input and outcomes), validation of variants (guard -> ≡
  provably; post -> the court distinguishes), apply_patch -> a genome diff. Scar-13
  reproduced and closed by a mechanism.
- The go-stdlib DIALECT (dialects/go_stdlib/): emit (floorDiv/floorMod — Go's truncated
  division WOULD DIVERGE from the canon, conformance would catch it), skeleton (the
  whole organism is printed from the reference, HTTP/log/dedup parity with the core),
  gates (build + printer-conformance 240/240 = certificate D28). Gotcha of the day:
  mux patterns "POST /event" are gated by the go.mod directive — 1.21 silently turns
  off routing (404), you need go 1.22.
- Bench: full-path 7.4μs (go) vs 76μs (python, wire parity) = 9.4x; rule-path 0.8ns vs
  23μs = ~29,000x — the warm path beyond the target.
- D27 (the printer = rung 0, the SLM only for skills), D28 (the dialect certificate
  without an embedded interpreter until F5); UNEXPRESSIBLE: int64 vs unbounded, the
  floor semantics of division.
- pytest 32/32, lint CLEAN. Next: F3 "Second language" (python-fastapi, zero core
  edits) — and there, the first live SLM on skills.

## 2026-08-20 · session 1, F1 "The living reference" — PASSED
- The organism lives WITHOUT codegen: core/{expr,genome,organism,serve}.py — the Expr
  interpreter (the canon), a typed Genome (extra=forbid, a full typecheck at load), an
  event log JSONL + write-ahead + fsync, the ledger with a hash chain (D16), dedup by
  a WINDOW (retry_window=8 for booking), invariant observers, stdlib HTTP; the judge
  (onto judge) — an external black box.
- Rule bodies — IN THE GENOME (reference semantics §10.1): genomes/booking.yaml.
- Exam exams/f1.py — 5/5: the judge green; kill -9 → replay identical (the dedup window
  restored); the smuggler (204 AST nodes) rejected as a skill; invariant_violation in
  the ledger. pytest 21/21, lint CLEAN.
- The Expr conformance suite (D17/P12): 240 cases, exams/conformance_expr.jsonl
  committed — the bar for embedded dialect interpreters in F2+.
- D25 (a contract violation = refusal+ledger), D26 (the window — a genome level);
  UNEXPRESSIBLE.md created (div0, per-channel windows, str, int-only state, P8).
- PREDICTIONS: P2 ✅ holds (zero codegen), P7 ✅ the AST limit works, P8 ◐ the judge
  coverage checker deferred to F2 (recorded in UNEXPRESSIBLE).
- Next: F2 "The court and the first tissue" (SMT gate, CEGIS, the go dialect, the
  interview).

## 2026-08-20 · session 1, F0 — PASSED
- Addendum (after passing): D24 — machine surfaces translated to English (errors of
  ir/lint/cli/the spike); docs and comments — Russian.
- The skeleton of the engine `onto`: a uv project (py3.13, lock), src/onto/{core,
  dialects,theory}, the CLI (version|lint|fix), its own .venv (ST1 closed).
- The Expr spike (spikes/expr/): the py-ast subset WON (D23) — a typecheck with Russian
  coordinates, Go+Python printers, z3: the post of reserve PROVED, the mutant without a
  guard — counterexample [av=0,cap=1]. B(lark)/C(cel) rejected.
- Hub versions (core/ir.py): onto:N, a converter v0→v1, refusal of a future version,
  `onto fix`. Invariant linters (lint.py): I1/extra-allow/machine paths; "lint: allow"
  — visible exceptions (the linter caught itself — the mechanism worked on the very
  first day).
- EXAM: 10/10 pytest — the planted violations go red, the engine itself is clean.
- Decisions: D11, D12, D22, D23 closed. Next: F1 "The living reference".

## 2026-08-20 · session 1 (design)
- Done: SPEC (§0–§12, base = proofs/metabolism/interview), NOT (29), SCARS (15 v0
  scars), PLAN (F0–F7, interpreter-first), PREDICTIONS (10), DECISIONS (D1–D13),
  CLAUDE.md (protocol), the artifact "Anatomy of v1" (docs/anatomy.html). Numbering
  v0/v1, the directory renamed.
- Open: D11 (the genome format), D12 (the second dialect) — spike F0.
- Next step: F0 — the Expr spike (CEL vs Starlark vs our own, criterion: typecheck +
  2 printers + SMT encoding + readability), the repo skeleton, CI linters.
- Parking: the biology vocabulary (gene/mRNA/chaperone) — possibly §0.5 of SPEC, not
  urgent.

## 2026-08-20 · session 1, continued (the stack)
- Done: STACK.md (the ideal/scars ST1–ST7/decisions); DECISIONS D14–D21; NOT §30–33;
  PREDICTIONS P11–P14; edits to SPEC §10.1 and PLAN F0–F2.
- Key finding: the question of delivery exposed a hole in §10 — where the interpreter
  lives when the path is evicted. Decision D17: two-tier (a canonical one in the engine
  + one embedded in each dialect's runtime), the Expr conformance suite mandatory from
  F1.
- Open remain D11 (the genome format), D12 (the second dialect) — spike F0.
