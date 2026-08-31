# Part V. Polishing and the Theorem on the necessity of hierarchy

The status of the corpus changes: not «the apparatus is finished off» but a **working theory under polishing**. Part V does two things:

1. **Corrections** — eight concrete places in Parts III–IV where the statement was stronger than the proof (following the review; each correction is marked ✦N by the number of the remark).
2. **Narrowing and deepening**: the core of the theory is reassembled into four components, and from them the central result is proved (within honestly stated limits) — the **Theorem on the necessity of hierarchy**: under physical locality and the bounded context of the computer, hierarchy is not convenient but mathematically inevitable.

---

# 1. Corrections

## ✦1. Theorem 2′: two certificates instead of one norm

In Part III the left-hand side of the equality (the vector defect) and the right-hand side (the operator norm) were of different types. The correction — **two** defects:

\[
\eta_{\mathrm{op}}
:=\sup_{\substack{\psi\in W_m\\\|\psi\|=1}}
\big\|(\mathcal U-\widehat{\mathcal U})\psi\big\|_{L^2(\mu)}
=\big\|(\mathcal U-\widehat{\mathcal U})\big|_{W_m}\big\|,
\qquad
\eta_{\mathrm{rms}}
:=\Big(\tfrac1m\textstyle\sum_{i=1}^m\|(\mathcal U-\widehat{\mathcal U})\psi_i\|^2\Big)^{1/2},
\]

with the relation \(\eta_{\mathrm{rms}}\le\eta_{\mathrm{op}}\le\sqrt m\,\eta_{\mathrm{rms}}\). The worst direction and the average coordinate are different promises: \(\eta_{\mathrm{op}}\) feeds Lemma 1 (accumulation) and Theorem 7 (the loop), \(\eta_{\mathrm{rms}}\) feeds the MDL accounting and monitoring. The level certificate from now on carries both.

## ✦2. Davis–Kahan honestly: a conditioning parameter

The EDMD matrix is in general non-normal; a single gap \(g\) is not enough — a small perturbation can move the invariant subspaces strongly when the eigenvectors are poorly conditioned. Lemma 5 is rewritten in Stewart's form: if \(\operatorname{sep}(\widehat{\mathcal U}|_{W_m},\widehat{\mathcal U}|_{W_m^\perp})=s>0\) and \(\|E\|<s/4\), then

\[
\|\sin\Theta\|\;\le\;\frac{2\,\kappa_{\mathrm{id}}\,\|E\|}{s},
\]

where \(\kappa_{\mathrm{id}}\) is the conditioning of the basis of the invariant subspace (in the normal case \(\kappa_{\mathrm{id}}=1\), \(s=g\) — the old form is recovered). The conceptual upshot, which the critique correctly named a new parameter:

\[
\boxed{
\text{level quality}
=
\text{small residual}
+\text{spectral separation}
+\text{conditioning}.
}
\]

A level can be **predictively good but fragilely identifiable** — this distinction is now visible in the certificate (see §2).

## ✦3. DKW: two theorems instead of a universal \(M_{\mathrm{eff}}\)

The replacement \(M\to M_{\mathrm{eff}}\) in Part III was not a consequence of DKW — it is retracted. The correct pair:

**Theorem 8a (i.i.d.).** For an independent sample of defects — the rigorous DKW with Massart's constant: \(\mathbb P\big(\sup_t|\widehat F_M(t)-F(t)|>\epsilon\big)\le2e^{-2M\epsilon^2}\).

**Theorem 8b (dependent trajectory).** Suppose the series of defects is \(\beta\)-mixing with coefficients \(\beta(b)\). The blocking technique (Yu): for block length \(b\) and number of blocks \(\lfloor M/b\rfloor\)

\[
\mathbb P\Big(\sup_t|\widehat F_M(t)-F(t)|>\epsilon\Big)
\;\le\;
2\exp\big(-2\lfloor M/b\rfloor\,\epsilon^2\big)
\;+\;
2\,\tfrac{M}{b}\,\beta(b),
\]

with optimization over \(b\). The level certificate in the dependent regime must carry \((b,\beta(b))\) — i.e. **an estimate of the mixing rate of the subsystem**, which is meaningful: mixing is anyway a dynamical property that EMERGE observes.

## ✦5. Theorem 7′: the spectral radius is not enough to bound the error

