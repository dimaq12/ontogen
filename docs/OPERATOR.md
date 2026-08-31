# The onto organism operator — a one-scroll page


## Bring an organism up
```bash
onto serve genomes/hotel.yaml --port 8090 --data ./data
# with skills: --skills-cache cache_skills
# under supervision (molting/monitors/REVOKE): onto warden genomes/hotel.yaml ...
```

## The organism's HTTP
| method | path | what |
|---|---|---|
| POST | `/event` | event: `{"id": "e1", "type": "ChargeRequested", "wallet": "bob", "amount": 100}` — flat JSON: required `id` (string, unique — deduplicated by the retry_window window) and `type`, plus ALL of the event's fields from the genome |
| GET | `/state/<entity>/<instance>` | instance state, e.g. `/state/wallet/bob` |
| GET | `/q/<name>` | genome query -> `{"value": ...}` |
| GET | `/health` | counters (including by_type — load) + warmth + external attestations |
| GET | `/list/<entity>?field=val&_limit&_offset` | selection with filter and pagination |
| GET | `/instances/<entity>` | keys of live instances |
| GET | `...?repr=human` | decimal/timestamp in human-readable form (D66) |
| GET | `/admin` | ADMIN PANEL from the genome: tables, event forms, queries (D61) |
| GET | `/ops` | OPERATOR CONSOLE: ledger with filters, attestations, checkpoint (D69) |
| POST | `/skill/<name>` | skill input as JSON fields params -> `{"out": [...]}` |
| POST | `/ext/<name>` | call an island through the membrane (drift monitors) |
| POST | `/checkpoint` | snapshot with a hash certificate |

Auth (if the genome has an `auth` section, D67): mutations require
`Authorization: Bearer <token>`; the token is resolved by an IdP island; deny-by-default.

Response to /event: `{"status": "applied|dup|error", "outcomes": {"wallet.charge":
"applied|noop(guard)|rejected(post)|unknown-instance:..."}}` — `noop(guard)`
means the guard held back the transition (this is not an error).

## Change the system (the only path — the genome)
1. What to read: `onto explain genomes/hotel.yaml <entity>` — a slice instead of the whole thing.
2. Edit a gene module (rules/contracts) or the root (bind/invariants).
   A state field without init defaults to 0. A rule body is assignments
   `s.<field> = expression` + if/else; a guard is a boolean over `s` and `ev`.
3. `onto validate <root>` -> `onto court <root>` (the court is mandatory: ALL PROVED).
4. Under the warden, an edit to the file is picked up on its own (molting within
   seconds); for a rejection see `<data>/warden.jsonl`. Changing a rule's BEHAVIOR
   under the same contracts requires `ack_behavior_change: ["entity.rule"]` in the
   root — the rejection will quote an executable example of the divergence.
5. Programmatically/from an LLM: `onto mcp <root>` — the `propose` tool with the same gates.

## Commands
`onto version | validate | court | explain | serve | warden | judge |
materialize | conformance | mcp | unit | fix | lint | new | attest |
harden | growisland` — each prints usage when called without arguments.

## Guarantee attestation (before releasing an organism — mandatory)
    onto attest <genome.yaml> [--skills-cache DIR]
Prints and writes attest.json/md: WHAT is proved (court, per-mark + end-to-end
paths), WHAT is assumed (membranes, weakest seam BY NAME, auth), WHAT is
monitored, survival hazard-moves, provenance (genome hash, engine version,
IR fingerprint). This is the reviewable unit of a release (D74).

## Incident in prod (3 a.m.)
1. The organism's `/ops`: ledger tail, filter by kind (auth_denied,
   drift_violation, revoke_external_trust, nu_drift, spectral_drift...).
2. Every rejection carries a why provenance. `onto explain <root> <entity>` — a
   slice of the genome instead of reading the whole thing.
3. Skill escape (wrong-but-passes): get the correct output from the incident
   oracle and harden the gates:
       onto harden <genome> --skill <name> --case '<json>' --expect '<json>'
   A body that does not pass the escape suite loses its certificate (is not mounted).
4. Load drift (nu_drift) = the spectral thresholds have gone stale — rebuild
   the calibration (restarting the warden begins a new healthy window).
5. A molt broke — the warden rolled itself back from backup (ledger: the reason).
   The worst recovery time is in the attestation (hazard-moves, h=1).

## Don't know the answer to an interview question? That's legal (D74/U12)
An unknown is declared as a hole with a monitor (assumptions.yaml next to the
genome): the warden writes hits of the region into the ledger; once you learn
the answer — resolve, and the hole is retracted. Never guess in a contract.

## External integrations: an island grows a model (D63)
Describe the integration in the genome (`externals.<name>`): `intent` (protocol,
address/env, response format, retry policy — in plain prose), `cases` (acceptance
calls: payload -> required subset of the response, `"*"` = field must be present),
`assumptions` (assumption-monitors). Then:

    onto growisland <genome.yaml> <name>

The SLM will write `islands/<...>.py` and pass the machine gates: import allowlist,
acceptance through the LIVE upstream (flakiness is survived by retries — otherwise
red), assumptions intact. You only review and accept the file (it is small).
Ladder exhausted -> exit code 3: write the island by hand (a legal exception).
