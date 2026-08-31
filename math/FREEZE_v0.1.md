> Status: this document is part of a free-form compilation of known results written without a literature check. The map to public sources and the relation of each statement to them: [README.md](README.md). No priority is claimed.

# MATHEMATICAL CORE v0.1 — FROZEN

Freeze date: 2026-08-12. Six revisions, ten parts, three final bolts torqued down.

## The title idea

\[
\boxed{\textbf{Global knowledge has a physical price.}}
\]

Hierarchy is not magic but **compression + persistent summaries + amortized communication**. Reach, freshness, latency, capacity, and hierarchy are never free all at once. The subject of the corpus: a theory of the cost of maintaining global knowledge in a distributed physical system; the organism is the richest known example; the ontogenic system is the language for describing points on the cost surface.

## Map of the corpus

| file | contents |
|---|---|
| `ontogenic_system_math_core.md` | Part I: the object \(\mathfrak O\), 5 axioms, 6 primitives (original) |
| `ontogenic_system_math_pillars.md` | Part II: 5 pillars, theorems 1–7, certificates |
| `ontogenic_system_math_proofs.md` | Part III: full proofs, DKW, expanders, Cheeger, MDL |
| `ontogenic_system_math_hypotheses.md` | Part IV: the cancer dichotomy (thm. 10), two-dimensional connectedness (thm. 11), a counterexample |
| `ontogenic_system_math_polish.md` | Part V: 8 corrections, the fragility vector, GL, thm. 12 |
| `ontogenic_system_math_survival.md` | Part VI: the killed operator, hazard \(\mathcal D(S)\), thm. 10a′, the honesty budget |
| `ontogenic_system_math_tradeoff.md` | Part VII: the dependency cone, thm. 13, 12a′ (living semantics), 12b′ (its own proof) |
| `ontogenic_system_math_htn.md` | Part VIII: the HTN name, the surface of architectures, evolution as optimization |
| `ontogenic_system_math_wire.md` | Part IX: HTN-A/HTN-P, the price of the wire, thm. 14, prop. 7′, \(\mathcal Q(y)\) |
| `ontogenic_system_math_layers.md` | Part X: the fold, \(T_q/T_f\), the price of a level, the five-axis object |

## The three bolts of v0.1 (as of the sixth revision)

1. **Thm. 14**: the upper bound \(\mathcal W_{\text{tower}}=O(Nr_0)\) is proven; the lower bound \(\Omega(Nr_0)\) is open (entered into the task registry).
2. **Prop. 7 → 7′**: the cut-local form \(T\cdot\operatorname{Cap}(C)\ge I_{\mathrm{cross}}(C)\) for every cut + averaging over the family with a semantic demand on *all* of its cuts (the quantifier defect is removed); the transport demand \(\mathcal Q(y)=\int I_{\mathrm{cross}}\,dC\) is introduced; the program target \(T\mathcal W\gtrsim\mathcal Q(y)\). Corollary 11: \(H_y=\Theta(N),\,T=O(1)\Rightarrow\mathcal W=\Omega(r_0N^{1+1/D})\); for \(T=\mathrm{polylog}\) — \(\widetilde\Omega\).
3. **"Transport forces emerge" weakened**: transport forces *compression*; `emerge` = compression + adaptivity (the sufficient statistic is not known in advance or shifts with the environment).

## Main results (green zone)

- **HTN-0** (thm. 13′): \(\mathcal T\cdot\max(\mathcal H,\mathcal R)\ge cN^{1/D}\) — the fold; floor \(T=\Omega(\log N)\) under bounded degree.
- **HTN-1** (thm. 15, 16): \(T_f\ge\mathcal H/\mathcal R\); the query/freshness split; staleness is a term of the defect (cor. 10).
- **Thm. 14**: the tower — \(O(Nr_0)\) of wire at \(T_q=O(\log N)\) against \(\Theta(N^{1+1/D})\) for all-to-all.
- **12a′**: the separator kills not memory but alignment.
- **12b′** (self-contained): \(k_{\mathrm{code}}\,d^{1/D}\le4Dr_0N\) ⇒ flat death.
- **Thm. 10a′** (survival): unexplained metastability ⇒ an unexplained slow mode; hazard \(=1/(1-\rho(P_S))\), conductance is merely its lower certificate.
- **Two-dimensional connectedness**: \(\Gamma=(\gamma_{\mathrm{int}},\gamma_{\mathrm{align}})\in[0,1]^2\); classical vs. free composition; a compatibility test (not identification).
- **Certificate discipline**: quantile certificates (DKW), the fragility vector \(\boldsymbol\kappa\), horizons of validity, death/molt of levels, MDL hysteresis.
- **Integrity**: expander contracts (thm. 4′′′), repair semantics via \(\pi\), regeneration from \(C_M(y)\), redundancy bounds.

## Open tasks (registry as of the freeze)

1. Survival: adversarial starts without uniform hazard; the irreversible case.
2. Spectral identifiability (when the compatibility test → identification).
3. Mixed interaction/alignment calculus (operator-valued subordination with error in \(\Gamma\)).
4. Sharpness of \(1/(D-1)\) in 12b′; nonlinear predicates.
5. Coupling of the \(\boldsymbol\kappa\) coordinates (legalizing the scalarization).
6. An exact theorem \(T\mathcal W\gtrsim\mathcal Q(y)\) (the \(\mathcal B\) axis); a unified 4D bound \((T_q,T_f,\mathcal W,\mathcal B)\).
7. Infrastructure lower bounds: \(\mathcal W=\Omega(N)\) at \(T_q=O(\log N)\); \(\mathcal W_{\text{tower}}=\Omega(Nr_0)\).
8. Physics of the broadcast medium (the price of fan-in \(\Theta(N)\)).
9. A theorem on the demand spectrum (prop. 6 → theorem).
10. The "dangerous ⇒ visible" dichotomy in the non-normal case (a temporal test).

## Next stop

**`ONTORUNTIME_0`** — hands in the dirt: a minimal runtime; 30 dim-witted local cells must give rise to at least one useful certified macro-object through the EMERGE pipeline, with an honesty check (a structureless world ⇒ refusal) and level life (drift ⇒ revocation of the certificate).