The stability criterion \(\rho(M)<1\), \(M=(1-\beta)(A-\alpha\gamma I)\) is correct and remains. But the bound \(\limsup\|e_t\|\le u_{\max}/(1-\rho(M))\) in an arbitrary norm does not follow from \(\rho(M)\) alone: for a non-normal \(M\) the transient amplifications can be enormous. The honest form — via a power-law majorant:

\[
\|M^k\|\le C_M\,r^k\ (r<1)
\quad\Longrightarrow\quad
\limsup_t\|e_t\|
\;\le\;
\frac{C_M}{1-r}\,u_{\max},
\qquad u_{\max}=(1-\beta)\eta+\beta\sigma .
\]

The pair \((C_M,r)\) (equivalently, the Kreiss constant of \(M\)) enters the loop certificate. When \(\|M\|<1\) the simple version \(C_M=1\), \(r=\|M\|\) works.

## ✦6. MDL: correction of the constants

From \(|\widehat{\mathrm{DL}}_i-\mathrm{DL}|\le c\) follows \(|\Delta\widehat{\mathrm{DL}}_i-\Delta\mathrm{DL}|\le2c\), and **between two proxies** — \(4c\), not \(2c\). The corrected bands: the proxy's decision agrees with the sign of the ideal \(\Delta\mathrm{DL}\) when \(|\Delta\mathrm{DL}|>2c\); two proxies are guaranteed to agree when the observed margin is \(>4c\). The hysteresis acceptance norm: accept when \(\Delta\widehat{\mathrm{DL}}<-2c\) (this still guarantees \(\Delta\mathrm{DL}<0\)), the waiting band is widened to \([-2c,+2c]\), the inter-proxy invariance — from \(4c\).

## ✦7. Cancer: what is already closed by Part IV, what remains open

The remark about the sweep («it will find *some* cut, not necessarily crossing \(B\)») is valid against Proposition 3 of Part III — and Proposition 3 is **retracted in favor of Theorem 10** of Part IV, which is free of this defect: detection proceeds not by the graph \(K\) but by the operator (the escape rate), and not by a single sweep but by **iteration with deflation**: the found \(S\) is processed (registered or destroyed), its mode is deflated, the audit is repeated; as long as \(B\) is unexplained, its mode \(\ge1-4\varepsilon\) remains in the unexplained spectrum (Thm. 10a) and surfaces within a finite number of rounds (the slow modes are finitely many). The second half of the remark is **correct and accepted**: the compressibility of the macro-dynamics does not entail a small conductance in \(K\); dynamical autonomy and topological separatedness are different things (this is why Part IV moved from \(K\) to the operator). The open problem is recorded:

\[
\boxed{
\text{When does predictive closure}\Rightarrow\text{a detectable structural bottleneck?}
}
\]

## ✦8. An example: achievability ≠ necessity

The phrase «a rate-1/2 code by Thm. 5′-b withstands \(\rho=1/4\)» was an error of direction: Thm. 5′-b is a **necessary** condition (the ceiling \(\rho\le1/4\)), not achievability. The correction: a Sipser–Spielman code is taken with expansion parameters giving a **proved** correction radius \(\rho_0\) (a constant, strictly less than the ceiling); the example features \(\rho_0\), and the ceiling 1/4 is mentioned as an upper bound from 5′-b.

## ✦4. Corollary 4 retracted

The most serious one. Corollary 4 of Part III («a flat system cannot maintain integrity») is **refuted by its own Theorem 4′′′**: an expander code gives bounded degree, local checks, a constant rate, and correction of a constant fraction of damage for arbitrarily large \(N\). The growth of \(N\) by itself does not force a hierarchy. The missing link is a physical postulate; §3 is devoted to it and to the main result.

---

# 2. The fragility \(\kappa\): one parameter, three appearances

Corrections ✦2 and ✦5 introduce seemingly different corrections — the conditioning of identification and the transient amplification of the loop. Part IV (§1.4) added a third: the pseudospectral visibility in the non-normal audit. This is not a coincidence: all three are manifestations of the **non-normality** of the respective operator. A single certificate parameter is introduced:

\[
\boxed{
\kappa_{\mathcal L}
:=
\max\Big\{
\underbrace{\kappa_{\mathrm{id}}}_{\text{conditioning of }W_m},\;
\underbrace{C_M}_{\text{loop transients}},\;
\underbrace{\sup_{\varepsilon}\tfrac{\rho_\varepsilon(G)-\rho(G)}{\varepsilon}}_{\text{pseudospectral inflation}}
\Big\}
}
\]

