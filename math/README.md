# The math corpus and its map to public sources

## Status of the corpus

The files in this directory (Parts I–X, `FREEZE_v0.1.md`, `MANIFESTO.md`) and
`PART_VII.md` are a **free-form compilation**: known results from
several fields, rewritten in one vocabulary (levels, certificates, contracts,
repair, emerge, molt) to serve as the design rationale for the `onto` engine.
The corpus was written quickly and autonomously, **without a literature
check**; theorems were named from the inside, not from the literature.

This file is the bridge. For every named object of the corpus it gives the
public name, the canonical source (all references below were verified against
the web on 2026-08-31), and the *relation* between the corpus's version and the
source. It makes **no novelty claims** in either direction: "source not found"
means exactly that, not "new"; "same as" means the corpus should be read as a
restatement of the cited result.

The internal status labels of the corpus (proved / measured / hypothesis /
norm) are about *internal* rigor and stay as they are. Priority is a separate
question, and this file answers it: none is claimed.

Language: the entire corpus (Parts I–X, the two root documents, the map), Part VII, and all engine documents are in English.

## Relation vocabulary

| tag | meaning |
|---|---|
| **same** | the corpus's statement is the cited result, possibly renamed or specialized to our objects |
| **special case** | a restriction of the cited result (weaker exponent, finite chains, linear class, …) |
| **assembly** | a routine combination of two or more cited results; no new step |
| **framing** | the mathematics is cited; the *reading* (as a software-design law, as a currency, as a norm) is the corpus's own wording |
| **model** | not a theorem: a modeling assumption or a policy of the engine |
| **not found** | I could not locate a public source for this exact formulation; see §14 |

## Map of the corpus

| file | part | subject |
|---|---|---|
| `ontogenic_system_math_core.md` | I | the object 𝔒=(Θ,X,R,Π,C), five axioms, six primitives |
| `ontogenic_system_math_pillars.md` | II | five pillars: emerge, bounded context, integrity, ΔΘ grammar, level reconciliation |
| `ontogenic_system_math_proofs.md` | III | proofs: EDMD residual, DKW certificates, expander repair, Cheeger search, MDL |
| `ontogenic_system_math_hypotheses.md` | IV | cancer dichotomy (thm 10), two-dimensional coupling (thm 11), counterexample |
| `ontogenic_system_math_polish.md` | V | eight corrections, fragility vector κ, GL locality, thm 12 |
| `ontogenic_system_math_survival.md` | VI | killed operator, danger 𝒟(S), thm 10a′, budget |
| `ontogenic_system_math_tradeoff.md` | VII | dependency cone, thm 13 (HTN), 12a′, 12b′ |
| `ontogenic_system_math_htn.md` | VIII | multiplicative HTN, architecture surface, evolution as optimization |
| `ontogenic_system_math_wire.md` | IX | HTN-A/HTN-P, wire cost 𝒲, thm 14, prop 7′ |
| `ontogenic_system_math_layers.md` | X | the fold (max), T_q/T_f, cost of a level, five-axis object |
| `FREEZE_v0.1.md` | — | frozen summary of I–X and open problems |
| `MANIFESTO.md` | — | the twelve theses |
| `PART_VII.md` | v1/VII | growth statistics, measurement pipeline, ν-bridge, certificate algebra |

---

## 1. Part I — the object and the axioms

| corpus | public name | source | relation |
|---|---|---|---|
| Ω_t=(Θ_t,X_t): state space that changes its own ontology | constructive dynamical systems; chemical organization theory | [19] Fontana & Buss 1994; [20] Dittrich & Speroni di Fenizio 2007 | framing — the corpus's Θ is the type signature; Fontana–Buss's objects are λ-terms, Dittrich's are species sets |
| entities that spawn / die / differentiate; recursive universality (macro objects are entities) | (M,R)-systems; autopoiesis; hierarchical modularity | [21] Rosen 1991; [22] Maturana & Varela 1980; [21b] Ravasz & Barabási 2003 | framing |
| interaction kernel K(e_i,e_j,X) instead of a stored graph | kernel / metric-induced neighborhoods (folklore in particle systems, kernel methods) | — | not found as a named result; standard practice |
| **emergent closure** π∘U ≈ G∘π (commutative diagram) | lumpability of Markov chains; commuting coarse-graining as a level criterion | [23] Kemeny & Snell 1960 §6.3; [3] Pfante et al. 2014; [4] Rosas et al. 2020; [5] Hoel et al. 2013 | same — Pfante et al. compare exactly this criterion with Markovianity and informational closure |
| algorithmic-information bound K(X_t) ≲ K(R)+K(X_0)+K(η) | subadditivity / invariance of Kolmogorov complexity | [22p] Li & Vitányi, ch. 2 | same |
| six primitives (entity, rule, spawn, field, emerge, constraint) | — | — | model (language design proposal) |

## 2. Part II — five pillars

