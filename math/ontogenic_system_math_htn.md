# Part VIII. The HTN theorem: multiplicative form, the surface of architectures, evolution as optimization

Official renaming: Theorem 13 (Part VII) is henceforth the **HTN theorem** (Hierarchy–Time–Nonlocality Tradeoff). Part VIII adds no mechanisms: it derives the multiplicative form (the hypothesis of the fourth revision turns out to be a corollary, not a new hypothesis), constructs the space of architectures, and formalizes the evolutionary interpretation, carefully separating theorems from models.

---

# 1. The multiplicative form: \(f(N)\) computed

Define three currencies in dimensionless form:

\[
\mathcal H:=s^{L}
\quad(\text{hierarchical reach}),\qquad
\mathcal T:=T
\quad(\text{coordination time}),\qquad
\mathcal R:=\frac{R}{r_0}
\quad(\text{relative range}).
\]

**Corollary 9 (multiplicative HTN).** Exponentiating Theorem 13(b) gives

\[
\boxed{
\mathcal H\cdot\mathcal T\cdot\mathcal R
\;\ge\;
c\,N^{1/D},
}
\]

and Theorem 13(a) adds an irreducible floor:

\[
\mathcal T\;\ge\;\frac{\log(cN)}{\log(\Delta+1)} .
\]

*Proof.* Substitute the definitions into \(L\log s+\log T+\log(R/r_0)\ge\frac1D\log(cN)-O(1)\). ∎

In sum, the hypothetical \(f(N)\) of the fourth revision is determined exactly: **the geometric part is \(N^{1/D}\)** (the light cone), **the additive floor is \(\log_\Delta N\)** (fan-in); both constants come from Lemmas A–B of Part VII. No combination of currencies drops below the time floor: globality is never cheaper than a logarithm.

## 1.1. The key asymmetry: hierarchy is a currency with a logarithmic price tag

The multiplicative form makes visible what the additive form hid: \(\mathcal T\) and \(\mathcal R\) enter the budget *directly*, whereas the depth \(L\) enters **in the exponent** (\(\mathcal H=s^L\)). To double the contribution of time, one must double the time; to double the contribution of hierarchy, one must add **one level**:

\[
\boxed{
\text{Time and range grow linearly in price; hierarchy is the only currency that grows logarithmically.}
}
\]

This is precisely the mathematical reason why nature "so loves" hierarchy: at large \(N\), any architecture that pays its bill in time or in wiring pays polynomially; one that pays in levels pays logarithmically (§3).

---

# 2. The surface of architectures

The space of architectures: points \((\mathcal H,\mathcal T,\mathcal R)\in[1,\infty)^3\); the admissible region is above the surface \(\mathcal H\mathcal T\mathcal R=cN^{1/D}\) (and above the \(\mathcal T\) floor). The pure strategies are the edges of the surface:

| strategy | point | biological referent |
|---|---|---|
| \(\mathcal H=\mathcal R=1\) | \(\mathcal T\ge cN^{1/D}\) | local chemistry, diffusion: flat, local, slow |
| \(\mathcal R\uparrow\), \(\mathcal H=1\) | \(\mathcal T\sim N^{1/D}/\mathcal R\) | nervous system: long-range wires bought in exchange for latency |
| \(\mathcal R\sim N^{1/D}\) | \(\mathcal T=O(\text{floor})\) | hormonal field: near-global reach by broadcasting |
| \(\mathcal H\uparrow\), \(\mathcal R=1\) | \(\mathcal T=O(\text{polylog})\) at \(L\sim\log N\) | organs/tissues: levels instead of wires and waiting |

A real organism is **not a vertex, but an interior point**: a hybrid that distributes different functions over different regions of the surface. The formal explanation of hybridity is in §3.2.

**Honest note (the missing axis).** HTN counts *reachability*, not *throughput*: a hormonal field has enormous reach \(\mathcal R\), but its channel to the whole system is single and narrow. The axis of channel capacity (bits/tick per channel) is absent from the theorem; with it the tradeoff becomes four-dimensional (\(\mathcal H,\mathcal T,\mathcal R,\mathcal B\)) — added to the tasks (§4). It is precisely for this reason that broadcasting (a hormone) and an addressed line (an axon) are different strategies, even though both are "action at a distance".

