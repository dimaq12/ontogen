# Part VI. The survival spectrum and the geometry of relations

A response to the second review (Parts IV–V). The review's verdict is accepted almost in full; the main points:

- **The red zone is confirmed.** The transition «\(\varepsilon(S)>c\Rightarrow\mathbb E[\tau_S]<1/c\)» was wrong (a sticky core inside a leaky \(S\)); Corollary 6 (the safety budget) is **retracted** and reproved on the correct object — the **killed operator**. «Spectral forensics» is **demoted** from a corollary to a compatibility test of models.
- The finale's formula is officially changed: **«The main conjectures have not vanished; they have decomposed into more precise statements.»**

Structure: §1 — the survival theory (replacing the false budget with a rigorous one); §2 — precise formulations of 10(b) and the pseudospectrum; §3 — the object \(\Gamma(A,B)\), the repair of the constants in 11b, fixing the model in 11a, the four-regime table; §4 — the three open problems of v1 and status.

---

# 1. The survival spectrum: hazard as an object

## 1.1. Why conductance is not the lifetime

\(\varepsilon(S)=Q(S,S^c)/\mu(S)\) is the *average* one-step leakage on a start from the stationary slice \(S\). A small \(\varepsilon\) gives retention over times \(\sim1/\varepsilon\); but a large \(\varepsilon\) does **not** give a fast exit: if \(S=S_{\text{sticky}}\cup S_{\text{leaky}}\), the average over \(S\) is large, while trajectories that have fallen into the sticky core live arbitrarily long. Conductance is an averaged, not a worst-case, characteristic.

## 1.2. The killed operator

**Definition 12.** For a measurable \(S\):

\[
P_Sf:=\mathbf 1_S\,P(\mathbf 1_Sf),
\qquad
\rho_S:=\rho(P_S)
\]

— the **killed operator** and its spectral radius (in the reversible case \(P_S\) is self-adjoint, \(\rho_S=\lambda_{\max}(P_S)\)). The survival time \(\tau_S=\min\{t:X_t\notin S\}\).

**Definition 13 (hazard).**

\[
\boxed{
\mathcal D(S):=\frac{1}{1-\rho_S}
}
\]

— the expected lifetime on a start from the quasi-stationary distribution (item (iii) below). Hazard is **monotone**: \(S'\subset S\Rightarrow\rho_{S'}\le\rho_S\) (a supremum over a smaller class of supports) — a sticky core always drags hazard into the enveloping set; this is exactly what broke the old budget.

**Lemma 6 (properties).** In the reversible case:

1. \(\rho_S=\sup\{\langle Pf,f\rangle/\|f\|^2:\ \operatorname{supp}f\subset S\}\ \ge\ 1-\varepsilon(S)\) (substituting \(f=\mathbf 1_S\)); hence \(\mathcal D(S)\ge1/\varepsilon(S)\): **conductance is a cheap one-sided certificate of hazard** (a lower bound), not its measure.
2. For a start \(\nu\) with density \(g=d\nu/d\mu\), \(\operatorname{supp}g\subset S\):
\[
\mathbb P_\nu(\tau_S>t)\;=\;\langle g,\,P_S^{\,t}\mathbf 1_S\rangle_\mu\;\le\;\|g\|_{L^2(\mu)}\sqrt{\mu(S)}\;\rho_S^{\,t},
\qquad
\mathbb E_\nu[\tau_S]\;\le\;\frac{\|g\|_{L^2}\sqrt{\mu(S)}}{1-\rho_S}.
\]
3. The quasi-stationary distribution \(\nu_{\mathrm{qsd}}\propto\varphi\,d\mu\) (\(\varphi\ge0\) is the Perron eigenfunction of \(P_S\)) gives the exact geometry: \(\mathbb P_{\mathrm{qsd}}(\tau_S>t)=\rho_S^{\,t}\), \(\mathbb E_{\mathrm{qsd}}[\tau_S]=1/(1-\rho_S)\).
4. **Uniform hazard**: if \(\inf_{x\in S}P(x,S^c)\ge h\), then \(\sup_x\mathbb P_x(\tau_S>t)\le(1-h)^t\) and \(\rho_S\le1-h\) — the only regime that gives pointwise (adversarial-in-the-start) guarantees.

*Proofs.* (1) — substitution and the variational principle; (2) — \(\mathbb P_\nu(\tau>t)=\mathbb E_\nu\prod_{k\le t}\mathbf 1_S(X_k)\), expressed through \(P_S^t\), Cauchy–Schwarz, summing the geometric series; (3) — the spectral decomposition of \(P_S\); (4) — step-by-step majorization. ∎

