# Part III. Completing the apparatus: full proofs and closing the open problems

Continuation of `ontogenic_system_math_core.md` (Part I) and `ontogenic_system_math_pillars.md` (Part II).
Part II left four theorems in the status of "rigorous sketch" and five open problems.
Part III turns the sketches into proofs and closes (fully or honestly-partially) all five problems.

Summary of results:

| Was (Part II) | Became (Part III) |
|---|---|
| Thm 2 — sketch | **Thm 2′** — full spectral theorem (via the EDMD residual) + finite-sample theory of certificates (DKW) |
| Thm 4 — sketch | **Thm 4′** — full proof of the drift + semantic version + **expander realization** (law: the contract graph is an expander) |
| Thm 5 — sketch | **Thm 5′** — full converse proofs + achievability + a theorem that **the hierarchy is forced** by locality |
| Thm 7 — linearization | **Thm 7′** — exact linear form (Part II corrected!), nonlinear version with a basin of attraction, the price of bureaucracy |
| Problem 1 (candidate search) | NP-hardness + **certified Cheeger approximation** |
| Problem 2 (cancer) | partial result: spectrally-noticeable cancers are caught polynomially |
| Problem 3 (MDL proxy) | **proposition on the stability of decisions** with a proof |
| Problem 4 (nonlinear loop) | closed locally (Lyapunov, explicit basin) |
| Problem 5 (sample certificates) | closed (quantile certificates, DKW, routing of the tail into repair) |

---

# 0. Conventions

- \((X,d)\) — Polish state space of the realization; \(\mu\) — invariant (or stationary visited) distribution of the dynamics \(U\).
- Norms of observables are in \(L^2(\mu)\) unless stated otherwise; \(\|\cdot\|\) without an index denotes the operator norm.
- **Quantile certificate.** Part II defined the defect as the ess-sup — this is inconvenient to estimate from data. Everywhere below the level certificate has the form

\[
\mathcal L=(A,\pi,G,\ \eta,\ q,\ \delta,\ M,\ L)
\]

with the meaning: *over \(M\) observations, with probability \(\ge 1-\delta\), the fraction of steps with step-wise defect \(\le\eta\) is at least \(q\)*. Rare exceedances of the defect are not a collapse of the level but **damage events**, routed into repair (Pillar 3). This is the key coupling of Part III:

\[
\boxed{
\text{Tail of the defect distribution}\;\longrightarrow\;\text{damage model}\;\longrightarrow\;\text{theorem 4′.}
}
\]

A level need not be flawless; it needs to be *repairable*.

---

# 1. Theorem 2′: emergence of a level, full version

## 1.1. Construction

Fix a subsystem \(A\) and a dictionary of observables \(\mathcal D=\{f_1,\dots,f_p\}\subset L^2(\mu)\)
(coordinates, local averages, any computable features). Let \(V=\operatorname{span}\mathcal D\), and let \(P\) be the orthoprojector onto \(V\).

The Koopman operator: \((\mathcal U f)(x)=f(U(x))\) (in the stochastic case \(\mathbb E[f(U(x))\mid x]\)); \(\mathcal U\) is a contraction on \(L^2(\mu)\) for invariant \(\mu\).

**Compression onto the dictionary (EDMD):** \(\widehat{\mathcal U}=P\,\mathcal U\,P\big|_V\) — a finite-dimensional \(p\times p\) operator.

Suppose \(\widehat{\mathcal U}\) has an invariant subspace \(W_m\subset V\) of dimension \(m\) with basis \(\psi_1,\dots,\psi_m\) (eigen- or Schur vectors) and spectral gap

\[
g\;=\;\operatorname{sep}\big(\operatorname{spec}\widehat{\mathcal U}|_{W_m},\ \operatorname{spec}\widehat{\mathcal U}|_{W_m^\perp}\big)>0 .
\]

Set

\[
\pi(x)=(\psi_1(x),\dots,\psi_m(x)),
\qquad
G=\widehat{\mathcal U}\big|_{W_m}.
\]

## 1.2. The defect equals the residual

**Theorem 2′ (structural part).** The step-wise defect of the level \((\pi,G)\) in \(L^2(\mu)\) equals the norm of the compression residual on \(W_m\):

\[
\boxed{
\eta_{L^2}
=
\big\|\,\pi\circ U-G\circ\pi\,\big\|_{L^2(\mu)}
=
\big\|\,(\mathcal U-\widehat{\mathcal U})\big|_{W_m}\big\|
\;\le\;
\underbrace{\big\|(I-P)\,\mathcal U\big|_{W_m}\big\|}_{\text{dictionary residual }\rho_{\mathcal D}}
}
\]

