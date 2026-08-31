# ISLAND: payment gateway — a foreign organism with the worst profile (lag, 500s).
# The only legal place for network I/O; the flakiness lives in the upstream (exam).
import json
import os
import urllib.request

PORT = int(os.environ.get("MEGA_GATEWAY_PORT", "8689"))


def charge(payload):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/charge",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1) as r:
        data = json.loads(r.read())
    if data.get("status") != "ok":
        raise ValueError(f"gateway said {data!r}")
    return {"auth": data["auth"]}
