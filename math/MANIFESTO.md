> Status: this document is part of a free-form compilation of known results written without a literature check. The map to public sources and the relation of each statement to them: [README.md](README.md). No priority is claimed.

# A Manifesto for Ontogenic Software

*dnaContract / ONTORUNTIME / ARCHGEN — 2026*

We build software the way we draft blueprints — and then we are surprised
that it can neither grow, nor heal, nor admit its own obsolescence. What
follows is a different way. Not one line here is metaphor: behind each
thesis stands a theorem (Parts I–X, FREEZE v0.1) or a working experiment
(the ONTORUNTIME v0–v5 series).

---

## 1. A program is not a blueprint but a genome

Don't store the organism — store the rule that lets you make the organism
again. Code is phenotype: it materializes from the genome, regenerates on
demand, and is never the source of truth. The diff between two
implementations of one contract is a meaningless question. **Code is not
unique; the contract is.**

## 2. Existence must be earned

```text
existence := certified predictive usefulness
```

An object in the system exists only as long as its certificate agrees with
observation. The world shifts — the certificate is refuted — the object
loses its ontological standing. There are no eternal modules, no eternal
services, no eternal abstractions. There are only certificates still in
force.

## 3. Global knowledge has a physical price

Reach, freshness, latency, capacity, and hierarchy are never free all at
once (the HTN theorem). An architecture is a point on a tradeoff surface —
not a fashion, not a worldview. "Monolith or microservices" is not a
matter of faith: these are coordinates, and they are computed from the
spectrum of demand.

## 4. Hierarchy is not magic

Hierarchy does not violate the light cone. It is compression + persistent
summaries + amortized communication: expensive to build, cheap to use. It
is the only currency of scale with a logarithmic price tag — which is why
nature loves it, and why we love it too. But every level pays its own way:
in cache, in refresh, in repair. A level that fails to cover its own
homeostasis has no right to exist.

## 5. Structure proposes — dynamics decides

The dependency graph, the package layout, the diagram of little boxes —
these are hypotheses. The judge is behavior. A dull environment cannot
refute a false model: the truth of a level is won by **intervention**. A
strong abstraction is one that stays closed under every admissible
experiment that leaves the mechanism untouched. Everything else is
phenomenology, honest only within its own regime.

## 6. Power to act ≤ strength of proof

```text
candidate -> observational -> interventional -> runtime-stable
```

You may predict once you hold a weak certificate. You may rebuild someone
else's substrate only once you hold a strong one. Rights grow with the
proof and are **revocable**: an unsure model loses its grip on the world
in the very tick its certificate dies. An obsolete ontology does not
merely admit its error — it loses the ability to do harm with it.

## 7. Death is topology; healing is the future

To kill an entity is not to write a zero into it: **absence of signal ≠ a
signal of zero**. Death = excision from the topology + renormalization of
the surviving links; the dead, left in the topology, poison their
neighbors. And healing does not roll history back — history is
irrecoverable in principle, even for an oracle. Healing returns the system
not to its past but to the set of viable futures: the same hand, not the
same cells.

## 8. Trust is built on repairability, not on infallibility

Executors have the right to be cheap and dumb — the ribosome is under no
obligation to be smart. The errors of cheap models are damage, and damage
is owed repair. Intelligence lives in the genome and in the certification
gates, not in the size of the executor. A cell reaches 10⁻¹⁰ accuracy with
an enzyme accurate to 10⁻⁵ — through repair, and we do the same.

## 9. Growth is a molt, not a rewrite

One and the same genome lives as a monolith at small scale and as a tower
of services at large. The boundaries are certified from day one — a
service is extracted along a seam that carries a passport, not along a
line dreamed up in a meeting. "Start with the monolith, then the agonizing
rewrite" is a disease of the blueprint era. Organisms are not rewritten.
They molt.

## 10. The runtime puts questions to the world

```text
EMERGE = Discover + Experiment + Certify
```

The system does not wait for the environment to refute its delusions by
chance. It designs, itself, the experiment on which the competing
explanations diverge the most, runs it, and kills the loser. Science is
not an external procedure applied to the system; science is one of its
organs.

## 11. Homeostasis is obliged to be honest

A system that repairs the world is obliged to subtract its own actions
from its own measurements — otherwise repair masks the drift, and the
bureaucracy sets about repairing the world into an obsolete ontology and
calling it stability. Monitoring measures the world's deviation, not the
diligence of its own corrections.

## 12. The industry already does all of this — blindly

Reconciliation loops are top-down constraints without a certificate of
truth. Chaos engineering is falsification without experimental design.
Canary is a ladder of rights without formal rights. SLOs are a certificate
without closure. Refactoring is a molt without a criterion of
obsolescence. We are not proposing a new religion. We are offering the
mathematics for the practices the industry earned the hard way, by feel.

---

## Status

The mathematical core is frozen (FREEZE v0.1: the HTN theorem with its
fold, the price of the wire, the two clocks, survival theory,
two-dimensional connectedness, certificates with DKW guarantees). The
organism is alive (ONTORUNTIME v0–v5: full ontogeny on a single generic
engine — birth, a certified tower, homeostasis, damage routing, drift
detection, revocation of power, molting). The applied vector is set
(ARCHGEN: telemetry = x_t; the repository proposes structure — traffic
decides).

An abstraction was born of dynamics, proved useful, died when it stopped
being true — and resurrected its substrate without losing itself.

**Existence — earned. Rights — proven. Growth — molted. Code — grown back
anew.**
