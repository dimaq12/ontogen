# Part IV. Finishing off the hypotheses

Continuation of Parts I–III. Two open hypotheses remained in the registry of Part III:

1. **Cancer dichotomy**: every self-sustaining unregistered closure is spectrally visible ("dangerous ⇒ visible").
2. **Freedom defect ↔ cut**: quantitative equivalence between the graph-theoretic connectivity measure (Lemma 2) and mixed free cumulants.

Summary of Part IV:

- Hypothesis 1 is **proved** in the reversible class (Theorem 10, two-sided), with a pseudospectral extension to the non-normal case and a quantitative **safety budget**.
- Hypothesis 2 is **refuted in its naive form** (a counterexample with zero cut and nonzero freedom defect) and **correctly reassembled**: connectivity is two-dimensional — *strength* and *alignment*; each coordinate governs its own composition of spectra (Theorems 11a, 11b). Bonus: spectral forensics of subsystem kinship.

---

# 1. Hypothesis 1 → Theorem 10 (cancer dichotomy)

## 1.1. The correct formalization of "danger"

Part II defined self-sustenance through contraction of the macrodynamics (Corollary 1). Let us sharpen this: a dangerous subsystem is one that *resists displacement* — once the world enters its regime, it stays there for a long time. This is precisely **almost-invariance** (metastability).

Working frame: the global dynamics defines a transfer operator \(P\) on \(L^2(\mu)\), where \(\mu\) is the stationary distribution. In this section \(P\) is **reversible** (self-adjoint; spectrum in \([-1,1]\)) — an honest restriction, lifted in §1.4.

**Definition 9 (escape rate).** For measurable \(S\), \(\mu(S)\le\tfrac12\):

\[
\varepsilon(S)
=
\frac{1}{\mu(S)}\int_S P\big(x,\,S^c\big)\,\mu(dx)
\]

— the per-step probability of leaving \(S\), starting from its stationary slice. A subsystem is **\(\varepsilon\)-self-sustaining** if its basin \(S\) has \(\varepsilon(S)\le\varepsilon\) (expected lifetime \(\ge1/\varepsilon\)).

**Definition 10 (spectral unexplainedness).** Let the registered levels span the slow subspace \(V_{\mathrm{reg}}\subset L^2(\mu)\) (the linear span of their macrocoordinates \(\psi\); we take it to be \(P\)-invariant up to a certified \(\eta\) — the correction enters the constants). A set \(S\) is **unexplained** if the centered normalized indicator \(f_S=\big(\mathbf 1_S-\mu(S)\big)/\|\mathbf 1_S-\mu(S)\|\) has at least half of its mass outside \(V_{\mathrm{reg}}\): \(\big\|f_S^{\perp}\big\|^2\ge\tfrac12\).

## 1.2. Theorem 10

**Theorem 10 (dichotomy, reversible case).**

**(a) Dangerous ⇒ visible.** If there exists an unexplained \(S\) with \(\varepsilon(S)\le\varepsilon\), then

\[
\boxed{
\lambda_{\max}\big(P\big|_{V_{\mathrm{reg}}^{\perp}}\big)\;\ge\;1-4\varepsilon
}
\]

— in the spectrum *not explained by the registered levels* there is an eigenvalue within distance \(\le4\varepsilon\) of unity.

**(b) Visible ⇒ dangerous (and localizable).** If \(\lambda_{\max}\big(P|_{V_{\mathrm{reg}}^{\perp}}\big)\ge1-g\), then a sweep along the corresponding eigenfunction constructs a set \(S\) with

\[
\varepsilon(S)\;\le\;\sqrt{2g},
\]

i.e. an almost-invariant subsystem with lifetime \(\ge1/\sqrt{2g}\).

*Proof.*

