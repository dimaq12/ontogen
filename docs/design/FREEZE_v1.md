# FREEZE v1 (onto 1.1.0) — product readiness inventory · 2026-08-31

## What is frozen
- **IR v1.0** (D72): the genome format under a mechanical tooth — a fingerprint
  of the json schema in ir.py + tests/test_freeze.py; changing the format without a bump
  of HUB_VERSION + a converter does NOT pass CI.
- **Core**: Expr (a Python subset, one AST -> court/interpreter/
  printers), organism (write-ahead log, dedup, replay, snapshots,
  kill -9 safety), court (z3: post/conserves inductively, mutants),
  membrane (islands, assumptions, drift, REVOKE), warden (molt with
  backup, timers, monitors for assumptions/load/spectrum), skills
  (CEGIS+cache), modules/migrations (functor + declared lossiness).

## End-to-end scenario (the product's claim, proven by the glove)
A natural-language description -> NL front (Sonnet->Opus ladder, gates: checkers+
COURT+self-accept) -> a proven organism: /admin, /ops, /list, timers,
webhooks, auth -> any stack (the dialect generator is grown with the model) ->
onto new. Glove: 8/8 distant domains, the inexpressible honestly rejected.

## Guarantees (what the organism's passport says and what backs it)
- proved: rule contracts inductively (court), end-to-end paths (attest);
- assumed: membranes with a named weakest seam, auth deny-by-default,
  not-knowing holes with monitors;
- monitored: drift of externals, load (nu_drift), spectrum+variance
  (corruption/freeze), timers; failures — in the ledger with provenance (hash chain);
- survival: hazard moves (REVOKE h=1, rollback h=1 given a live backup);
- growth: determinism-via-certification (fcold: 0 calls with a dead
  key), hardening of escapes (certificate revocable retroactively).

## NOT guaranteed (honest boundaries — PARADIGM_LIMITS/UNEXPRESSIBLE)
Island content (containment only); quality perception; webhook
delivery (fire-and-forget); spectral |Δλ|-transfer without κ; state-
dependent defects under changing load; institutional acceptance.

## How to check the freeze (any person, one command)
    ./tools/check.sh        # 21 exams + 77 tests: ALL CHECKS GREEN
Network exams (not in CI, cache makes reruns free): fideal, fnl,
fgauntlet, fisland, fgrow, fgengrow, fp15, fcold. growport: fgrowport (grows a port codec via SLM). Packaging: fship (uv build + clean-venv install; needs uv, deps from PyPI first time).

## Open for after-freeze (does not block the product)
P16-refit (telemetry accumulating: 133/200), open-3 (Γ-fabrics), κ-attestation,
state-dependent ν-transfer, web interview, second echelon (gene pool).
Unpassable from within: calendar life (launched, see life/README.md),
F7 — the operator's hands.