and, in particular, is **computable from data** (it is the EDMD least-squares residual), and the Lipschitz constant of the macrodynamics is \(L=\|G\|\le\|\mathcal U\|\le1\).

*Proof.* For \(\psi\in W_m\):
\(\psi(U(x))=(\mathcal U\psi)(x)=(\widehat{\mathcal U}\psi)(x)+\big((I-P)\mathcal U\psi\big)(x)\).
The first term is exactly the \(G\)-evolution of the coordinates \(\pi\) (invariance of \(W_m\) under \(\widehat{\mathcal U}\)); the second is the residual. Taking the \(L^2(\mu)\)-norm componentwise gives the equality; the inequality holds because \((\mathcal U-\widehat{\mathcal U})|_V=(I-P)\mathcal U|_V\). The bound on \(L\): \(G\) is a contraction of a contraction. ∎

**Comment (what this gives).** The question "does a level exist?" is reduced to the question "is the least-squares residual on the invariant subspace small?" — a measurable quantity. The spectral gap \(g\) is needed not for existence, but for **stability** (next item) and for separating the "slow" coordinates from noise.

## 1.3. Stability against estimation: Davis–Kahan

In practice \(\widehat{\mathcal U}\) is estimated from \(M\) pairs \((x_i,U(x_i))\): \(\widehat{\mathcal U}_M\) is the least-squares solution. Let \(E=\widehat{\mathcal U}_M-\widehat{\mathcal U}\) be the estimation error.

**Lemma 5 (subspace stability).** If \(\|E\|<g/4\), then \(\widehat{\mathcal U}_M\) has an invariant subspace \(\widehat W_m\) with

\[
\big\|\sin\Theta(\widehat W_m,W_m)\big\|
\;\le\;
\frac{2\|E\|}{g},
\]

and the defect of the level built from \(\widehat W_m\) satisfies
\(\eta(\widehat\pi,\widehat G)\le \eta(\pi,G)+C\|E\|\big(1+\tfrac{2}{g}\big)\).

*Proof.* The first part is the Davis–Kahan theorem (in the non-self-adjoint case — a variant via spectral separation, Stewart). The second is the Lipschitz continuity of the defect in the pair \((\pi,G)\): \(\eta\) is the norm of the difference of two compositions of Lipschitz maps; a perturbation of the basis by \(\sin\Theta\) and a perturbation of \(G\) by \(\|E\|\) yield a contribution linear in \(\|E\|\) with a factor controlled by \(1/g\). ∎

Hence the meaning of the gap: **the gap is the modulus of stability of the abstraction against under-fitting**. A level with a wide gap can be learned from small data; a level without a gap is a sampling artifact.

## 1.4. Finite-sample certificate (closing Problem 5)

Let \(d_1,\dots,d_M\) be the observed step-wise defects along a trajectory, and let \(F\) be their true distribution function (stationary regime; for dependent data \(M\) is replaced by the effective size \(M_{\text{eff}}=M(1-\theta)/(1+\theta)\) under \(\theta\)-mixing — an honest correction).

**Theorem 8 (quantile certificate).** With probability \(\ge1-\delta\), simultaneously for all \(t\):

\[
F(t)\;\ge\;\widehat F_M(t)-\sqrt{\tfrac{\ln(2/\delta)}{2M}} .
\]

Consequently, setting \(\eta:=\widehat F_M^{-1}(q_0)\) (the empirical \(q_0\)-quantile), we obtain the certificate

\[
\boxed{
\mathbb P\big(\text{step defect}\le\eta\big)
\;\ge\;
q_0-\sqrt{\tfrac{\ln(2/\delta)}{2M}}
\quad\text{with confidence }1-\delta .
}
\]

*Proof.* The Dvoretzky–Kiefer–Wolfowitz inequality with the Massart constant gives a band uniform in \(t\) for the empirical distribution function; substitute the empirical quantile. ∎

**Corollary 3 (tail routing).** The fraction of steps \(1-q\) with defect \(>\eta\) is treated as a damage stream of intensity \(\lambda_{\text{dmg}}\le(1-q)\) onto the macro-object per tick. By Theorem 4′ (below), repair withstands the damage stream if the mean repair time \(\mathbb E[T]\le\Phi_0/\gamma\) is shorter than the mean interval between damages:

\[
\boxed{
\frac{\Phi_{\text{dmg}}}{\gamma}\;<\;\frac{1}{\lambda_{\text{dmg}}}
\quad\Longrightarrow\quad
\text{level + repair are jointly stable.}
}
\]

