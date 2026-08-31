# Part IX. The price of the wire: HTN without smuggling

The fifth revision found the last fundamental trap: in the Part VII model a macro-hop transfers influence over \(r_0s^\ell\) in a single tick, even though all channels are declared physical — **the hierarchy was secretly smuggling nonlocality**, and the independence of the three currencies (the very thing that makes HTN substantive) was under threat of double counting. Part IX closes the trap along both proposed routes and extracts from the physical route a new theorem and one important corollary. Plus three technical revision fixes.

---

# 1. The fork: two legitimate HTNs

**HTN-A (abstract).** Theorem 13 is declared a theorem about an **abstract computational architecture**: a communication graph with three kinds of edges (geometric, hierarchical, long-range), each kind a self-standing primitive resource. In this model there is no double counting by construction; the Part VII proofs are correct as they stand. The price of honesty: HTN-A says nothing about *how much* a hierarchical edge costs in the physical world.

**HTN-P (physical).** A hierarchical edge must be laid out in geometry: a child↔parent channel of length \(\lambda\) is a **wire**, and it has a cost. A fourth currency is introduced:

\[
\boxed{
\mathcal W=\text{total length of built channels (infrastructure)},
}
\]

with \(\mathcal R\) **dissolving into \(\mathcal W\)**: long-range connectivity is also a wire, just one not built into the tower. The latency of any built channel is 1 tick (a fast medium: an axon, not diffusion); an unbuilt one does not exist. The rules of the Part VII model change in one place: a macro-hop is permitted ⟺ the corresponding wire is included in \(\mathcal W\).

From here on — HTN-P: it is the more interesting one, because in it the hierarchy ceases to be a teleport and becomes what the revision named it — **communication amortization**.

---

# 2. Theorem 14: the tower costs linearly

**Tower model.** A space-filling tower: a level-\(\ell\) region contains \(k^\ell\) cells, hence (GL, bounded density) has diameter \(\rho_\ell\le c_1r_0k^{\ell/D}\); the reach factor is \(s=k^{1/D}\). The macro's cache is materialized in the cells of its region; the wires run from the children's caches to the parent's cache, of length \(\le\rho_\ell\).

**Theorem 14 (amortization).** For \(D\ge2\) the full tower of depth \(L=\log_kN\) has

\[
\boxed{
\mathcal W_{\text{tower}}
\;\le\;
\frac{c_1k}{1-k^{1/D-1}}\;N\,r_0
\;=\;
O(N\,r_0),
}
\]

and provides live global semantics with \(T=O(\log_kN)\) (up \(L\) hops, down \(L\), local glaze \(O(1)\)), which matches the absolute floor 13(a) up to a constant. For \(D=1\): \(\mathcal W=O(Nr_0\log N)\). *(Fix v0.1: only the upper bound is proved; the lower bound \(\mathcal W_{\text{tower}}=\Omega(Nr_0)\) is not automatic — it requires, for example, a nonzero average geometric length of the bottom-level connections — and is deferred to the infrastructure lower-bound problem.)*

*Proof.* Level \(\ell\): \(N/k^\ell\) macros, each with \(k\) wires of length \(\le c_1r_0k^{\ell/D}\); the level's total is \(c_1kNr_0\,k^{\ell(1/D-1)}\). For \(D\ge2\): \(k^{1/D-1}\le k^{-1/2}<1\) — a geometric series, sum \(\Theta(kNr_0)\), dominated by the **bottom** levels. For \(D=1\) all terms are equal — a factor \(L\). Capacity overhead: caches total \(\sum N/k^\ell=O(N/k)\) cells. Latency — a hop count. ∎

**Comparison of tariffs** (the very thing the currency \(\mathcal W\) was introduced for):

| architecture | \(\mathcal W\) | \(T\) of global consensus |
|---|---|---|
| flat chemistry (substrate only) | \(0\) | \(\Theta(N^{1/D})\) |
| direct long-range links to everyone (naive nonlocality) | \(\Theta(N^{1+1/D})\) | \(O(1)\)–\(O(\log N)\) |
| **tower** | \(O(N)\) (lower bound open) | \(O(\log N)\) |
| single nerve (a pair of points) | \(\Lambda\) | fast — but only for that pair |
| hormone (broadcast medium) | \(\sim\)volume | \(O(1)\) reach, **1 narrow channel** (the \(\mathcal B\) axis) |

\[
\boxed{
\text{Hierarchy}=\text{the minimal known infrastructure that buys logarithmic time:}
}
\]

