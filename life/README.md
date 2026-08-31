# Calendar life (the exam that time takes)

Started 2026-08-31: a "meeting rooms" organism (NL-grown, court ALL
PROVED) lives under a FULL warden: molting, monitors, timers (collecting
maintenance fees every hour on its own), unknowns holes, a spectral audit with
ν-monitoring. The pulse sends light traffic once every ~20 s.

- Start/restart: `./run.sh` (idempotent; replay continues the history).
- Watch: http://127.0.0.1:8878/ops — ledger, attestations, counters;
  /admin — state of the world.
- Logs: warden.log, pulse.log, data/warden.jsonl (supervision ledger),
  data/<organism>/ledger.jsonl.
- What counts as PASSING (over the weeks): the organism is alive; timers kept
  charging the fee the whole time; not a single unrecovered crash; molts (edit
  genome.yaml — the warden picks it up) went through with backups; the ledger
  explains every rejection; the spectral audit stayed silent on the healthy
  organism and spoke up on corruption.
- Data/logs do NOT go into git (.gitignore).
