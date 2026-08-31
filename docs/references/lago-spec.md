# LAGO CAMPAIGN: implementing the core of an open-source billing system on onto

Reference source: **Lago** (getlago.com, open-source usage-based billing).
Method: semantics are taken from their public documentation; the judge is built from their
API examples; every expressibility snag = an IR wave through UNEXPRESSIBLE (§8.1).

## Reference semantics (from the docs, 2026-08-20)
- **Usage events**: `{transaction_id (idempotency!), external_subscription_id,
  code (metric), timestamp?, properties?}` — transaction_id = exactly our dedup.
- **Billable metrics** (aggregations over events for a period): COUNT / SUM(field) /
  MAX(field) / COUNT_UNIQUE(field) / LATEST / WEIGHTED_SUM / CUSTOM.
- **Plans**: interval (month/…), amount_cents (fee, advance|arrears), charges
  by metric: standard (per unit) / graduated / package / volume / percentage.
- **Wallets**: prepaid credits (granted/purchased), rate_amount (1 credit = N
  of currency), applied to subscription invoices after taxes; balance / ongoing.
- **Invoices**: per period: fee + charges − credits; statuses draft/finalized.

## Lago-core v0 slice (first exam)
One tenant = one genome (a Lago configuration = our genome — an honest match).
- metrics: api_calls (COUNT), storage_mb (SUM value), peak_conn (MAX value);
- plan: monthly, fee 4900¢, arrears; charges standard: 2¢/call, 10¢/MB, 50¢/conn;
- subscriptions: DYNAMIC (created by an event), active/terminated;
- wallet: per-subscription (v0 simplification: in Lago it is per-customer; noted),
  granted top-up, rate 1 credit = 100¢, applied at period close;
- period close: a BillingPeriodClosed event (sent by warden/cron — like a Lago
  job) → invoice: total = fee + Σ charges; applied = min(credits, total);
  due = total − applied; period counters reset to zero; the actual invoice = an event in the log
  (the log = the invoice registry; the invoice read-model — later).

## Correspondences (ROSETTA lines)
| Lago | onto |
|---|---|
| transaction_id idempotency | dedup by retry_window window (D26) |
| usage event code | genome event type |
| COUNT/SUM/MAX metric per period | int fields of subscription state + increment rules |
| period close (job) | BillingPeriodClosed from a warden ticker |
| tenant configuration | genome |
| payment gateway | an island behind a membrane |

## Expressibility blocks -> waves (living list)
| block | wave | status |
|---|---|---|
| subscriptions created on the fly | **DYNAMIC INSTANCES** (Entity.instances: dynamic) | DOING NOW |
| COUNT_UNIQUE (set in state) | deferred: set-state or a skill | UNEXPRESSIBLE |
| invoice as an object with line items | read-model over the log / lists in state | UNEXPRESSIBLE (log = registry v0) |
| graduated/volume charge models | expressions with ranges (Expr handles via if) | after standard |
| wallet per-customer + cross-entity application | sagas/emission | UNEXPRESSIBLE (v0: wallet in the subscription) |
| WEIGHTED_SUM (prorate over time) | TIME wave | later |