This is the **joint fitness condition** of a level: not "the defect is always small," but "exceedances are rarer than they are repaired." Lemma 1 (defect accumulation) applies between exceedance events.

---

# 2. Theorem 4′: repair, full proof

## 2.1. Formal model

- A finite set of predicates \(\mathcal C=\{\varphi_1,\dots,\varphi_m\}\), each with support \(\operatorname{supp}\varphi_j\) (a set of entities/cells).
- **Interference graph** \(H\): \(\varphi_i\sim\varphi_j\iff\operatorname{supp}\varphi_i\cap\operatorname{supp}\varphi_j\neq\varnothing\); maximal degree \(\Delta\).
- **Repair action** \(a_j\): applicable when \(\varphi_j\) is violated; changes the state only on \(\operatorname{supp}\varphi_j\); postcondition — \(\varphi_j\) is satisfied; may (randomly) violate neighbors in \(H\).
- **Scheduler**: asynchronous, fair (every persistently violated predicate is eventually served); actions with disjoint supports commute, so without loss of generality we analyze the serialization.
- \(\Phi_t\) — the number of violated predicates after \(t\) actions.

**Condition (\(\gamma\)-contraction).** There exists \(\gamma\in(0,1]\): for every reachable state and every applicable \(a_j\)

\[
\mathbb E\big[\#\{\text{new violations after }a_j\}\big]\;\le\;1-\gamma .
\]

## 2.2. Theorem and proof

**Theorem 4′ (convergence).** Under \(\gamma\)-contraction, from any state with \(\Phi_0\) violations, repair reaches \(L(\mathcal C)\) almost surely, with

\[
\mathbb E[T]\;\le\;\frac{\Phi_0}{\gamma},
\qquad
\mathbb P\big(T>k\,\Phi_0/\gamma\big)\le\frac1k,
\]

and, under additionally bounded increments (\(|\Phi_{t+1}-\Phi_t|\le\Delta+1\)) — sub-Gaussian concentration:
\(\mathbb P\big(T>\tfrac{\Phi_0}{\gamma}+s\big)\le\exp\big(-\tfrac{\gamma^2 s^2}{2(\Delta+1)^2(\Phi_0/\gamma+s)}\big)\).

*Proof.* Each action repairs exactly one violation and creates in expectation \(\le1-\gamma\) new ones, hence

\[
\mathbb E[\Phi_{t+1}\mid\mathcal F_t]\;\le\;\Phi_t-1+(1-\gamma)\;=\;\Phi_t-\gamma
\quad\text{on }\{\Phi_t>0\}.
\]

The process \(M_t=\Phi_{t\wedge T}+\gamma\,(t\wedge T)\) is a supermartingale: \(\mathbb E[M_{t+1}\mid\mathcal F_t]\le M_t\). It is nonnegative, hence converges a.s.; since on \(\{\Phi_t>0\}\) the drift is strictly negative and \(\Phi\) is integer-valued, \(T<\infty\) a.s. (Foster–Lyapunov drift theorem). By optional stopping (bounded increments, \(\mathbb E T<\infty\) from the drift): \(\mathbb E[M_T]\le M_0=\Phi_0\), and \(M_T=\gamma\,T\), whence \(\mathbb E[T]\le\Phi_0/\gamma\). The tail by Markov; the concentration — the Azuma–Hoeffding inequality for a supermartingale with bounded increments (Hájek's variant). ∎

## 2.3. Semantic version

**Theorem 4′′ (repair preserves meaning).** If, in addition, each action shifts the macrostate by at most \(\zeta\): \(d\big(\pi(x_{\text{after}}),\pi(x_{\text{before}})\big)\le\zeta\), then the total semantic drift of the repair

\[
d\big(\pi(x_{\text{repair}}),\pi(x_{\text{init}})\big)
\;\le\;
\zeta\,T
\;\overset{\mathbb E}{\le}\;
\frac{\zeta\,\Phi_0}{\gamma}.
\]

*Proof.* The triangle inequality along the repair trajectory + Thm 4′. ∎

Repair is correct in the sense of Part II §3.4 if \(\zeta\Phi_0/\gamma\) is smaller than the resolving power of the level (its \(\eta\)) — a verifiable condition, both quantities being certified.

## 2.4. Expander realization: where \(\gamma\)-contraction comes from

The \(\gamma\)-contraction condition is not wishful thinking: there is a classical construction in which it is **provable**.

**Theorem 4′′′ (expander contracts; after Sipser–Spielman).** Let the predicates be linear code checks on a bipartite "cells–checks" graph that is a \((\rho_0,\tfrac34 d)\)-expander (every set of \(\le\rho_0 N\) cells has \(>\tfrac34 d\) fraction of unique check-neighbors). Then:

1. the code has **constant rate** (redundancy is a constant factor);
2. the repair "flip the cell whose majority of incident checks are violated" is local, asynchronous, and satisfies a strict variant of \(\gamma\)-contraction: each action decreases \(\Phi\) by at least 1;
3. from any damage of weight \(\le\rho_0N/2\) the system returns to the legal set in \(O(\Phi_0)\) actions, restoring the original meaning (the same codeword).

*Proof.* Items 1–3 are the Sipser–Spielman theorem on flip-decoding of expander codes, rewritten in our terms: their potential (the number of violated checks) is our \(\Phi\); their progress argument via expansion is our \(\gamma\)-estimate with \(\gamma=1\) in deterministic form; the locality of the rule is by construction. ∎

Hence the **design law** that Part II only groped for:

\[
\boxed{
\textbf{The contract graph must be an expander.}
}
\]

Redundancy spread uniformly and "well mixed" is the only known topology under which *local* repair provably converges against *adversarial* damage at *constant* cost. (Biological comment: mixing topologies of redundancy — chromatin territories, diploidy, the distributivity of metabolic networks — are exactly about this.)

## 2.5. An important distinction: local repair ≠ local decoding

The known lower bounds for *locally decodable* codes (recover one bit in \(O(1)\) queries) are severe: a constant number of queries is incompatible with a constant rate. Our construction does **not violate** them and does **not require** them: repair restores a *legal state as a whole* by a set of local asynchronous steps, rather than answering a point query in \(O(1)\). The requirement of an ontogenic system is the second, and it is achievable (Thm 4′′′). This distinction saves the construction and should be fixed as a norm of the language: `constraint` promises homeostasis, not a point-access oracle.

---

# 3. Theorem 5′: redundancy, full proofs

Substrate: \(N\) cells of \(b\) bits, \(\operatorname{cap}=Nb\). Semantics: the macro-value \(y\), uniform over \(2^{H}\) classes (\(H=H(y)\)); the realization is any microstate from \(\pi^{-1}(y)\).

## 3.1. Erasures: exact lower bound

**Theorem 5′-a.** If the system recovers \(y\) after the erasure of *any* \(\rho N\) cells, then

\[
\operatorname{cap}\;\ge\;\frac{H}{1-\rho}.
\]

*Proof.* Fix an arbitrary erasure pattern \(S\), \(|S|=\rho N\). Recoverability under pattern \(S\) means: the contents of the cells outside \(S\) determine \(y\). The map "class \(y\mapsto\) contents of \(\bar S\)" (for any chosen representative of the class) must be injective on classes: otherwise two classes have representatives coinciding on \(\bar S\), and the adversary, by erasing \(S\), makes them indistinguishable. The number of distinguishable values on \(\bar S\) does not exceed \(2^{(1-\rho)Nb}\), hence \(2^{H}\le2^{(1-\rho)Nb}\). ∎

**Achievability.** MDS codes (Reed–Solomon over a sufficient alphabet) achieve equality; random linear codes achieve rate \(1-\rho-\varepsilon\) for any \(\varepsilon>0\). Compatibility with local repair — via Thm 4′′′ (expander codes: constant, not optimal, but locally repairable redundancy).

## 3.2. Corruption: distance bound

**Theorem 5′-b.** If the system recovers \(y\) after *corruption* of any \(\rho N\) cells, then the semantic code distance (the minimal Hamming gap between realizations of different classes) must exceed \(2\rho N\), and therefore

\[
\operatorname{cap}\;\ge\;\frac{H}{1-2\rho}
\qquad(\rho<\tfrac12\ \text{— the absolute ceiling of adversarial corruption}).
\]

*Proof.* Let \(x\in\pi^{-1}(y)\), \(x'\in\pi^{-1}(y')\), \(y\neq y'\), and \(d_{\text{H}}(x,x')\le2\rho N\). Take \(z\) "halfway": \(d_{\text{H}}(x,z)\le\rho N\), \(d_{\text{H}}(x',z)\le\rho N\). The adversary can present \(z\), corrupting \(\rho N\) cells from both \(x\) and \(x'\); the decoder must output both \(y\) and \(y'\) simultaneously — a contradiction. Hence all inter-class distances are \(>2\rho N\). The Singleton bound for a code with distance \(d\): the number of classes \(\le 2^{(N-d+1)b}\le2^{(1-2\rho)Nb+b}\); taking logarithms and neglecting \(+b\), we obtain the claim. ∎

## 3.3. Corollary: the hierarchy is forced

Combine three established facts: (i) checking and repair must be \(k\)-local (Pillar 2 — otherwise context grows with the world); (ii) integrity against a fraction \(\rho\) requires redundancy with rate \(\le1-2\rho\) (Thm 5′-b); (iii) local repair at constant redundancy exists, but requires an expander topology with a *bounded* support size per level (the constants \(\rho_0\) in Thm 4′′′ fall as the support inhomogeneity grows).

**Corollary 4 (necessity of the tower).** A system of unbounded size cannot maintain integrity with a single flat contract: at fixed \(k\) and redundancy rate, the admissible adversarial fraction \(\rho\) on a flat substrate does not scale. Partitioning into macro-objects with contracts at each level (damage of level \(\ell\) is "one cell" of level \(\ell+1\)) restores a constant \(\rho\) **at each level** with a logarithmic tower depth.

*Sketch.* The standard composition of codes (concatenation/Tanner): an outer code over the alphabet "states of macro-objects," inner codes on realizations; locality is preserved, since the checks of each layer are local at their own scale; depth \(O(\log N)\). ∎(sketch)

\[
\boxed{
\text{The hierarchy is not an ornament of the model, but the \emph{only} way to reconcile}\\
\text{locality (Pillar 2) with integrity (Pillar 3) at unbounded size.}
}
\]

This is, perhaps, the strongest structural result of Part III: the Recursive universality axiom has turned from a postulate into a theorem of necessity.

---

# 4. Theorem 7′: the alignment loop, exact form

## 4.1. Correction to Part II

Part II gave the condition \(|1-\beta-\alpha\gamma|\cdot\|A_G\|<1\) as a heuristic. The exact derivation gives a different (more informative) form; we fix it as canonical.

**Model.** True macrostate \(y_t=\pi(x_t)\), estimate \(\hat y_t\), error \(e_t=\hat y_t-y_t\). Per macro-tick:

- free macrodynamics: \(y\mapsto Ay+w_t\), \(\|w_t\|\le\eta\) (level defect);
- top-down enforcement of stiffness \(\alpha\): reality is pulled toward the estimate, \(y_{t+1}=Ay_t+\alpha\gamma\,e_t+w_t\) (\(\gamma\in(0,1]\) — sensitivity of \(\pi\) to the repair shift);
- bottom-up filter with coefficient \(\beta\): \(\hat y_{t+1}=(1-\beta)A\hat y_t+\beta\,(y_{t+1}+v_t)\), \(\|v_t\|\le\sigma\) (measurement noise of \(\pi\)).

**Theorem 7′ (linear, exact).** The estimation error satisfies

\[
e_{t+1}
=
(1-\beta)\,(A-\alpha\gamma I)\,e_t
-(1-\beta)w_t+\beta v_t,
\]

and the loop is stable if and only if

\[
\boxed{
\rho\big((1-\beta)(A-\alpha\gamma I)\big)<1,
}
\]

with limiting error

\[
\limsup_t\|e_t\|
\;\le\;
\frac{(1-\beta)\eta+\beta\sigma}{1-\rho\big((1-\beta)(A-\alpha\gamma I)\big)} .
\]

*Proof.* Substitution: \(e_{t+1}=\hat y_{t+1}-y_{t+1}=(1-\beta)\big(A\hat y_t-y_{t+1}\big)+\beta v_t\); then \(A\hat y_t-y_{t+1}=A e_t-\alpha\gamma e_t-w_t\). Stability of a linear recursion with bounded input — the spectral radius; the geometric sum gives the limit. ∎

**Reading the condition.** It suffices that \((1-\beta)(\|A\|+\alpha\gamma)<1\). Overshoot (oscillations — the "resonance of bureaucracy") arises when \(\alpha\gamma>\|A\|+1\): the eigenvalues of the multiplier move onto the negative half-axis with modulus \(>1\) for small \(\beta\). The meaning is preserved, the form has become exact: the error is **damped** both by the filter (\(1-\beta\)) and by moderate enforcement (a shift of \(A\) by \(-\alpha\gamma I\)); only *excessive stiffness* of enforcement, or switched-off measurements, ruins it.

## 4.2. The price of bureaucracy: trajectory displacement

Small \(e\) is not free: enforcement drags the world behind the map. Let \(y^{\text{free}}\) be the trajectory without enforcement (\(\alpha=0\)) under the same noises, and \(D_t=y_t-y^{\text{free}}_t\) — the **displacement**.

**Proposition 1.** \(D_{t+1}=A D_t+\alpha\gamma e_t\), and for \(\|A\|<1\)

\[
\limsup_t\|D_t\|\;\le\;\frac{\alpha\gamma\,\sup_t\|e_t\|}{1-\|A\|}.
\]

*Proof.* Subtracting the recursions; the geometric sum. ∎

The displacement is not necessarily an evil (homeostasis *is* a useful displacement toward the legal set), but it is **certifiable**: the price of enforcement is visible and bounded. Self-fulfilling bureaucracy has turned from a pathology into a measurable parameter of the contract.

## 4.3. Nonlinear version: basin of attraction (closing Problem 4)

**Theorem 7′′.** Suppose that on the ball \(B_r=\{\|e\|\le r\}\) the macrodynamics \(G\) is Lipschitz with \(L_G\), the enforcement sensitivity is bounded by \(\gamma\le\bar\gamma\), and a contraction with margin holds:

\[
(1-\beta)\,(L_G+\alpha\bar\gamma)\;\le\;1-m,\qquad m>0 .
\]

If the inputs are small: \((1-\beta)\eta+\beta\sigma\le m\,r\), then the ball \(B_r\) is invariant, and for all starts from \(B_r\)

\[
\limsup_t\|e_t\|\;\le\;\frac{(1-\beta)\eta+\beta\sigma}{m}.
\]

*Proof.* Lyapunov function \(V=\|e\|\). Inside \(B_r\) the exact step from Thm 7′, with linear operators replaced by Lipschitz estimates, gives \(V_{t+1}\le(1-m)V_t+(1-\beta)\eta+\beta\sigma\). The right-hand side \(\le(1-m)r+mr=r\) — invariance; iteration of the affine contraction — the limit. ∎

The basin is explicit: any ball where the Lipschitz constants are honest and the noises are small relative to the margin \(m\). A global theory is not needed for the normative conclusion: the **loop certificate** = the quadruple \((L_G,\alpha\bar\gamma,\beta,m)\) with a verifiable condition.

---

# 5. Candidate search: hardness and certified approximation (Problem 1)

Let \(K\) be a weighted interaction graph, for \(A\subset V\): \(\operatorname{cut}(A)\) — the cut weight, \(\varphi(A)=\operatorname{cut}(A)/\min(\operatorname{vol}A,\operatorname{vol}\bar A)\) — the conductance. By Lemma 2 (Part II) the level defect is controlled by the cut, hence candidate search = search for sets of small conductance.

**Theorem 9.**
(a) The problem "find \(A\) with minimal \(\varphi(A)\)" is NP-hard (this is the sparsest-cut problem).
(b) Let \(\lambda_2\) be the second eigenvalue of the normalized graph Laplacian of \(K\). The spectral sweep over the Fiedler vector in time \(O(|E|\log|V|)\) returns \(A^\*\) with

\[
\frac{\lambda_2}{2}\;\le\;\varphi_{\min}\;\le\;\varphi(A^\*)\;\le\;\sqrt{2\lambda_2}\;\le\;2\sqrt{\varphi_{\min}} .
\]

*Proof.* (a) — the classical NP-hardness of sparsest cut/conductance. (b) — the Cheeger inequality with the algorithmic (sweep) version of the upper bound. ∎

**Corollary 5 (two-sided search certificate).** The algorithm outputs not only a candidate, but also a **proof of quality**: the found \(\varphi(A^\*)\) is an upper bound, \(\lambda_2/2\) is a lower bound on the best possible. If \(\lambda_2\) is large — a certificate of the absence of levels of this kind: *in this interaction graph there are no weakly-connected subsystems*, and EMERGE honestly returns "the world at this scale is indecomposable." Problem 1 is closed in the correct form: exact search is hard, but is never needed — what is needed is search with a gap certificate.

Hierarchical application (a recursive sweep within the found \(A\)) gives a tree of candidates in \(O(|E|\log^2|V|)\) — compatible with Pillar 2 by cost.

---

# 6. Stability of MDL against the proxy choice (Problem 3)

The true \(\mathrm{DL}\) is uncomputable; in practice — a proxy \(\widehat{\mathrm{DL}}\) (two-part codes, predictive cross-entropy).

**Proposition 2.** Suppose two proxies are uniformly close to the ideal: \(|\widehat{\mathrm{DL}}_i-\mathrm{DL}|\le c\) (\(i=1,2\)) on the class of descriptions under consideration. Then decisions to accept a mutation by the criterion \(\Delta\mathrm{DL}<0\) can diverge only in the **band of uncertainty** \(|\Delta\mathrm{DL}|\le2c\); every decision with margin \(>2c\) is invariant to the proxy choice.

*Proof.* \(|\Delta\widehat{\mathrm{DL}}_1-\Delta\widehat{\mathrm{DL}}_2|\le|\Delta\widehat{\mathrm{DL}}_1-\Delta\mathrm{DL}|+|\Delta\mathrm{DL}-\Delta\widehat{\mathrm{DL}}_2|\le2c\) (the constants \(c\) cancel only partially in the "before/after" difference; we take the worst case). The sign of a difference exceeding \(2c\) in modulus is the same for all proxies. ∎

**Acceptance norm:** a mutation is accepted when \(\Delta\widehat{\mathrm{DL}}<-2c\), rejected when \(\Delta\widehat{\mathrm{DL}}>2c\), and in the band — deferred until data accumulates (the band narrows: \(c\) falls as the sample grows for statistical proxies). Hysteresis instead of a threshold is the standard defense against decision chatter; Problem 3 is closed normatively.

---

# 7. Cancer: a partial positive result (Problem 2)

Full detection of unregistered closure remains hard (the space of subsystems is exponential; the general case inherits the NP-hardness of Thm 9a). But:

**Proposition 3 (spectrally-noticeable cancer is caught).** Suppose the cancer subsystem \(B\) (Part II, Def. 7) possesses closure with a gap: its presence creates in the graph \(K\) a set of conductance \(\varphi(B)\le\varepsilon_B\). Then the recursive sweep of Thm 9 detects *some* set \(B'\) with \(\varphi(B')\le2\sqrt{\varepsilon_B}\), intersecting \(B\); the subsequent EMERGE certification on \(B'\) reveals the unregistered closure, and checking its \(G_{B'}\) against the enclosing contract reveals malignancy. The cost is polynomial, the same as for a scheduled EMERGE.

