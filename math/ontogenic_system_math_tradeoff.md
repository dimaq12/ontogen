# Part VII. Reforging Theorem 12: Hierarchy–Time–Nonlocality

This is not a new chapter but the execution of the verdict of the third revision: **take only Theorem 12 and turn it into one iron thing**. All three attacks of the revision are accepted:

- 12(a) in the claimed generality is **false** — the counterexample with a replicated bit is valid; the theorem is reformulated through *live semantics*.
- 12(d) proved the depth of a computational circuit, not the depth of emergent levels; the correct object is the **three-currency tradeoff** (depth / time / range).
- 12(b) cannot be closed by the words "reduction to the BPT"; below is a **self-contained proof of its own** (with a weaker exponent, which, however, suffices for the needed corollary).

Plus three accepted minor edits: a fragility vector instead of a scalar, normalization of \(\Gamma\), a ladder of generality for the survival theory.

The single instrument of the whole part is the **dependency cone** in GL geometry with a tower.

---

# 1. The dependency-cone model

**Objects.** Cells \(V\) in GL\((D,r_0)\) geometry (bounded density: \(\le c_0\) cells per \(r_0\)-ball). A tower of macro-entities: a macro of level \(\ell\) has \(\le k\) children of level \(\ell-1\) (cells are level 0), and **geometric coverage**: all cells under a macro of level \(\ell\) lie in a ball of diameter \(\rho_\ell\le r_0\,s^{\ell}\) (\(s\) — the coverage factor per level). Maximal depth \(L\).