| corpus | public name | source | relation |
|---|---|---|---|
| Def. 1 closure defect η, δ_n; Lemma 1 (defect accumulation, η(L^n−1)/(L−1)) | discrete Grönwall inequality / error propagation for Lipschitz maps | any numerical-analysis text (e.g., Lütkepohl [26e] for linear case) | same |
| Def. 2 level certificate, "shelf life" n*(ε) | — | — | framing of Lemma 1 |
| Thm 1 (minimal exact level, predictive equivalence) | causal states, ε-machine minimality and uniqueness | [1] Crutchfield & Young 1989; [2] Shalizi & Crutchfield 2001 | same (cited in corpus) |
| Thm 2 (spectral gap ⇒ level; dominant eigenspace as macro-coordinates) | Perron cluster analysis of the transfer operator; metastable sets from dominant eigenvalues | [6] Schütte et al. 1999; [7] Deuflhard & Weber 2005 (PCCA+); [24] Koopman 1931 | same — this is the metastability theory of conformation dynamics |
| Lemma 2 (defect ≤ Lipschitz · cut of K) | — | — | not found as a named lemma; elementary |
| §1.4 information-bottleneck curve; levels as knees | information bottleneck; predictive IB; state-space compression | [12] Tishby, Pereira, Bialek 1999; [13] Still 2014; [14] Wolpert et al. 2014 | same |
| Algorithm EMERGE (candidates by community cut → spectral fit → MDL acceptance) | community detection + EDMD + MDL model selection | [19c] Chung 1997 (sweep); [8] Williams et al. 2015; [13p] Rissanen 1978 | assembly |
| §1.6 online certificate check; CUSUM on residuals; learn / molt / die | change-point detection | [23p] Page 1954 | same (mechanism), framing (life cycle of a level) |
| (L1)–(L2) exponential decay + doubling dimension; Lemma 3 truncation | Lieb–Robinson bounds / light cone; locality of interactions | [15] Lieb & Robinson 1972 | same in spirit (cited in corpus); the corpus's version is a deterministic Lipschitz truncation, not the quantum bound |
| Thm 3 bounded-context theorem; Cor. 2 "model ⊇ rule, not model ⊇ world" (SLM legalization) | locality of distributed computation | [15]; [1v] Linial 1992 | framing — the inequality is a truncation count; the reading is the corpus's |
| Def. 5 contracts with k-local predicates; Def. 6 ρ-damage | design by contract; self-stabilization legitimate states | [23e] Meyer 1992; [4p] Dijkstra 1974 | framing |
| Thm 4 repair convergence (potential Φ, expected O(Φ_0/γ) steps) | Foster–Lyapunov drift; Moser–Tardos resampling; self-stabilization | [1p] Foster 1953; [2p] Meyn & Tweedie 1993/2009; [3p] Moser & Tardos 2010; [4p] Dijkstra 1974 | assembly (cited in corpus) |
| §3.4 "repair correct ⇔ π(repair(damage(x)))=π(x)" | — | — | framing of lumpability |
| Thm 5 redundancy lower bounds (erasures H/(1−ρ); corruption H/(1−2ρ)) | Singleton bound; erasure-channel counting; Gilbert–Varshamov | [5p] Singleton 1964; [6p] Gilbert 1952, Varshamov 1957 | same |
| §3.6 regeneration from C_M(y) | — | — | framing (constraint as blueprint) |
| §3.7 ontological cancer, boundary surveillance, apoptosis | — | — | framing; formal content is in Part IV thm 10 |
| §4.1–4.2 ontology as signature; five mutations μ_1–μ_5; emerge = Quot_π | algebraic specification; theories over an institution; quotient types | [12v] Goguen & Burstall 1992 | framing — the corpus's μ_i are a specific grammar over the classical notions |
| Thm 6 conservativity of definitional extensions; migration functor | conservative / definitional extensions (classical logic); functorial data migration | standard logic texts; [13v] Spivak 2012 | same |
| §4.3 "central dogma" (ΔΘ only through a typed, deterministically checked channel) | — | — | model (engine policy); the biological metaphor is Crick's |
| §4.4 category **Ont**, merging as pushout, conflict = no pushout | colimits of theories / "putting theories together" | [12v] Goguen & Burstall 1992 (and Burstall & Goguen 1977) | same |
| §4.5 MDL acceptance criterion; metarules triggered by residuals | minimum description length | [13p] Rissanen 1978; [14p] Grünwald 2007 | same |
| §5.2 upward filter ŷ←(1−β)G(ŷ)+βπ(x) | Kalman / exponential filtering | [21p] Kalman 1960 | same (scalar gain) |
| Thm 7 loop stability |1−β−αγ|·‖A_G‖<1; "bureaucracy resonance" | linear feedback stability | standard control theory | same; corrected in Part III thm 7′ |
| Lemma 4 tower telescoping | — | — | elementary |
| §5.6 sibling conflict → joint emerge | — | — | model |

## 3. Part III — proofs

| corpus | public name | source | relation |
|---|---|---|---|
| quantile certificate (η,q,δ,M,L) | empirical-quantile confidence via DKW | [8p] DKW 1956, Massart 1990 | same |
| Thm 2′ defect = EDMD residual on the invariant subspace | EDMD; Galerkin projection residual | [8] Williams et al. 2015; [9] Klus et al. 2018 | same |
| Lemma 5 subspace stability (sin Θ ≤ 2‖E‖/g) | Davis–Kahan sin Θ theorem; Stewart's sep-based bound for non-normal case | [10] Davis & Kahan 1970; [11] Stewart 1973 | same |
| Thm 8 quantile certificate; M_eff for dependent data | DKW with Massart constant; blocking for β-mixing | [8p]; [9p] Yu 1994 | same (Part V ✦3 corrects the M_eff shortcut into 8a/8b — this matches Yu) |
| Cor. 3 tail routed to repair; joint viability Φ_dmg/γ < 1/λ_dmg | — | — | assembly (framing of thm 4′ + thm 8) |
| Thm 4′ repair convergence (supermartingale, optional stopping, Azuma tail) | Foster–Lyapunov; optional stopping; Azuma–Hoeffding | [1p], [2p]; [26p] Williams 1991; [24p] Azuma 1967, Hoeffding 1963 | same |
| Thm 4′′′ expander contracts; "the contract graph must be an expander" | expander codes with bit-flip decoding | [7p] Sipser & Spielman 1996 | same (cited in corpus); the *design law* reading is framing |
| §2.5 local repair ≠ local decoding | locally decodable codes lower bounds (Katz–Trevisan 2000 and successors) | not verified here | framing |
| Thm 5′-a,b | Singleton bound; erasure counting | [5p] Singleton 1964 | same |
| Cor. 4 "hierarchy is forced" | — | — | **retracted** in Part V ✦4 |
| Thm 7′ exact linear loop; Prop. 1 displacement; Thm 7′′ Lyapunov basin | linear systems with bounded input; Lyapunov functions | standard control theory | same |
| Thm 9 NP-hardness of min-conductance; Cheeger sweep with two-sided certificate | sparsest cut NP-hard; conductance NP-complete; Cheeger inequality for graphs and chains | [12p] Matula & Shahrokhi 1990; Šíma & Schaeffer 2006 (conductance); [19c] Chung 1997; [10p] Lawler & Sokal 1988; [11p] Jerrum & Sinclair 1989 | same |
| Prop. 2 MDL proxy stability (band 2c); hysteresis norm | — | — | elementary; corrected in Part V ✦6 |
| Prop. 3 spectrally visible cancer | — | — | **retracted** in Part V ✦7 in favor of thm 10 |
| §8 worked example (slow rotation + fast block) | textbook two-timescale example | — | illustration |
| §9 bridge to `resona` (matrix-free spectra, Gauss–Radau brackets) | stochastic Lanczos quadrature, Koopman lifting | not verified here (tooling note, not a claim) | model |

## 4. Part IV — cancer dichotomy and two-dimensional coupling

| corpus | public name | source | relation |
|---|---|---|---|
| Def. 9 escape rate ε(S) | conductance / bottleneck ratio of a set | [10p] Lawler & Sokal 1988; [11p] Sinclair & Jerrum 1989 | same |
| Thm 10a (unexplained almost-invariant set ⇒ eigenvalue ≥ 1−4ε on V_reg^⊥) | easy direction of Cheeger, restricted to an invariant complement | [10p]; [19c] | assembly — Rayleigh quotient of an indicator plus orthogonal decomposition |
| Thm 10b (eigenvalue near 1 ⇒ sweep set with ε(S) ≤ √(2g)) | hard direction of Cheeger with sweep | [10p]; [11p]; [19c] | same; Part VI §2.1 correctly weakens the label |
| Algorithm IMMUNE-AUDIT (Lanczos on V_reg^⊥ → sweep → EMERGE → register or quarantine) | Perron cluster analysis, deflation | [6], [7] | assembly; "immune system = discovery system" is framing |
| Prop. 4 pseudospectral visibility (spec G_B ⊂ Λ_η(𝒰)) | ε-pseudospectrum definition | [16] Trefethen & Embree 2005 | same (definition) |
| Cor. 6 safety budget 4h_max/ε_a | — | — | **retracted** in Part VI (replaced by 6′) |
| §2.1 counterexample: tensor independence ≠ freeness; mixed cumulant σ_a²σ_b² | classical vs free independence | [18p] Nica & Speicher 2006 | same (textbook) |
| Thm 11a (‖V‖_F bounds W_2 distance of spectral measures) | Hoffman–Wielandt inequality | [17p] Hoffman & Wielandt 1953 | same |
| Def. 11 freeness defect; Thm 11b (moment deviation from ⊞ bounded by mixed cumulants) | free cumulants; mixed cumulants vanish iff free; moment–cumulant formula over NC(n) | [18p] Voiculescu 1991; Nica & Speicher 2006 | assembly — multilinearity of cumulants; constants are the corpus's (corrected in Part VI 11b′) |
| Cor. 7 "spectral forensics" | — | — | **downgraded** in Part VI to a compatibility test |
| Protocol JOINT-EMERGE | — | — | model |

