> Status: Part VII belongs to the theory corpus in , which is a free-form compilation of known results written without a literature check. The map to public sources: [README.md](README.md) §12. No priority is claimed.

# Part VII. The mathematics of growing (the first block of theory, born from v1 practice)

Parts I–VI were written BEFORE the live engine. v1 delivered what the corpus
lacked: growth telemetry (90 calls of CEGIS ladders), living organisms with logs
and gates. Part VII is the first block where theory is OBLIGED to converge with
measurement: every statement is either proved, or fitted and checked by an exam
(exams/fmath.py), or honestly declared a hypothesis. The corpus's style is
preserved: definitions → theorems/propositions → data → open questions. There
are FOUR categories of statement: proved / measured (with an exam) / hypothesis /
NORM (engine policy — not a statement about the world; flagged explicitly).

---

# §0. Inventory: concepts from v1 practice and the status of their formalization

| concept from practice | where it lives | formalization status |
|---|---|---|
| CEGIS ladder (model+gates+counterexamples) | ribosome, nlfront, grow* | §1 (this part) |
| cheatsheet (admixtures of bench knowledge) | nlfront IR_CHEATSHEET | §1.4 |
| determinism-through-certification (cache) | D6, fcold | §1.5 (norm) |
| organism as a measurable operator | organism.handle | §2 (this part) |
| survival/hazard-moves (REVOKE, rollback) | D74 queue | §2.3 + Part VI |
| quantile gates, attestation | attest, gate_semantics | §3 (this part) |
| escape/hardening | harden | Cor.3 of Part III (already implemented) |
| unknowns as a hole with a monitor | declare_unknown | islands-over-knowledge; formalization open |
| Γ for tissues (gate factorization) | growgen practice | open (open-3) |

---

# §1. Theory of growing: growth as an absorbing chain with an informative loop

## 1.1. Objects

**Definition 1 (growth task).** A triple \(T=(\Sigma, G, \mathcal H)\):
specification \(\Sigma\) (description+cheatsheet), gates \(G\) (a machine judge:
checkers, court, acceptance), the admissible space of artifacts \(\mathcal H\).
An artifact \(a\) is **green** if \(G(a)=\varnothing\) (no counterexample).

**Definition 2 (oracle-model).** A stochastic map
\(O_m(\Sigma, C)\mapsto a\), where \(C\) is a finite list of counterexamples
from past attempts. The parameter \(m\) is the model (sonnet, opus, qwen…).

**Definition 3 (CEGIS loop).** \(a_t=O_m(\Sigma,C_{t-1})\);
\(C_t=C_{t-1}\cup\{G(a_t)\}\) on red; stop on green or at
\(t=K\) (exhaustion of the rung; escalation RESETS \(C\) — measured in v1:
nlfront/growdialect zero out cxs on a new model).

## 1.2. Two competing models of an attempt

- **Model A (memoryless):** \(\Pr[\text{green at }t]=p\) — a constant.
  Counterexamples are useless, the loop is just retries.
- **Model B (informative loop):** \(p_t=\min(1,\,p_0+\beta(t-1))\),
  \(\beta>0\): each counterexample narrows the oracle's error class.

**v1 data (fgauntlet gauntlet, 8 unfamiliar domains, Sonnet, K=8):**
green on attempts {1 (warehouse), 4 (delivery), 6 (fitness)}; 5 tasks
exhausted (8 reds). In total 51 attempts, 3 greens, first-try 1/8.
The fmath §1 exam fits A and B by maximum likelihood.
**Measurement result (VALUABLE NEGATIVE):** \(\hat\beta=0\), LR=0 — over 51
attempts the data gives no advantage to model B. The draft predicted
\(\hat\beta>0\) and was refuted by its own exam.
**Review caveat (accepted, review §1.1):** the comparison was made with FULL
POOLING of heterogeneous tasks into a single p; a mixture of constant \(p_{task}\)
mimics negative aging of the aggregate hazard and may mask
\(\beta>0\) within a task — the conclusion is narrowed to: "in the pooled
setting no advantage of B was detected". The refit protocol (P16, pre-registered):
a hierarchical model \(p_{task}\sim\mathrm{Beta}\) against the same + β;
the threshold — chi-bar-squared (β on the boundary), level 0.05; N≥200 attempts from
usage_*.jsonl (telemetry accumulates on its own). Qualitative cases
of informativeness (growgen: 2 counterexamples → green) are anecdotes until the refit.

## 1.3. Model strength — a shift in \(p_0\), not the loop

