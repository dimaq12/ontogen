# Part II. Five pillars: completing the mathematics of the ontogenic system

Continuation of the document `ontogenic_system_math_core.md` (hereafter "Part I").
Part I introduced the object \(\mathfrak O=(\Theta,X,R,\Pi,C)\) and five axioms.
Part II closes the five main gaps and turns the manifesto into a theory:

1. **Constructive `emerge`** — how to *find* levels, not merely verify them; when a level dies.
2. **Bounded Context Theorem** — why each step of evolution is computable by a small deterministic oracle (SLM), independently of the size of the system.
3. **Integrity theory (dnaContract)** — repair, redundancy, regeneration, immunity.
4. **Grammar of \(\Delta\Theta\)** — typed mutations of the ontology, conservativity, branch merging, MDL acceptance criterion.
5. **Level reconciliation** — who is right when micro/macro disagree, without a global arbiter.

---

# Pillar 1. Constructive `emerge`

## 1.1. From criterion to certificate

Part I defined a level by the condition \(\pi\circ U\approx G\circ\pi\). Let us make "\(\approx\)" measurable.

**Definition 1 (closure defect).** For a subsystem \(A\), a map \(\pi:X_A\to Y\), a dynamics \(G:Y\to Y\), and a distribution \(\mu\) over the states that occur:

\[
\eta(\pi,G)
=
\operatorname*{ess\,sup}_{x\sim\mu}
\;
d\big(\pi(U(x)),\,G(\pi(x))\big)
\]

— the **one-step defect**, and

\[
\delta_n(\pi,G)
=
\operatorname*{ess\,sup}_{x\sim\mu}
\;
\max_{1\le k\le n}
d\big(\pi(U^k(x)),\,G^k(\pi(x))\big)
\]

— the **defect on horizon \(n\)**.

**Lemma 1 (defect accumulation).** If \(G\) is Lipschitz with constant \(L\), then

\[
\boxed{
\delta_n\;\le\;
\eta\cdot\frac{L^n-1}{L-1}
\qquad(\delta_n\le \eta\,n\ \text{when }L=1).
}
\]

*Proof.* Induction: \(e_{k+1}\le \eta + L\,e_k\), telescoping. ∎

**Corollary 1 (which abstractions are long-lived).** When \(L<1\) the defect is bounded forever: \(\delta_\infty\le \eta/(1-L)\).

\[
\boxed{
\text{Long-lived levels}=\text{contracting (dissipative) macrodynamics.}
}
\]

This is the first substantive result: a stable abstraction is not just any one, but one whose own dynamics damps perturbations. (This is exactly why "pressure" is a good macro-variable, while "the position of molecule no. 7" is not.)

**Definition 2 (level certificate).** A level is not a pair \((\pi,G)\), but a sextuple

\[
\mathcal L=(A,\ \pi,\ G,\ \eta,\ L,\ \mu)
\]

with the **validity horizon** computed from Lemma 1

\[
n^\*(\varepsilon)=\max\Big\{n:\ \eta\tfrac{L^n-1}{L-1}\le\varepsilon\Big\}.
\]

The certificate is the level's public promise: "on horizon \(n^\*\) my predictions may be trusted to accuracy \(\varepsilon\)." Everything that follows (Pillars 2, 3, 5) rests on certificates, not on faith.

## 1.2. Canonicity: `emerge` has a correct answer

The worry: pairs \((\pi,G)\) form a continuum, so the search is arbitrary. This is not so: a canonical object exists.

