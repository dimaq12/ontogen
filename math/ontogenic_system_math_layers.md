# Part X. HTN in two layers: the fold, freshness, the price of knowledge

The sixth revision (the "final boss") is accepted on all points. The result of the rebuild:

1. The multiplicative surface of Part VIII was a **weakening**: the canonical form uses the fold (\(\max\)), the product admitted fictitious points. Corollary 9 is demoted to a derivative.
2. The time floor is not an absolute but the **price of bounded degree**; broadcast legally buys \(O(1)\).
3. \(\mathcal H\) is **not a causal currency**: the A/B dilemma is formalized, the hierarchy turns out to be a *caching* technology; time splits into \(T_q\) (query) and \(T_f\) (freshness).
4. Proposition 5 is recast in conditional form; the honest price of a level returns Pillar 3 to the central theorem.
5. Hybridity is now *only* from the demand spectrum (the fold forbids mixed payment for one function).

---

# 1. HTN-0: the pure causal theorem (layer 1)

## 1.1. The fold

Lemma B of Part VII always said \(\max\), not the product: \(|\mathcal D(o,T)\cap V|\le c_0\big(T\max(\mathcal R,\mathcal H)\big)^D\). The canonical form:

**Theorem 13′ (HTN-0).** For live semantics (Def. 14′, \(|\mathrm{Supp}|\ge cN\)):

\[
\boxed{
\mathcal T\cdot\max(\mathcal H,\mathcal R)\;\ge\;c\,N^{1/D}
}
\qquad\Longleftrightarrow\qquad
\log\mathcal T+\max(\log\mathcal H,\log\mathcal R)\ \ge\ \tfrac1D\log N-O(1).
\]

Corollary 9 (the product) is formally correct but **withdrawn as the canonical surface**: it follows from the fold via \(\max(\mathcal H,\mathcal R)\le\mathcal H\mathcal R\) and therefore admits fictitious points — for example \(\mathcal H=\mathcal R=N^{1/(2D)},\ \mathcal T=1\) satisfies the product, yet \(\mathcal T\max=N^{1/(2D)}\ll N^{1/D}\): there is no real cone.

**Meaning of the fold.** For a single task, hierarchical reach and long-range action **do not add up their speedups** — they are two alternative ways to increase the spatial step, and time multiplies the stronger one. The feasible surface is not a smooth plane but a ridge: paying both "spatial" currencies at once for one function is pointless (the corollary for hybridity — §5).

## 1.2. The floor is the price of bounded degree

From Lemma A: \(T\ge\log(cN)/\log(\Delta+1)\), where \(\Delta=\max(k+1,\,c_0\mathcal R^{D},\,\text{broadcast fan-in})\). The precise formulation:

\[
\boxed{
T=\Omega(\log N)\ \textbf{under bounded degree};
\qquad
\Delta=\Theta(N)\ (\text{broadcast})\ \Rightarrow\ \text{floor}=O(1).
}
\]

The hormonal regime is legal: a global field — fan-in \(N\), time \(O(1)\); its true cost is neither time nor floor but **channel capacity** (one summary for all, Proposition 7) and the physical broadcast medium. The phrase "faster than log is impossible at all" from Part VIII is withdrawn.

---

# 2. \(\mathcal H\) is not a currency but a technology: the A/B dilemma

Let a level-\(L\) macro span \(r_0\mathcal H\), and a child read it in one tick. Where does the information in the cache come from?

**Variant A (there is a long channel).** Then this is bought nonlocality: \(\mathcal R_{\mathrm{eff}}\ge\mathcal H\), paid for in \(\mathcal W\). This is exactly how the Part IX tower is built: its top wires have length \(\sim r_0N^{1/D}\) — HTN-P was Variant A with honest payment from the very start, so there is no contradiction with the fold: for the tower \(\max(\mathcal H,\mathcal R_{\mathrm{eff}})=\Theta(N^{1/D})\), and \(\mathcal T\cdot\max\ge cN^{1/D}\) holds at \(\mathcal T=O(\log N)\)… no: \(\mathcal T\ge c\) — the cone is honestly closed by long wires.