**Fact (measured; formulation narrowed per review §1.2):** after
Sonnet was exhausted the counterexamples were reset; Opus solved from scratch and closed
**5/5 on the first attempt** under the SAME \(\Sigma\) (the cheatsheet did not
change within the run). Test of the hypothesis \(p_{\text{opus}}=p_{\text{sonnet}}\):
conservative toward selection (Opus received only the tasks that Sonnet
failed — on those the true null is even smaller than the marginal); an
interval estimate of the null: even at \(p^{\text{first}}_{\text{sonnet}}=0.3\) (the upper
edge compatible with 1/8 successes) \(\Pr[5/5]=0.3^5\approx2.4\cdot10^{-3}\)
— rejected at 0.01. The claim "strength does not act on the slope β" is
RETRACTED: there is no data on \(\beta_{\text{opus}}\) (Opus did not work with
\(C\neq\varnothing\)).

**Fact (measured, growgen):** on the meta-task "generator of generators"
the qwen rungs are 0/8, Sonnet green on the 3rd (the loop finished it off in 2 counterexamples):
task classes are ordered by \(p_0(m,\text{class})\), and the ladder is an
ascent along \(p_0\).

## 1.4. The cheatsheet: transferring \(p_0\) without changing the model

**Fact (measured, NL waves):** before the "SAGA PATTERN" lesson Sonnet
oscillated on cross-entity preconditions (0 first-try); after the lesson was added —
scooters and rooms converge on the 1st attempt (~4k tokens). The cheatsheet is a narrowing
of \(\mathcal H\) to the subspace compatible with the bench's unspoken
contracts: it acts as a rise in \(p_0\) for ALL tasks of the class.

**Norm 1 (economics of growth; POLICY, not a theorem — review §1.3
accepted).** A cheatsheet lesson is not a one-time payment but a rent: +\(\Delta_{tok}\)
tokens IN EVERY call (the lesson lives in \(\Sigma\)). An honest comparison over
\(n\) tasks of the class: escalation \(n\cdot\Delta_{\text{esc}}\) versus
\(n\cdot\Delta_{tok}+\Delta_{\text{authoring}}\). Measured in v1:
\(\Delta_{\text{esc}}\approx40\)k tok/task, a lesson \(\Delta_{tok}\approx
0.4\)k/call — a ~100× benefit at n=1, but NOT "strictly" (lesson
interference — a growing cheatsheet may drop the \(p_0\) of other classes — is not
ruled out; the P15 run showed no interference: the other lessons kept
working). Norm: a ladder-exhaustion pattern becomes a cheatsheet lesson.

**P15 — status after the second review: IN-SAMPLE (accepted).** The test ran
the same tasks whose lessons went into the cheatsheet — this is the effectiveness of lessons on their
own class, NOT generalization. HELD-OUT (fheldout, unseen domains):
fan-out transfers (chess_club green on the 1st attempt), two-sided accounting
— does not (tool_rental island): lessons transfer UNEVENLY, and this
is a measured fact, not a blemish. The original entry is kept below as history: The lessons of 5 opus tasks were added →
a repeat sonnet-only run, clean cache: **4/5 green (was 0/5), 2
first-try** (tickets, leaderboard — 20 s each). The computed null (as
required by the review): at \(p=\hat p_{\text{MLE}}=0.06\), by retries
\(\Pr[\ge4/5\text{ green}]\approx0.008\),
\(\Pr[\ge2\text{ first-try}]\approx0.03\) — jointly \(<10^{-3}\);
the transfer of \(p_0\) by the cheatsheet is real.
**library finale [08-31]: 5/5.** The "under-taught class" turned out to be a GATE BUG:
the judge crashed on keys with spaces ("War and Peace") -> stdout empty ->
COUNTEREXAMPLE EMPTY -> the model was fixing blind for 16 attempts. Fixing the judge
(URL-quoting + trace into the verdict) -> Sonnet green in 3 attempts. The lesson
rises to the rank of a thesis: growth convergence = f(cheatsheet, COUNTEREXAMPLE QUALITY);
an empty counterexample is indistinguishable from an inexpressible task — and this is one more
argument that an "island" as a verdict must carry gate diagnostics.

## 1.5. Determinism-through-certification (a norm, already proved by practice)

A green artifact + a spec hash = a certificate; a repeat request is a cache read
with a REPEATED run of the gates (fcold: 0 model calls). The oracle's stochasticity
does not enter the system's reliability: it enters only the COST of growth.
Formally: growth is a Markov chain with absorption; the product is only the
absorbed states. All of §1's theory is about the time to absorption, and not one
word of it affects the guarantees of the finished organism (those are given by the court).