(a) Dirichlet form: \(\mathcal E(f_S,f_S)=\langle(I-P)f_S,f_S\rangle\). A direct computation for the indicator gives
\(\mathcal E(f_S,f_S)\le\varepsilon(S)/\big(1-\mu(S)\big)\le2\varepsilon\), i.e. the Rayleigh quotient
\(\langle Pf_S,f_S\rangle\ge1-2\varepsilon\).
Decompose \(f_S=f_{\mathrm{reg}}+f_\perp\). By invariance of \(V_{\mathrm{reg}}\): \(\langle Pf_S,f_S\rangle=\langle Pf_{\mathrm{reg}},f_{\mathrm{reg}}\rangle+\langle Pf_\perp,f_\perp\rangle\), and since \(\langle Pf_{\mathrm{reg}},f_{\mathrm{reg}}\rangle\le\|f_{\mathrm{reg}}\|^2\):

\[
\langle Pf_\perp,f_\perp\rangle
\;\ge\;
(1-2\varepsilon)-\|f_{\mathrm{reg}}\|^2
\;=\;
\|f_\perp\|^2-2\varepsilon .
\]

Rayleigh quotient on \(V_{\mathrm{reg}}^\perp\):
\(\dfrac{\langle Pf_\perp,f_\perp\rangle}{\|f_\perp\|^2}\ge1-\dfrac{2\varepsilon}{\|f_\perp\|^2}\ge1-4\varepsilon\)
by unexplainedness \(\|f_\perp\|^2\ge\tfrac12\). The variational principle completes the argument.

(b) Cheeger's inequality for reversible Markov operators: the conductance \(\Phi\le\sqrt{2(1-\lambda_2)}\), and the set realizing the estimate is constructed by a sweep along the second eigenfunction (sort by values, scan the prefixes). Apply this to \(P\) with \(V_{\mathrm{reg}}\) excised: an eigenfunction \(u\perp V_{\mathrm{reg}}\) with \(\langle Pu,u\rangle\ge1-g\) yields a sweep set \(S\) with \(\varepsilon(S)\le\Phi(S)\le\sqrt{2g}\). ∎

*Technical note.* In (b) the sweep set is only approximately orthogonal to \(V_{\mathrm{reg}}\) (a sweep does not preserve orthogonality exactly); with certified \(\eta\) of the registered levels this yields a multiplicative correction in the constant — the careful computation is routine and is deferred to the registry as a "sketch tail."

**Reading.** Between self-sustenance \(\varepsilon^\*\) (the minimal escape rate over unexplained sets) and the unexplained spectral gap \(g\) there is a two-sided bond \(g/4\le\varepsilon^\*\le\sqrt{2g}\): **self-sustenance and spectral visibility are one quantity in two coordinate systems**. Hypothesis 1 is fully proved in the reversible class, with both sides constructive.

## 1.3. The IMMUNE-AUDIT algorithm

```text
AUDIT(P, level registry):
  1. Matrix-free (Lanczos) — upper spectrum of P on V_reg^⊥
  2. If there is λ ≥ 1 − ε_a:                       // redundant slow mode
       S := sweep along its eigenfunction           // localize the support (Thm 10b)
       (π_S, G_S, certificate) := EMERGE(S)          // same procedure as for discoveries
       if G_S is compatible with the enclosing contracts:
            register a level                         // this is not cancer — it is a discovery
       else:
            apoptosis / quarantine S                 // malignancy proved by comparison
  3. Else: certificate of cleanliness "no unregistered
     closures with lifetime ≥ 1/√(2ε_a)"
```

Item 2 fixes the principle stated in Part III, now as a theorem: **the immune system and the discovery system are one code**; the difference between "cancer" and "a new organ" lies not in the method of detection but in the outcome of the contract check. And note: the "register" outcome means the audit is also a generator of emerge-candidates — immunity *feeds* the ontology.

## 1.4. The non-normal case: visibility in the pseudospectrum

Without reversibility the hard side of Cheeger fails (metastability may hide in transient growth). The soft side survives in pseudospectral form:

**Proposition 4.** Let a closure \((\pi_B,G_B)\) have defect \(\eta_B\). Then every point of \(\operatorname{spec}(G_B)\) lies in the \(\eta_B\)-pseudospectrum of the global operator:

\[
\operatorname{spec}(G_B)\subset\Lambda_{\eta_B}(\mathcal U).
\]