**Variant B (no channels, the cache is updated locally).**

**Theorem 15 (the price of freshness).** If all channels have reach \(\le r_0\mathcal R\), then the age (staleness) of any maintained summary state of span \(\mathcal H\) satisfies

\[
\boxed{
T_f\;\ge\;\frac{\mathcal H}{\mathcal R}.
}
\]

*Proof.* The dependency cone, applied to the cache cell as an output: fresh input at the edge of a region of diameter \(r_0\mathcal H\) must physically reach the cache; the displacement per hop is \(\le r_0\mathcal R\) (Lemma B); hops \(\ge\mathcal H/\mathcal R\). ∎

**Conclusion.** There are two causal currencies: \(\mathcal T\) and \(\mathcal R\) (plus the infrastructure \(\mathcal W\), with which \(\mathcal R\) is paid for). \(\mathcal H\) is a **derived technology**: the hierarchy does not violate the light cone, it **caches already assembled information**. The revision's formula is accepted as the definition of layer 2:

\[
\boxed{
\text{Hierarchy buys low query latency at the price of update latency.}
}
\]

---

# 3. HTN-1: the cache layer — two times

**Definitions.** \(T_q\) is the time to read a maintained global representation; \(T_f\) is its age (the update period/delay).

**Theorem 16 (query/freshness splitting).** For a global summary (span \(\mathcal H\ge cN^{1/D}\)):

**(a) Query.** With the tower (infrastructure \(\mathcal W=O(Nr_0)\), Thm. 14): \(T_q=O(\log N)\).

**(b) Freshness, without long channels:** \(T_f\ge cN^{1/D}/\mathcal R\) (Thm. 15); in particular, on the pure substrate \(T_f\ge cN^{1/D}\) — **the hierarchy does not repeal this bound**.

**(c) Freshness with infrastructure:** the tower wires give \(T_f=O(\log N)\), but pay \(\mathcal W=O(N)\), and the freshness flow is bounded by Proposition 7′:

\[
I_{\mathrm{fresh}}\;\le\;T_f\cdot\Big(\frac{\mathcal W}{r_0N^{1/D}}+c_2N^{(D-1)/D}\Big)
\]

— the capacity bound \(\mathcal B\cdot T_f\gtrsim I_{\mathrm{fresh}}\) from the revision in precise form: only the compressed can be fast (§3.1 of Part IX).

*Proofs.* (a) — Thm. 14; (b) — Thm. 15; (c) — a hop count over the wires + Proposition 7. ∎

All in all the hierarchy is a triple technology, and all three components are now paid for explicitly:

\[
\boxed{
\text{hierarchy}=\text{compression}(\pi)+\text{caching}(T_q\!\ll\!T_f)+\text{connection amortization}(\mathcal W=\Theta(N)).
}
\]

## 3.1. Staleness enters the certificate

A cache of age \(T_f\) emits \(y(t-T_f)\) instead of \(y(t)\). The read error is the accumulated prediction defect over \(T_f\) steps (Lemma 1):

\[
\eta_{\mathrm{eff}}\;\le\;\eta\cdot\frac{L^{T_f}-1}{L-1}
\qquad(\le\ \eta\,T_f\ \text{at }L=1,\quad \le\ \tfrac{\eta}{1-L}\ \text{at }L<1).
\]

**Corollary 10.** For contracting levels (\(L<1\), Corollary 1 of Part II) staleness is **bounded forever**: the summary can be updated rarely, and it remains honest within \(\eta/(1-L)\). Dissipative macrodynamics are the only ones for which the cache costs almost nothing; this is why viable slow levels are contracting, now also on the cache side. Freshness has ceased to be a separate entity: it is a term of the defect, paid for by the certificate's currency.

---

# 4. The honest price of a level: Pillar 3 returns to the center

