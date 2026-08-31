# DECISIONS: decision log (ADR-style; supersede, do not delete)

Format: D<n> [date] status — decision. Why — in one line.
Statuses: ACCEPTED / REVOKED→Dm / OPEN.

- D1 [08-19] ACCEPTED — v1 in a separate directory, v0 (archgen) is a donor of
  scars; from its code we carry over only: cache, ledger, migrate, propcheck,
  the gate-runner.
- D2 [08-19] ACCEPTED — module composition via interfaces, not inheritance;
  extending a provider = a new version with a functor. Why: theorem 6 for free.
- D3 [08-19] ACCEPTED — admixtures = knowledge of the DIALECT (body kind), not
  of the project; certified by the gates; finite in the number of body kinds.
  Why: anti-RAG.
- D4 [08-20] ACCEPTED — borrow the expression language wherever possible
  (candidate CEL); resolved by spike F0. Why: not owning the lexicon = not being
  able to migrate it.
- D5 [08-20] ACCEPTED — hub-and-spoke genome versions (onto:N + converters +
  onto fix). Why: v0 froze itself (S6).
- D6 [08-20] ACCEPTED — cache bodies by semantic hash (norm-AST+dialect+
  admixtures+model+seed), not by prompt text. Why: v0 was "byte-for-byte".
- D7 [08-20] ACCEPTED — base mechanisms: proofs/CEGIS (§9), metabolism/
  interpreter-first (§10), interview by counterexamples (§11), gene pool as the
  second echelon (§12). Why: user said "put it in the base."
- D8 [08-20] ACCEPTED — numbering: archgen=v0, spec=v1; directory v2→v1.
- D9 [08-20] ACCEPTED — F1 = parser→typecheck→interpreter→judge, zero
  codegen/SLM. Why: cuts off the predicted bloat (P2).
- D10 [08-20] ACCEPTED — Expr must have a direct SMT encoding (LIA + bounded
  aggregates); whatever breaks that goes into skills. Why: otherwise §9 is empty.
- D11 [08-20] ACCEPTED (spike F0) — genome carrier: YAML + version onto:N; we do
  not invent our own format. Why: v0's disease is cured by typing the hub, not by
  syntax.
- D12 [08-20] ACCEPTED (spike F0) — second dialect: python-fastapi. Why: with
  D23, the Python printer is nearly free — the cheapest proof of I1.
- D13 [08-20] ACCEPTED — the project runs by the CLAUDE.md protocol: a session =
  a JOURNAL entry + a commit; decisions go only here. Why: v0 died from the
  evaporation of knowledge, not from code.
- D14 [08-20] ACCEPTED — engine: Python 3.13 + uv (lock, pinned); a language
  review only after F6. Why: v0's rake was hygiene, not the language (STACK ST1).
- D15 [08-20] ACCEPTED — two repo archetypes: engine and organism-workspace; the
  organism pins the engine version. Why: ST5, ST7.
- D16 [08-20] ACCEPTED — ledger JSONL append-only + hash chain; SQLite is a
  derived index outside git; the cache is committed into the organism. Why: ST3.
- D17 [08-20] ACCEPTED — the interpreter is two-tier: a canonical one in the
  engine + one embedded in each dialect's runtime; the Expr conformance suite
  ships with F1. Why: metabolism requires eviction IN THE PROCESS (exposed by the
  question of delivery). Risk: P12.
- D18 [08-20] ACCEPTED — toolchains via a dialect manifest + doctor; hardcoded
  paths are forbidden. Why: ST2.
- D19 [08-20] ACCEPTED — the phenotype skeleton: zero mandatory dependencies;
  dialect dependencies vendorable, offline build. Why: ST4.
- D20 [08-20] ACCEPTED — determinism = cache + gates; the local provider is the
  anchor, the cloud is an accelerator with an integrity check. Why: ST6.
- D21 [08-20] ACCEPTED — delivery: uv tool install (engine), a systemd unit
  (organism), docker/k8s only on request from a F7 operator. Why: ST7.
- D22 [08-20] ACCEPTED — engine/CLI name for v1: `onto` (package onto, commands
  version|lint|fix...); archgen remains the name of v0. Why: onto:N/onto fix are
  already in the docs' lexicon.
- D23 [08-20] ACCEPTED (spike, spikes/expr/RESULTS.md) — Expr = a SUBSET OF
  PYTHON EXPRESSIONS via stdlib ast + a whitelist of nodes; rule bodies are the
  same ast (exec: Assign/If). Why: we own neither the grammar nor the parser; the
  python printer is free; the SMT court was demonstrated in the spike (post
  proved, mutant caught by a counterexample). B(lark)/C(cel) rejected — see
  RESULTS.md.
- D24 [08-20] ACCEPTED — language of surfaces: project DOCUMENTS and code
  comments — Russian; MACHINE surfaces (errors, CLI, ledger, prompts, checker/
  court messages) — English. Why: the primary reader of errors is the model
  (CEGIS counterexamples into the prompt, the SLM reads the gates, MCP clients);
  coder models are trained on English messages; F7/the external user. Russian F0
  errors were inertia from v0, caught by the user.
- D25 [08-20] ACCEPTED — violating one's OWN contract (post/conserves) or an
  EvalError in the reference = the entity transition is REJECTED + a ledger entry;
  invariants (cross-entity) are observers, they do not block. Why: a genome's
  self-contradiction must be visible, not silently committed.
- D26 [08-20] ACCEPTED — retry_window in F1 is a genome-level contract;
  per-channel windows return with channels in F4 (UNEXPRESSIBLE).
- D27 [08-20] ACCEPTED — rung 0 of the ribosome ladder = a DETERMINISTIC PRINTER
  from the reference: rule bodies are printed, not generated — an SLM is not
  needed in rules at all (free, correct by construction, the court confirms ≡).
  The SLM remains for skills (F3+). Consequence: the "CEGIS ribosome" of F2 = the
  mechanics of counterexamples (court+interview) without a live SLM — a conscious
  deviation from the letter of the PLAN, recorded here.