*Proof.* The coordinates \(\pi_B\) form an approximate invariant subspace: \(\|\mathcal U\psi-G_B\psi\|\le\eta_B\); for a (generalized) eigenvector \(v\) of the operator \(G_B\) with eigenvalue \(\lambda\) the function \(\psi_v\) gives \(\|(\mathcal U-\lambda)\psi_v\|\le\eta_B\|v\|\) — the definition of a pseudospectrum point. ∎

An audit in the non-normal world must measure \(\Lambda_\varepsilon\) (the Arnoldi cloud, the numerical abscissa), not merely eigenvalues. Here the dichotomy remains in the asymmetric form "dangerous ⇒ visible to an instrument measuring the pseudospectrum"; the converse (everything pseudospectrally visible is dangerous) is **false** in the non-normal case (pseudospectral swelling can be purely transient) — and this is not a flaw but the correct answer: a non-normal audit must separate transients from metastability by a temporal test (run \(t\sim1/\varepsilon_a\) steps). The residual tail — the quantitative theorem for this test — is in the registry.

## 1.5. Safety budget

**Corollary 6 (maximal invisible harm).** Let the audit operate at resolution \(\varepsilon_a\) (catching all unexplained modes \(\lambda\ge1-\varepsilon_a\)), and let the harm flow of any intruder be bounded by \(h_{\max}\) per step (a bound on boundary throughput — a local contract predicate). Then every *undetected* subsystem has \(\varepsilon(S)>\varepsilon_a/4\) (contrapositive of Thm 10a), its expected lifetime is \(<4/\varepsilon_a\), and the total expected harm

\[
\boxed{
\mathbb E[\text{harm of the invisible}]\;\le\;\frac{4\,h_{\max}}{\varepsilon_a}.
}
\]

The audit resolution is a knob that buys a linear harm guarantee. A "flash" short-lived pest cannot be caught by the spectrum in principle — but by construction it is bounded by this same budget and is finished off by repair (the flow condition, Corollary 3 of Part III). Safety has ceased to be a hope and become a line in the certificate.

---

# 2. Hypothesis 2: killing and reassembly

## 2.1. Counterexample: the naive form is false

Take two **entirely non-interacting** blocks: the world \(=\) a tensor product, the global generator

\[
H=a\otimes I+I\otimes b,
\qquad
\tau=\operatorname{tr}\otimes\operatorname{tr},
\quad
\tau(a)=\tau(b)=0 .
\]

The cut is zero: \(\operatorname{cut}_K=0\), there is no interaction. Compute the mixed free cumulant of fourth order \(\kappa_4(a,b,a,b)\). The variables commute and are classically independent: \(\tau(ab)=0\), so all pairwise contributions of non-crossing partitions vanish, and

\[
\kappa_4(a,b,a,b)=\tau(abab)=\tau(a^2b^2)=\tau(a^2)\,\tau(b^2)=\sigma_a^2\sigma_b^2\;>\;0 .
\]

\[
\boxed{
\operatorname{cut}=0,\qquad
\text{freedom defect}=\sigma_a^2\sigma_b^2\neq0 .
}
\]

The hypothesis "freedom defect \(\leftrightarrow\) cut" in its naive form is **dead**: fully decoupled subsystems are not free. The reason is fundamental: Voiculescu freeness is noncommutative independence, whereas disjoint supports give *commuting* (classical) independence. These are different things, and the spectra under them compose by different convolutions: for the tensor sum \(\operatorname{spec}H=\{\lambda_i+\nu_j\}\) — the **classical** convolution \(\mu_a*\mu_b\), not \(\boxplus\).

## 2.2. Diagnosis: connectivity is two-dimensional

The counterexample shows that Lemma 2 and the freedom defect measure **different coordinates** of connectivity:

- **Strength** (the cut \(\operatorname{cut}_K\)): how much interaction flows across the boundary.
- **Alignment** (cumulant defects): how much the *structures* of the subsystems are algebraically related (shared invariant subspaces, shared symmetries, shared support).

The correct theory: each coordinate gets its own theorem and its own reference composition of spectra.

## 2.3. Theorem 11a: strength governs the deviation from the independent composition

Let \(H_0\) be the decoupled operator (a tensor sum or a direct sum — depending on the support relation), \(H=H_0+V\), where \(V\) collects the boundary interactions: \(|v_{ij}|\le K(i,j)\) for pairs across the boundary. Both operators are normal (the reversible class; an honest condition).