Proposition 5 of Part VIII is recast in conditional form (the revision's verdict): what was proved was only "*if* the price of a level is \(O(1)\) independently of scale, the hierarchy wins". The honest price:

\[
C_H(L)=\sum_{\ell=1}^{L}\Big(C_{\mathrm{cache}}^{(\ell)}+C_{\mathrm{refresh}}^{(\ell)}+C_{\mathrm{repair}}^{(\ell)}\Big).
\]

**Proposition 8 (operating price of the tower; model).** For a space-filling tower: caches \(O(N/k)\) cells; updating level \(\ell\) — \(O(k)\) work per macro with cadence \(1/\tau_\ell\), where \(\tau_\ell\) is consistent with the certificate horizon (and by Corollary 10 for contracting levels may grow with \(\ell\)); repair — by the flow condition (Corollary 3) with local predicates. In total:

\[
\text{opex}(\text{tower})
=\sum_\ell\frac{N}{k^\ell}\cdot\frac{O(k)}{\tau_\ell}
\;=\;O(N)\ \text{work/tick}\ \big(O(1)\ \text{per cell}\big),
\]

dominated by the bottom levels and decreasing with growing \(\tau_\ell\). At this (computed, not postulated) price the conclusion of Proposition 5 is restored: the hierarchy remains asymptotically cheap **both in capital** (Thm. 14) **and in operating** costs — provided \(O(1)\)-maintenance of a macro, which is itself ensured by bounded context (Thm. 3) and bounded dimension of \(y\).

The coupling the revision demanded is achieved: **the cost of the hierarchy = the cost of the homeostasis of its caches** — the repair intensity (Thm. 4′), the flow condition (Cor. 3), the certificate horizons (Pillar 1) and the update cadences (Cor. 10) enter \(C_H\) as terms. The central theorem is no longer isolated from the theory of integrity — it is *paid for* by it.

---

# 5. Hybridity — only from the demand spectrum

The fold (Thm. 13′) destroys the last alternative mechanism of hybridity: for **one** function \(\max\) makes simultaneous payment of \(\mathcal H\) and \(\mathcal R\) pointless. Consequently, mixed architectures are explained **solely** by the inhomogeneity of demand (Proposition 6 of Part VIII, promoted from a secondary model to the sole explanation): functions with small \(T^{\max}\) — onto wires; global slow ones — onto broadcast; mass consistency — onto the tower; local ones — onto nothing. The organism is the optimum over the spectrum \((T^{\max},\mathrm{scope},I_{\mathrm{fresh}})\), and now this is not an observation but a consequence of the shape of the surface.

---

# 6. The five-axis object and status

The full space of architectures:

\[
\boxed{
(\mathcal H,\ T_q,\ T_f,\ \mathcal R,\ \mathcal B)
}
\qquad+\qquad
\mathcal E=\text{price of maintaining the point }(C_H,\ \mathcal W,\ \text{opex}).
\]

The cap-like phrase of the corpus — in the revision's form:

\[
\boxed{
\textbf{Reach, freshness, latency, capacity and hierarchy are never free simultaneously.}
}
\]

The subject to which the corpus has converged: **a theory of the cost of maintaining global knowledge in a distributed physical system**; the organism is the richest known example of optimization on this surface, and the ontogenic system (Parts I–VI) is the language in which the points of the surface are described by certificates, contracts and mutations.

**Register of Part X.** Rigorous: Thm. 13′ (the fold — a direct reading of Lemma B), Thm. 15 (the price of freshness), Thm. 16 (the splitting; (c) — under the predicates of Proposition 7), Cor. 10 (staleness in the certificate). Withdrawn/demoted: Cor. 9 (the product — a derivative of the fold), "faster than log is impossible" (→ the price of bounded degree), the unconditional form of Prop. 5 (→ conditional + Prop. 8). Model status: Prop. 8 (opex). Problems (on top of the previous ones): a precise four-dimensional bound \((T_q,T_f,\mathcal W,\mathcal B)\) in one theorem; the lower bound \(\mathcal W=\Omega(N)\) at \(T_q=O(\log N)\); a formalization of the broadcast medium (the physical price of \(\Delta=\Theta(N)\)-fan-in).