---

# §2. The organism as a measurable operator (a bridge to Part VI)

## 2.1. Definition

**Definition 4 (organism operator under load).** An organism \(g\) with a
finite (or discretized) state space \(X\) and an event stream
\(\nu\) (the fuzz/load distribution) defines a chain
\(x_{t+1}=\mathrm{handle}(x_t,e_t)\), \(e_t\sim\nu\), — the transition kernel
\(P^{g,\nu}\). THIS IS NOT A MODEL BUT A MEASUREMENT: \(\widehat P\) is estimated
by running the real organism.handle (not by a genome formula!) — a divergence
of \(\widehat P\) from the genome's intent is itself diagnostic.

For int-states of small cardinality \(\widehat P\) is an honest matrix;
for large/dynamic ones an observable dictionary is needed (EDMD, Theorem 2′) AND a test
of the observables' Markovianity (review §2.3: on a non-toy organism dedup/
retry_window/multi-entity can break Markovianity — then \(\widehat P\)
becomes a model, not a measurement). All quantities in §2 are CONDITIONAL ON \(\nu\)
(the load is a model of the environment): certificates are written \(P^{g,\nu}\) with an explicit
\(\nu\); pointwise \(\hat\rho_S,\hat h\) require (δ, M)-bands as in §3
— the double standard is removed by a norm: the §2.3 attestation carries (ν, δ, M).

## 2.2. Calibration of the measurement pipeline on an object with known ground truth
(fmath §2 exam; renamed per review §2.1: lemmas are theorems and "failing to
converge" is not something they can do; the exam checks the PIPELINE — the \(\widehat P\)
estimator, the sampler, the Markovianity of handle in observable coordinates, — on an organism where
the truth is known)

The "swamp" construction: a random-walk organism pos∈{0..4} under ν(±1), plus
an "evacuation" move reset: pos:=0 from any state (ν(reset)=0.1);
\(S=\{3,4\}\). The lesson of the construction (a result in itself): WITHOUT reset the
uniform hazard of the swamp is zero — from the depth of the chain-like S you
cannot get out in one step, and Lemma 6.4 is trivial; reset is exactly the
engineering hazard-move (REVOKE/molt-rollback): one move out of any swamp
outward, h≥ν(reset). The theory of Part VI and the D74 queue met on a live
example. The exam measures ON THE LIVE handle():
1. \(\widehat P\), the killed \(\widehat P_S\), \(\rho_S\),
   \(\mathcal D(S)=1/(1-\rho_S)\);
2. the empirical \(\mathbb E_{\mathrm{qsd}}[\tau_S]\) by simulation —
   convergence to \(\mathcal D(S)\) (Lemma 6.3);
3. \(\mathcal D(S)\ge1/\varepsilon(S)\) (Lemma 6.1: conductance is a cheap
   one-sided certificate);
4. the hazard majorant: \(\sup_x\widehat{\Pr}_x(\tau_S>t)\le(1-h)^t\),
   \(h=\min_{x\in S}P(x,S^c)\) (Lemma 6.4).

The point: the apparatus of Part VI ceases to be a theory "about a future system" —
it is computed on an executable genome. The next step (open): the same quantities
on a NON-toy organism via an observable dictionary.

## 2.4. The spectral step on a non-toy organism (fspectral exam)

The booking observable dictionary (int fields of rooms + a counter of active bookings),
load \(\nu\) with a cancellation parameter: the linear estimate \(A\) gives
\(\lambda_{\text{slow}}=0.874\) (hold-out R²=0.33). TWO corruption regimes:
- metastable (cancellations rare, 0.5→0.1): \(\lambda\to0.996\) —
  the spectral shift CATCHES it (the spirit of Proposition 3 on a live organism);
- freeze (no cancellations): the LESSON OF MEASUREMENT — this is NOT a slow mode (variance→0,
  the spectrum has nothing to measure); caught by a variance monitor.
The corruption detector is TWO-COMPONENT: spectrum (metastability) + variance
(death of the dynamics).

## 2.5. The spectral audit as an organ (faudit exam; BUILT)