## 5. Part V — corrections and theorem 12

| corpus | public name | source | relation |
|---|---|---|---|
| ✦1 two defects η_op, η_rms | operator norm vs Frobenius/RMS | elementary | same |
| ✦2 Stewart form with conditioning κ_id | invariant-subspace perturbation, sep | [11] Stewart 1973 | same |
| ✦3 thm 8a/8b (i.i.d. DKW; β-mixing blocks) | [8p]; [9p] Yu 1994 | same |
| ✦5 power-bounded majorant ‖M^k‖ ≤ C_M r^k; Kreiss constant | Kreiss matrix theorem | [18] Kreiss 1962; LeVeque & Trefethen 1984; Spijker 1991 | same |
| §2 fragility κ_L = max(κ_id, C_M, pseudospectral inflation) | non-normality measures; Bauer–Fike; pseudospectra | [17] Bauer & Fike 1960; [16] Trefethen & Embree 2005 | assembly; the single-parameter packaging is the corpus's (vectorized again in Part VII §5.1) |
| (GL) geometric locality postulate | bounded-density metric graphs; VLSI/lattice models | [2v] Thompson 1979; [6v]/[7v] Bravyi–Terhal, BPT | model |
| Thm 12a separator kills global consistency | cut/separator argument | elementary; see 12a′ | — |
| Thm 12b "flat death" via BPT-type bound k·d^{1/(D−1)} ≤ CN | Bravyi–Poulin–Terhal tradeoff (2D classical: k√d = O(n)); cleaning/union lemmas | [7v] BPT 2010; [6v] Bravyi & Terhal 2009 | special case / attribution note: BPT 2010 states the classical bound for D=2 only; the general-D classical form is a folklore extension. The corpus's own 12b′ (Part VII) proves the weaker k·d^{1/D} ≤ 4Dr_0N by the union lemma (BPT 2010, Lemma 2) |
| Thm 12c hierarchical rescue under i.i.d. noise | reliable cellular automata (hierarchical self-simulation) | [8v] Gács 1986, 2001; [9v] Gray 2001 | same (cited in corpus) |
| Thm 12d depth ≥ log N / log k | fan-in counting | [1v] Linial 1992 (locality); elementary | same |
| "separation of timescales is a theorem" (light cone Ω(N^{1/D})) | light-cone / diameter bound | [15]; [2v] | same |

## 6. Part VI — survival spectrum

| corpus | public name | source | relation |
|---|---|---|---|
| Def. 12 killed operator P_S, ρ_S; Def. 13 danger 𝒟(S)=1/(1−ρ_S) | substochastic (killed) kernel; quasi-stationary distributions; survival time under the QSD is geometric with mean 1/(1−ρ) | [15p] Darroch & Seneta 1965; [16p] Collet, Martínez, San Martín 2013 | same — Lemma 6 (1)–(4) is standard QSD theory for finite reversible chains |
| Lemma 6.1 ρ_S ≥ 1−ε(S) ("conductance is a one-sided certificate") | variational principle with the indicator test function | [10p] | same |
| Lemma 6.4 uniform hazard ⇒ (1−h)^t | elementary majorization | — | same |
| Thm 10a′ with Perron function (constant 1−2h) | Rayleigh quotient with the QSD eigenfunction | [16p]; [25p] Perron–Frobenius | assembly |
| Cor. 6′ budget for L² starts; no pointwise budget without uniform hazard | — | — | assembly; honest scope note is the corpus's |
| §2.2 pseudospectrum with σ_min(T) | pseudospectra; Bauer–Fike | [16]; [17] | same |
| §3 Γ=(γ_int, γ_align); four-regime plane; Cor. 7′ compatibility test | — | — | framing over thm 11a/11b; the corpus itself lowers "forensics" to "compatibility" |
| Lemma 7 (|κ_n| ≤ 16^p max(1,M)^p) | Möbius inversion on NC(n), Catalan bounds | [18p] Nica & Speicher 2006 | same |
| §5.3 generality ladder (finite → countable → compact positive → Polish) | Krein–Rutman; Doeblin; QSD on general spaces | [16p] | same (program, not result) |

## 7. Part VII (tradeoff) — dependency cone and HTN

| corpus | public name | source | relation |
|---|---|---|---|
| dependency cone 𝒟(v,T); Lemma A |𝒟| ≤ (Δ+1)^T; Lemma B geometric displacement | T-round locality (the output depends only on the radius-T neighborhood); light cone | [1v] Linial 1992; [15] Lieb & Robinson 1972 | same |
| Def. 14/14′ "live semantics", essential causal support | sensitivity / influence of an input on an output (Boolean function influence; causal cone) | standard | same |
| **Thm 13 (HTN)** L·log s + log T + log R/r_0 ≥ (1/D) log N; floor T ≥ log N / log(Δ+1) | reach-vs-time counting: to touch N^{1/D} cells you need T·(step size) ≥ N^{1/D}; fan-in lower bound | [1v]; [2v] Thompson 1979/1980 (information-flow across cuts); [3v] Leiserson 1985 (trees buy log depth) | assembly — the inequality is Lemma B logarithmed; the three-currency reading is framing |
| Thm 12a′ "a separator kills consistency, not memory" | cut argument on the causal cone | elementary | same |
| Thm 12b′ k_code·d^{1/D} ≤ 4Dr_0N via union lemma | union-of-correctable-regions lemma; tiling by correctable cubes | [7v] BPT 2010 Lemma 2; [6v] Bravyi & Terhal 2009 (cleaning lemma) | special case (weaker exponent than BPT, self-contained proof; corpus says so) |
| §5.1 fragility vector | see Part V §2 | — | framing |
| §5.2 normalized Γ ∈ [0,1]² | — | — | framing |

## 8. Part VIII — multiplicative HTN and the architecture surface

| corpus | public name | source | relation |
|---|---|---|---|
| Cor. 9 𝓗·𝓣·𝓡 ≥ cN^{1/D} | exponentiated Lemma B | — | same (retracted as canonical in Part X in favor of the max form) |
| "hierarchy is the only currency with a logarithmic price tag" | tree networks give O(log N) diameter; small-world navigation | [3v] Leiserson 1985; [20v] Watts & Strogatz 1998; [14v] Kleinberg 2000 | framing |
| architecture surface; chemistry / nerves / hormones / organs as pure strategies | — | — | model |
| Prop. 5 asymptotic dominance of hierarchy; Prop. 6 hybrids from demand spectrum | — | — | model (the corpus labels them so) |
| missing capacity axis 𝓑 | bandwidth vs reachability | see Part IX | — |

## 9. Part IX — wire cost

