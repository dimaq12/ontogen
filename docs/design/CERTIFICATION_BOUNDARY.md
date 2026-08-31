# CERTIFICATION BOUNDARY (D90) — every part proven or delegated

The rule, ENFORCED (not merely stated): **no part of a genome ships
uncertified.** Each tissue is EITHER

1. **PROVEN here** — the court proves rule contracts + entity induction +
   fixed-instance invariants; skills pass properties+fuzz+budget+teeth;
   dialects/ports pass fold-parity — OR
2. **DELEGATED to a NAMED external guarantor** — a vetted library / standard
   whose OWN audit is the guarantee. We do not verify the guarantor's source;
   the membrane verifies (provenance: import + version + optional checksum)
   that it is really the pinned one, and the passport CHAINS to its audit
   reference. A mismatch REVOKES; a claimed-but-absent guarantor refuses to load.

`onto attest` prints the GUARANTEE CHAIN and FLAGS any part that is neither
(contained-only). A contained-only part is a white spot the operator must
close — add acceptance cases (functional) or a guarantee (delegation).

## Why: the court certifies a narrow shape

The court's certificate is a statement about VALUES on a DISCRETE, DECIDABLE
domain, checked against a reference. Everything outside that shape escapes it.
The full classification of what escapes, and the honest move for each:

### A. Continuum (not discrete) — the engine is an int-carrier
1. **Float / numerical accuracy** ⭐new. Rounding error, stability, condition
   number, catastrophic cancellation. You can check vectors, but not an error
   bound over the continuum. A hole for scientific/ML kernels.
2. **Cryptographic strength** (discussed): constant-time, side-channels — a
   property of physical execution, not of values.

### B. Physical (not values)
3. **Hard real-time / real latency**: the organism is timeless (the fold).
   "the handler finishes in <10ms" is MEASURED (ν-bridge), not proved.
4. **Concurrency / memory-model** ⭐: the court proves the arithmetic of state,
   not happens-before. Lock-free under a memory model is outside the court
   (the atomics conversation).
5. **Resources**: memory, GC pauses, cache, allocations — physics, not a
   contract. The budget gives a RELATIVE speedup (lesson D38), not an absolute.

### C. Undecidable / unbounded
6. **Skill termination** ⭐: a skill may loop (the sandbox is "hygiene, not a
   sandbox"); halting is undecidable, the engine does not prove it.
7. **Deeply-nonlinear contracts**: the court is decidable on int theory;
   Fermat-like guards -> solver unknown -> fuzzed, not proved.
8. **Dynamic-population invariants**: only the fixed-instance conserves-class is
   proved; dynamic -> monitored.
9. **Cross-entity cascade invariants** -> monitored.
10. **Spectrally-invisible corruption** (Problem 2): a class of self-sustaining
    corruption below the spectral gap — provably hard to detect.

### D. World / meaning (no reference / predicate)
11. **Island content** — only contained, not proven (the membrane monitors
    behavior, not code).
12. **Truth of the oracle / assumption**: harden trusts the incident oracle,
    declare_unknown trusts the region predicate; the world need not comply.
13. **Underdetermined MEANING**: the interview reveals it but does not decide
    which reading is "intended" — the meaning is the human's.
14. **Non-formalizable requirements**: taste, "reasonable retry", murky
    regulation — no predicate to fuzz.
15. **Wrong-but-passes**: a body passes weak properties yet is semantically
    wrong (the gate-strength race; mitigated by mutants/teeth/harden, not
    eliminated).

### E. Statistics (confidence only, not proof) ⭐
16. **ML correctness / generalization**: model accuracy, transfer — not a
    formal predicate. Held-out MEASURES with confidence (DKW-style), but "the
    model is correct" is not certified — only estimated.

### F. Meta / trust / supply chain
17. The engine itself (trust-base), the model edge (growth needs the model),
    institutional acceptance, the supply chain of the pinned lib behind the door.

## The key: one of four honest moves for EVERY class

This is the project's spirit — not to pretend, but to turn uncertainty into a
visible form. All four moves are first-class and surfaced in the passport;
what is never allowed is a silent "trust me".

| Move | Applied to |
|---|---|
| **MEASURE** (ν-bridge, DKW quantile, spectral) | latency (3), perf (5), ML (16), float accuracy (1) |
| **CONTAIN** (membrane, REVOKE) | island content (11), a crypto lib behind the door (2), supply chain (17) |
| **DECLARE** (assumption / ack / unknown / declared_loss) | oracle truth (12), meaning (13), requirements (14) |
| **NAME unproven** (UNEXPRESSIBLE / passport) | strength (2), side-channels, perceptual, memory-model (4), skill termination (6), Problem 2 (10) |

And **DELEGATE** (D90): route a class that a named guarantor DOES cover to that
guarantor (crypto -> a vetted lib / HACL* / ct-verif; float -> interval
analysis; concurrency -> CBMC/TSan; ML -> held-out+DKW) — the passport chains
to the guarantor's audit. PROVE / DELEGATE / MEASURE / CONTAIN, never silence.

## The stronger-model non-conflation

Climbing the growth ladder (qwen -> sonnet -> opus) raises the probability of
PASSING a gate; it never changes WHAT a gate certifies. A stronger model grows
functional bodies more reliably; it does not make security (or any escaping
class) provable. Never confuse a smarter generator with a stronger certificate —
that is exactly how wrong-but-passes would slip in where it costs most.

## Enforced per class (D91): `onto certify`

The taxonomy is not only documented — `onto certify <genome>` emits a COVERAGE
MATRIX: for every one of the 17 classes a mechanical STATE (N/A by construction
/ PROVEN / DELEGATED / MEASURED / CONTAINED / MONITORED / DECLARED /
NAMED_UNPROVEN / UNCOVERED). Nothing is silent. A tissue that should carry a
certificate but doesn't (a contained-only island) is flagged UNCOVERED (exit 1)
and must be closed (add cases or delegate). The guarantee is not "everything is
proven" — it is "every class is in a KNOWN, enforced state".

## Honesty of the matrix (D91.1)

The per-class state is DERIVED from the artifact, not a decorative constant:
a class prints DECLARED/CONTAINED/MEASURED only when the genome actually carries
the thing (assumptions.yaml, grown tissue, engine.pin) — otherwise N/A. Two
classes (4 memory-model, 10 spectrally-invisible) are honest STANDING limits,
tagged as such. The D90 checksum covers exactly one file: for a native-backed
guarantor it verifies the Python wrapper, and says the native backend is
delegated to the guarantor's own audit — it is integrity, not a crypto audit.

## Status

Enforced (exam fguarantee 5/5): the `guarantee` declaration on islands
(membrane.Guarantee), load-time provenance verification (import + version +
checksum), REVOKE on mismatch, and the attest GUARANTEE CHAIN that classifies
every tissue (proven / delegated / contained-only) and flags the uncovered.
Specialized certifiers (ct-verif, HACL*, CBMC, held-out/DKW) plug in as further
guarantors under the same routing — open-ended.