## 1.3. Theorem 10a′: a formulation via survival (and a better constant)

**Theorem 10a′.** Let \(S\) be a region with \(\rho_S\ge1-h\), let \(\varphi\) be its Perron function (extended by zero, \(\|\varphi\|=1\)), and let the region be **unexplained**: \(\|\varphi_\perp\|^2\ge\tfrac12\) (the projection outside \(V_{\mathrm{reg}}\)). Then

\[
\boxed{
\lambda_{\max}\big(P\big|_{V_{\mathrm{reg}}^\perp}\big)\;\ge\;1-2h .
}
\]

*Proof.* \(\varphi\) is concentrated in \(S\), hence \(\langle P\varphi,\varphi\rangle=\langle P_S\varphi,\varphi\rangle=\rho_S\ge1-h\). The decomposition \(\varphi=\varphi_{\mathrm{reg}}+\varphi_\perp\) and the invariance of \(V_{\mathrm{reg}}\):
\(\langle P\varphi_\perp,\varphi_\perp\rangle\ge(1-h)-\|\varphi_{\mathrm{reg}}\|^2=\|\varphi_\perp\|^2-h\),
whence the Rayleigh quotient on \(V_{\mathrm{reg}}^\perp\) is at least \(1-h/\|\varphi_\perp\|^2\ge1-2h\). ∎

Replacing the indicator with the Perron function **improved the constant** (it was \(1-4\varepsilon\) by conductance, it became \(1-2h\) by survival) and, above all, tied visibility to the correct quantity: not to the average leakage, but to the survival spectrum. The review's formula is accepted as canonical:

\[
\boxed{
\text{unexplained metastability}\;\Longrightarrow\;\text{unexplained slow mode,}
}
\qquad
\text{metastability}:=\rho_S .
\]

## 1.4. The safety budget: retraction and re-proof

The old Corollary 6 is **retracted** (its derivation relied on the false transition). The new version:

**Corollary 6′ (the budget, honest domain of applicability).** Suppose the audit is clean at resolution \(\varepsilon_a\): \(\lambda_{\max}(P|_{V_{\mathrm{reg}}^\perp})<1-\varepsilon_a\). Then every region \(S\) whose Perron function is unexplained (\(\|\varphi_\perp\|^2\ge\tfrac12\)) has \(\rho_S<1-\varepsilon_a/2\) (the contrapositive of 10a′), and:

1. **\(L^2\)-starts:** for any initial \(\nu\) with \(\|d\nu/d\mu\|_{L^2}\le C_\nu\):
\[
\mathbb E_\nu[\tau_S]\le\frac{2C_\nu\sqrt{\mu(S)}}{\varepsilon_a},
\qquad
\mathbb E_\nu[\text{harm}]\le\frac{2C_\nu h_{\max}}{\varepsilon_a}.
\]
2. **Adversarial starts** (the adversary picks the point): a guarantee only under uniform hazard (Lemma 6.4); without it there is **no** pointwise budget, and this is not a gap in the proof but the actual state of affairs — a sticky core with tiny mass is invisible to the \(L^2(\mu)\)-theory. Auditing adversarial starts is a separate mechanism (for example, hazard-predicates in contracts: each cell locally certifies its own leakage).

*Proof.* (1) — Lemma 6.2 with \(1-\rho_S>\varepsilon_a/2\); (2) — Lemma 6.4. ∎

A remark on the second half of the condition: a region whose Perron function is explained (\(\varphi\) lies mostly in \(V_{\mathrm{reg}}\)) is by definition metastability already described by the registered levels; it is not an «invisible cancer» but accounted-for dynamics.

---

# 2. Precise formulations: 10(b) and the pseudospectrum

## 2.1. 10(b): to find is not to classify

Accepted: a sweep over the eigenfunction \(u\perp V_{\mathrm{reg}}\) yields a set \(S\) with \(\varepsilon(S)\le\sqrt{2g}\), but the indicator of the found \(S\) is **not obliged** to remain orthogonal to \(V_{\mathrm{reg}}\). The canonical formulation:

\[
\text{unexplained slow mode}
\;\Longrightarrow\;
\text{a metastable region exists}
\quad(\textbf{without the label «unregistered»}).
\]