| corpus | public name | source | relation |
|---|---|---|---|
| HTN-P, currency 𝒲 = total wire length; "hierarchy secretly smuggled nonlocality" | VLSI layout cost models (area = wire); Rent's rule | [2v] Thompson 1979/1980; [4v] Landman & Russo 1971; [5v] Leighton 1992 | same (model) |
| **Thm 14** tower wire O(N r_0) for D ≥ 2 (geometric series dominated by the bottom), latency O(log N) | H-tree / fat-tree layouts; Leiserson's universality of fat-trees under a hardware-volume budget | [3v] Leiserson 1985; [5v] Leighton 1992 | same — note: Leiserson's theorem is stated as volume-universality with polylog slowdown, not as "O(N) wire, log depth"; the O(N) wire sum for a tree layout is the classical H-tree calculation in [5v] |
| **Prop. 7′** T·Cap(C) ≥ I_cross(C) for every cut; averaging over a family of parallel cuts | Thompson's bisection-width × time ≥ information-flow argument (AT² bound) | [2v] Thompson 1979 (STOC), 1980 (thesis) | same — this is the AT² argument with T·(#wires crossing) in place of A |
| Cor. 11 all-to-all infrastructure Ω(N^{1+1/D}) | wire-area lower bounds for high-bisection networks | [2v]; [5v] | same |
| §3.1 "fast global cargo can only be summaries"; transport forces compression; emerge = compression + adaptivity | — | — | framing |
| tariff table (flat / all-to-all / tower / single nerve / hormone) | network cost comparisons | [5v] | framing |

## 10. Part X — the fold, two times, cost of a level