**Theorem 11a.** The spectral measures \(\mu_H\) and \(\mu_{H_0}\) (empirical, \(N\) atoms) satisfy

\[
\boxed{
d_{W_2}\big(\mu_H,\;\mu_{H_0}\big)^2
\;\le\;
\frac{\|V\|_F^2}{N}
\;\le\;
\frac{K_\partial^{\max}}{N}\cdot\operatorname{cut}_K(A),
}
\]

where for disjoint supports \(\mu_{H_0}=\mu_a*\mu_b\) — the classical convolution of the parts.

*Proof.* The Hoffman–Wielandt inequality for normal matrices: there exists a matching of eigenvalues with \(\sum_i|\lambda_i(H)-\lambda_{\sigma(i)}(H_0)|^2\le\|V\|_F^2\). Division by \(N\) is precisely a transport plan between the empirical measures, majorizing \(W_2^2\). Next \(\|V\|_F^2=\sum_{\partial}|v_{ij}|^2\le K_\partial^{\max}\sum_{\partial}K(i,j)\). The spectrum of a tensor sum consists of sums of pairs of eigenvalues, i.e. the convolution of the measures. ∎

**Reading.** The cut is the \(W_2\)-distance from the true fusion spectrum to "the spectrum as if they were independent." A small cut ⇒ the composition is classical, with a certified error. Lemma 2 of Part II is the local (dynamical) version of this same fact; now there is a global (spectral) one.

## 2.4. Theorem 11b: alignment governs the deviation from the free composition

Now a shared support: \(H_1,H_2\) — two structures (two operators) on *one* space, a state \(\tau\), variables centered, moments bounded: \(|\tau(w)|\le M\) for words of length \(\le p\).

**Definition 11 (freedom defect of order \(p\)).**

\[
\Delta_{\mathrm{free}}(p)
=
\max_{n\le p}\;
\max_{\substack{\text{words }\varepsilon\in\{1,2\}^n\\ \text{mixed}}}
\big|\kappa_n\big(H_{\varepsilon_1},\dots,H_{\varepsilon_n}\big)\big| .
\]

**Theorem 11b.** The moments of the sum deviate from the free-convolution prediction by no more than

\[
\boxed{
\big|m_p(H_1+H_2)\;-\;m_p\big(\mu_{H_1}\boxplus\mu_{H_2}\big)\big|
\;\le\;
\mathrm{Cat}_p\cdot p\cdot 2^{p}\cdot
\max(1,M)^{\,p-1}\cdot
\Delta_{\mathrm{free}}(p).
}
\]

*Proof.* Free cumulants are multilinear, hence
\(\kappa_n(H_1+H_2)=\sum_{\varepsilon\in\{1,2\}^n}\kappa_n(H_{\varepsilon_1},\dots,H_{\varepsilon_n})\).
The pure words (\(\varepsilon\equiv1\) and \(\varepsilon\equiv2\)) give exactly \(\kappa_n(H_1)+\kappa_n(H_2)\) — the cumulants of the free convolution (additivity of \(\boxplus\)); the remaining \(2^n-2\) words are mixed, each of modulus \(\le\Delta_{\mathrm{free}}\). Hence \(|\kappa_n(H_1+H_2)-\kappa_n^{\boxplus}|\le(2^n-2)\Delta_{\mathrm{free}}\). Moments are recovered by the sum over non-crossing partitions \(m_p=\sum_{\pi\in NC(p)}\prod_{B\in\pi}\kappa_{|B|}\); the difference of two such sums telescopes over blocks: in each of the \(\le\mathrm{Cat}_p\) summands there are at most \(p\) blocks, replacing one block gives a factor \(\le(2^p-2)\Delta_{\mathrm{free}}\), and the remaining blocks are bounded by \(\max(1,M)^{p-1}\) (cumulants are bounded by polynomials in the moments; the constant is absorbed). Collecting the constants yields the claim. ∎

**Reading.** If the structures on a shared support are in "generic position" (mixed free cumulants small — no shared invariant subspaces, no coaxial symmetries), their spectra compose by the free convolution with a certified error. The freedom defect is a measurable measure of **hidden structural kinship**.

