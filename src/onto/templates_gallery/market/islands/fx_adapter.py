import json
import os
import time
import urllib.request
import urllib.error


def convert(payload: dict) -> dict:
    port = os.environ.get("FX_PORT", "8641")
    url = f"http://127.0.0.1:{port}/rate"
    data = json.dumps({
        "from": payload["from"],
        "to": payload["to"],
        "amount": payload["amount"]
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    retries = 3
    delay = 0.05

    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=1)
            result = json.loads(resp.read())
            return {
                "converted": result["converted"],
                "rate": result["rate"]
            }
        except (urllib.error.HTTPError, urllib.error.URLError):
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise