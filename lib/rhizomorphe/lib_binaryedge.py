import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("BINARYEDGE_API_KEY")
    if not api_key:
        raise RuntimeError("BINARYEDGE_API_KEY not set — skipping BinaryEdge")
    session = requests.session()
    session.headers = {"X-Key": api_key, "User-Agent": "Mozilla/5.0"}
    url = "https://api.binaryedge.io/v2/query/domains/subdomain/{}".format(domain)
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = json.loads(resp.text)
    return sorted(set(data.get("events", [])))