The label is assigned by the next step of the pipeline: EMERGE-certification of \(S\) and a check against the registry/contracts (step 2 of the AUDIT algorithm) — this check is decidable, and the algorithm of Part IV, as noted in the review, already does the right thing; only the caption under the theorem was wrong. The completeness guarantee of the iteration is preserved: as long as an unexplained sticky region exists, Theorem 10a′ keeps its mode in the unexplained spectrum, and deflation over a finite number of rounds brings it to processing.

## 2.2. The pseudospectrum with the conditioning of the embedding

The operator notation (accepted from the review): let \(T:\mathbb C^m\to L^2(\mu)\) be the embedding of the macro-coordinates, \(\mathcal UT-TG=R\). For \(Gv=\lambda v\):

\[
(\mathcal U-\lambda)Tv=Rv
\quad\Longrightarrow\quad
\boxed{
\lambda\in\Lambda_{\;\|R\|/\sigma_{\min}(T)}(\mathcal U).
}
\]

Proposition 4 of Part IV is replaced by this form. \(\sigma_{\min}(T)\) is the same conditioning of the representation as in ✦2 and in \(\kappa_{\mathcal L}\) (Part V §2): the review is right that this is a **fundamental quantity of the certificate**, not a technical correction — it already enters \(\kappa_{\mathcal L}\), and from now on explicitly: a poorly conditioned embedding of the macro-coordinates weakens both identifiability (✦2), and transients (✦5), and visibility in the audit (this formula) — in three ways at once, by a single number.

---

# 3. The geometry of subsystem relations

## 3.1. The object \(\Gamma\)

Accepted as the canonical object of the theory of connectedness:

\[
\boxed{
\Gamma(A,B)=\big(\Gamma_{\mathrm{int}},\ \Gamma_{\mathrm{align}}\big),
\qquad
\Gamma_{\mathrm{int}}\sim\operatorname{cut}_K,
\quad
\Gamma_{\mathrm{align}}\sim\Delta_{\mathrm{free}} .
}
\]

The first coordinate: how much interaction physically flows. The second: how far the internal structures are correlated relative to the chosen algebra. Connectedness is a point in the plane, not a scalar.

## 3.2. 11a: the model \(H_0\) is fixed explicitly

Accepted: \(\mu_{H_0}=\mu_a*\mu_b\) is a property of the **chosen model** \(H_0=a\otimes I+I\otimes b\) with a product state, not a consequence of a small cut. The canonical formulation of 11a: *in the independent-composition model \(H_0\) (tensor sum, product state), for \(H=H_0+V\) with \(|v_{ij}|\le K(i,j)\) on the boundary:*
\(d_{W_2}(\mu_H,\mu_a*\mu_b)^2\le K^{\max}_\partial\operatorname{cut}_K/N\)
*under Hermiticity/normality of \(H,H_0\).* A small cut bounds the deviation **from the chosen reference model**; the choice of the reference is a separate (modeling) act. The same distinction is in §3.4.

## 3.3. 11b: an honest constant

Accepted: free cumulants are not bounded by \(M\) directly. The corrected pair of statements:

**Theorem 11b′.** Let \(B_p:=\max_{n\le p}\max\big\{|\kappa_n(H_1)|,\,|\kappa_n(H_2)|\big\}\). Then

\[
\boxed{
\big|m_p(H_1+H_2)-m_p(\mu_1\boxplus\mu_2)\big|
\;\le\;
\mathrm{Cat}_p\cdot p\cdot2^{p}\cdot\max(1,B_p)^{\,p-1}\cdot\Delta_{\mathrm{free}}(p).
}
\]

*Proof* — as in Part IV (multilinearity of cumulants; in each \(NC\)-partition one block telescopes, the rest are majorized by \(B_p\)), now with the correct majorant for the blocks. ∎

**Lemma 7 (bounding \(B_p\) via moments).** If \(|\tau(w)|\le M\) for all words of length \(\le p\), then

\[
B_p\;\le\;16^{\,p}\max(1,M)^{\,p}.
\]

*Proof.* Möbius inversion on the lattice \(NC(n)\): \(\kappa_n=\sum_{\pi\in NC(n)}\mu(\pi,1_n)\prod_{B\in\pi}m_{|B|}\); the number of terms is \(\le|NC(n)|\le4^n\), the Möbius coefficients \(|\mu(\pi,1_n)|\le\mathrm{Cat}_{n}\le4^n\), the products of moments \(\le\max(1,M)^n\). ∎

The constant is deliberately generous; its optimization is a technical task, not a structural one.