- D28 [08-20] ACCEPTED — the dialect certificate at the scope of F2 = the printer
  against the conformance corpus (240/240) + build; the EMBEDDED interpreter
  comes with the first eviction (F5). Risk P12 remains open until F5.
- D29 [08-20] ACCEPTED (supersedes D12) — second dialect: python-STDLIB, not
  python-fastapi. Why: the risk of F3 is I1 (a language without core edits),
  fastapi adds nothing to that proof, and D19 requires a skeleton with zero
  dependencies. A fastapi dialect comes when we reach the "framework migration"
  exam (the same persistence/http section, a different tissue).
- D30 [08-20] ACCEPTED — the dialect registry (dialects/registry.py): data, not
  branching; the dialect interface at the scope of F3 = {skeleton.generate,
  gates.build, gates.certificate}.
- D31 [08-20] ACCEPTED — F4 composition: module(gene) = onto+module+exports
  (events)+entities(without instances)+requires.events with STRUCTURAL
  subtyping (a module is typechecked against its own interface-subset); the root
  = imports+bind(instances)+cross-module invariants/queries; linking -> a flat
  hub-Genome (organism/court/dialects know nothing about modules). Overriding
  others' rules is structurally impossible (the root has no entities).
- D32 [08-20] ACCEPTED — an equivalent mutant PROVED by the court gives the
  verdict "EQUIVALENT (proved)", not a blind spot; blindness = only solver-unknown
  with a silent contract. Found on sku.reserve (qty>0 -> qty>=0 with a body
  neutral at qty=0) — a class that v0's fuzzer silently missed.
- D35 [08-20] ACCEPTED — migration in an event-sourced world = rewrite the LOG
  with a functor (rename events/fields, drop); state is recomputed by replay for
  free. The functor (migrations in the NEW root) must cover every breaking change
  from diff_genomes, otherwise it refuses with a listing; the log is backed up;
  the migration is idempotent.
- D36 [08-20] ACCEPTED — subtracting one's own actions: replay does NOT touch
  counters/heat/ledger at all (otherwise a restart = a phantom storm of
  violations and a phantom load for the Placer). Lesson from v0/v5, now in the
  organism.
- D37 [08-20] ACCEPTED — the warden survives ANY broken mutation (incl. broken
  YAML): reject into the ledger, the old organism lives on; the ladder of rights:
  a REVOKE by monitor quota downgrades interventional -> observational in the same
  tick.
