# THEORY↔ENGINE BRIDGE: verdicts on the proposals of 2026-08-31

Checked against the texts: survival.md (§1-4), proofs.md (thm.8, cor.3, thm.4',
prop.2 §6, prop.3 §7), hypotheses.md (thm.10), tradeoff.md (thm.13).

## ACCEPTED (agrees with the theorems verbatim)
- **Survival hazard-passport** [survival cor.6'.2, lemma 6.4, open-1]:
  a crash = an adversarial start; the L2 budget does not work there (sticky core) —
  the theory DIRECTLY recommends hazard predicates in contracts. The engine already
  has the moves: REVOKE (h=1), molt-rollback from backup (h=1 given a live backup —
  an assumption into the membrane). Integration: a survival section in attest —
  bad sets S -> declared move + h -> worst recovery time 1/h.
- **Quantile gate certificates** [thm.8 DKW, cor.3]: the fuzzer already runs M
  cases — publish (η,q,δ,M), not a boolean checkmark. harden = an implementation of
  cor.3 (routing the tail into repair) — built BEFORE reading the
  theorem: a sign of consistency. Murky requirements (P4) — a special case:
  a declared observable + a quantile.
- **Judging the incident oracle** [core §6: hysteresis; our apparatus:
  properties]: an escape's expect is run through check_properties + canon;
  a lie violating proven properties is rejected at the harden intake.
- **Punchline**: P1/P2/P5 ↔ open-1/2/3 survival §4 — an exact correspondence.

## REJECTED / PARKED (stretches, named honestly)
- **Spectral audit of an organism** [thm.10, prop.3]: the theorems live on
  the transfer operator with graph K — for an organism this object is UNDEFINED.
  A precondition-wave: a Koopman operator over the event stream + a dictionary of
  observables + its own gates. A mechanism without an object = vibes with a signboard.
- **A numeric "maximum invisible harm"** [cor.6']: the constant ε_a
  is defined via the spectral audit (see above). Until it exists, the passport speaks
  QUALITATIVELY: "monitors see only the declared observables." A passport
  printing uncomputable numbers lies — that is worse than a hole.
- **"The lie's robustness margin is computed"** [prop.2 §6]: the theorem is about
  the invariance of the MDL solution to the choice of PROXY (band 2c), not about a lying
  oracle. A discretely-wrong expect is not a small perturbation. Object substitution.
- **Γ-mechanization of stacks** [§3.5, open-3]: the coordinates (cut, Δ_free) are
  operator-based; for fabrics still a metaphor. The engineering core is already done in
  practice (shared gates judge+parity+kill-9, per-stack only syntax).

## Integration queue (on command)
1. hazard section in attest (+ moves: REVOKE/rollback/restart with their h);
2. quantile form of skill gates and membrane statistics -> attest;
3. harden: oracle judging (properties + reproduction) + hysteresis.