warden.tick_spectral: sliding windows of observables; the THRESHOLD IS CALIBRATED on
the first (healthy) window — sub-windows give a spread of λ, threshold = max+3σ, nothing
by hand; dictionary selection (select_coords: a trend filter + relative
variance — both filters mined from fspectral v2 failures) is part of the
calibration CERTIFICATE; the observables' Markovianity is tested there too
(lag-2 vs lag-1). Live run: health stays silent (0 false positives), corruption
λ=0.845>0.788 -> spectral_drift in the ledger, freeze -> variance_freeze.
The immune audit became a scheduled organ. Everything is conditional on ν.

## 2.3. The engine's hazard-moves (a bridge to D74)

v1's moves and their hazard: REVOKE and molt-rollback — h=1 BY THE CONSTRUCTION OF THE MOVE
(deterministic, ν-INDEPENDENT; rollback — given a live backup: an assumption →
membrane); restart by the warden — h<1 and ν-CONDITIONAL (a crash may recur),
in the attestation honestly "NOT MEASURED" until measured with (ν, δ, M) per §2.2. The attestation (attest) must print per-S:
move, h, 1/h — built into the D74 queue.

---

# §3. Algebra of certificates (composition of attestations)

**Definition 5 (corrected per review §3.3).** Quantile certificate:
\(c=(\eta,q,\delta,M,L)\) — over \(M\) observations under the DECLARED input
distribution \(\nu\), with prob. \(\ge1-\delta\) the fraction of ticks with defect
\(\le\eta\) is at least \(q\); \(L\) is the Lipschitz constant of input-defect
transfer, the ATTESTED part of the certificate (as in Theorem 8's
\(\mathcal L\) of Part III — it had been erroneously trimmed). For dependent
observations \(M\to M_{\text{eff}}\) (θ-mixing, caveat of Theorem 8).

**Theorem VII.1′ (sequential composition; conditions (i)–(iii)
explicit — review §3.1-3.3 accepted).** Suppose:
(i) the cascade is SYNCHRONOUS: a composition tick = one tick of A + the one tick of
B it induces (a common index set; fan-out/batching — outside the theorem);
(ii) certificate B is obtained IN SITU — on the actual outputs of A (or the
event "defect B ≤ η_B" is robust to an input perturbation ≤ η_A);
(iii) \(L_B\) is the attested constant of attestation B (Def. 5), not
derived (the reference to Corollary 1 of Part II is RETRACTED: it assumes
Lipschitzness rather than proving it).
Then the cascade has
\[
c_{AB}=\big(\eta_B+L_B\,\eta_A,\ \ q_A+q_B-1,\ \ \delta_A+\delta_B,\ \
\min(M_A,M_B),\ \ L_BL_A\big).
\]
*Proof.* Under (i) the fractions are counted on a single set of ticks:
the cleanliness of both \(\ge q_A+q_B-1\) — the Fréchet bound, valid under ANY
dependence (achieved by an antithetic coupling); simultaneity of the
certificates — a union bound (valid under any dependence);
on a clean tick, under (ii)-(iii), the defect \(\le\eta_B+L_B\eta_A\). ∎

Corollaries: (a) the composition's attestation is computable from the parts' attestations UNDER
(i)-(iii) — for an organism's end-to-end path (i) holds on 1:1 cascades,
(ii) is verified BY THE ENGINE (fcompose exam): a live saga-cascade,
tick = input event (1:1 — (i) by construction), the certificates of both
stages in situ on a single set of ticks; the bound q_A+q_B-1=0.742
is ACHIEVED on live data (the dependence turned out to be ~antithetic);
transfer into the attestation of the end-to-end path — open;
(b) q decreases additively with the cascade's length — a quantitative form of "system
guarantee = min over the seams": long cascades require high q at every seam
(a budget as in Theorem 13). The fmath §3 exam: a DKW certificate of a real skill +
a simulation check of the composition bound.

---

# §4. Status and open questions of Part VII

- §1: models A/B are fitted and NOT SEPARATED (a valuable negative; the pooled
  setting — a review caveat); Norm 1 is a policy with a measured (not
  proved) benefit; P15 is CONFIRMED (4/5, null ~10^-3).
- §2: the measurement pipeline is CALIBRATED on an object with known ground truth
  (renamed per the review); the spectral step is done (fspectral §2.4);
  open: a test of observables' Markovianity, (δ,M)-bands for ρ̂_S.
- §3: VII.1′ is proved UNDER CONDITIONS (i)-(iii); the conditions are not yet
  verified by the engine (in-situ measurement — open); the former status "proved"
  without conditions is retracted. Open: fan-out composition, composition through
  a membrane.
- §6: VII.2 is proved and measured (linearity 0.020, shift ≤ TV,
  per-event transfer C=3.5); open: transfer of state-dependent defects
  (shift of the stationary distribution), κ-attestation for |Δλ|.