- D38 [08-20] ACCEPTED — a skill's budget is COMPLEXITY-based: t(k*n)/t(n) <=
  max_ratio (O(n^2) at k=4 ~16, cut off; O(n log n) ~5, passes). Reason: a live
  exam showed that "X times faster than naive" is a FALSE contract when the SLM
  writes an efficient naive (two-pointer) from the first phase; the budget must be
  true (v0's lesson), and a complexity budget carries across machines.
- D39 [08-20] ACCEPTED — skills are written in the LANGUAGE OF THE CANON (Python),
  judged in-process (property-fuzz with the canonical Expr, equivalence, budget);
  printing skills into other dialects is a separate wave. The sandbox (no
  imports/dunder + constructors of declared types) is hygiene, NOT a security
  boundary (SLM code is trusted after the gates, as in v0).
- D40 [08-20] ACCEPTED — a single mutation gate (core/mutgate.py):
  conservativeness+functor -> COURT (all contracts proved) -> semantic diff (a
  change of behavior under the same contracts = an interview question; accepted
  only with ack_behavior_change in the root). Both mouths — warden.tick_watch and
  propose — call the SAME gate (otherwise they diverge — a v0 scar).
- D41 [08-20] ACCEPTED — a skill = an organ of the organism: POST /skill/<name>
  executes the body from the CERTIFIED cache (fast, fallback naive; named
  artifacts <skill>.<phase>.py are written by the ribosome). A skill without a
  body is an honest 404. Printing skills into the go dialect remains UNEXPRESSIBLE.
- D42 [08-20] ACCEPTED — the MCP mouth of v1 (onto mcp): read tools + propose as
  the only write path (mutgate); the organism is governed by the warden through a
  file watch — propose writes files, the warden picks them up.
- D43 [08-20] ACCEPTED — the membrane of v1 (core/membrane.py, v0's DIRT
  doctrine): external = an island (a trusted hand-written python file, the only
  place with network/IO) + assumptions — boolean Expr over windowed statistics
  {latency_ms, error_rate_pct, calls} (NOT a regex-DSL, NOT §3 upheld); a
  violation = drift_violation in the ledger, quota -> revocation of trust
  (cert_valid=False in the /health passport). An island error = 502, the organism
  lives.
- D44 [08-20] ACCEPTED — snapshots of v1: checkpoint.json = state+seen+log line
  count+HASH; startup = snapshot+tail; a broken snapshot is rejected by hash ->
  an honest full replay (+ ledger). A torn log line (kill -9 mid-write) is skipped
  with torn_lines in the ledger — the truth stays with the log.
- D45 [08-20] ACCEPTED — skill fuzzing: str category fields (sku etc.) come from
  a SMALL shared pool, ids are unique. Unique categories kept cross-parameter
  properties (completeness guards) forever asleep — a toothless fuzzer accepted
  allocate whose contract said nothing about duplicate warehouse lines; the new
  pool exposed the fuzziness, the contract was refined to aggregate semantics
  (sum of available by sku), the ribosome re-synthesized (the semantic cache D6
  was invalidated by the contract change — as designed).
- D46 [08-20] ACCEPTED — a shared event vocabulary = a gene without entities
  (commerce_events; shared_events from v0's EPIC): an exporter of full fields,
  consumers (stock, orders) require their own subsets. A double export of an
  event = linker refusal (caught live).
- D47 [08-20] ACCEPTED — an inductive post cannot express "after transition X,
  property Y": conjunctive strengthening ends up in the pre and goes blind; the
  correct form is a CONDITIONAL post ("s.phase != 5 or s.paid == 0"). Lesson M2
  for interview variants.
- D48 [08-20] ACCEPTED — EventStore (core/store.py): the log = wire history
  (duplicates are legal, dedup is the organism's semantics); tissues jsonl
  (default, fsync/event) and sqlite (WAL, synchronous=NORMAL — the loss window is
  honestly documented); the migration functor and snapshots work over both; the
  fold of one history is byte-identical. sqlite: check_same_thread=False — access
  is serialized by the serve/warden lock.
- D49 [08-20] ACCEPTED — historical phase checks in exams are pinned to a RANGE
  of commits (F2..F3), not "up to HEAD" — otherwise live growth of the core
  breaks CI retroactively (lesson of tools/check.sh).
- D50 [08-20] ACCEPTED — release 0.1.0: README, tools/check.sh (lint+tests+
  5 exams without network) as a single CI entry point, git tag v1-0.1.0.
- D51 [08-20] ACCEPTED — DYNAMIC INSTANCES: Entity.instances: "dynamic" — an
  instance is born with the first event carrying its key (init = zygote), the same
  way in all tissues (interpreter, go, python); an empty key = refusal. Demanded
  by the LAGO campaign (subscriptions are not known at deploy time) — the first
  universal building block of any real product.
- D52 [08-20] ACCEPTED — MAX_BODY_NODES 64 -> 256: Lago's honest invoicing rule =
  145 nodes of PURE arithmetic. The rule/skill boundary is structural (loops/
  algorithmicity), the node limit is a sanitary cap. The growth is under pressure
  from a real domain (§8.1), not speculative.
- D53 [08-20] ACCEPTED — the LAGO campaign: a Lago tenant configuration = our
  genome (metrics/plan/rate — genome constants); transaction_id = dedup D26; the
  billing job = BillingPeriodClosed events from warden/cron; the actual invoice =
  an event in the log (the log = the registry). Court lesson: an inductive post
  must CARRY the hypotheses it uses (period_conn_max >= 0 — counterexample -99).
- D54 [08-20] ACCEPTED — the POLICY wave (the last major IR primitive, ordered
  twice by UNEXPRESSIBLE): Rule.emit = derived events from the POST-state
  (fields/when — Expr, full typecheck against the event schema). Semantics: the
  cascade is SYNCHRONOUS, depth cap 8 (overflow -> ledger); derived events are NOT
  logged and NOT deduped — they are recomputed by replay (determinism by
  construction; the log = only the external world). In all three tissues. Gate: a
  change of emission is unprovable by the court (cascades) => it requires
  ack_behavior_change (mutgate).
- D55 [08-20] ACCEPTED — str state fields (LAGO v2): state: int|str, init default
  ""; str in bodies/emissions (in expressions only ==/!=); all three tissues +
  court (z3.String). Demanded by the domain: a subscription must remember its own
  customer.
- D56 [08-20] ACCEPTED — the invoice registry = a DYNAMIC entity invoice, born by
  the InvoiceIssued emission (the job supplies the id); the CreditsApplied saga —
  a two-key fan-out (one event updates the subscription and the invoice, each by
  its own key). /state/invoice/<id> = Lago GET /invoices/:id. A graduated tariff =
  an IfExp pattern, WITHOUT growing the IR.
- D57 [08-20] ACCEPTED — MODEL.md: the universal development model as the
  constitution of the method (5 layers, the cycle, the roles of intelligence, the
  physics of coverage by software category, the UNIVERSAL U1-U8 program). The
  user's goal — "a packaged system for any software" — is fixed as the frame; the
  point of full demonstration: U1+U2+U5 (an entire SaaS from a genome).
- D58 [08-30] ACCEPTED — growing dialects (IDEAL, pearl 5, growdialect.py): a new
  language = an SLM translation of the canonical phenotype per-genome; gates:
  syntax -> the SAME judge -> parity of folds with the canon -> kill -9/replay;
  CEGIS with judge failures in the prompt; cache by hash (genome+reference+
  language+model) — a certified artifact, like a skill. FACT: the node hotel
  organism was grown by qwen3-coder on the 1st attempt (9 calls, 72k tokens,
  ~$0.02), zero core edits. Bench lesson (the same v0 scar for the third time!):
  the token limit clipped a long file — grow gets max_tokens=12000; strip_code
  understands js/go fences.
- D59 [08-20] ACCEPTED (reconstructed in DECISIONS on 08-30 — the record fell out,
  it lived only in code) — U2 TIME: timers in the genome
  {every_s, event, fields, per?}; executed by the WARDEN (the organism is
  deterministic and has no clock); id = timer:<name>:<epoch>[:<inst>] -> dedup
  makes the tick idempotent; per: an event for each live instance.
- D60 [08-20] ACCEPTED (reconstructed 08-30) — U1 QUERIES: parametric queries
  ({params, expr} with p.<name> in Expr) + generic
  /list/<entity>?field=value&_limit&_offset (equality filter, sort by key,
  pagination) — read models without growing the IR.
- D61 [08-20] ACCEPTED (reconstructed 08-30) — U5 ADMIN PANEL: /admin is printed
  from the genome (population tables via /list, event forms from schemas, query
  buttons); zero hand-written UI code for the operator.
- D62 [08-20] ACCEPTED (reconstructed 08-30) — U6 WEBHOOKS: webhooks
  {event type -> url}, delivery AFTER application, fire-and-forget, an error ->
  ledger webhook_error; the client's organism does not wait.
- D63 [08-30] ACCEPTED — the wave "THE MODEL GROWS THE ISLANDS" (IDEAL pearl 4,
  growisland.py): the island adapter is written by the SLM from the external spec
  in the genome. IR growth (External): intent (an NL description of the
  integration — the model's input) and cases (acceptance: [{payload, expect}],
  expect is a subset of the response, "*" = the field must be present). Gates
  (CEGIS, cache by spec hash): (1) compile + provides + a whitelist of imports
  (json/os/time/math/hashlib/urllib — a sanitary membrane; the final accept is a
  human); (2) ACCEPTANCE THROUGH FLAKINESS: cases are run through MonitoredAdapter
  against a LIVE (flaky) upstream — the model is FORCED to write retries,
  otherwise the cases are red; (3) the passport after the run: cert_valid and the
  assumptions are intact. Retries are the island's duty (a prompt requirement),
  NOT IR growth. A manual island remains a legal exception (trusted code).
- D64 [08-30] ACCEPTED — the wave "GENERATOR GROWTH" (pearl 5, form v1): the model
  grows not the organism (per-genome, D58) but a GENERATOR — a python module
  `generate(g, outdir)` that prints organism.js for ANY genome of a class (v0
  bounds: without dynamic/emit/skills/externals — like hotel/shop/booking). The
  model's input: the reference generator of the python dialect + a sample grown
  organism.js (hotel) + the genome API. Gates (CEGIS): a CERTIFICATION SET of >=2
  genomes (hotel, shop) — on each, the same gates as D58 (node --check -> the SAME
  judge -> parity of folds with the canon -> kill -9/replay); failures tagged with
  the genome -> into the prompt. A certified generator must pass a CONTROL on an
  unseen genome (booking) WITHOUT calling the model — this is exactly what
  distinguishes a generator from a per-genome translation. Cache by hash
  (reference+sample+language+model). Expr bodies are translated by the generator
  (ast); a full conformance corpus for grown dialects is the next step, a tail in
  the PLAN.
- D59 [08-30] ACCEPTED — U2 TIME: timers in the genome {every_s, event, fields,
  per?}; executed by the warden (the organism is deterministic, has no clock);
  id=timer:<name>:<epoch> — the tick is idempotent; per: an event to each live
  instance (/instances). Flows do not depend on a clock (the judge has no
  scheduler).
- D60 [08-30] ACCEPTED — U1 QUERIES: parametric queries {params, expr}
  (env p.*; /q/name?arg=v) + generic /list/<entity>?field=value&_limit&_offset
  (equality filter, pagination) — without growing Expr.
- D61 [08-30] ACCEPTED — U5 ADMIN PANEL: /admin — HTML from the genome (population
  tables, forms for all events, query buttons; auto-refresh). Zero hand-written
  UI code.
- D62 [08-30] ACCEPTED — U6 WEBHOOKS: webhooks {event: url} — POST outward after
  applied, fire-and-forget, errors into the ledger.
- D63 [08-30] ACCEPTED — the membrane received the island-growing spec
  (intent+cases) — pearl 4 is prepared.
- D64 [08-30] ACCEPTED — NL FRONT (the spine): a description -> genome+acceptance;
  gates = checkers+COURT+self-acceptance by the judge; CEGIS. The CHEATSHEET =
  knowledge of the system (analog of admixtures), grown by EXAMS: a worked example
  of clamps, the SAGA PATTERN (cross-entity preconditions), "totals = queries",
  "guard amount>0", "flows are sequential on ONE organism — a global query is
  cumulative", "test timers in flows with their own event". The Sonnet->Opus
  ladder. Convergence lessons: both strong models failed on the SAME unspoken
  contracts of the testbench — fixed by the cheatsheet, not by model strength.
- D65 [08-30] ACCEPTED — packaging: onto new <name> --template
  scooters|hotel|lago|market; release 0.2.0.
- D66 [08-30] ACCEPTED — U3 TYPES-2 as REPRESENTATION (not semantics): decimal
  (minor units, scale 2) and timestamp (unix seconds UTC) — field types of
  state/events; load normalizes them to the int carrier + a map g.reprs. The
  court/log/replay/dialects see ONLY the carrier. The HTTP membrane: the input
  always accepts human forms ("12.34", ISO-8601), the output is by ?repr=human;
  the admin panel knows the hints. optional/list-state primitives were REJECTED
  (NOT §34-35): a flag/""-sentinel; a list = the population of a dynamic entity.
- D67 [08-30] ACCEPTED — U4 AUTH GENE: auth {idp, rules} in the genome; the rules
  are bool-Expr over {principal.role, principal.subject, ev.*} (the same Expr, the
  same typecheck — NOT §3); the IdP is an island behind the membrane (drift
  monitors judge it too); deny-by-default (an event without a rule = 403);
  refusals are auth_denied in the ledger with provenance; mutations are protected
  (POST /event), the admin panel gets a token field. Zero hand-written
  authorization code.
- D68 [08-30] ACCEPTED — GROWTH OF THE DIALECT GENERATOR (pearl 5, rung 2): the
  model itself writes the emitter emit(genome)->organism.js (growgen.py); the
  gates are MULTI-GENOME CEGIS: certification on a set of genomes
  (hotel+shop+billing2), on each — node --check, the same judge, parity with the
  canon, kill -9/replay (growdialect's gates reused). Homology: the samples in the
  prompt are our own printing emitter of python-stdlib + the js phenotype of rung
  1. Exam: qwen/qwen3-coder and -plus exhausted 4 attempts each (the meta-task "a
  generator of generators" is beyond them), Sonnet — GREEN on the 3rd; then a
  FRESH genome (booking) was printed WITHOUT calling the model and passed all
  gates. The dialect stopped costing tokens: the ladder just did not reach the
  free rung at the moment of growth, beyond that — pure printing. fgengrow is
  networked — outside CI.
- D69 [08-30] ACCEPTED — U8 OPERATOR CONSOLE: /ops from the organism — the ledger
  (tail, filter by kind, provenance, the hash chain visible), external passports
  (REVOKE visible), heat, a checkpoint button. Interview/molt remain CLI (offline
  design mechanics) — the console shows their TRACES in the ledger; a button-driven
  web interview is not built, an honest remainder.
- D70 [08-30] ACCEPTED — release 0.3.0: U1-U6, U8 of the constitution are closed;
  all 5 IDEAL pearls are alive (the 5th in two rungs: per-genome growth + generator
  growth). The IR is NOT frozen: we will declare the v1.0 freeze after U7 (skills
  in all tissues) — it is too early to freeze the format before the last organ.
- D71 [08-30] ACCEPTED — U7 SKILLS IN ALL TISSUES: (1) the python tissue — PRINT
  certified bodies from the ribosome cache into the phenotype (fast|naive,
  materialize --skills-cache; without a body — an honest 404); (2) the go tissue —
  RPC to the canon (ONTO_SKILL_CANON; without it — 501 with a hint). Printing does
  not re-judge (the ribosome gates were passed at synthesis), the exam judges
  parity: fy7 — 60 fuzz cases print==canon, 30 cases go==canon, 0 divergences.
  Along the way: printing survives a clean core (events: {}).
- D72 [08-30] ACCEPTED — FREEZE OF IR v1.0 (release 1.0.0): the fingerprint
  sha256(json schema of the genome models) is embedded in
  ir.FROZEN_V1_FINGERPRINT; tests/test_freeze.py fails on ANY change of format.
  The legal path: bump HUB_VERSION + a converter vN->vN+1 + a new fingerprint in
  ONE commit. Silent format evolution is mechanically forbidden. The whole genome
  gallery loads in the frozen format (except the deliberately broken smuggler).
- D73 [08-30] ACCEPTED — THE MAIN EXAM "ANY PRODUCT" (fgauntlet): a gauntlet of
  universality — 8 deliberately distant domains (library, parking, auction,
  support+escalation, fitness+freeze, delivery with a 3-sided saga, a warehouse
  with inventory, a game rating with a clamp and bans), each: a description -> NL
  front -> an independent COURT. 8/8 PASSED (268k tokens, 64 calls, 21.5 min). The
  ladder worked for real: Sonnet converged on 3/8 by itself (warehouse — on the
  2nd attempt), 5/8 finished by Opus after an honest exhaustion of 8 Sonnet
  attempts. The ninth description was DELIBERATELY inexpressible (video hosting+
  ffmpeg+HLS): an honest REFUSAL (island), not a fake — the boundary of
  expressiveness is examined as a feature. Networked, outside CI; the cache makes
  repeats free.
- D74 [08-30] ACCEPTED — REMOVING THE PARADIGM'S SHORTCOMINGS (PARADIGM_LIMITS ->
  mechanisms; fparadigm 13/13, fcold 4/4):
  §1+5+9 `onto attest` — the GUARANTEE PASSPORT: clause-by-clause court,
  assumptions, monitors, the WEAKEST SEAM NAMED, provenance (genome hash, engine,
  IR fingerprint); attest.json/md — a signable release artifact.
  §3 HARDENING: `onto harden` — an escape (wrong-but-passes from production) ->
  a regression corpus regressions/<skill>.jsonl; the corpus judges both SYNTHESIS
  (the ribosome) and the CACHE at mount time — an escape revokes the certificate
  retroactively (ledger skill_cert_revoked_by_escape).
  §4 NOT-KNOWING: a third interview outcome — declare_unknown -> assumptions.yaml
  (next to the genome, the IR untouched): a typed hole with a watch-Expr;
  warden.tick_assumptions writes hits in the region of uncertainty into the
  ledger; resolve_unknown revokes it. Islands, applied to knowledge.
  §6 LOSSINESS: drop_events without migrations.declared_loss — the gate is red;
  the warden writes declared_loss into the ledger. A loss is legal only when
  declared.
  §8 COLD REASSEMBLY: fcold — the key is physically dead, the NL genome and the
  grown island are reassembled from certified caches, 0 network calls;
  genomes/.grown — a permanent cache in the repo (like cache_skills).
  §11 ENGINE PIN: onto new writes engine.pin (version+IR fingerprint); on a
  mismatch, serve gives a WARNING + ledger engine_pin_mismatch ("an upgrade = a
  molt, not a silent merge").
  Non-mechanisms (§2 non-formalizable properties, §7 a real incident, §9 org
  institutions, §10 the price of the first stack) — honestly in
  PARADIGM_LIMITS/UNEXPRESSIBLE.
- D75 [08-31] ACCEPTED — the "MATHEMATICS" EPIC: Part VII of the corpus
  (v1/math/PART_VII.md) — the first block of theory, born from practice and
  OBLIGED to agree with measurement (exams/fmath, in CI). Wave results:
  §1 growth as an absorbing chain: a VALUABLE NEGATIVE — the gauntlet telemetry
  (51 attempts) does NOT distinguish memoryless from an informative loop (β̂=0,
  LR=0); the draft predicted the opposite and was refuted by its own exam (the
  theory was fixed, not the exam). Positive: model strength = a shift of p0
  (P[Opus 5/5|p=1/8]=3e-5), the cheatsheet = a transfer of p0 without changing the
  model; Proposition 1 (economics: a cheatsheet lesson amortizes, escalation is
  paid each time; the norm "exhaust the ladder -> a lesson").
  §2 the organism as a MEASURABLE operator: lemmas 6.1/6.3/6.4 of Part VI computed
  for the first time on a live organism.handle() (a swamp: D(S)=3.7≈E[τ]=3.6,
  D≥1/ε, hazard majorant); a construction lesson: without a reset move the uniform
  hazard of a swamp is ZERO — reset ≡ REVOKE/rollback, the theory and D74 closed
  together.
  §3 theorem VII.1 (composition of quantile certificates, weakest-link:
  (η_B+L_B η_A, q_A+q_B-1, δ_A+δ_B)) — proved + verified; a DKW certificate of a
  real skill: (η=0, q≥0.906, δ=0.01, M=300).
- D76 [08-31] ACCEPTED — the MATHEMATICS EPIC, waves M2-M5:
  M2 (P15 CONFIRMED): gauntlet lessons (a fan-out router, two-sided accounting,
  pointer keys, money-via-emit) written into the cheatsheet -> 5 former opus tasks:
  4/5 sonnet-green (was 0/5), 2 first-try; the nul ~10^-3. The transfer of p0 by
  the cheatsheet is real. Remainder: library (two-sided accounting) — an island:
  the lesson is under-learned, the class is not covered.
  M3 (fspectral, in CI): the operator of a non-toy organism (booking) is measured
  (λ_slow=0.874, R²=0.33); metastable corruption is caught by the spectrum
  (λ→0.996), a freeze by variance: the corruption detector is TWO-COMPONENT (the
  lesson of the first run, which refuted the naive design). The threshold is not
  calibrated — it is not declared in the passport.
  M4: attest carries DKW quantiles of skills (relative to ν_gen) and hazard
  survival moves (REVOKE h=1, rollback h=1 by construction of the move, crash_loop
  honestly NOT MEASURED) — fparadigm extended.
  M5 (an adversarial review, math/REVIEW_1.md): accepted almost entirely —
  VII.1 -> VII.1' with explicit conditions (i)-(iii), Proposition 1 -> Norm 1
  (the rental cost of a lesson), "verification of lemmas" -> "calibration of the
  pipeline", the retraction of "strength does not act on β". The reviewer won by
  DEED: the demand for live telemetry instead of constants immediately found an
  error (a lost impossible series). fmath: telemetry live, an antithetic coupling
  (the Fréchet bound is reached), a chi-bar threshold.
- D77 [08-31] ACCEPTED — the REMAINDER OF THE MATHEMATICS EPIC (faudit 5/5,
  fcompose 4/4, library 5/5, all in CI):
  SPECTRAL AUDIT IN THE WARDEN (tick_spectral): the threshold is calibrated from a
  healthy window (not by hand), the vocabulary selection (trend + relative
  variance — both filters mined from exam failures) in the calibration certificate,
  a Markov test; health is silent, corruption -> spectral_drift, a freeze ->
  variance_freeze in the ledger.
  IN-SITU VII.1' (fcompose): conditions (i)-(ii) verified by the engine on a live
  saga; the Fréchet bound reached by live data.
  AN ENGINE RAKE FOUND THROUGH "MODEL WEAKNESS": library did not converge because
  the judge CRASHED on keys with spaces -> an empty counterexample -> blind CEGIS.
  Fixed judge (URL quoting), serve+py-skeleton (unquote), nlfront (judge trace into
  the verdict). After the fix Sonnet closed library in 3 attempts. P15 result: 5/5.
  P16 mechanism: N attempts is counted across all telemetry (now 133), the refit is
  preregistered at N>=200.
- D78 [08-31] ACCEPTED — the ν-BRIDGE (Part VII §6, fnu 7/7 in CI): the gap
  fuzz-ν ↔ prod-ν (the review v2 frontier) is closed by a theorem+mechanism.
  Theorem VII.2: the organism kernel is LINEAR in ν (MEASURED: 0.020 at noise 0.04)
  => the operator shift ≤ TV(ν',ν) (measured: 0.537≤0.55); per-event certificates
  transfer with a domination factor C (q' ≥ 1-C(1-q)); a spectral transfer WITHOUT
  OATHS (κ not attested, empirics: monotonicity in TV). Mechanism: the organism
  counts by_type; the calibration certificate carries ν̂ and nu_tol FROM subwindows
  (not by hand); the warden measures load TV, nu_drift into the ledger BEFORE the
  silent staleness of thresholds. Load = a membrane assumption (the D43/U12
  pattern). The v2 retraction was re-checked by a run: the figures are confirmed (a
  correction: R²=0.34 against a gate of 0.2 — margin, not "right at the edge").
  Open: state-dependent defects, κ-attestation.
- D79 [08-31] ACCEPTED — PRODUCT FREEZE (1.1.0, FREEZE_v1.md): attest prints
  END-TO-END PATHS (event->rule cascade->webhook; PROVED end-to-end by
  clause-by-clause court; the webhook honestly fire-and-forget); CLI help complete;
  OPERATOR.md grew to all organs (all surfaces, a passport before release, a
  3-a.m.-incident runbook, harden, not-knowing); the warden CLI ticks ALL organs
  (watch, monitors, timers, spectrum+ν, not-knowing holes); CALENDAR LIFE LAUNCHED
  (life/: an NL-grown meeting-room organism under a full warden + a pulse, nohup;
  it passes the test of time). Networked exams outside CI are listed in FREEZE.
  What is open after the freeze is there too, nothing hidden.
- D80 [08-31] ACCEPTED — THE SECOND EXTERNAL REVIEW: ALL SIX HOLES CONFIRMED BY
  REPRODUCTIONS AND REMOVED (+3 class findings; tests/test_review2.py — 8 guards in
  CI):
  (1) DIVISION SEMANTICS: the court encoded // as SMT-euclidean — it proved
  -7//-2==4 while the canon is 3. Fix: an exact floor encoding
  If(b>0, div(a,b), div(-a,-b)) + mod through it. Class findings: division by zero
  (the canon throws, SMT is total) — now the obligation "divisor != 0" (guard
  divisors without context — lazy and; the rest under a guard), otherwise
  unsupported; the js % of the grown generator — JS semantics (sign of the
  dividend) — recorded in UNEXPRESSIBLE as a certification boundary.
  (2) "PROVED" WAS SELF-INDUCTION: init⊭post and neighboring rules gave "ALL PROVED
  and dead". Fix: prove_entity — entity induction by the HOUDINI ALGORITHM (the
  maximal inductive subset of posts + posts under I∧guard without the noop branch).
  The WHOLE gallery is ENTITY-INDUCTIVE ("a refusal by post is impossible from
  init" — earned, not declared); the passport distinguishes self-induction from
  entity induction. A FINDING IN BATTLE: lago invoice.issue accepted ev.total<0
  (the post is refutable) — a guard was added.
  (3) MUTGATE SILENTLY SWALLOWED UNKNOWN (a violation of I7, the court/mutgate
  mouths diverged): unsupported/unknown now = "NOT certified, ack_behavior_change
  required".
  (4) A BROKEN SNAPSHOT + dynamic: the reset iterated the string 'dynamic'
  (letters-as-instances) and did NOT bury the ghost for static. Fix: a full reset
  of populations.
  (5) THE HASH CHAIN WAS NOT VERIFIED (decoration, NOT §12): Ledger.verify()
  + chain in /ops/ledger. A class finding IN THE FIX: kind was not part of the hash
  — substituting the record kind did not break the chain; hv=2 includes kind
  (legacy is verified).
  (6) ATTEST LIED ABOUT INVARIANTS (in 'proved' while checked at runtime): moved
  into monitored.runtime_checked_invariants.
  METHODOLOGY (accepted): P15 in-sample — acknowledged; the HELD-OUT test
  (fheldout, 2 unseen domains): fan-out GENERALIZES (green on the 1st), two-sided
  accounting — NOT (an island): lessons transfer unevenly, the "5/5" of P15 is
  reclassified as in-sample efficiency. The gauntlet's "proved" = range posts +
  (now) entity induction.
- D81 [08-31] ACCEPTED — REPO SHIPPED IN ENGLISH: all prose, comments,
  docstrings, printed strings and theory/docs translated Russian->English
  (8 parallel translation agents over disjoint file groups, then a
  theory/flows sweep and a genome-intent sweep). Coined phase/wave ID
  tokens transliterated 1:1 to Latin (phase F, wave U, packaging P, LAGO L,
  dirt G, math-epic M, and Cyrillic decision-refs merge into Latin D). CI
  stayed green: runtime loads
  skills by name.phase and islands by file path, so translating `intent:`
  (which IS in the growth cache_key) does not affect the served organism —
  only growth caches (network exams) would regrow once. FREEZE HARDENED:
  ir.schema_fingerprint now strips description/title so the freeze guards
  STRUCTURE (field names/types/required), not prose — a docstring
  translation is not a format change; fingerprint rebaselined in this same
  commit. Deliberate residual: cache_skills/.grown are clean; docs/
  anatomy.html and lago/SPEC.md, spikes/expr/* handled in a follow-up.
- D82 [08-31] ACCEPTED — P2 DELIVERY WIRING: `onto init` (scaffold.py)
  couples a project to the engine + harness in one shot: .onto/{cache,ledger,
  checkpoints,hooks} + genome/ starter + engine.pin + config.toml.example +
  .gitignore; for the Claude harness — .mcp.json (registers `onto mcp
  genome/genome.yaml`), a workflow skill, a CLAUDE.md fragment, and THE
  KILLER MOVE: a PreToolUse EDIT-GUARD HOOK (.onto/hooks/guard_edit.py +
  .claude/settings.json) that mechanically blocks Edit/Write to onto-owned
  paths and tells the harness to use `propose` — invariant I4 turned into a
  rail the harness physically cannot bypass. Ownership is explicit
  (genome/ + materialized output in .onto/owned.json; materialize appends
  its out-dir); the rest of the repo is the human's. Exam finit: init ->
  scaffold complete -> hook BLOCKS genome edit / ALLOWS non-owned edit ->
  starter court entity-inductive -> materialized phenotype auto-protected.
  Coupling (MCP read/court/explain/propose) already existed; this closes the
  delivery gap, not architecture.
- D83 [08-31] ACCEPTED — TIER A (pre-release math dial-up; ftier_a 11/11,
  in CI): four upgrades, zero new mechanisms, no compromise with "proved".
  #5 INVARIANTS PROVED: court.prove_invariants inductively proves the
  decidable class — an invariant over exactly ONE entity with FIXED
  instances (reachability premise = the entity's proven posts). Passport
  splits invariant: proved | monitored; cross-entity/dynamic stay monitored
  with an honest reason. money_sane (refund unbounded) correctly stays
  monitored (real counterexample), market still green — invariants never
  fail court, they only UPGRADE. Answers "from testing to proving" where
  money lives.
  #8 SPECTRAL ORGAN GETS HANDS: a tick_spectral verdict now DEMOTES rights
  (interventional -> observational) + records a recalibrate_proposal, not
  just a ledger note — satisfies the project's own law (NOT S3: a formula
  must act or it is decoration). Part VII stops being a diary, becomes an
  organ with consequences.
  #10 onto replay --until <event>: time-machine debugger — read-only replay
  into a scratch dir (real log untouched), prints state/watch at the stop.
  The event-sourcing answer to "where is my breakpoint".
  #4 ENTITY-COURT IS THE HEADLINE: onto court/attest already ran entity
  induction (D80); now it is named the strong guarantee ("post rejection
  impossible from init"), per-rule marked self-induction. PROVED means what
  the operator thinks it means.
  Validated against a second agent's proposal set: #4/#7 were already done,
  #6 (z3 auto-synthesis of interview variants) overstated as feasible ->
  deferred; the rest confirmed and built here.
- D84 [08-31] ACCEPTED — TIER B cheap pair (release-safe, no compromise):
  #6 INTERVIEW GENERATES VARIANTS (interview.generate_variants; fvariants
  5/5, in CI): the interview now PROPOSES completion variants instead of
  only checking hand-written ones (SPEC §11 promised A/B/don't-know).
  Templates are enumerated from the court counterexample (sign guards,
  field orderings, non-negativity/bound posts) and each is CERTIFIED by the
  court via _variant_resolves — intelligence in the gate, enumeration cheap.
  On the F2 booking case the system re-discovers 's.booked > 0' unaided;
  every offered variant provably resolves; unresolved -> the U12 'I don't
  know' path stays the honest fallback. detect(variants=None) auto-fills;
  the explicit-variants path (tests) is preserved.
  TRUST.md: honest execution-boundary page — what runs (rule Expr / SLM
  skill bodies / islands / printed phenotype), who authored it, and the
  plain statement that skills are hygiene-not-sandbox and islands are
  unrestricted, so a foreign genome+cache runs untrusted code. Guaranteed
  vs NOT guaranteed spelled out; real process isolation (rlimit+seccomp)
  deferred to the pre-gene-pool wave (validated cost: 2-4d + permanent
  cross-platform tail, closes an as-yet-nonexistent scenario).
  Tier B verdict recorded: ship the cheap pair (#6 + TRUST.md, ~2d, both
  advance spirit); defer #1b seccomp and #9 full LSP (adoption/security,
  not math, with permanent tails) to post-release.
- D85 [08-31] ACCEPTED — GENE POOL DISTRIBUTES DNA NOT PROTEINS + FREE IDE
  (fgene 6/6, in CI): three moves that DISSOLVE the seccomp/LSP tails into
  the doctrine instead of paying them.
  MOVE 1 (design lock, ship before anyone gets used to shipping caches): a
  gene distributes as CONTRACT ONLY (the Skill model is already body-free —
  params/returns/types/intent/properties/budget; bodies live in cache_skills/
  separately). Bodies NEVER travel; a body regrows locally via the local
  ribosome against the received contract, through local gates, into the local
  cache (mechanism already exists: ribosome + D6 cache + CEGIS; cost ~$0.001-
  0.02/skill once). You never execute a stranger's Turing-complete code —
  seccomp's threat model largely dissolves. Residual risk named in TRUST.md:
  foreign INTENT is a prompt-injection vector -> MITIGATION: onto court runs
  a property-strength gate (gate_teeth) — a gene whose properties a lazy
  return-[] oracle survives is REJECTED, cannot be installed. Strong
  properties = the immune check.
  MOVE 2 (deferred, but re-scoped cheaper): local-body isolation = capability
  starvation (subprocess, empty env, closed fds, resource.rlimit CPU/RSS) +
  determinism double-execution gate — bounded POSIX, NOT a rotating seccomp
  profile; the pre-gene-pool wave. seccomp may never be needed.
  MOVE 3 (shipped): frozen IR = free IDE. `onto schema` dumps the genome JSON
  Schema from pydantic (one line); `onto init` writes it + a modeline, so any
  editor's yaml-language-server (maintained by Red Hat) gives autocomplete +
  diagnostics — ZERO tail (schema derived from the frozen fingerprint, D72).
  `onto watch` gives live Expr diagnostics with coordinates next to any
  editor — no LSP, no protocol, no marketplace. Full LSP deferred until a
  live F7 human says schema+watch is not enough (then demand justifies tail).
  Validated a second agent's three moves against the code: all three sound;
  LSP-protocol rot was slightly overstated (LSP 3.x is stable — the real tail
  is the marketplace extension, which onto schema sidesteps entirely).
- D86 [08-31] ACCEPTED — MODEL REGISTRY in the ribosome (fmodels 11/11, in
  CI): easy, broad, user-friendly provider/model config (Claude-Code /
  Kilo-Code style). Any number of named OpenAI-compatible providers
  ([provider.<name>]); models referenced as 'provider:model' or bare (->
  [default].provider); ':' is the split ('/' stays inside OpenRouter model
  names). base_url PRESETS for known names (openrouter/openai/groq/together/
  deepseek/mistral/fireworks/xai/ollama/local/lmstudio) — name a provider,
  give only a key. Key resolution is safe+flexible: '${ENV}', '$ENV',
  '@/path/to/keyfile', or literal — never hardcode. PER-TASK LADDERS
  ([ladders] skills/nl/dialect/island) that can MIX providers
  (e.g. nl=["anthropic/... via openrouter","local:qwen2.5-coder"]); nl never
  falls back to a weak skills ladder, growth tasks inherit a configured
  skills ladder. New `onto models` prints providers (key present?), the
  default, and the ladders (no network). FULLY BACK-COMPATIBLE: the legacy
  single-[provider.openrouter] + [ribosome].skills_ladder form still loads;
  all exams unchanged. Rich config.toml.example + scaffold updated.
- D87 [08-31] ACCEPTED — SHIP P3+P4 PACKAGING + LEGACY CLEANUP (fship 10/10):
  P3: templates now ship as PACKAGE DATA (src/onto/templates_gallery/{starter,
  hotel,lago,market}, self-contained genome+flows+modules+islands); `onto new`
  reads them via importlib.resources, so it works from an installed wheel with
  NO repo and NO network. pyproject ships the gallery (artifacts glob).
  LEGACY REMOVED: the broken 'scooters' template (referenced gitignored
  build/scooters_nl) is dropped; `onto new` default is now 'starter'; repo-path
  reads (v1root/genomes, /modules) gone from the runtime path.
  P4: exam fship (packaging suite, not offline CI — needs uv + PyPI deps once):
  build wheel -> install into a CLEAN venv -> onto version/new/court/schema/
  serve/judge/attest run offline on a packaged template with the env stripped
  of the repo; plus a repo-hygiene gate (no keys/pyc/attest/build/.onto
  tracked). fship immediately caught a real regression — the `onto new`
  rewrite had deleted the init/models/schema/watch command blocks; restored.
  Scan confirmed no dead src modules and no orphan genomes; the non-CI local
  exams (f2/f5/f6) and the network exams are the validation corpus, kept.
- D88 [08-31] ACCEPTED — PORTS: transport is a configurable, NATIVE functor on
  the I/O boundary (exam fports 5/5, in CI). One law generates every beast:
  the fold is the invariant, a port is a (decode, encode, driver) triple that
  must preserve it (fold-parity gate — the same as growdialect/D48 — plus
  round-trip). Sync=pull (state/query), async=push (emissions D54); one
  organism exposes MANY ports at once, each a projection of one fold ->
  consistent by construction. Untrusted delivery = membrane (stats -> drift ->
  REVOKE, port_trust_revoked in ledger); retries+backoff are a port policy.
  Built: src/onto/ports/ (base: Bus + registry + fold_parity law-gate; http:
  reference sync/pull port + web-out with retries; queue: async in/out with
  retries + REVOKE). Declared in ports.yaml next to the genome (NOT the frozen
  IR — transport is a surface). `onto serve --ports` runs all ports over one
  organism. A thin emit-hook on the organism surfaces D54 emissions to
  out-ports (observation only, no IR/semantics change). Real Kafka/gRPC
  adapters are grown against the same gate (growport) — open-ended, 1..inf.
- D89 [08-31] ACCEPTED — growport: the transport tissue is GROWN, not
  hand-written (exam fgrowport 3/3, network, cached like fisland). Declare the
  beast as a spec (intent + cases); the model writes the wire codec
  (decode/encode); the GATE certifies it by (1) sanitize + import whitelist,
  (2) ROUND-TRIP over the cases (both directions), (3) FOLD-PARITY through the
  codec (drive flows as wire -> byte-identical fold, the same certificate as
  growdialect/D48). qwen3-coder grew an envelope codec on the FIRST attempt;
  the grown codec plugs into a live QueuePort (cfg 'codec' path). Offline-
  provable on the in-process Bus; a real Kafka/gRPC adapter is the same grown
  codec behind a driver swap at deploy (dependency in the door, not the brain).
  Now EVERY tissue is grown+gated: genome->dialect (growdialect), I/O->island
  (growisland), generator (growgen), transport->port (growport). Ports 1..inf
  generated by the fold-parity law, none hand-written.
