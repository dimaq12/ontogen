#!/usr/bin/env bash
# CALENDAR LIFE: a long-lived organism under a full warden + pulse.
# Idempotent: kills the previous ones, brings them back up (replay continues the life).
cd "$(dirname "$0")"
pkill -f "onto[.]cli warden genome[.]yaml" 2>/dev/null
pkill -f "life/pulse[.]py" 2>/dev/null
sleep 1
mkdir -p data
nohup ../.venv/bin/python -m onto.cli warden genome.yaml \
  --data data --port 8878 --interval 2 >> warden.log 2>&1 &
echo "warden pid $!"
sleep 3
nohup ../.venv/bin/python pulse.py >> pulse.log 2>&1 &
echo "pulse pid $!"
echo "alive: http://127.0.0.1:8878/ops (console) /admin (admin panel)"