| corpus | public name | source | relation |
|---|---|---|---|
| Thm 13′ fold: 𝓣·max(𝓗,𝓡) ≥ cN^{1/D} | direct reading of Lemma B | — | same (the corpus's own correction of Cor. 9) |
| "the floor is the price of bounded degree; broadcast buys O(1)" | fan-in vs broadcast media | elementary | same |
| Thm 15 staleness T_f ≥ 𝓗/𝓡 (cache without long channels) | light cone applied to the cache cell | [15]; [1v] | same |
| Thm 16 split query latency T_q vs freshness T_f | memory-hierarchy / cache models; consistency-vs-latency tradeoffs | [26v] Aggarwal & Vitter 1988 (two-level I/O model); Aggarwal–Alpern–Chandra–Snir 1987 (hierarchical memory, not verified here); [10v] Gilbert & Lynch 2002; [11v] Abadi 2012 (PACELC) | framing — the corpus itself calls it "CAP-like" |
| Cor. 10 staleness bounded forever for contracting levels (η/(1−L)) | Lemma 1 again | — | same |
| Prop. 8 opex of the tower O(N) per tick | — | — | model (labeled so) |
| §5 hybrids only from the demand spectrum | — | — | model |
| five-axis object (𝓗,T_q,T_f,𝓡,𝓑) + 𝓔 | — | — | framing |

## 11. MANIFESTO and FREEZE

The twelve theses are readings of the rows above; none is a mathematical
claim on its own. Thesis 12 ("industry already does this blind") names
reconciliation loops, chaos engineering, canaries, SLOs — these are
engineering practices, cited in §13 where the engine uses them.

## 12. v1/math/PART_VII — engine-side measurements

| corpus | public name | source | relation |
|---|---|---|---|
| §1 growth task, oracle model, CEGIS loop (Defs. 1–3) | counterexample-guided inductive synthesis; oracle-guided synthesis | [5e] Solar-Lezama et al. 2006, 2008; [4e] Jha et al. 2010; [29e] Gulwani et al. 2017 | same |
| §1.2 models A (memoryless) vs B (p_t = p_0 + β(t−1)); MLE, LR; chi-bar threshold for β on the boundary | geometric-trial models; likelihood ratio under boundary conditions | [20p] Self & Liang 1987 | same (statistics); the measurement is the corpus's |
| §1.3 model strength shifts p_0 | — | — | measured; no theorem |
| Norm 1 (cheat sheet as rent-paying lessons) | — | — | model (engine policy) |
| §2.1 organism as a Markov operator P^{g,ν}; empirical transition matrix from `handle` | empirical Markov chain estimation; Koopman/transfer operator of a deterministic map under random input | [24] Koopman 1931; standard | same |
| §2.2 "swamp" calibration: ρ_S, 𝒟(S), E_qsd[τ], conductance certificate, hazard majorant | QSD theory on a 5-state chain | [15p]; [16p] | same (numerical check of the cited facts on a toy) |
| §2.4–2.5 spectral step: VAR(1) fit by OLS, spectral radius by power iteration, hold-out R², lag-2 vs lag-1 Markov test; two-component detector (λ→1 vs var→0) | vector autoregression; EDMD with a linear dictionary; Perron cluster idea | [26e] Lütkepohl 2005; [8] Williams et al. 2015; [6] | assembly — a VAR(1) drift detector calibrated on a healthy window |
| §3 Def. 5 quantile certificate; Thm VII.1′ sequential composition (η_B + L_B η_A, q_A+q_B−1, δ_A+δ_B) | DKW; Fréchet (Boole–Fréchet) inequality; union bound | [8p]; [19p] Fréchet 1935 | assembly |
| §6 kernel linear in the load: P^{g,ν} = Σ ν(e) K_e | mixture of deterministic kernels | elementary | same |
| Thm VII.2 (a) TV shift ≤ TV(ν′,ν); (b) q′ ≥ 1 − C(1−q) with C = sup ν′/ν; (c) ‖ΔP‖ ≤ 2TV | convexity of TV; change of measure / likelihood-ratio domination; Bauer–Fike / Weyl for the honest caveat | elementary; [17] Bauer & Fike 1960 | same |
| ν-drift monitor in the warden | drift detection with a calibrated threshold | [23p] Page 1954 (CUSUM family) | assembly |

## 13. Engine mechanisms of v1 (same treatment)

| v1 mechanism | public name | source | relation |
|---|---|---|---|
| genome: guards, bodies, `post`, `conserves`, invariants; proof obligations | Event-B (events with guards/actions, invariants, INV/GRD obligations), Rodin | [1e] Abrial 2010; [2e] Abrial et al. 2010 | same (specialized to a small expression language) |
| design-by-contract semantics of `post` | [23e] Meyer 1992 | same |
| one genome → Go / Python / Node phenotypes; core knows no language (I1) | model-driven engineering, domain-specific modeling with full code generation; Event-B code generators | [30e] Schmidt 2006; Kelly & Tolvanen 2008; [3e] Méry & Singh 2011 (EB2ALL) | same |
| SMT court over Expr (z3) | SMT-based verification | [21e] de Moura & Bjørner 2008; [20e] Leino 2010 (Dafny, for the style) | same |
| mutants calibrate the contract; equivalent mutants proved by SMT | mutation testing; specification mutation; equivalent-mutant detection | [9e] DeMillo, Lipton, Sayward 1978; [11e] Ammann & Black 1999; [12e] Sullivan et al. 2017 (MuAlloy); [10e] Papadakis et al. 2015 | same (applied to contracts) |
| counterexample interview (distinguishing input → question to the operator) | oracle-guided inductive synthesis with distinguishing inputs | [4e] Jha et al. 2010; [22e] Clarke et al. 2000 (CEGAR, for the loop shape) | same (applied to contract underdetermination) |
| mutgate: semantic diff of old vs new rule, `ack_behavior_change` | semantic differencing; regression verification | [25e] Jackson & Ladd 1994; [6e] Lahiri et al. 2012 (SymDiff); [7e] Godlin & Strichman 2009 | same |
| CEGIS ribosome with SLM; LLM + verifier loops | sketching/CEGIS; SyGuS; LLM-with-verifier systems | [5e]; [27e] Alur et al. 2013; [15e] Baldur 2023; [16e] Clover 2024; [17e] Lemur 2024 | same |
| skills judged by properties on fuzz; "teeth of completeness" | property-based testing; invariant inference by traces (for contrast) | standard (QuickCheck-family); [28e] Ernst et al. 2001 (Daikon) | same |
| event log as truth, replay, snapshots | event sourcing | [19e] Fowler 2005 | same |
| membrane: assumptions as Expr monitors, drift → revoke | runtime verification; assume-guarantee; circuit breaker | [13e] Leucker & Schallhart 2009; [24e] Pnueli 1985; [25v] Nygard 2007 | same |
| placer: warm hot paths by measured heat, evict cold | profile-guided / tiered JIT compilation | [14e] Paleczny et al. 2001 (HotSpot C2; tiering itself is later HotSpot work) | framing ("architecture as a control loop") |
| growing a dialect with a model against conformance + judge | neural transcompilation certified by tests | [18e] Rozière et al. 2020 | same |
| attest: guarantee passport, weakest seam, honest section | assurance cases (GSN) | [22v] Kelly & Weaver 2004 | same |
| warden: monitor → analyze → act loop; rights ladder | autonomic computing (MAPE-K); organic computing observer/controller | [15v] Kephart & Chess 2003; [16v] Müller-Schloer et al. 2011 | same |
| DECISIONS.md, PREDICTIONS.md, SCARS.md | architecture decision records; preregistration | [24v] Nygard 2011; [23v] Nosek et al. 2018 | same (preregistration transferred to engineering) |
| Alloy-style lightweight formal modeling (for contrast with the interpreter-first choice) | [8e] Jackson 2006 | — |

## 14. Source not found (which is not "new")

Formulations for which I did not locate a public statement in this exact
form. Each has an obvious elementary proof or is a naming choice; the list
exists so that a later reader knows where to look, not to mark priority.

- Lemma 2 of Part II (closure defect bounded by the K-cut).
- The two-component corruption detector (spectral radius for metastability
  plus variance for freeze) as a named pair (v1/VII §2.4).
- The fold form 𝓣·max(𝓗,𝓡) ≥ cN^{1/D} as a stated architectural inequality
  (Part X thm 13′) — the content is Lemma B; the packaging is the corpus's.
- Γ = (interaction, alignment) as a two-coordinate coupling object (Part VI §3).
- "Danger" 𝒟(S) = 1/(1−ρ_S) as a *name*; the quantity is the QSD mean
  survival time [15p][16p].
- The candidate open question ✦7 (Part V): "when does predictive closure imply
  a detectable structural bottleneck?" — I found no source answering it; it
  may well exist under the vocabulary of metastability vs graph cuts.

## 15. Candidates (our taxonomy, not a claim)

Kept deliberately short. A row leaves this list the moment a source is found
and moves to the tables above.

| candidate | form | demotion condition |
|---|---|---|
| the vocabulary itself: one set of names (certificate, level, contract, repair, emerge, molt) spanning computational mechanics, metastability, coding theory, self-stabilization, MDL, and light-cone bounds, used as a software-design rationale | synthesis | a prior design theory for software with the same span (organic/autonomic computing are the closest and are cited) |
| "the contract graph must be an expander" as a design law for software integrity | hypothesis about software, untested | any prior transfer of Sipser–Spielman into software architecture |
| ✦7: predictive closure vs structural bottleneck | open question | a published answer |
| the engine as a measurable Markov operator conditional on load ν, with certificates carrying (ν, δ, M) | measurement discipline | a prior runtime-verification framework stating certificates conditional on the input distribution in this form |

---

## References

All entries verified against the web on 2026-08-31. Where my recollection was
wrong the correction is noted.

### Dynamical systems, emergence, spectra
- [1] J. P. Crutchfield, K. Young, "Inferring statistical complexity", Phys. Rev. Lett. 63(2):105–108, 1989. doi:10.1103/PhysRevLett.63.105
- [2] C. R. Shalizi, J. P. Crutchfield, "Computational mechanics: pattern and prediction, structure and simplicity", J. Stat. Phys. 104(3–4):817–879, 2001. doi:10.1023/A:1010388907793
- [3] O. Pfante, N. Bertschinger, E. Olbrich, N. Ay, J. Jost, "Comparison between different methods of level identification", Adv. Complex Syst. 17(2):1450007, 2014. doi:10.1142/S0219525914500076 (compares lumpability, Markovianity, informational closure, predictive efficiency)
- [4] F. E. Rosas et al., "Reconciling emergences: an information-theoretic approach to identify causal emergence in multivariate data", PLoS Comput. Biol. 16(12):e1008289, 2020. doi:10.1371/journal.pcbi.1008289
- [5] E. P. Hoel, L. Albantakis, G. Tononi, "Quantifying causal emergence shows that macro can beat micro", PNAS 110(49):19790–19795, 2013. doi:10.1073/pnas.1314922110
- [6] Ch. Schütte, A. Fischer, W. Huisinga, P. Deuflhard, "A direct approach to conformational dynamics based on hybrid Monte Carlo", J. Comput. Phys. 151(1):146–168, 1999. doi:10.1006/jcph.1999.6231
- [7] P. Deuflhard, M. Weber, "Robust Perron cluster analysis in conformation dynamics", Linear Algebra Appl. 398:161–184, 2005. doi:10.1016/j.laa.2004.10.026
- [8] M. O. Williams, I. G. Kevrekidis, C. W. Rowley, "A data-driven approximation of the Koopman operator: extending dynamic mode decomposition", J. Nonlinear Sci. 25(6):1307–1346, 2015. doi:10.1007/s00332-015-9258-5
- [9] S. Klus, F. Nüske, P. Koltai, H. Wu, I. Kevrekidis, C. Schütte, F. Noé, "Data-driven model reduction and transfer operator approximation", J. Nonlinear Sci. 28(3):985–1010, 2018. doi:10.1007/s00332-017-9437-7
- [10] C. Davis, W. M. Kahan, "The rotation of eigenvectors by a perturbation. III", SIAM J. Numer. Anal. 7(1):1–46, 1970. doi:10.1137/0707001
- [11] G. W. Stewart, "Error and perturbation bounds for subspaces associated with certain eigenvalue problems", SIAM Review 15(4):727–764, 1973. doi:10.1137/1015095
- [12] N. Tishby, F. C. Pereira, W. Bialek, "The information bottleneck method", Proc. 37th Allerton Conf., pp. 368–377, 1999. arXiv:physics/0004057
- [13] S. Still, "Information bottleneck approach to predictive inference", Entropy 16(2):968–989, 2014. doi:10.3390/e16020968
- [14] D. H. Wolpert, J. A. Grochow, E. Libby, S. DeDeo, "Optimal high-level descriptions of dynamical systems", arXiv:1409.7403 (2014; v2 2015; SFI WP 15-06-017). No journal version found.
- [15] E. H. Lieb, D. W. Robinson, "The finite group velocity of quantum spin systems", Commun. Math. Phys. 28(3):251–257, 1972. doi:10.1007/BF01645779
- [16] L. N. Trefethen, M. Embree, *Spectra and Pseudospectra: The Behavior of Nonnormal Matrices and Operators*, Princeton University Press, 2005.
- [17] F. L. Bauer, C. T. Fike, "Norms and exclusion theorems", Numer. Math. 2:137–141, 1960. doi:10.1007/BF01386217
- [18] H.-O. Kreiss, "Über die Stabilitätsdefinition für Differenzengleichungen die partielle Differentialgleichungen approximieren", BIT 2(3):153–181, 1962; R. J. LeVeque, L. N. Trefethen, "On the resolvent condition in the Kreiss matrix theorem", BIT 24(4):584–591, 1984; M. N. Spijker, "On a conjecture by LeVeque and Trefethen related to the Kreiss matrix theorem", BIT 31(3):551–555, 1991 (sharp constant eN).
- [19] W. Fontana, L. W. Buss, "'The arrival of the fittest': toward a theory of biological organization", Bull. Math. Biol. 56(1):1–64, 1994. doi:10.1007/BF02458289
- [20] P. Dittrich, P. Speroni di Fenizio, "Chemical organisation theory", Bull. Math. Biol. 69(4):1199–1231, 2007. doi:10.1007/s11538-006-9130-8
- [21] R. Rosen, *Life Itself*, Columbia University Press, 1991.
- [21b] E. Ravasz, A.-L. Barabási, "Hierarchical organization in complex networks", Phys. Rev. E 67:026112, 2003. doi:10.1103/PhysRevE.67.026112
- [22] H. R. Maturana, F. J. Varela, *Autopoiesis and Cognition: The Realization of the Living*, Boston Studies in the Philosophy of Science 42, D. Reidel, 1980. doi:10.1007/978-94-009-8947-4
- [23] J. G. Kemeny, J. L. Snell, *Finite Markov Chains*, Van Nostrand 1960; 2nd ed. Springer 1976, §6.3 "Lumpable chains".
- [24] B. O. Koopman, "Hamiltonian systems and transformation in Hilbert space", PNAS 17(5):315–318, 1931. doi:10.1073/pnas.17.5.315

### Probability, coding, repair, survival
- [1p] F. G. Foster, "On the stochastic matrices associated with certain queuing processes", Ann. Math. Statist. 24(3):355–360, 1953. doi:10.1214/aoms/1177728976
- [2p] S. P. Meyn, R. L. Tweedie, *Markov Chains and Stochastic Stability*, Springer 1993; 2nd ed. Cambridge University Press 2009.
- [3p] R. A. Moser, G. Tardos, "A constructive proof of the general Lovász Local Lemma", J. ACM 57(2), art. 11, 2010. doi:10.1145/1667053.1667060
- [4p] E. W. Dijkstra, "Self-stabilizing systems in spite of distributed control", Commun. ACM 17(11):643–644, 1974. doi:10.1145/361179.361202
- [5p] R. C. Singleton, "Maximum distance q-nary codes", IEEE Trans. Inf. Theory 10(2):116–118, 1964. doi:10.1109/TIT.1964.1053661
- [6p] E. N. Gilbert, "A comparison of signalling alphabets", Bell Syst. Tech. J. 31(3):504–522, 1952. doi:10.1002/j.1538-7305.1952.tb01393.x; R. R. Varshamov, "Estimate of the number of signals in error correcting codes", Dokl. Akad. Nauk SSSR 117:739–741, 1957.
- [7p] M. Sipser, D. A. Spielman, "Expander codes", IEEE Trans. Inf. Theory 42(6):1710–1722, 1996. doi:10.1109/18.556667
- [8p] A. Dvoretzky, J. Kiefer, J. Wolfowitz, "Asymptotic minimax character of the sample distribution function and of the classical multinomial estimator", Ann. Math. Statist. 27(3):642–669, 1956. doi:10.1214/aoms/1177728174; P. Massart, "The tight constant in the Dvoretzky–Kiefer–Wolfowitz inequality", Ann. Probab. 18(3):1269–1283, 1990. doi:10.1214/aop/1176990746
- [9p] B. Yu, "Rates of convergence for empirical processes of stationary mixing sequences", Ann. Probab. 22(1):94–116, 1994. doi:10.1214/aop/1176988849
- [10p] G. F. Lawler, A. D. Sokal, "Bounds on the L² spectrum for Markov chains and Markov processes: a generalization of Cheeger's inequality", Trans. Amer. Math. Soc. 309(2):557–580, 1988. doi:10.1090/S0002-9947-1988-0930082-9
- [11p] M. Jerrum, A. Sinclair, "Approximating the permanent", SIAM J. Comput. 18(6):1149–1178, 1989. doi:10.1137/0218077; A. Sinclair, M. Jerrum, "Approximate counting, uniform generation and rapidly mixing Markov chains", Inf. Comput. 82(1):93–133, 1989. doi:10.1016/0890-5401(89)90067-9
- [12p] D. W. Matula, F. Shahrokhi, "Sparsest cuts and bottlenecks in graphs", Discrete Appl. Math. 27(1–2):113–123, 1990. doi:10.1016/0166-218X(90)90133-W (NP-hardness of sparsest cut). For minimum conductance specifically: J. Šíma, S. E. Schaeffer, "On the NP-completeness of some graph cluster measures", SOFSEM 2006, LNCS 3831, pp. 530–537. doi:10.1007/11611257_51
- [13p] J. Rissanen, "Modeling by shortest data description", Automatica 14(5):465–471, 1978. doi:10.1016/0005-1098(78)90005-5
- [14p] P. D. Grünwald, *The Minimum Description Length Principle*, MIT Press, 2007.
- [15p] J. N. Darroch, E. Seneta, "On quasi-stationary distributions in absorbing discrete-time finite Markov chains", J. Appl. Probab. 2(1):88–100, 1965. doi:10.2307/3211876
- [16p] P. Collet, S. Martínez, J. San Martín, *Quasi-Stationary Distributions: Markov Chains, Diffusions and Dynamical Systems*, Springer, 2013. doi:10.1007/978-3-642-33131-2
- [17p] A. J. Hoffman, H. W. Wielandt, "The variation of the spectrum of a normal matrix", Duke Math. J. 20(1):37–39, 1953. doi:10.1215/S0012-7094-53-02004-3
- [18p] D. Voiculescu, "Limit laws for random matrices and free products", Invent. Math. 104(1):201–220, 1991. doi:10.1007/BF01245072; A. Nica, R. Speicher, *Lectures on the Combinatorics of Free Probability*, LMS Lecture Note Series 335, Cambridge University Press, 2006.
- [19p] M. Fréchet, "Généralisation du théorème des probabilités totales", Fund. Math. 25:379–387, 1935.
- [20p] S. G. Self, K.-Y. Liang, "Asymptotic properties of maximum likelihood estimators and likelihood ratio tests under nonstandard conditions", J. Amer. Statist. Assoc. 82(398):605–610, 1987. doi:10.1080/01621459.1987.10478472
- [21p] R. E. Kalman, "A new approach to linear filtering and prediction problems", Trans. ASME, J. Basic Eng. 82(1):35–45, 1960. doi:10.1115/1.3662552
- [22p] M. Li, P. Vitányi, *An Introduction to Kolmogorov Complexity and Its Applications*, Springer, 3rd ed. 2008 / 4th ed. 2019. doi:10.1007/978-3-030-11298-1
- [23p] E. S. Page, "Continuous inspection schemes", Biometrika 41(1/2):100–115, 1954. doi:10.1093/biomet/41.1-2.100
- [24p] K. Azuma, "Weighted sums of certain dependent random variables", Tohoku Math. J. 19(3):357–367, 1967. doi:10.2748/tmj/1178243286; W. Hoeffding, "Probability inequalities for sums of bounded random variables", J. Amer. Statist. Assoc. 58(301):13–30, 1963. doi:10.1080/01621459.1963.10500830
- [25p] O. Perron, "Zur Theorie der Matrices", Math. Ann. 64:248–263, 1907. doi:10.1007/BF01449896; G. Frobenius, "Über Matrizen aus nicht negativen Elementen", Sitzungsber. Preuss. Akad. Wiss. Berlin, 1912, pp. 456–477; textbook: C. D. Meyer, *Matrix Analysis and Applied Linear Algebra*, SIAM, 2000, ch. 8.
- [26p] D. Williams, *Probability with Martingales*, Cambridge University Press, 1991 (Thm 10.10, optional stopping).

### Locality, VLSI, hierarchy, codes, systems
- [1v] N. Linial, "Locality in distributed graph algorithms", SIAM J. Comput. 21(1):193–201, 1992. doi:10.1137/0221015
- [2v] C. D. Thompson, "Area-time complexity for VLSI", Proc. 11th ACM STOC, pp. 81–88, 1979. doi:10.1145/800135.804401; C. D. Thompson, *A Complexity Theory for VLSI*, PhD thesis, CMU-CS-80-140, 1980.
- [3v] C. E. Leiserson, "Fat-trees: universal networks for hardware-efficient supercomputing", IEEE Trans. Computers C-34(10):892–901, 1985. doi:10.1109/TC.1985.6312192. Correction to my recollection: the theorem is stated as universality under a hardware-*volume* budget with polylogarithmic slowdown, not as "O(N) wire, log depth".
- [4v] B. S. Landman, R. L. Russo, "On a pin versus block relationship for partitions of logic graphs", IEEE Trans. Computers C-20(12):1469–1479, 1971. doi:10.1109/T-C.1971.223159 (Rent's rule)
- [5v] F. T. Leighton, *Introduction to Parallel Algorithms and Architectures: Arrays, Trees, Hypercubes*, Morgan Kaufmann, 1992.
- [6v] S. Bravyi, B. M. Terhal, "A no-go theorem for a two-dimensional self-correcting quantum memory based on stabilizer codes", New J. Phys. 11:043029, 2009. doi:10.1088/1367-2630/11/4/043029 (cleaning lemma; restriction lemma). Correction: the union lemma is not here but in [7v].
- [7v] S. Bravyi, D. Poulin, B. Terhal, "Tradeoffs for reliable quantum information storage in 2D systems", Phys. Rev. Lett. 104:050503, 2010. doi:10.1103/PhysRevLett.104.050503. States kd² = O(n) (2D quantum), k√d = O(n) (2D classical), k ≤ cn/d^{2/(D−1)} (D-dim quantum); Lemma 2 = union of separated correctable regions is correctable. Correction: the general-D *classical* bound k·d^{1/(D−1)} = O(n) used in Part V is not stated in this paper.
- [8v] P. Gács, "Reliable computation with cellular automata", J. Comput. Syst. Sci. 32(1):15–78, 1986. doi:10.1016/0022-0000(86)90002-4; P. Gács, "Reliable cellular automata with self-organization", J. Stat. Phys. 103(1–2):45–267, 2001. doi:10.1023/A:1004823720305
- [9v] L. F. Gray, "A reader's guide to Gács's 'positive rates' paper", J. Stat. Phys. 103(1–2):1–44, 2001. doi:10.1023/A:1004824203467
- [10v] E. A. Brewer, "Towards robust distributed systems (abstract)", Proc. 19th ACM PODC, p. 7, 2000. doi:10.1145/343477.343502; S. Gilbert, N. Lynch, "Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services", ACM SIGACT News 33(2):51–59, 2002. doi:10.1145/564585.564601
- [11v] D. J. Abadi, "Consistency tradeoffs in modern distributed database system design: CAP is only part of the story", IEEE Computer 45(2):37–42, 2012. doi:10.1109/MC.2012.33 (PACELC)
- [12v] J. A. Goguen, R. M. Burstall, "Institutions: abstract model theory for specification and programming", J. ACM 39(1):95–146, 1992. doi:10.1145/147508.147524 (theories over an institution form a category; colimits exist when signature colimits do; "putting theories together" originates in Burstall & Goguen 1977)
- [13v] D. I. Spivak, "Functorial data migration", Inf. Comput. 217:31–51, 2012. doi:10.1016/j.ic.2012.05.001
- [14v] J. M. Kleinberg, "Navigation in a small world", Nature 406:845, 2000. doi:10.1038/35022643 (the hierarchical variant is Kleinberg, NIPS 2001)
- [15v] J. O. Kephart, D. M. Chess, "The vision of autonomic computing", IEEE Computer 36(1):41–50, 2003. doi:10.1109/MC.2003.1160055 (the acronym MAPE-K is from IBM's later Architectural Blueprint)
- [16v] C. Müller-Schloer, H. Schmeck, T. Ungerer (eds.), *Organic Computing — A Paradigm Shift for Complex Systems*, Birkhäuser, 2011. doi:10.1007/978-3-0348-0130-0
- [17v] R. M. Tanner, "A recursive approach to low complexity codes", IEEE Trans. Inf. Theory 27(5):533–547, 1981. doi:10.1109/TIT.1981.1056404
- [18v] G. D. Forney, Jr., *Concatenated Codes*, MIT Press, 1966.
- [19c] F. R. K. Chung, *Spectral Graph Theory*, CBMS 92, AMS, 1997 (ch. 2: Cheeger inequality and the sweep).
- [20v] D. J. Watts, S. H. Strogatz, "Collective dynamics of 'small-world' networks", Nature 393:440–442, 1998. doi:10.1038/30918
- [22v] T. Kelly, R. Weaver, "The Goal Structuring Notation — a safety argument notation", Proc. DSN 2004 Workshop on Assurance Cases, 2004.
- [23v] B. A. Nosek, C. R. Ebersole, A. C. DeHaven, D. T. Mellor, "The preregistration revolution", PNAS 115(11):2600–2606, 2018. doi:10.1073/pnas.1708274114
- [24v] M. Nygard, "Documenting architecture decisions", Cognitect blog, 2011-11-15. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- [25v] M. T. Nygard, *Release It! Design and Deploy Production-Ready Software*, Pragmatic Bookshelf, 2007 (2nd ed. 2018).
- [26v] A. Aggarwal, J. S. Vitter, "The input/output complexity of sorting and related problems", Commun. ACM 31(9):1116–1127, 1988. doi:10.1145/48529.48535 (two-level model; the multilevel hierarchical-memory model is Aggarwal, Alpern, Chandra, Snir, STOC 1987 — not verified here)

### Software engineering
- [1e] J.-R. Abrial, *Modeling in Event-B: System and Software Engineering*, Cambridge University Press, 2010.
- [2e] J.-R. Abrial, M. Butler, S. Hallerstede, T. S. Hoang, F. Mehta, L. Voisin, "Rodin: an open toolset for modelling and reasoning in Event-B", STTT 12(6):447–466, 2010. doi:10.1007/s10009-010-0145-y
- [3e] D. Méry, N. K. Singh, "Automatic code generation from Event-B models", Proc. SoICT '11, pp. 179–188, 2011. doi:10.1145/2069216.2069252 (EB2ALL)
- [4e] S. Jha, S. Gulwani, S. A. Seshia, A. Tiwari, "Oracle-guided component-based program synthesis", ICSE 2010, pp. 215–224. doi:10.1145/1806799.1806833
- [5e] A. Solar-Lezama, L. Tancau, R. Bodík, S. A. Seshia, V. Saraswat, "Combinatorial sketching for finite programs", ASPLOS XII, pp. 404–415, 2006. doi:10.1145/1168857.1168907; A. Solar-Lezama, *Program Synthesis by Sketching*, PhD thesis, UC Berkeley, UCB/EECS-2008-176, 2008.
- [6e] S. K. Lahiri, C. Hawblitzel, M. Kawaguchi, H. Rebêlo, "SymDiff: a language-agnostic semantic diff tool for imperative programs", CAV 2012, LNCS 7358, pp. 712–717. doi:10.1007/978-3-642-31424-7_54
- [7e] B. Godlin, O. Strichman, "Regression verification", DAC 2009, pp. 466–471. doi:10.1145/1629911.1630034; journal version STVR 23(3):241–258, 2013. doi:10.1002/stvr.1472
- [8e] D. Jackson, *Software Abstractions: Logic, Language, and Analysis*, MIT Press, 2006; revised ed. 2012/2016.
- [9e] R. A. DeMillo, R. J. Lipton, F. G. Sayward, "Hints on test data selection: help for the practicing programmer", IEEE Computer 11(4):34–41, 1978.
- [10e] M. Papadakis, Y. Jia, M. Harman, Y. Le Traon, "Trivial compiler equivalence: a large scale empirical study of a simple, fast and effective equivalent mutant detection technique", ICSE 2015, pp. 936–946.
- [11e] P. Ammann, P. E. Black, "A specification-based coverage metric to evaluate test sets", HASE 1999, pp. 239–248. doi:10.1109/HASE.1999.809499
- [12e] A. Sullivan, K. Wang, R. Nokhbeh Zaeem, S. Khurshid, "Automated test generation and mutation testing for Alloy", ICST 2017, pp. 264–275. doi:10.1109/ICST.2017.31 (MuAlloy)
- [13e] M. Leucker, C. Schallhart, "A brief account of runtime verification", J. Log. Algebr. Program. 78(5):293–303, 2009. doi:10.1016/j.jlap.2008.08.004
- [14e] M. Paleczny, C. Vick, C. Click, "The Java HotSpot server compiler", USENIX JVM '01, 2001. Correction: this is the C2 compiler paper, not the source for tiered compilation (later HotSpot releases).
- [15e] E. First, M. N. Rabe, T. Ringer, Y. Brun, "Baldur: whole-proof generation and repair with large language models", ESEC/FSE 2023. doi:10.1145/3611643.3616243
- [16e] C. Sun, Y. Sheng, O. Padon, C. Barrett, "Clover: closed-loop verifiable code generation", SAIV 2024, LNCS 14846, pp. 134–155. doi:10.1007/978-3-031-65112-0_7 (arXiv:2310.17807)
- [17e] H. Wu, C. Barrett, N. Narodytska, "Lemur: integrating large language models in automated program verification", ICLR 2024. https://openreview.net/forum?id=Q3YaCghZNt
- [18e] B. Rozière, M.-A. Lachaux, L. Chanussot, G. Lample, "Unsupervised translation of programming languages", NeurIPS 33, 2020 (TransCoder).
- [19e] M. Fowler, "Event Sourcing", martinfowler.com, 2005-12-12. https://martinfowler.com/eaaDev/EventSourcing.html
- [20e] K. R. M. Leino, "Dafny: an automatic program verifier for functional correctness", LPAR-16, LNCS 6355, pp. 348–370, 2010.
- [21e] L. de Moura, N. Bjørner, "Z3: an efficient SMT solver", TACAS 2008, LNCS 4963, pp. 337–340. doi:10.1007/978-3-540-78800-3_24
- [22e] E. M. Clarke, O. Grumberg, S. Jha, Y. Lu, H. Veith, "Counterexample-guided abstraction refinement", CAV 2000, LNCS 1855, pp. 154–169. doi:10.1007/10722167_15
- [23e] B. Meyer, "Applying 'Design by Contract'", IEEE Computer 25(10):40–51, 1992. doi:10.1109/2.161279
- [24e] A. Pnueli, "In transition from global to modular temporal reasoning about programs", in K. R. Apt (ed.), *Logics and Models of Concurrent Systems*, NATO ASI F13, Springer, pp. 123–144, 1985. doi:10.1007/978-3-642-82453-1_5
- [25e] D. Jackson, D. A. Ladd, "Semantic Diff: a tool for summarizing the effects of modifications", ICSM 1994, pp. 243–252.
- [26e] H. Lütkepohl, *New Introduction to Multiple Time Series Analysis*, Springer, 2005 (ch. 3, VAR estimation by OLS). doi:10.1007/978-3-540-27752-1
- [27e] R. Alur et al., "Syntax-guided synthesis", FMCAD 2013, pp. 1–8.
- [28e] M. D. Ernst, J. Cockrell, W. G. Griswold, D. Notkin, "Dynamically discovering likely program invariants to support program evolution", IEEE TSE 27(2):99–123, 2001 (Daikon).
- [29e] S. Gulwani, O. Polozov, R. Singh, "Program Synthesis", Foundations and Trends in Programming Languages 4(1–2):1–119, 2017. doi:10.1561/2500000010
- [30e] D. C. Schmidt, "Guest Editor's Introduction: Model-Driven Engineering", IEEE Computer 39(2):25–31, 2006. doi:10.1109/MC.2006.58; S. Kelly, J.-P. Tolvanen, *Domain-Specific Modeling: Enabling Full Code Generation*, Wiley-IEEE CS Press, 2008.

### Not verified in this pass (named for orientation only)
Katz & Trevisan 2000 (locally decodable codes lower bounds); Aggarwal, Alpern, Chandra, Snir 1987 (hierarchical memory model); Kleinberg NIPS 2001 (hierarchical small-world); Burstall & Goguen 1977 ("Putting theories together to make specifications"); Krein–Rutman theorem; Doeblin conditions. Treat these as pointers, not citations.