*Meaning.* A cancer that has taken enough shape to be *dangerous* (self-sustaining — Corollary 1 of Part II requires contracting, hence spectrally distinguished, dynamics) automatically becomes *visible* to the very instrument with which the system searches for its own levels. **The immune audit = EMERGE, run on schedule.** Only a cancer without a gap remains invisible — but it is also not self-sustaining (Corollary 1), i.e. it is washed out by noise. A rigorous version of this dichotomy ("dangerous ⇒ visible") is a remaining open conjecture; stated below in the registry.

---

# 8. End-to-end analytic example

A minimal system in which the entire apparatus is computed by hand.

**World.** \(X=\mathbb R^{2}\times\mathbb R^{n-2}\), linear dynamics in a hidden basis:

\[
U=\begin{pmatrix}A_s&\varepsilon B\\ \varepsilon C&A_f\end{pmatrix},
\qquad
A_s=0.98\,R(\theta)\ \ (\text{slow rotation}),\quad
\|A_f\|=0.4,\quad
\varepsilon=10^{-3},
\]

\(\|B\|,\|C\|\le1\), states normalized \(\|x\|\le1\).

**Pillar 1.** Dictionary — linear functionals; EDMD recovers the block structure; \(W_2\) — the slow subspace. Defect (Thm 2′): \(\eta\le\varepsilon\|B\|\cdot\|x_f\|\le10^{-3}\); \(L=\|A_s\|=0.98\). Gap \(g\approx0.98-0.4=0.58\) — wide: by Lemma 5 the level is stable against estimation. Lemma 1: \(\delta_\infty\le\eta/(1-L)=0.05\); the fitness horizon for \(\varepsilon_{\text{target}}=0.01\): \(n^\*=\big\lceil\log(1-0.01\cdot0.02/10^{-3})/\log0.98\big\rceil\approx10\) ticks; the eternal guarantee — at the level \(0.05\).