## 3.4. Forensics demoted: a compatibility test, not identification

Accepted in full. Spectral data do not identify the joint structure: different joint structures give identical spectra of the sums. Corollary 7 of Part IV is **reformulated**:

**Corollary 7′ (compatibility test of compositions).** Comparing the observed \(\mu_{H_1+H_2}\) with \(\mu_1*\mu_2\) and \(\mu_1\boxplus\mu_2\) (with the tolerances from 11a and 11b′) gives one of **four** verdicts:

\[
\texttt{compatible-classical}\quad
\texttt{compatible-free}\quad
\texttt{neither}\quad
\texttt{both/ambiguous}
\]

— a statement about **compatibility with a dependence model**, not about the causal structure of the carriers. The \(\texttt{both/ambiguous}\) regime is mandatory (the measures may coincide by chance). Identification — model selection on top of the test plus external information (the graph \(K\), the carriers) — and the conditions under which it is possible are deferred to open problem 2 (§4).

## 3.5. The four-regime plane

Instead of the three-line dictionary of Part IV — the \(\Gamma\) plane:

\[
\begin{array}{c|c|c}
&\Delta_{\mathrm{free}}\ \text{small}&\Delta_{\mathrm{free}}\ \text{large}\\\hline
\operatorname{cut}\ \text{small}
&\begin{array}{c}\text{decoupled, generic position}\\\Rightarrow\ \text{merge by }*\text{ or }\boxplus\text{ (test 7′)}\end{array}
&\begin{array}{c}\textbf{weakly interacting, but aligned}\\\Rightarrow\ \text{hidden common structure without a channel}\end{array}\\\hline
\operatorname{cut}\ \text{large}
&\begin{array}{c}\text{strong generic coupling}\\\Rightarrow\ \text{perturbed merge (11a)}\end{array}
&\begin{array}{c}\textbf{strongly interacting and aligned}\\\Rightarrow\ \textbf{a candidate for a parent level}\end{array}
\end{array}
\]

The lower-right quadrant is the main trigger of a joint emerge; the upper-right is the most intriguing (agreement without a visible channel: a common ancestor in the history, a common field, or an unregistered mediator — a signal for the audit of §1). The classification has ceased to be binary and has become a **geometry of the space of relations**; the JOINT-EMERGE protocol of Part IV switches from three branches to this plane with the 7′ verdicts.

---

# 4. Status and the three v1 problems

The official replacement of the finale of Part IV:

\[
\boxed{
\textbf{The main conjectures have not vanished; they have decomposed into more precise statements.}
}
\]

The two axes revealed by Part IV and confirmed by the review remain the main values of the corpus:

\[
\text{predictive closure}\leftrightarrow\text{metastability}\leftrightarrow\text{slow spectral structure}
\]
\[
\text{subsystem relation}=(\text{strength},\ \text{alignment})
\]

**The three open problems of v1** (closing which will earn the right to say «the mathematics of v1 is closed»):

1. **Survival-spectrum theorem.** Status after Part VI: the core is built (Lemma 6, Theorem 10a′, Corollary 6′ for \(L^2\)-starts). What remains: the pointwise (adversarial-start) theory without uniform hazard — either prove impossibility and make hazard-predicates a mandatory part of contracts; the irreversible case (the killed operator + the pseudospectrum of §2.2 together); sharpness of the constants.
2. **Spectral identifiability.** Under what additional conditions (the structure of the graph \(K\), several observed states, variation of parameters) the compatibility test 7′ becomes an identification of the type of dependence. Includes the construction of non-identifiability examples (different joint structures, identical spectra of the sums) as lower bounds.
3. **Mixed interaction/alignment calculus.** A unified certificate of merge when \(\operatorname{cut}\) and \(\Delta_{\mathrm{free}}\) are simultaneously large (the lower-right quadrant): operator-valued subordination with an error bound in terms of \(\Gamma\).

**Summary of Part VI's changes:** Corollary 6 retracted (replaced by 6′), Corollary 7 demoted (replaced by 7′), clarified: 10(b) (to find ≠ to classify), Proposition 4 (\(\sigma_{\min}(T)\)), 11a (the model \(H_0\) made explicit), 11b (the constant via \(B_p\) + Lemma 7). The constant of 10a is improved (\(1-4\varepsilon\to1-2h\)) by passing from conductance to the Perron function of the killed operator. Hazard has received a definition: \(\mathcal D(S)=1/(1-\rho_S)\); conductance is its cheap one-sided certificate.