capital expenditure \(O(N)\) — no higher in order than the substrate itself — versus \(\Theta(N^{1+1/D})\) for hierarchy-free nonlocality. "Expensive to build — cheap to use": the revision's formula became a row in the tariff table. (The precise lower bound "\(T=O(\log N)\Rightarrow\mathcal W=\Omega(N)\)" is an open problem; fan-in gives a floor on \(T\), but not on the wire.)

---

# 3. Proposition 7: the transport bound (the first theorem of the \(\mathcal B\) axis)

The wire resolves reachability, but not throughput. Channels have unit capacity (1 bit/tick).

*(Fix v0.1 — quantifiers.)* The original formulation contained a logical subtlety: the semantically important cut was postulated to be *one*, while averaging over wire lengths found a cut of small capacity — **not necessarily the same one**. The canonical form is cut-local, with subsequent averaging over a family on which *both* properties hold.

**Definition 16 (transport demand).** For a cut \(C\): \(I_{\mathrm{cross}}(C)\) is the number of bits of fresh semantics whose essential causal support (Def. 15) lies on both sides of \(C\). The transport demand of the semantics:

\[
\mathcal Q(y)\;=\;\int I_{\mathrm{cross}}(C)\,dC
\qquad(\text{integral over a family of parallel cuts}).
\]

**Proposition 7′ (cut bound, cut-local form).**

**(i) For each cut \(C\):** \(\;T\cdot\operatorname{Cap}(C)\ \ge\ I_{\mathrm{cross}}(C)\), where \(\operatorname{Cap}(C)\) is the number of channels crossing \(C\).

**(ii)** Let the semantics be **distributed relative to the family** \(\mathcal C\) of parallel cuts of the central layer of width \(\Lambda\sim r_0N^{1/D}\): \(I_{\mathrm{cross}}(C)\ge c\,H_y\) for **every** \(C\in\mathcal C\). Then

\[
\boxed{
T\cdot\Big(\frac{\mathcal W}{\Lambda}+c_2\,N^{(D-1)/D}\Big)
\;\ge\;
c\,H_y ,
}
\]

and in integral form \(\;T\cdot\big(\mathcal W+\Lambda\,c_2N^{(D-1)/D}\big)\ \ge\ \mathcal Q(y)|_{\mathcal C}\).

*Proof.* (i) — a bit with support on both sides requires crossing \(C\) by a causal flow; the flow per tick is \(\le\operatorname{Cap}(C)\). (ii) — a wire of length \(\lambda\) crosses each cut of the family \(\le1\) time, hence \(\int_{\mathcal C}\#\{\text{wire crossings}\}\,dC\le\mathcal W\), and **within the family** there exists a \(C^\*\) with \(\le\mathcal W/\Lambda\) wires; since the demand \(\ge cH_y\) holds on *all* cuts of the family, including \(C^\*\), applying (i) to \(C^\*\) gives the box. The integral form is the integration of (i) over \(\mathcal C\). ∎

**Corollary 11 (infrastructure arithmetic; fix v0.1).** For \(H_y=\Theta(N)\): \(T=\mathrm{polylog}\,N\Rightarrow\mathcal W=\widetilde\Omega\big(r_0N^{1+1/D}\big)\) (with a polylog correction), and for \(T=O(1)\) — \(\mathcal W=\Omega\big(r_0N^{1+1/D}\big)\) without corrections: the power-law scale of all-to-all infrastructure arises from the bound, not by postulate. The programmatic goal of the \(\mathcal B\) axis: a precise theorem of the form \(T\,\mathcal W\gtrsim\mathcal Q(y)\) with geometric corrections for arbitrary (not only layered) cut families.

**Check on the tower.** \(\mathcal W=O(Nr_0)\Rightarrow\mathcal W/\Lambda=O(N^{(D-1)/D})\): for \(H_y=\Theta(N)\) we get \(T\ge c\,N^{1/D}\) — **even the tower cannot rapidly refresh linear entropy**; for \(H_y=\mathrm{polylog}\) the bound is empty — consistent with \(T=O(\log N)\) of Theorem 14. Dependency semantics (\(H_y=O(1)\), e.g. a global predicate) is untouched by the bound — exactly the distinction "dependency vs entropy" predicted by Problem 6 of Part VIII: the \(\mathcal B\) axis has received its first theorem.

## 3.1. Corollary: transport forces compression (and `emerge` is compression + adaptivity)

Juxtapose Theorem 14 and Proposition 7:

- only low-entropy semantics can be globally **fresh** (\(H_y\lesssim T\cdot N^{(D-1)/D}\); for \(T=\mathrm{polylog}\) this is \(\tilde O(N^{(D-1)/D})\) bits, a fraction \(o(N)\));
- the raw microstate (\(H=\Theta(N)\)) cannot be globally fresh under any architecture cheaper than \(\mathcal W=\Theta(N^{1+1/D})\) — and even under that one it hits the capacity wall.

\[
\boxed{
\textbf{Only summaries can be fast global cargo.}\\
\text{Coarse-graining }\pi\text{ is not a representational convenience but a transport necessity:}\\
\text{levels exist because the road is expensive and the summaries are light.}
}
\]

*(Fix v0.1 — the exact strength of the claim.)* Transport proves the necessity of **compression** (sufficient summaries / coarse-graining), but not of `emerge` specifically: a fixed summary \(\pi\) can be designed in advance, and the transport bound will be satisfied. To force `emerge` proper, a second premise is needed: **the required sufficient statistic is unknown in advance or changes together with the environment**. Then:

\[
\boxed{
\text{transport pressure}+\text{variable predictive structure}
\;\Longrightarrow\;
\text{adaptive discovery of coarse-graining}=\texttt{emerge}.
}
\]

All in all the corpus gives three independent pressures toward compression — MDL (description, Pillar 4), depth (HTN), channel (transport) — and one adaptivity condition that turns compression into `emerge`. This is more honest and, in essence, stronger: it makes visible *which exact* property of the environment renders static design insufficient.

---

# 4. Technical revision fixes

## 4.1. Renaming into 12b′

The notation collision is removed: the code dimension in Part VII §4 is henceforth \(k_{\mathrm{code}}\) (\(k\) remains the tower fan-in). Theorem 12b′ reads: \(k_{\mathrm{code}}\cdot d^{1/D}\le4D\,r_0\,N\).

## 4.2. Precise formulation of flat death

The phrase "does not survive even a constant number of corruptions" is replaced by the precise:

\[
\boxed{
\text{for }k_{\mathrm{code}}=hN\ \text{the number of guaranteed-correctable adversarial errors stays }O(1)\ \text{as }N\to\infty,
}
\]

namely \(\le d/2\le\tfrac12(4Dr_0/h)^D\) — a fixed constant the code can withstand, a number growing with \(N\) it cannot.

## 4.3. Essential causal support

The definition of live semantics (Def. 14) is cast in ironclad form. For a deterministic system with input vector \(a\):

**Definition 15 (essential causal support).**

\[
\mathrm{Supp}_t(y)
=
\big\{v:\ \exists\,a,a'\ \text{differing only at }v,\ \ y_t(a)\neq y_t(a')\big\}.
\]