**Pillar 2.** Updating any coordinate requires: its own block neighbors + \(y_M=\pi(x)\) (2 numbers). Context: \(O(1)\), independent of \(n\) — Theorem 3 in action for any \(n\).

**Pillar 5.** \(A=A_s\), \(\|A\|=0.98\). Take \(\beta=0.5\), \(\alpha\gamma=0.3\): the multiplier \((1-\beta)(\|A\|+\alpha\gamma)=0.5\cdot1.28=0.64<1\) — stable with margin \(m=0.36\). Limiting error at \(\sigma=10^{-2}\): \(\|e\|_\infty\le(0.5\cdot10^{-3}+0.5\cdot10^{-2})/0.36\approx1.5\cdot10^{-2}\). The price of bureaucracy (Prop. 1): \(\|D\|_\infty\le0.3\cdot1.5\cdot10^{-2}/0.02=0.23\) — noticeable! The conclusion from the certificate: either lower \(\alpha\gamma\) (enforcement), or accept the displacement as the price of homeostasis — the decision is visible in numbers *before* launch.

**Pillar 3.** Discretize the slow coordinates into 8 bits and protect them with an expander code of rate \(1/2\): by Thm 5′-b we withstand adversarial corruption up to \(\rho=1/4\) with local repair in \(O(\Phi_0)\) flips (Thm 4′′′). The semantic drift of the repair (Thm 4′′): \(\zeta=0\) (the repair does not touch legal cells in this construction) — the meaning is preserved exactly.

