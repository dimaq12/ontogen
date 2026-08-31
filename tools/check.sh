#!/usr/bin/env bash
# onto CI entrypoint: invariant lint + tests + fast exams (no network/SLM).
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
# hygiene: zombie organisms from crashed runs hold ports with a stale schema
pkill -f "onto[.]cli serve" 2>/dev/null || true
pkill -f "organism [-]-port" 2>/dev/null || true
echo "== lint ==";   $PY -m onto.lint 2>/dev/null || .venv/bin/onto lint
echo "== pytest =="; $PY -m pytest -q
for e in f1 f3 f4 f8 frelease flago ftypes2 fauth fops fy7 fparadigm fmath fspectral faudit fcompose fnu finit ftier_a fvariants fgene fmodels fports; do
  echo "== exam $e =="
  $PY exams/$e.py > /tmp/onto-check-$e.log 2>&1 \
    && tail -1 /tmp/onto-check-$e.log \
    || { echo "EXAM $e FAILED"; tail -20 /tmp/onto-check-$e.log; exit 1; }
done
echo "ALL CHECKS GREEN"