**Definition 3 (predictive equivalence).** Fix the observables \(\mathcal O\). States \(x\sim x'\) are **predictively equivalent** if the distributions of future observable trajectories coincide:

\[
x\sim x'
\iff
\forall n:\ \operatorname{Law}\big(o(U^{1..n}x)\big)
=
\operatorname{Law}\big(o(U^{1..n}x')\big).
\]

**Theorem 1 (minimal exact level; adaptation of Crutchfield–Shalizi).** The quotient map \(\pi_c:X\to X/\!\sim\) is the *coarsest* map with exact closure (\(\eta=0\)) relative to \(\mathcal O\); it is unique up to isomorphism, and every other exact level is a refinement of it.

*Meaning.* `emerge` is not a needle-in-a-haystack search, but a descent down the lattice of partitions from the identity toward \(\pi_c\); allowing \(\eta\le\varepsilon\), we obtain an entire **scale of levels parametrized by coarseness** — this is precisely the hierarchy of Part I §7, now as a mathematical object (the lattice of \(\varepsilon\)-closed partitions).

## 1.3. Spectral algorithm: where to look for \(\pi\)

The practical mechanism goes through the **transfer operator** (Koopman): \((\mathcal U f)(x)=\mathbb E[f(U(x))]\), acting on observables \(f\).

**Theorem 2 (spectral gap ⇒ level).** Let \(\mathcal U\) be quasi-compact with spectrum \(|\lambda_1|\ge\dots\ge|\lambda_m|>|\lambda_{m+1}|\) and let \(\pi\) be the projection coordinates onto the dominant eigen-subspace \(V_m\), with \(G=\mathcal U|_{V_m}\). Then the one-step defect is controlled by the tail of the spectrum:

\[
\eta\;\le\;
C\cdot\Big|\frac{\lambda_{m+1}}{\lambda_m}\Big|
\cdot\|x\|_{V_m^\perp},
\]

that is, **a gap in the spectrum is a certificate that a level exists**, and the dimension of the macro-state \(=\) the number of modes up to the gap.

*Sketch.* For the spectral projector \(P_m\): \(\pi\mathcal U-G\pi=\pi\,\mathcal U(1-P_m)\); the norm is bounded by the tail of the spectrum. Inexactness arises from estimating \(V_m\) on finite data and from nonlinearity — this is exactly \(\eta\). ∎(sketch)

**Lemma 2 (defect via a cut of the interaction graph).** If \(A\) is a candidate subsystem, then

\[
\eta(A)\;\le\;
\operatorname{Lip}(\pi)\cdot\operatorname{Lip}(F)\cdot
\!\!\sum_{i\in A,\ j\notin A}\!\! K(i,j,X)
\;=\;
c\cdot\operatorname{cut}_K(A).
\]

*Meaning.* Good candidates for a macro-object are dense communities of the interaction-function graph \(K\) (Part I §3) with a weak cut to the outside. Candidate search = community detection; this is a **justification of the heuristic, not a heuristic**.

## 1.4. Variational form: levels as kinks of the information curve

A dual formulation via the information bottleneck:

\[
\pi_\beta^\*
=
\arg\max_\pi\;
\underbrace{I\big(\pi(x_t);\,x_{t+1..t+n}\big)}_{\text{predictive power}}
\;-\;
\beta\,
\underbrace{I\big(\pi(x);\,x\big)}_{\text{description cost}}.
\]

The parameter \(\beta\) is the "coarseness knob." Sweeping \(\beta\) from 0 to \(\infty\), we obtain the "compression ↔ prediction" curve.

\[
\boxed{
\text{Natural levels}=\text{kinks (knees) of the convex hull of this curve.}
}
\]

The hierarchy is not postulated — it is **read off the curve**. This is a falsifiable claim: for a system without emergent levels the curve is smooth.

## 1.5. The EMERGE algorithm

```text
EMERGE(world X, rules R):
  1. CANDIDATES: communities of graph K with small cut_K(A)   // lemma 2
  2. FOR each A:
       sample trajectories U on X_A (with the environment frozen)
       (π, G) := spectral fit (thm. 2) or IB (1.4)
       (η, L) := estimate on held-out trajectories
  3. CERTIFICATION: accept the level ⟺ MDL gain (see 4.5):
       DL(world with level) < DL(world without level)
  4. REGISTRATION: create m_A, s(m_A)=π(X_A), ρ(m_A)=A,
       record the certificate (A, π, G, η, L, μ)
```

Step 3 matters: a level is not a free entity. It is accepted if and only if it **compresses the description of the world** (storing \(G\) + the certificate is cheaper than predicting with the microdynamics). This is the defense against level inflation.

## 1.6. Death, learning, and the molt of a level

The certificate is checked *online*: the residual \(d_t=d(\pi(U x_t),\,G(\pi x_t))\) is an observable time series; on it runs a shift detector (e.g., CUSUM). Three response regimes:

\[
\begin{array}{lll}
d_t\le\eta &\Rightarrow& \text{normal: the level works}\\[2pt]
\eta<d_t\le\eta_{\text{crit}},\ \text{drift} &\Rightarrow& \textbf{learning}: \text{refit } G \text{ with the same } \pi\\[2pt]
d_t>\eta_{\text{crit}} \text{ persistently} &\Rightarrow& \textbf{molt}: \text{re-emerge } \pi \text{; if that fails — } \textbf{death}
\end{array}
\]

**Death of a level** \(=\) revocation of the certificate: the macro-object \(m_A\) dissolves (\(m_A\to\varnothing\)), its constraints \(C_M\) are lifted, and the realization \(A\) goes on living. The death condition is what was absent in Part I; now a level is a **living object with an expiry date**, not an eternal axiom.

---

# Pillar 2. Bounded Context Theorem

Goal: to prove that under the axioms of Part I each step of evolution is computable by a function whose input has a fixed size, **independent of the size of the system**. This is the mathematical legalization of cheap models.

## 2.1. Assumptions

**(L1) Exponential decay of interaction.** There exist \(C,\xi>0\):

\[
\Big\|\frac{\partial F_i}{\partial x_j}\Big\|
\le
C\,e^{-d(i,j)/\xi},
\]

where \(d\) is the metric on entities induced by \(K\) (for example, \(d=-\xi\log K\)).

**(L2) Bounded dimension.** The metric has doubling dimension \(D\): \(|B_r(i)|\le c\,r^D\).

**(L3) Mediation of long-range action.** *An axiom of language design:* every interaction at distance greater than \(O(\xi)\) is obliged to pass through a `field` or through a macro-entity. There is no direct long-range action — as in physics.

L3 is not a loss of generality but a **prohibition on bad architecture**: any long-range action can be realized by a field; the language simply does not let you cut the corner.

## 2.2. Near field: the truncation lemma

**Lemma 3 (context truncation).** Under (L1)–(L2), replacing the exact update \(F_i(x)\) by \(F_i(x|_{B_r(i)})\) (context truncated to the ball of radius \(r\)) yields a one-step error

\[
\big\|F_i(x)-F_i(x|_{B_r})\big\|
\;\le\;
C'\,r^{D-1}e^{-r/\xi},
\]

whence for accuracy \(\varepsilon\) a radius

\[
r(\varepsilon)=O\big(\xi\,(\log\tfrac1\varepsilon + D\log\xi D)\big),
\qquad
|B_{r(\varepsilon)}|
=
O\big(\xi^D\log^D\tfrac1\varepsilon\big).
\]

suffices.

*Proof.* Summation of the tail \(\sum_{r'>r}|\partial B_{r'}|\,Ce^{-r'/\xi}\) with the estimate (L2). ∎

The key point: the right-hand side **does not contain \(N=|X|\)**.

## 2.3. Far field: through certified macro-states

By (L3) the influence of the rest of the world on \(e_i\) passes through: the values of the incident fields \(\phi_1(p_i),\dots,\phi_F(p_i)\) and the states of the enclosing macro-entities \(y_{M_1},\dots,y_{M_L}\) (a tower of depth \(L\)). By the level certificates (Pillar 1) each \(y_{M_\ell}\) represents its subsystem with error \(\le\varepsilon_\ell\) on its horizon.

## 2.4. The main theorem

**Theorem 3 (local sufficiency / Bounded Context Theorem).**
Let the system satisfy (L1)–(L3), and let a tower of levels of depth \(L\) be certified with defects \(\varepsilon_1,\dots,\varepsilon_L\). Then the update of any entity \(e_i\) is computable to accuracy

\[
\varepsilon_{\text{total}}
\;\le\;
\underbrace{C'r^{D-1}e^{-r/\xi}}_{\text{truncation}}
+
\sum_{\ell=1}^{L}c_\ell\,\varepsilon_\ell
\]

from a context of size

\[
\boxed{
k
=
O\Big(
\underbrace{\xi^D\log^D\tfrac1\varepsilon}_{\text{neighbors}}
+
\underbrace{F\cdot\dim\phi}_{\text{fields}}
+
\underbrace{L\cdot\dim y}_{\text{macro-stack}}
\Big)
\quad\text{— independent of }|X|.
}
\]

*Proof.* Decompose the influence into near (Lemma 3) and far (by L3 — only through fields and macro; the error of each channel comes from the certificate; telescoping over levels). ∎

## 2.5. Corollary: the cheap-chemistry theorem

**Definition 4 (bounded-capacity oracle).** A deterministic function \(\hat f:\Sigma^{\le k}\to\Sigma^{\le k'}\) with fixed \(k,k'\) (realization: a call to an SLM at temperature 0, with a strict input/output schema). Correctness requirement: \(\hat f\) agrees with the semantics of a rule \(r\in R\) on legal inputs.

**Corollary 2 (SLM legalization).** To realize the dynamics \(U\), a family of oracles of capacity

\[
\operatorname{cap}(\hat f)\;\gtrsim\;\max_{r\in R}K(r)
\qquad\text{— the complexity of the \emph{rules},}
\]

suffices, and one **never** needs \(\operatorname{cap}\gtrsim K(X_t)\) — the complexity of the *world*.

\[
\boxed{
\text{Agentic approach: model}\supseteq\text{world.}\qquad
\text{Ontogenic approach: model}\supseteq\text{rule.}
}
\]

Intelligence lives in the genome \((\Theta,R)\) and in the architecture (certificates, contracts); chemistry has the right to be stupid. This is a direct consequence of the Locality axiom carried to quantitative form, plus the bound of Part I §11: the complexity of the world is accrued by *time*, not by the capacity of the step-computer.

## 2.6. And what if the oracle errs?

An oracle error is a perturbation of the microstate. We do **not** require chemistry to be error-free: oracle errors by construction fall into the damage model of Pillar 3 and are fixed by repair. This is the second pillar of SLM legalization:

\[
\boxed{
\text{An SLM can be trusted not because it does not err,}\\
\text{but because the system knows how to fix its errors.}
}
\]

This is exactly how a cell is arranged: the polymerase errs at \(\sim10^{-5}\), yet the final accuracy is \(\sim10^{-10}\) — through repair, not through a perfect enzyme.

---

# Pillar 3. Integrity theory (dnaContract)

## 3.1. Contracts

**Definition 5 (contract).** The contract of a macro-entity \(M\) is a quadruple

\[
\mathcal C_M
=
(\underbrace{A}_{\text{scope}},\;
\underbrace{\{\varphi_1,\dots,\varphi_m\}}_{\text{predicates}},\;
\underbrace{R_{\text{rep}}}_{\text{repair rules}},\;
\underbrace{\uparrow}_{\text{escalation}})
\]

where each predicate \(\varphi_j\) is **\(k\)-local**: it depends on an \(O(k)\)-neighborhood and on \(y_M\). The legal set: \(L(\mathcal C)=\{x: \forall j\ \varphi_j(x,y_M)\}\). This is the formalization of \(C_M:Y_M\to\mathcal P(X_A)\) from Part I §8, supplemented with a *mechanism* of maintenance.

\(k\)-locality of the predicates is mandatory: an integrity check must not require reading the whole world (otherwise Pillar 2 collapses).

## 3.2. The damage model

**Definition 6 (\(\rho\)-damage).** An adversary (or noise, or an oracle error — the model is one) applies to \(x\in L(\mathcal C)\) up to \(\rho|A|\) elementary edits: corruption of state, deletion of an entity, insertion of a junk entity.

This subsumes: SLM errors (§2.6), races of competing rules, external failures, malicious interference. One formalism for everything.

## 3.3. Convergence of repair

Potential: \(\Phi(x)=\sum_j w_j\,[\neg\varphi_j(x)]\) — the weighted number of violated predicates. A repair rule \(r\in R_{\text{rep}}\) is **correct** if it fires only on a violation and fixes it; the **interference graph** connects predicates that share support.

**Theorem 4 (convergence of repair).** Suppose each firing of repair fixes its own violation and in expectation creates \(<1-\gamma\) new violations (a contraction condition on the interference graph of bounded degree). Then from any \(\rho\)-damaged state the system returns to \(L(\mathcal C)\) in

\[
\mathbb E[\text{number of local steps}]
=
O\big(\Phi_0/\gamma\big),
\]

and the repair is asynchronous and requires no coordinator.

*Sketch.* \(\Phi\) is a supermartingale with expected step \(-\gamma\); optional stopping. The contraction condition is a constructive analogue of the Lovász local lemma (the Moser–Tardos argument); the link with Dijkstra self-stabilization: \(L(\mathcal C)\) is the set of legitimate states, and repair is the stabilizing protocol. ∎(sketch)

## 3.4. What "fixed" means: the semantics of repair

Demanding restoration of the exact microstate is impossible and unnecessary. The right criterion is given by Pillar 1:

\[
\boxed{
\text{The repair is correct}
\iff
\pi\big(\operatorname{repair}(\operatorname{damage}(x))\big)
=
\pi(x)
}
\]

— the **meaning** (the macro-state) is restored, the micro-details are free. A healed cut does not bring back the same cells — it brings back the same hand. Levels (Pillar 1) determine *what exactly* repair is obliged to preserve; without `emerge` the notion of integrity cannot even be stated. The pillars are interlocked.

## 3.5. The price of homeostasis: bounds on redundancy

**Theorem 5 (lower bound on redundancy).** To withstand erasure of a fraction \(\rho\) of the support \(A\) while preserving the macro-state \(y=\pi(x)\) of entropy \(H(y)\) bits, the realization must satisfy

\[
\operatorname{cap}(A)\;\ge\;\frac{H(y)}{1-\rho}
\qquad\text{(erasures)},
\]

and against \emph{corruption} (not erasure) of a fraction \(\rho\) — more stringently, of order \(\operatorname{cap}(A)\ge H(y)/(1-H_2(2\rho))\) (a Singleton / Gilbert–Varshamov type bound).

*Meaning.* Homeostasis is not a free virtue but the **rate of an error-correcting code**: if you want to survive \(\rho\), pay in redundancy \(\ge 1/(1-\rho)\). Achievability — by a redundant realization:

- **double helix**: the coherence invariant \(s(m_A)=\pi(X_A)\) — the macro-cache and the micro-truth store the same thing and fix each other both ways;
- **quorum**: critical \(y\) are duplicated across neighboring macro-entities with voting.

The coherence invariant is itself a local predicate of the contract — that is, the double helix is fixed by the very mechanism of Theorem 4.

## 3.6. Regeneration: repair by generation

Suppose the micro-support \(A\) is destroyed beyond the threshold of Theorem 4, but \(y_M\) has survived (by Theorem 5 it survives \(\rho\)-catastrophes). Then:

\[
\boxed{
\text{Regeneration: choose any } x'\in C_M(y_M)
\text{ by generative rules; correct, since } \pi(x')=y_M.
}
\]

Requirements: **viability** of the contract (\(C_M(y)\neq\varnothing\) for all reachable \(y\)) and **completeness** of the generative rules relative to \(C_M\) (they can build at least one representative). This is morphogenesis: an organism regrows a limb from the macro-description, because the lower constraint set is precisely the specification for the rebuild. The top-down constraint (Part I §8) turns out to be a **blueprint for regeneration** — a second application of the same object \(C_M\).

## 3.7. Immunity: cancer as a formal object

**Definition 7 (ontological cancer).** A subsystem \(B\) that (i) has attained its own emergent closure \(\pi_B\circ U\approx G_B\circ\pi_B\), (ii) is locally legal by its own predicates, but (iii) whose \(G_B\) systematically violates the contract of the enclosing level: the trajectories of \(G_B\) drive \(X_A\) out of \(C_M(y_M)\).

Closure makes it resilient (Corollary 1 — it is self-sustaining), local legality makes it invisible to a naive check. The response:

- **boundary surveillance**: contract predicates on the flows across \(\partial B\) (a cell consuming anomalously much resource is visible at the boundary);
- **audit of unregistered closures**: a statistical search for subsystems with high self-predictability that lack a certificate (EMERGE run "against" the system);
- **apoptosis**: a metarule \(\neg C_M\text{-compatibility, persistent} \Rightarrow B\to\varnothing\), executed locally, by the environment of \(B\).

*Honest note.* Detecting an unregistered closure in full generality is semi-decidable; hostile emergence is a deep open problem (and, incidentally, it has the same mathematical form as the alignment problem). We provide a surveillance mechanism, not a theorem that catches all cancers.

---

# Pillar 4. Grammar of \(\Delta\Theta\)

## 4.1. The ontology as a signature

\(\Theta=(\mathcal T,\mathcal O,\mathcal R)\) is a typed signature (an algebraic theory): types, observables-as-terms, rules-as-typed-operations. The world \(X_\Theta\) is a model of this theory. "To change the ontology" = a morphism of signatures. Then \(\Delta\Theta\) ceases to be "anything is allowed" and becomes a generated language.

## 4.2. Five generating mutations

\[
\begin{array}{ll}
\mu_1\ \textbf{Form:} & \mathcal T\mathrel{+}= F(\mathcal T),\quad F\in\{\times,\ +,\ \mathrm{List},\ \mathrm{Sub}_\varphi,\ \mathrm{Quot}_\pi\}\\[3pt]
\mu_2\ \textbf{View:} & \mathcal O\mathrel{+}= o,\quad o\ \text{— a definable term over }\Theta\\[3pt]
\mu_3\ \textbf{Law:} & \mathcal R\mathrel{+}= r,\quad r\ \text{— a typed, guarded rule}\\[3pt]
\mu_4\ \textbf{Forgetting:} & \text{deprecation with a mandatory migration morphism}\\[3pt]
\mu_5\ \textbf{Elevation:} & \text{emerge-induced type: } Y=\mathrm{Quot}_{\pi}(X_A)\ \text{+ realization }\rho
\end{array}
\]

**Key identification:**

\[
\boxed{
\texttt{emerge}=\mathrm{Quot}_\pi:\ \text{every new level is a quotient type by predictive equivalence.}
}
\]

Pillar 1 (dynamics) and Pillar 4 (types) are one mechanism seen from two sides: the spectral gap *detects* the type, \(\mu_5\) *legalizes* it in the ontology. New types are not invented — they **crystallize out of the dynamics**.

## 4.3. The conservativity law and the central dogma

**Theorem 6 (preservation of the past).** The mutations generated by \(\mu_1\)–\(\mu_3\), \(\mu_5\), are *definable extensions* of the theory, and hence **conservative**: every morphism \(\mu:\Theta\to\Theta'\) is equipped with a migration functor \(M_\mu:X_\Theta\to X_{\Theta'}\) under which the old observables retain their values (\(o'\circ M_\mu=o\)), and every statement in the language of \(\Theta\) true before the mutation is true after it. Checking correctness of a mutation is a typecheck, and is **decidable**.

*Sketch.* Classical logic: definable / conservative extensions; \(\mathrm{Quot}\) and \(\mathrm{Sub}\) come with explicit interpretations. \(\mu_4\) requires separate care: migration is a retraction with a default value; conservativity holds only relative to the non-deprecated fragment. ∎(sketch)

The consequence is the **central dogma of the ontogenic system**:

\[
\boxed{
X\ \text{cannot change}\ \Theta\ \text{directly.}\quad
\Delta\Theta\ \text{— only through the typed channel }\mu_i\ \text{with a deterministic check.}
}
\]

As in a cell: proteins do not rewrite DNA arbitrarily; mutations pass through a narrow, proofread channel (a polymerase with proofreading = our typechecker). Mutation proposals may come from noisy sources (SLM, heuristics, a human) — **acceptance** is always deterministic. A retrovirus = an attempt to bypass the channel; forbidden by construction.

## 4.4. The category of ontologies: git for worlds

Ontologies and mutations form a category \(\mathbf{Ont}\); the evolutionary history is a path; each snapshot of the world carries a version of \(\Theta\). Then:

- **branch merging** \(\Theta_1\leftarrow\Theta_0\rightarrow\Theta_2\) — a pushout in \(\mathbf{Ont}\), when one exists;
- **conflict** = absence of a pushout (incompatible quotient types, contradictory rules) — not an error but a *genuine design decision*, escalated upward (up to a human);
- migrations compose, so any history can be replayed on a new ontology.

Two populations of the system that evolved apart can be **merged like branches**, with a mathematically defined notion of conflict.

## 4.5. The MDL acceptance criterion: Occam's razor as mechanics

When *should* a mutation be accepted? The full description length of the current world:

\[
\mathrm{DL}
=
\mathrm{DL}(\Theta)
+\sum_{\mathcal L\in\Pi}\mathrm{DL}(\mathcal L)
+\mathrm{DL}(X\mid\Theta,\Pi)
+\lambda\,\mathrm{DL}(\text{residuals: defects, violations, remainders}).
\]

\[
\boxed{
\text{Accept }\mu
\iff
\mathrm{DL}_{\text{after}}<\mathrm{DL}_{\text{before}}.
}
\]

Consequences:

- a new type is accepted only if it *compresses* the world (explains persistent residuals more briefly than they weigh);
- the level from EMERGE (step 3 of the algorithm) is a special case;
- **mutation trigger**: metarules \(\mathcal R_{\text{meta}}\) are typed as \((\text{persistent residuals})\to(\text{proposal of }\mu)\) — the ontology grows not by whim but when the world *presses* on it with unexplained regularities. This is the machine form of the scientific method: anomaly → hypothesis (a new type) → acceptance by compression.

*Honest note:* \(\mathrm{DL}\) is not exactly computable (Kolmogorov); in practice one uses computable proxies (two-part codes, predictive cross-entropy). The criterion loses none of its normative force from this.

---

# Pillar 5. Level reconciliation without a global arbiter

## 5.1. Setting

Both levels live simultaneously (Part I §6): micro evolves by \(U\), macro by \(G\), and on the macro-tick \(\tau\) their predictions diverge:

\[
d_t=d\big(\pi(x_{t+\tau}),\ G(\hat y_t)\big)>0.
\]

Who is right? The answer: **the question is posed wrongly**. \(\hat y\) is not a second truth but an *estimate* of the macro-variable; \(\pi(x)\) is its *measurement*. Reconciliation is a filtering problem, solved locally by each level.

## 5.2. Upward: data assimilation

Each macro-entity runs its own filter:

\[
\boxed{
\hat y_{t+1}
=
(1-\beta)\,G(\hat y_t)
+
\beta\,\pi(x_{t+\tau})
}
\]

with a trust coefficient \(\beta\), computed from the certificates (the variance of the defect \(\eta\) against the noise of the measurement \(\pi\) — in the linear-Gaussian case this is exactly the Kalman gain). No arbiter: each level has its own filter, working on its own contract.

## 5.3. Downward: repair toward the constraint

Simultaneously the micro is pulled toward the contract (Pillar 3):

\[
x\ \longmapsto\ x+\alpha\,\big(\operatorname{proj}_{C_M(\hat y)}(x)-x\big),
\]

with stiffness \(\alpha\). The danger is obvious: if \(\hat y\) is wrong, the constraint pulls reality toward the error — a **self-fulfilling bureaucracy**.

## 5.4. Loop stability theorem

Linearize the estimation error \(e_t=\hat y_t-\pi(x_t)\) around the reconciled regime. The filter damps it by the factor \((1-\beta)\); the downward constraint moves \(\pi(x)\) itself toward \(\hat y\) with coefficient \(\alpha\gamma\) (\(\gamma\) — the sensitivity of \(\pi\) to the repair shift). Together, with the macrodynamics matrix \(A_G\):

\[
e_{t+1}\approx(1-\beta-\alpha\gamma)\,A_G\,e_t
+(\text{defect }\eta).
\]

**Theorem 7 (stability of the micro–macro loop).** The reconciliation loop is stable, and the estimation error is bounded by \(O(\eta)\), if

\[
\boxed{
|1-\beta-\alpha\gamma|\cdot\|A_G\|<1.
}
\]

As \(\beta+\alpha\gamma\to 2\), overshoot with a sign change arises — the **resonance of bureaucracy**: measurement and enforcement strike in antiphase, and the system oscillates between "rewrite the map" and "reshape the territory." The theorem's condition is a quantitative prohibition: *the total stiffness of the corrections in both directions per tick must not exceed one, with a margin for \(\|A_G\|\)*.

*Honest note:* the claim is a linearization; the nonlinear analogue (basins of attraction) is an open problem, but the engineering rule is already normative: \(\alpha\) and \(\beta\) are parameters of the *contract*, and their product is bounded by the certificate.

## 5.5. Consistency of the tower: telescoping

**Lemma 4 (tower).** If each adjacent pair of levels \((\ell,\ell+1)\) is reconciled to accuracy \(\varepsilon_\ell\) (in the sense of Theorem 7), then the whole tower of depth \(L\) is reconciled to accuracy

\[
\varepsilon_{\text{tower}}
\le
\sum_{\ell=1}^{L}\varepsilon_\ell\prod_{j>\ell}L_j,
\]

where \(L_j\) are the Lipschitz constants of the higher \(G_j\). Global consistency is a **consequence of pairwise contracts**; a third floor of governance does not exist. (The same principle as in 2.4: properties of the whole are assembled by telescoping certificates.)

## 5.6. Sibling conflict

Two macro-entities \(M_1, M_2\) with overlapping supports impose on the shared region \(C_{M_1}(\hat y_1)\cap C_{M_2}(\hat y_2)\).

**Definition 8 (pathology).** Persistent emptiness of the intersection: \(C_{M_1}\cap C_{M_2}=\varnothing\) on the shared support for longer than the horizon of both certificates.

Resolution, in order: (i) the filters of both (perhaps someone's \(\hat y\) is simply wrong); (ii) priority by certificate quality (smaller \(\eta\), fresher validation — a formal seniority lattice); (iii) **forced joint emerge**: a persistent incompatibility of siblings is a residual that, by 4.5, generates a proposal for a parent level \(M_{12}\) whose contract reconciles both. A conflict of levels is not a failure but a *signal to give birth to the next level*. This is exactly how tissue conflicts of cells are resolved by the appearance of organismal regulation.

## 5.7. Summary table of regimes

\[
\begin{array}{lll}
\textbf{Observation} & \textbf{Diagnosis} & \textbf{Action}\\\hline
d_t\le\eta & \text{normal} & \text{—}\\
\text{drift } d_t & \text{the world has changed} & \text{learning }G\ (\text{1.6})\\
\text{persistent } d_t>\eta_{\text{crit}} & \text{the abstraction has died} & \text{molt }\pi\ \text{or death of the level}\\
x\notin C_M(\hat y) & \text{micro damage} & \text{repair (thm. 4), regeneration (3.6)}\\
\text{oscillation } e_t & \text{resonance of bureaucracy} & \text{lower }\alpha\beta\ (\text{thm. 7})\\
C_1\cap C_2=\varnothing & \text{sibling conflict} & \text{filters}\to\text{seniority}\to\text{joint emerge}\\
\text{closed unregistered subsystem} & \text{cancer} & \text{audit, apoptosis (3.7)}
\end{array}
\]

---

# Synthesis: the ontogenic system, version 2

\[
\boxed{
\mathfrak O_2
=
\big(\Theta,\ X,\ R,\ \widehat\Pi,\ \widehat C,\ \mathbf M\big)
}
\]

- \(\Theta\) — the ontology-signature with a version in the category \(\mathbf{Ont}\) (Pillar 4);
- \(X\) — the realization, with the locality metric from \(K\), fields as the sole channel of long-range action (L3);
- \(R\) — the rules, realized by bounded-capacity oracles (Theorem 3, Corollary 2);
- \(\widehat\Pi\) — the **certified** levels \(\{(A,\pi,G,\eta,L,\mu)\}\) with validity horizons, learning, molt, and death (Pillar 1);
- \(\widehat C\) — the **contracts** with local predicates, repair, regeneration, and apoptosis (Pillar 3), with bounded stiffnesses \(\alpha,\beta\) (Pillar 5);
- \(\mathbf M\) — the grammar of mutations \(\mu_1\)–\(\mu_5\) with conservativity, a typecheck gatekeeper, and MDL acceptance (Pillar 4).

The five axioms of Part I have each received a theorem:

\[
\begin{array}{lll}
\textbf{Axiom (Part I)} & \textbf{Theorem (Part II)} & \textbf{Classical support}\\\hline
\text{Generativity} & \text{thm. 5, 3.6: generation = repair = regeneration} & \text{codes, self-stabilization}\\
\text{Locality} & \text{thm. 3: bounded context} & \text{decay of correlations (Lieb–Robinson)}\\
\text{Ontological ext.} & \text{thm. 6: conservative mutations} & \text{logic of definable extensions}\\
\text{Emergent closure} & \text{thm. 1, 2: canonicity + spectral search} & \text{transfer operators, causal states, IB}\\
\text{Recursive universality} & \text{lem. 4, thm. 7: a tower of pairwise contracts} & \text{filtering, data assimilation}
\end{array}
\]

**The main interlocks** (what makes this one theory, not five chapters):

1. \(\texttt{emerge}=\mathrm{Quot}_\pi\): dynamic detection of a level and the birth of a type — one act (1↔4).
2. The level certificate is the currency of the whole system: it sets the context (2), the semantics of repair (3), the trust coefficients (5), and the price in MDL (4).
3. \(C_M\) is triple-purpose: constraint (I §8), regeneration blueprint (3.6), reconciliation channel (5.3).
4. The SLM is legal twice: by capacity (Corollary 2) and by errors (§2.6 + thm. 4).
5. A stable abstraction = contracting macrodynamics (Corollary 1) — the criterion for what is worth elevating into a type at all.

---

# Registry of rigor

**Proved at the level of a lemma** (short complete proofs): defect accumulation (lem. 1), context truncation (lem. 3), defect via a cut (lem. 2), tower telescoping (lem. 4), conservativity of definable extensions (thm. 6, classical).

**Rigorous sketch** (the statement is exact, the proof requires a careful write-up): the spectral gap theorem (thm. 2 — for nonlinear \(U\) via the Koopman operator and finite-sample estimates), convergence of repair (thm. 4 — exact conditions on the interference graph), redundancy bounds (thm. 5 — constants), loop stability (thm. 7 — beyond linearization).

**Open problems** (honestly):

1. The complexity of searching for candidates \(A\): in full generality NP-hard (akin to community / cut search); Lemma 2 justifies heuristics, but there is no guarantee of completeness of the level search.
2. Detection of an unregistered hostile closure (cancer, 3.7) is semi-decidable; the same form as alignment.
3. Non-computability of MDL — we work with proxies; a theorem on the stability of the criterion under the choice of proxy is needed.
4. A nonlinear theory of the loop (thm. 7): basins of attraction, not linearization.
5. Emerge for \(\pi\) realized by learnable functions (not partitions and not linear projections): when the certificate \((\eta,L)\) is honestly estimated from finite data — a sample theory is needed (PAC bounds on the defect).

Points 1–5 are not cracks in the foundation but a program of dissertations. The foundation is Theorems 1–7 and their interlocks.