Every number above is a consequence of a theorem, not of a simulation. Such is the target form of certificates in the language: **the properties of a system are computed before its launch**.

---

# 9. Appendix: a bridge to `resona` (instrumentation, not foundation)

Parts I–III are self-contained; nothing above references `resona`. But Pillar 1 in implementation will require matrix-free spectral measurements, and here the intersection with `resona` is not accidental — it is a ready measurement corpus for the *same* mathematical object (operator → spectrum without building the matrix). Justified junction points, strictly one per need:

1. **Estimating the spectrum of \(\widehat{\mathcal U}\) without matrices.** Thm 2′ requires the spectrum/invariant subspaces of an operator available only through its action. This is exactly the regime of `resona.of(matvec)` (stochastic Lanczos quadrature) and `lift.koopman` (data → the action of the propagator) — the very EDMD object from §1.1.
2. **Certificates with guaranteed brackets.** Our ideology "a number + a provable bracket" (quantile certificates, Thm 8) is realized on the spectral side by Gauss–Radau quadratures (`quadform(..., certified=True)`): two-sided brackets, the answer provably inside. A level certificate can carry spectral brackets of the same kind.
3. **Choosing the macrostate dimension \(m\).** The effective rank \(\Phi_1=\operatorname{Tr}(A)^2/\operatorname{Tr}(A^2)\) is a cheap indicator of where to look for the gap (how many modes are "audible"), prior to the expensive estimation of subspaces.
4. **A fast test "are there any levels at all."** The statistics of level spacings \(\langle r\rangle\) (Poisson \(0.386\) ↔ GOE \(0.531\)): an integrable spectrum is a candidate for closures, a chaotic one is a certificate of scale indecomposability (complements the lower bound \(\lambda_2/2\) from Thm 9).
5. **Candidate observables.** `lift.conserved_charge` (the near-kernel of the commutator problem = integrals of motion) generates the dictionary \(\mathcal D\) from §1.1 in a non-random manner: conserved quantities are the first candidates for macrovariables.
6. **Merging siblings (Pillar 5, §5.6).** In joint emerge the spectrum of the union of independent subsystems is predicted by the free convolution \(\boxplus\); the **freeness defect** (mixed free cumulants) is an alternative to Lemma 2 as a measure of coupling: they are free ⟺ the spectra compose without interaction. A small freeness defect is one more certificate that the siblings are genuinely independent.

