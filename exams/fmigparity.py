# -*- coding: utf-8 -*-
"""EXAM migration fold-parity (D93): a migration is a functor that must PRESERVE
the fold. The certificate (certify_migration_fold) is proven on the ACTUAL
stored history: a functor that preserves the fold is certified (None); a functor
that corrupts data (a rename the new rule can't read) is REJECTED with a
counterexample; an undeclared divergence never slips through. Offline, no SLM."""
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = []


def _genome(event_fields: dict, body: str):
    from onto.core.genome import Genome
    return Genome.model_validate({
        "onto": 1, "name": "wal", "retry_window": 8,
        "events": {"Charge": {"w": "str", **event_fields}},
        "entities": {"w": {"key": "w", "instances": ["bob"],
                     "state": {"bal": "int"}, "init": {"bal": 0},
                     "rules": {"r": {"when": "Charge", "body": body,
                               "contract": {"post": "s.bal >= 0"}}}}},
        "queries": {}})


def main():
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "src"))
    from onto.core import migrate

    old_g = _genome({"amount": "int"}, "s.bal = s.bal + ev.amount\n")
    # the stored history under the OLD genome
    old_events = [{"type": "Charge", "id": "e1", "w": "bob", "amount": 50},
                  {"type": "Charge", "id": "e2", "w": "bob", "amount": 30}]

    # --- 1. a fold-PRESERVING functor (rename amount->sum, new rule reads sum) ---
    new_ok = _genome({"sum": "int"}, "s.bal = s.bal + ev.sum\n")
    fx_ok = migrate.Migrations.model_validate(
        {"rename_event_fields": {"Charge": {"amount": "sum"}}})
    cx_ok = migrate.certify_migration_fold(old_g, new_ok, old_events, fx_ok)
    R.append((f"fold-preserving rename (amount->sum, rule reads sum) -> CERTIFIED "
              f"(None): {cx_ok}", cx_ok is None))

    # --- 2. a CORRUPTING functor: rename amount->sum but new rule still reads
    #        ev.amount (now absent) -> the charge is lost -> fold diverges ---
    new_bad = _genome({"sum": "int"}, "s.bal = s.bal + ev.amount\n")
    cx_bad = migrate.certify_migration_fold(old_g, new_bad, old_events, fx_ok)
    R.append((f"corrupting rename (new rule reads the vanished field) -> REJECTED "
              f"with a counterexample: {bool(cx_bad)}",
              cx_bad is not None and "fold-parity" in cx_bad))

    # --- 3. an undeclared DROP that changes the fold -> rejected ---
    fx_drop = migrate.Migrations.model_validate({"drop_events": ["Charge"]})
    #   drop Charge with NO declared_loss -> fold (bal) diverges 80 -> 0, undeclared
    cx_drop = migrate.certify_migration_fold(old_g, old_g, old_events, fx_drop)
    R.append((f"undeclared drop that changes the fold -> REJECTED: {bool(cx_drop)}",
              cx_drop is not None))

    # --- 4. a DECLARED loss is permitted (operator signed off, D74) ---
    fx_decl = migrate.Migrations.model_validate(
        {"drop_events": ["Charge"], "declared_loss": {"Charge": "intentionally purged"}})
    cx_decl = migrate.certify_migration_fold(old_g, old_g, old_events, fx_decl)
    R.append((f"DECLARED loss (drop + declared_loss) -> permitted (None): {cx_decl}",
              cx_decl is None))

    print(f"\n=== EXAM migration fold-parity ({time.time()-t0:.1f}s) ===")
    ok = True
    for name, passed in R:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok &= bool(passed)
    print("VERDICT:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