**Channels (physicality of coupling).** Per step an object reads: a cell — the cells within radius \(R\) (base range; in pure GL \(R=r_0\)) and the incident macros; a macro — its children and its parent. All channels are physically realized in the geometry (a macro's cache is materialized in the cells of its region; there are no ethereal links) — this is honest GL.

**Cone.** \(\mathcal D(v,0)=\{v\}\), \(\mathcal D(v,t+1)=\mathcal D(v,t)\cup\bigcup_{u\in\mathrm{nbr}(v)}\mathcal D(u,t)\). The system output is a distinguished object \(o\); the value computed at time \(T\) can depend only on inputs injected into cells from \(\mathcal D(o,T)\).

**Definition 14 (live semantics).** The global semantics \(y_t\) is **live with horizon \(T\)** if \(y_t\) is obliged to depend on fresh inputs (injected no earlier than \(t-T\)) in \(\Omega(N)\) distinct cells. (Static memory — dependence only on old inputs — is not live.)

**Lemma A (fan-in ceiling).** \(|\mathcal D(o,T)|\le(\Delta+1)^T\), where \(\Delta=\max(k+1,\ c_0(R/r_0)^D)\) is the maximal degree.

*Proof.* Induction on \(t\). ∎

**Lemma B (displacement ceiling).** Every cell in \(\mathcal D(o,T)\) lies in a ball of radius \(T\cdot\max(R,\ r_0s^{L})\) around the position of \(o\); therefore

\[
|\mathcal D(o,T)\cap V|
\;\le\;
c_0\Big(T\cdot\max\big(\tfrac{R}{r_0},\,s^{L}\big)\Big)^{D}.
\]

*Proof.* One hop displaces along the geometry by at most \(R\) (cellular) or by \(\rho_L\le r_0s^L\) (a jump through a macro: child→parent→another child — within the coverage). Induction on hops; counting cells in a ball — bounded density. ∎

---

# 2. Theorem 13 (Hierarchy–Time–Nonlocality Tradeoff)

**Theorem 13.** Let a system in the model of §1 support live global semantics with horizon \(T\). Then simultaneously:

**(a) Absolute floor (no architecture is faster than the log):**

\[
T\;\ge\;\frac{\log(cN)}{\log(\Delta+1)} .
\]

**(b) Three-currency budget:**

\[
\boxed{
L\log s\;+\;\log T\;+\;\log\frac{R}{r_0}
\;\ge\;
\frac1D\log(cN)\;-\;O(1).
}
\]

**(c) Corollaries by regime:**

| regime | price |
|---|---|
| flat and local (\(L=0\), \(R=r_0\)) | \(T\ge(cN)^{1/D}\) — polynomial time (light cone) |
| fast time (\(T=\mathrm{polylog}\,N\)) | \(L=\Omega\big(\frac{\log N}{D\log s}\big)\) **or** \(R\ge r_0N^{\Omega(1/D)}\) |
| no depth, but fast | \(R\ge r_0 N^{\Omega(1/D)}\) — long-range links as a currency |

*Proof.* (a) — Lemma A and \(|\mathcal D|\ge cN\). (b) — Lemma B: \(c_0\big(T\max(R/r_0,s^L)\big)^D\ge cN\), taking logarithms, \(\max\le\) the product. (c) — substitutions. ∎

\[
\boxed{
\textbf{To support live semantics from }\Omega(N)\textbf{ degrees of freedom,}\\
\textbf{a system with bounded local computation pays with at least one currency:}\\
\textbf{depth of hierarchy, propagation time, or range of links.}
}
\]

**Fate of 12(d).** Withdrawn toward strengthening: the old \(k^L\ge cN\) is a special case of (b) under the requirement of instantaneous representation (\(T=O(L)\)). The revision's counterexample (a global average by gossip) is legalized and situated: it is the "flat and local" regime, honestly paying \(T=\Theta(N^{1/D})\). A deep ontology is not the only way out; it is a **purchase of time**: the system chooses whether to keep the map of the world deep and fresh or flat and lagging. The separation of timescales across levels (Part V) is a consequence of the same budget.

---

# 3. Repair of 12(a): memory lives without coupling, live semantics does not

**The revision's counterexample is accepted.** A replicated bit (`LEFT=1, RIGHT=1`) survives eternal erasure of the separator: storing an already-agreed coupling semantics requires no coupling. The error of the old proof: the move "let the halves encode different values" is illegal for an adversary erasing only the separator from a legal agreed state.

**Theorem 12a′ (live semantics requires causal coupling).** Let an adversary with a budget of \(\omega\big(r_0N^{(D-1)/D}\big)\) erased cells per step keep a separating layer erased (GL isoperimetry, Part V). Then no architecture supports live (Def. 14) global semantics depending on fresh inputs **on both sides** of the cut: for any output \(o\) and any \(T\) the fresh part of \(\mathcal D(o,T)\) lies on one side of the layer.

*Proof.* All channels are physical (§1), every channel through the layer passes through erased cells and transmits nothing while the layer is erased; a dependency cone starting after the onset of the attack does not cross the layer. Dependence on fresh inputs of the far side is impossible; static copies (dependence on pre-attack inputs) are possible, which is exactly what the counterexample shows. ∎

\[
\boxed{
\text{The separator kills not memory but agreement:}\quad
\text{dynamic global semantics}\Rightarrow\text{causal communication.}
}
\]

This is stronger and more correct than the old 12(a): it is now homogeneous with Theorem 13 (the same cone), and both speak of one thing — the **price of life**, not the price of storage.

---

# 4. Repair of 12(b): a proof of its own instead of a citation

The revision's demand: do not close by "reduction to the BPT." Below is a self-contained proof of a weaker bound, which suffices for the "flat death" corollary. Class: linear codes over \(\mathbb F_2\), the checks being linear functionals with support of diameter \(\le r_0\) in GL\((D,r_0)\).

**Lemma C (small is correctable).** Every \(A\) with \(|A|<d\) is correctable under erasure: a nonzero codeword with support in \(A\) would have weight \(<d\).

**Lemma D (union).** If \(A,B\) are correctable and \(\operatorname{dist}(A,B)>r_0\), then \(A\cup B\) is correctable.

*Proof.* Let a codeword \(c\) have support in \(A\cup B\). Any check \(\varphi\) touches at most one of \(A,B\). If \(\varphi\) touches \(A\): \(\varphi(c|_A)=\varphi(c)-\varphi(c|_B)=0-0=0\) (the support of \(\varphi\) does not meet \(B\)); if it does not touch \(A\): \(\varphi(c|_A)=0\) trivially. Hence \(c|_A\) is a codeword with support in \(A\), equal to zero by correctability of \(A\); symmetrically \(c|_B=0\). ∎

**Theorem 12b′ (flat price, self-contained).** For any such code

\[
\boxed{
k\cdot d^{1/D}\;\le\;4D\,r_0\,N .
}
\]

*Proof.* Let \(w=\lfloor(d-1)^{1/D}\rfloor\ge2r_0\) (otherwise \(d\le(4r_0)^D=O(1)\) and the claim is trivial). Tile the support with cubes of side \(w\), separated by corridors of width \(2r_0\). Each cube contains \(\le w^D\le d-1\) cells — correctable (Lemma C); the cubes are pairwise separated by \(>r_0\) — their union \(R\) is correctable (iteration of Lemma D). Correctability of \(R\) means: the projection of the code onto the complement of \(R\) is injective (two words agreeing outside \(R\) differ by a word with support in \(R\), i.e. by zero), whence \(k\le N-|R|\). Coverage fraction: \(|R|/N\ge\big(\tfrac{w}{w+2r_0}\big)^D\ge1-\tfrac{2Dr_0}{w}\), so \(k\le\tfrac{2Dr_0}{w}N\le\tfrac{4Dr_0}{d^{1/D}}N\). ∎

**Corollary 8 (flat death, now its own).** At constant semantic density \(k=hN\): \(d\le(4Dr_0/h)^D=O(1)\) — a flat GL system of constant density does not survive even a constant number of adversarial corruptions. Exactly what was required for Theorem 12(b), **without external references**.

**What remains of the old statement.** The sharper exponent \(k\,d^{1/(D-1)}\le O(N)\) — status: known for the BPT class, not proved in our formalism; flagged as a task (interest: exact sharpness — the question of whether anisotropy of the predicates helps). It is not needed for Corollary 8. Nonlinear predicates — open; Lemmas C–D are essentially linear.

---

# 5. Accepted minor edits

## 5.1. Fragility vector

The scalarization \(\kappa_{\mathcal L}=\max\{\dots\}\) (Part V §2) is a premature merger. The canonical form is a vector:

\[
\boxed{
\boldsymbol\kappa_{\mathcal L}
=(\kappa_{\mathrm{id}},\ \kappa_{\mathrm{transient}},\ \kappa_{\mathrm{pseudo}})
}
\]

(conditioning of identification ✦2 / power-law majorant of the loop ✦5 / pseudospectral swelling with \(\sigma_{\min}(T)\), Part VI §2.2). Each theorem takes its own coordinate. The scalar norm \(\|\boldsymbol\kappa\|_*\) is introduced only if relations between the coordinates are proved; "all three are non-normality" remains a motif, not a theorem. Hypothesis for the registry: inequalities between the coordinates (for instance, \(\kappa_{\mathrm{transient}}\le f(\kappa_{\mathrm{id}})\) on the class of diagonalizable \(G\)).

## 5.2. Normalization of \(\Gamma\)

The dedimensionalization is accepted:

\[
\gamma_{\mathrm{int}}
=\frac{\operatorname{cut}_K(A,B)}{\min(\operatorname{vol}A,\operatorname{vol}B)}\in[0,1],
\qquad
\gamma_{\mathrm{align}}
=\frac{\Delta_{\mathrm{free}}(p)}{\Delta_{\mathrm{free}}(p)+B_p}\in[0,1),
\]

(\(B_p\) — the natural cumulant scale from Lemma 7). The plane \(\Gamma\in[0,1]^2\); "small/large" from Part VI become regions with thresholds from the tolerances of Theorems 11a/11b′ — the quadrants are now mathematical, not intuitive.

## 5.3. Ladder of generality for the survival theory

Accepted: the base domain of Part VI is **finite irreducible reversible chains** (there the existence of Perron, the QSD, and all items of Lemma 6 are unconditional facts). Extensions by program, each with its own conditions: finite → countable (recurrence conditions) → compact positive operators (Krein–Rutman) → Polish spaces (Doeblin/minimization conditions). The statements of Part VI are considered proved in the base and claimed in the extensions.

---

# 6. Status

**The central result of the corpus** is henceforth Theorem 13 (three currencies) together with 12a′ (live semantics) and 12b′/Corollary 8 (flat death, self-contained): one machine (the dependency cone) yields all three. The former "necessity of hierarchy" was its projection onto the case where paying with time and range is forbidden.

**Updated task list v1** (replacing the list of Part VI):

1. **Survival-spectrum**: adversarial starts without uniform hazard (or an impossibility theorem); the irreversible case; sharpness of the constants. Base — finite reversible chains (§5.3).
2. **Spectral identifiability**: when the compatibility test 7′ becomes identification.
3. **Mixed calculus**: a fusion certificate when both \(\Gamma\) coordinates are large.
4. **Sharpness of 12b′**: the exponent \(1/(D-1)\) in our formalism; nonlinear predicates.
5. **Relations of the \(\boldsymbol\kappa\) coordinates**: inequalities justifying (or forbidding) scalarization.

Not a single new mechanism has been added: Part VII only narrowed and reinforced. The next move per the revision plan is to strike at tasks 1–3, without expanding the corpus.