- A new candidate block (the next epic step): "thermodynamics of the cheatsheet" —
  lessons as compression of the description length of a task class (a bridge to the MDL of Part III
  §6: a lesson is accepted if \(\Delta\widehat{\mathrm{DL}}<-2c\) on the class).

---

# §6. The ν-bridge: transferring certificates between loads (the frontier of review v2)

Review v2 localized the "encounter with reality" into a single hole: everything in §2 is
conditional on the fuzz-\(\nu\), and the prod-\(\nu\) is different. The apparatus's answer:

**Identity (linearity of the kernel in the load).** An organism's kernel is a mixture of
deterministic maps: \(P^{g,\nu}=\sum_e \nu(e)\,K_e\), where
\(K_e(x,\cdot)=\delta_{\mathrm{handle}(x,e)}\). The proof is one
line (handle is deterministic). MEASURED live (fnu §1:
\(\max|P_{mix}-\tfrac12(P_1{+}P_2)|=0.020\) at noise 0.04).

**Theorem VII.2 (ν-bridge).** For loads \(\nu,\nu'\):
(a) \(\sup_x \mathrm{TV}\big(P^{\nu'}(x,\cdot),P^{\nu}(x,\cdot)\big)
\le \mathrm{TV}(\nu',\nu)\) — the operator shift is bounded by the load shift (linearity + convexity of TV);
(b) for an EVENT-BASED defect \(D\subset E\) (depends only on the event):
\(q'\ge 1-C\,(1-q)\), where \(C=\sup_e \nu'(e)/\nu(e)\) —
domination transfers per-event certificates;
(c) the spectral quantities of the measured matrix are perturbed by
\(\|\Delta P\|\le 2\,\mathrm{TV}(\nu',\nu)\); HONEST BOUND:
converting to \(|\Delta\lambda|\) requires normality (Weyl) or an
attested \(\kappa(V)\) (Bauer-Fike) — NOT CLAIMED; the pseudospectrum
of Part VI §2.2 is the right language; empirics (fnu §4): the λ shift is monotone
in TV. State-dependent defects also inherit the shift of the stationary
distribution — transfer (b) does NOT extend to them (open).
*Proofs.* (a): \(P^{\nu'}-P^{\nu}=\sum_e(\nu'-\nu)(e)K_e\),
each \(K_e\) is stochastic. (b): \(\Pr_{\nu'}[D]=\sum_{e\in D}\nu'(e)
\le C\sum_{e\in D}\nu(e)=C\Pr_\nu[D]\). ∎

**Mechanism (built, fnu §5-7):** the calibration certificate carries the
empirical \(\hat\nu\) AND a ν-drift threshold FROM the sub-window spread (not by
hand); at every audit period the warden measures
\(\mathrm{TV}(\hat\nu_{\text{window}},\hat\nu_{\text{cert}})\);
an exceedance -> nu_drift in the ledger: the certificate is declared conditional BEFORE
it silently goes stale. The load became a membrane assumption — the same
trust pattern as with islands (D43) and knowledge (D74-U12).

---

# §5. Response to the first review of Part VII (2026-08-31)

The review (full text — the epic's journal) is accepted ALMOST IN FULL; summary:
- ACCEPTED: the pooling confounder §1.2 (conclusion narrowed, refit pre-registered);
  the retraction of "strength does not act on β" §1.3 (no data); Proposition 1 →
  Norm 1 with the rent cost of a lesson; the §4↔§1.2 contradiction fixed;
  "verification of lemmas" → "calibration of the pipeline"; ν-conditionality and (ν,δ,M)
  in the §2 certificates; VII.1 → VII.1′ with explicit (i)-(iii), L returned to the
  tuple, the false attribution of Corollary 1 of Part II retracted; the preamble gained
  the "norm" category; the exam: tautological asserts replaced (chi-bar threshold
  instead of LR, antithetic coupling on the Fréchet bound, live telemetry
  from usage files instead of constants — with a fallback flag).
- PARTIALLY ACCEPTED: the "null for P15" — computed AFTER the run (not pre-
  registered — honestly; P16 is pre-registered already with a threshold).
- The review's formula "strong as a measurement diary, weak as mathematics" is
  accepted as a diagnosis; the treatment — strengthening the conditions and lowering the statuses,
  done above. VII preserves a feature unique in the corpus: every weak spot
  of it was found by its OWN exam or its own review
  and recorded in the text, not hidden by polishing.