---

# 3. Evolution as optimization on the surface

What follows is a **model on top of the theorem** (statuses marked): the bill is a theorem; the cost functional is a modeling assumption; the conclusions are propositions under those assumptions.

## 3.1. The problem

\[
\min_{L,T,R}\;\;
c_H\,L+c_T\,T+c_R\,R
\qquad\text{subject to}\qquad
L\log s+\log T+\log\frac{R}{r_0}\;\ge\;\frac1D\log(cN),
\]

(the cost \(c_H\) is per *level*: certification, caches, level repair; \(c_T\) is per tick of latency; \(c_R\) is per unit of wire range; energy \(\mathcal E\) is for now aggregated into the coefficients — its separation into an independent axis, like robustness/semantic fidelity as constraints, is in the tasks §4).

## 3.2. Two propositions

**Proposition 5 (asymptotic dominance of hierarchy).** At fixed unit prices and \(N\to\infty\): paying with time alone or range alone costs \(\Theta(N^{1/D})\); paying with levels costs \(c_H\log N/(D\log s)=\Theta(\log N)\). The optimum of the problem §3.1 has \(L=\Theta(\log N)\), \(T,R=O(\mathrm{polylog})\): **asymptotically, every cheap architecture is hierarchical**.

*Proof.* Comparison of the extreme strategies + monotonicity: at large \(N\), any shift of the budget from \(L\) to \(T\) or \(R\) increases the cost (a linear price against the exponential exchange rate of §1.1). ∎

**Proposition 6 (hybridity from heterogeneous demand; model).** Suppose the system serves a spectrum of functions \(\{(T_i^{\max},\,\text{scope}_i)\}\) — each function with its own admissible horizon and its own reach. The tower yields a latency of \(\Theta(L)\) hops for global reach; a function with \(T_i^{\max}\) *below* the tower's latency cannot be served by hierarchy at any price — for it a dedicated long-range line is forcibly bought (\(\mathcal R\)-currency), while slow global functions are cheapest to serve by broadcasting (a field). The optimum for a heterogeneous spectrum is a **mixed architecture**: bulk coordination by the tower (Prop. 5), latency-critical channels by wires, slow global by a field.

*Meaning.* A reflex arc exists not because hierarchy is bad, but because the reflex has a \(T^{\max}\) below the tower's depth in hops. The organism is an optimum over the *spectrum* of demands, not over a single demand; hence the observed hybrid point of §2.

## 3.3. What HTN explains with a single bill

Under the adopted model prices, different ways of paying follow from a single theorem:

- **hierarchies** (the cheap currency at large \(N\) — Prop. 5);
- **nervous systems** (latency-critical demand — Prop. 6);
- **circulation and hormones** (global slow reach by broadcasting; channel narrowness — the \(\mathcal B\) axis, §4);
- **local autonomous loops** (functions with local scope never reach the surface of the global tradeoff at all — no bill is issued to them);
- **separation of timescales across levels** (the \(\mathcal T\) floor grows with reach — Part VII, the light-cone addendum).

Not "because it is convenient", but "because that is how the bill is written" — exactly what was required of a cap-like theorem of developing systems.

---

# 4. Update to the tasks

The following are added to the list of Part VII (without replacing it):

6. **The capacity axis \(\mathcal B\)**: a four-dimensional HTN with channel throughput; separate broadcasting from addressed lines; the expected form is a budget over *pairs* (reach × refresh rate per bit).
7. **Energy and constraints**: separate \(\mathcal E\) out of the coefficients into an independent quantity (the cost of maintaining a level = a function of the repair intensity from Pillar 3 — a link to Theorem 4′); robustness and semantic fidelity — as constraints of the problem §3.1, connecting HTN to the safety budget (Corollary 6′).
8. **A theorem on the demand spectrum**: turn Proposition 6 from a model into a theorem — a characterization of optimal mixed architectures as a function of the distribution of \((T^{\max},\text{scope})\) over functions.

Status of the corpus: the central result is the **HTN theorem** (additive form — Thm. 13, multiplicative — Cor. 9, floor — 13(a)); around it are the four core components (Part V §4) and the operational pillars. Parts V–VIII have not added a single primitive to the six of Part I — all the depth grew out of them, which is itself an argument in favor of the choice of primitives.