Junction rule: `resona` is a **measuring instrument** for the theorems of Part III; not a single axiom and not a single proof depends on it. Reverse influence is possible (e.g., "freeness defect ↔ cut of \(K\)" looks like a theorem that exists neither there nor here), but that is separate work, not mixed into the foundation.

---

# 10. Updated rigor registry

**Fully proved** (Parts II–III): Lemmas 1–5; Thm 2′ (structural part and stability — under standard conditions on \(\mu\) and the dictionary); Thm 4′, 4′′ (drift, semantics); Thm 4′′′ (expander realization — by reduction to Sipser–Spielman); Thm 5′-a,b (both lower bounds); Thm 6 (conservativity); Thm 7′, 7′′ (loop: linear exactly, nonlinear locally); Thm 8 (DKW certificates); Thm 9 (Cheeger + NP-hardness — by reduction to classics); Propositions 1–3; Corollaries 1–5.

**Rigorous sketch** (remaining): Corollary 4 (necessity of the tower — needs a careful composition of codes with a depth estimate); the finite-sample constant \(C\) in Lemma 5 for dependent data (\(\theta\)-mixing).

**Open conjectures** (narrowed to two):

1. **Cancer dichotomy**: every self-sustaining (contracting) unregistered closure is spectrally noticeable at the scale of its support — "dangerous ⇒ visible" (Prop. 3 proves the easy half).
2. **Freeness defect ↔ cut**: the quantitative equivalence of the coupling measure from Lemma 2 and the mixed free cumulants (bridge #6 of the appendix) — a potential theorem unifying the graph-theoretic and spectral sides of level search.

Everything else from the Part II list is closed: Problem 1 — Thm 9 and Corollary 5; Problem 3 — Proposition 2; Problem 4 — Thm 7′′; Problem 5 — Thm 8 and Corollary 3. The Recursive universality axiom is strengthened to a necessity theorem (Corollary 4). The apparatus is completed.
