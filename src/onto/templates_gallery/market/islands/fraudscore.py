# ISLAND: anti-fraud scoring — sometimes a number, sometimes a string, sometimes a crash (real life).
import random

_rnd = random.Random(13)


def score(payload):
    roll = _rnd.random()
    if roll < 0.07:
        raise RuntimeError("model server OOM")
    if roll < 0.2:
        return {"score": "high??"}                    # type drifted
    return {"score": int(roll * 100)}