— the **dynamical fragility of the level**. The normal world: \(\kappa_{\mathcal L}=O(1)\), all theorems in simple form. The non-normal one: every guarantee is multiplied by \(\kappa_{\mathcal L}\), and a level with a large \(\kappa\) is legitimate but flagged: fragilely identifiable, prone to transients, requiring a pseudospectral audit. The substantive interpretation: non-normality = a hidden asymmetric feedback; fragility is its price, and it is now **one for all three theorems**.

The full level certificate after Part V:

\[
\mathcal L
=
\big(A,\ \pi,\ G,\ \eta_{\mathrm{op}},\ \eta_{\mathrm{rms}},\ q,\ \delta,\ M,\ (b,\beta(b)),\ L,\ s,\ \kappa_{\mathcal L}\big).
\]

---

# 3. The theorem on the necessity of hierarchy

## 3.1. The missing postulate

**(GL) Geometric locality.** Entities are embedded in a metric space of fixed doubling dimension \(D\) with bounded density; every interaction, check, and repair action has radius \(\le r_0\); the capacity of a cell is bounded by \(b\) bits.

This is a postulate about the *physics of the substrate* — stronger than (L1)–(L3) of Part III: there exponential decay was allowed (so an expander with long rare edges was legal), here there are no long-range edges at all. An expander does not embed into GL-geometry: for a ball in dimension \(D\) the boundary is small relative to the volume, whereas expansion requires the opposite. It is exactly this conflict — **the locality of physics versus the globality of integrity** — that generates the main result.

## 3.2. Statement

**Theorem 12 (necessity of hierarchy).** In the class of GL-systems with \(N\) cells:

**(a) Absolute ceiling (no-go for all).** No architecture — flat or hierarchical — preserves globally-consistent semantics against an adversary that erases \(\omega\big(r_0\,N^{(D-1)/D}\big)\) cells per tick.

**(b) Flat death.** For flat systems (the legal set given by predicates of radius \(\le r_0\), the linear class) a bound of Bravyi–Poulin–Terhal type holds:

\[
H(y)\cdot d^{\,1/(D-1)}\;\le\;C(r_0,D)\,N,
\]

whence, at constant semantic density \(H(y)=\Theta(N)\), the code distance \(d=O(1)\): a flat GL-system of constant density does not survive even a **constant number** of adversarial corruptions.

**(c) Hierarchical rescue.** There exist hierarchical constructions (depth \(\Theta(\log N)\), on each level — checks and repair local at their own scale) with \(H(y)=\Theta(N/\mathrm{polylog}\,N)\) that preserve the semantics for an unbounded time under independent noise of intensity \(\rho\le\rho_0\) with continuous repair.

**(d) Depth is forced.** In the ontogenic formalism (levels with bounded context \(k\) — Theorem 3) every tower whose top level certifies semantics depending on \(\Omega(N)\) cells has depth

\[
L\;\ge\;\frac{\log(cN)}{\log k}\;=\;\Omega(\log N).
\]

The hierarchy lives in the gap between two impossibilities: below the ceiling (a), above the flat death (b) — and only there.

## 3.3. Proofs

**(a).** GL isoperimetry: a hyperplanar layer of thickness \(r_0\) across the substrate contains \(O(r_0N^{(D-1)/D})\) cells (bounded density) and separates the system into two halves between which there is not a single interaction (radius \(\le r_0\)). The adversary erases the layer every tick. The state factorizes: no predicate crosses the cut (locality of predicates), no repair action carries information across it. Let the halves be in locally-legal states encoding different values of the global consistent bit: no predicate outside the erased layer is violated, the repair does not fire, the mismatch is eternal; a decoder obliged to output a single \(y\) cannot be correct for both halves. ∎

**(b).** A reduction to the Bravyi–Poulin–Terhal bound for geometrically local classical codes (the «cleaning» technique: partitioning the substrate into cubes of side \(\sim d^{1/(D-1)}\); the logical information is pushed out of the cubes whose boundaries are small relative to the distance, which yields \(k\,d^{1/(D-1)}\le CN\)). At \(k=H(y)=hN\): \(d\le(C/h)^{D-1}=O(1)\). By Thm. 5′-b adversarial robustness requires \(d>2\rho N\) — at constant \(\rho\) a contradiction already at \(N>d/2\rho\). *A note on rigor:* the bound is proved for linear local checks; the nonlinear generalization is expected but not written out — recorded in the registry.

**(c).** A reduction to Gács's construction (a reliable one-dimensional cellular automaton under i.i.d. noise — a hierarchy of simulated levels with repair at every scale) and to multiscale renormalization codes: each stage repairs the «droplets» of damage of its own scale, passing upward only the unrepaired part; the polylog price is for the layering of levels. Essentially: Gács's construction is *exactly* an ontogenic tower that arose as a response to noise, which makes it not a borrowing but the first historical instance of our object. *A note:* the noise model is random; against an unbounded adversary no one has a defense — item (a).

**(d).** The top macro \(y_{\mathrm{top}}\) with \(H(y_{\mathrm{top}})=\Theta(N)\) cannot depend on \(o(N)\) cells. Each level is a composition of maps with fan-in \(\le k\) (Theorem 3 on bounded context: a larger fan-in is forbidden by the computer itself). A composition of \(L\) layers of fan-in \(k\) depends on at most \(k^L\) inputs; \(k^L\ge cN\) gives \(L\ge\log(cN)/\log k\). ∎

An addendum (light cone): regardless of depth, one cycle of global consensus takes time \(\ge\operatorname{diam}/r_0=\Omega(N^{1/D})\) ticks — the pace of life of the upper levels is forcibly slower than that of the lower ones. **The separation of time scales of a hierarchy is also a theorem, not an observation.**

## 3.4. What this changes

Before Part V the hierarchy was a *possibility* (the Recursive universality axiom + convenience). Now:

\[
\boxed{
\textbf{GL-physics}+\textbf{bounded context}+\textbf{integrity at }H(y)=\Theta(N)
\;\Longrightarrow\;
\textbf{certified macro-levels of depth }\Omega(\log N).
}
\]

`emerge` is not an expressive feature of the language but a **necessary computational primitive of scalable systems**: any other language solving the same task in the same physics is obliged to contain its functional equivalent, explicitly or by smuggling. The division of labor among the theorems: (b) says that without mediators it is impossible; (d) — how many mediators at minimum; (a) — that even with mediators there is a physical ceiling; (c) — that the gap is non-empty.

*Limitations honestly:* (b) — the linear class; (c) — random noise (the adversarial case runs into (a)); the full nonlinear/adversarially-graded version is the main remaining goal of the core.

---

# 4. Reassembly of the core

As a result of the polishing the theory narrows down to four components (everything else is scaffolding):

\[
\boxed{\text{Local generative dynamics}}
\;+\;
\boxed{\text{Certified coarse-graining}}
\;+\;
\boxed{\text{Local semantic repair}}
\;+\;
\boxed{\text{Bounded mediation}}
\]

and one central result — Theorem 12, which links them by necessity. The correspondence map: the dynamics — Parts I–II; coarse-graining with the certificate \((\eta_{\mathrm{op}},\eta_{\mathrm{rms}},q,\delta,(b,\beta),s,\kappa)\) — Pillar 1 + ✦1–✦3 + §2; the repair — Pillar 3 (+ ✦8); the mediation — Pillar 2 + GL + Thm. 12. Pillars 4–5 (mutations, alignment) are operational consequences of the core, their theorems are not touched by the polishing, except ✦5–✦6.

# 5. Registry after Part V

**Corrected and rigorous:** ✦1 (two defects), ✦3 (8a rigorous; 8b under explicit \(\beta\)-mixing), ✦5 (the power-law majorant), ✦6 (the constants of the bands), ✦8 (the radius \(\rho_0\) instead of the ceiling), Thm. 12a (full proof), Thm. 12d (full proof).

**Rigorous under a stated class:** ✦2 (Stewart's form; the constants \(\kappa_{\mathrm{id}}\) — the standard of perturbation theory), Thm. 12b (linear local checks; reduction to BPT), Thm. 12c (random noise; reduction to Gács).

**Retracted:** Corollary 4 of Part III (in favor of Thm. 12), Proposition 3 of Part III (in favor of Thm. 10 of Part IV), the universal \(M_{\mathrm{eff}}\) of Part III.

**Open (core):** (i) «predictive closure ⇒ a structural bottleneck?» (✦7); (ii) the nonlinear version of Thm. 12b; (iii) the adversarially-graded Thm. 12c (the adversary's budget between random noise and the ceiling (a)); (iv) the mixed composition regime (Part IV §2.6); (v) the temporal transient/metastability test (Part IV §1.4).

Status: **a working theory with one central result and five open core problems.** We no longer grow in breadth.