**Def. 14′ (liveness).** The semantics is live with horizon \(T\) if \(|\mathrm{Supp}_t(y)\cap\{\text{inputs of time}\ge t-T\}|\ge cN\).

**Lemma E.** \(\mathrm{Supp}_t(y)\subseteq\mathcal D(o,T)\) (a change of input outside the dependency cone changes nothing inside the cone, in particular \(y\)). Hence both HTN bounds — Lemmas A and B — apply to \(|\mathrm{Supp}|\ge cN\) verbatim, in a few lines, with no appeals to "depends on". For stochastic systems \(\mathrm{Supp}\) is defined via a difference of distributions of \(y\) — the cone argument is unchanged.

---

# 5. Status

**The title theorem of the corpus is HTN-P**: the pair (Theorem 13 in the abstract HTN-A model) + (Theorem 14 and Proposition 7 in the physical model with the currency \(\mathcal W\)), with floor 13(a), liveness via \(\mathrm{Supp}\) (Def. 14′/Lemma E) and the corollary of §3.1 on the forced nature of `emerge`. The structure of the future paper is as prescribed by the revision: HTN on the first page; `emerge`, repair, dnaContract — as an architecture that knows how to live sensibly on the surface \((\mathcal H,\mathcal T,\mathcal W,\mathcal B)\).

**Update of the problems** (on top of the Part VII–VIII list):

- (replacement of Problem 6) the \(\mathcal B\) axis: Proposition 7 is the first theorem; carry it to a full four-dimensional HTN (joint lower bounds in \(\mathcal H,\mathcal T,\mathcal W,\mathcal B\));
- infrastructure lower bound: \(T=O(\log N)\Rightarrow\mathcal W=\Omega(N)\)? and \(\mathcal W_{\text{tower}}=\Omega(Nr_0)\)? (currently — only reachability \(O(N)\) and the fan-in floor on \(T\));
- a rigorous version of the naive-nonlocality tariff (\(\Theta(N^{1+1/D})\) — currently a count for direct links; expander wiring — to be estimated within our formalism, not by citation).

Double counting is removed: in HTN-A the currencies are independent by the model's definition, and in HTN-P the hierarchy pays for every meter of wire — and still wins, which is what makes the result substantive.