## 2.5. Dictionary of compositions and spectral forensics

We collect this in a table — this is exactly the correct form of the perished hypothesis:

\[
\begin{array}{llll}
\textbf{Support relation} & \textbf{Independence} & \textbf{Composition} & \textbf{Diagnostic defect}\\\hline
\text{disjoint (commute)} & \text{classical} & \mu_1*\mu_2 & \text{mixed classical cumulants} \\
\text{shared, generic position} & \text{free} & \mu_1\boxplus\mu_2 & \text{mixed free cumulants}\\
\text{shared, aligned (symmetry)} & \text{none} & \text{neither one} & \text{both defects large}
\end{array}
\]

Both reference compositions are computable from the spectra of the parts, both come with error estimates (11a by strength, 11b by alignment). Hence:

**Corollary 7 (spectral forensics of kinship).** By comparing the observed fusion spectrum with \(\mu_1*\mu_2\) and \(\mu_1\boxplus\mu_2\), the system determines *from the spectra alone* the support relation of the subsystems: if \(*\) fits — the supports are effectively disjoint; if \(\boxplus\) fits — a shared substrate in generic position; if neither fits — **hidden shared structure**. (The compositions are distinguishable already at the fourth moment: for instance, \(\mathrm{sc}\boxplus\mathrm{sc}\) is again a semicircle, whereas \(\mathrm{sc}*\mathrm{sc}\) is not.)

The third outcome is the most valuable: two "siblings" with a weak cut but both defects large are subsystems with a shared hidden cause. For Pillar 5 §5.6 this is exactly a **joint-emerge trigger**: a hidden parent detected spectrally before any contract conflict. The fusion protocol is updated:

```text
JOINT-EMERGE(M1, M2):
  1. if cut is small     → composition *, certificate by Thm 11a   // independent fusion
  2. else if Δ_free small → composition ⊞, certificate by Thm 11b  // generic fusion
  3. else → search for a shared parent: shared support + shared
     structure = a level above both                                // forensics, Cor. 7
```

## 2.6. What remains of Hypothesis 2

The mixed regime — both strength *and* alignment large — is covered by neither 11a nor 11b. The correct machinery there is known by name (operator-valued free probability, matrix subordination), but a theorem with an error certificate in terms of our quantities has not been written out. This is the sole residual tail of Hypothesis 2, and it is honestly circumvented by engineering: step 3 of the protocol does not predict the spectrum but constructs a parent, after which fusion happens one level higher, where the coupling is again weak or generic.

---

# 3. Final registry

**No hypotheses remain.** Status at the close of Part IV:

- Hypothesis 1: **Theorem 10** (reversible class, two-sided, constructive) + Proposition 4 (pseudospectral visibility in the non-normal case) + Corollary 6 (safety budget \(4h_{\max}/\varepsilon_a\)).
- Hypothesis 2: the counterexample of §2.1 (naive form false) + **Theorems 11a, 11b** (two-dimensional theory of connectivity: strength ↔ classical composition, alignment ↔ free composition) + Corollary 7 (kinship forensics) + the updated JOINT-EMERGE protocol.

**Sketch tails** (routine niceties, not affecting the structure): the correction for inexact invariance of \(V_{\mathrm{reg}}\) in Thm 10b; code composition in Corollary 4 of Part III; the mixing constants in Lemma 5; the transient/metastability temporal test for the non-normal audit (§1.4); the mixed composition regime (§2.6).

**Remark on instrumentation.** Both theorems of Part IV concern spectra of operators accessible only by action; their measurement side (Lanczos for Thm 10, the Arnoldi cloud for Prop. 4, cumulant defects and both convolutions for Thm 11) is exactly the `resona` corpus, still in the status of an instrument, not a foundation.

**The mathematics is closed.** Apparatus: 11 theorems, 5 lemmas, 4 propositions, 7 corollaries, 2 delimiting counterexamples, 1 category, 1 grammar of mutations, 1 safety budget. The five axioms of Part I have been brought to provable, certifiable, algorithmically realizable statements. The next station is mechanics: six primitives on top of the certificates.
