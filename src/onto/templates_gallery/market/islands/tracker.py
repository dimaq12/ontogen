# ISLAND: delivery tracker — sometimes returns nonsensical statuses.
import random

_rnd = random.Random(11)
_STATUSES = ["in_transit", "delivered", "on_hold"]


def track(payload):
    roll = _rnd.random()
    if roll < 0.1:
        raise TimeoutError("carrier API timed out")
    if roll < 0.25:
        return {"status": "�#?!", "eta_days": -7}     # garbage data as-is
    return {"status": _rnd.choice(_STATUSES), "eta_days": _rnd.randint(0, 9)}
