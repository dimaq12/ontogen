# -*- coding: utf-8 -*-
"""F6: conservativeness, coverage by the functor, idempotent log migration."""
import json
import pathlib

from onto.core import genome as G, migrate

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _hotel():
    return G.load(ROOT / "genomes" / "hotel.yaml")


def test_additive_is_not_breaking():
    old = _hotel()
    new = old.model_copy(deep=True)
    new.queries["extra"] = "sum(w.charges for w in wallet)"
    assert migrate.diff_genomes(old, new) == []


def test_breaking_detected_and_coverage():
    old = _hotel()
    new = old.model_copy(deep=True)
    new.events["ChargeRequested"] = {"wallet": "str", "sum": "int"}   # amount->sum
    br = migrate.diff_genomes(old, new)
    assert any("ChargeRequested.amount" in b for b in br)
    fx0 = migrate.Migrations()
    assert migrate.coverage(br, fx0)                        # uncovered
    fx = migrate.Migrations(rename_event_fields={"ChargeRequested": {"amount": "sum"}})
    assert migrate.coverage(br, fx) == []                   # covered


def test_migrate_log_idempotent_with_backup(tmp_path):
    log = tmp_path / "events.jsonl"
    evs = [{"id": "e1", "type": "ChargeRequested", "wallet": "bob", "amount": 5},
           {"id": "e2", "type": "Other", "x": 1}]
    log.write_text("".join(json.dumps(e) + "\n" for e in evs))
    fx = migrate.Migrations(rename_event_fields={"ChargeRequested": {"amount": "sum"}})
    st = migrate.migrate_log(fx, tmp_path, "v2")
    assert st["events_in"] == st["events_out"] == 2 and st["backup"]
    out = [json.loads(l) for l in log.read_text().splitlines()]
    assert out[0] == {"id": "e1", "type": "ChargeRequested", "wallet": "bob", "sum": 5}
    assert out[1] == evs[1]
    st2 = migrate.migrate_log(fx, tmp_path, "v2b")          # idempotent
    out2 = [json.loads(l) for l in log.read_text().splitlines()]
    assert out2 == out
