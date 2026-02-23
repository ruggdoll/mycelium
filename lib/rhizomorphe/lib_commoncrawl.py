import requests
import json
from urllib.parse import urlparse

def fetch_sub(domain):
    # Récupère l'index le plus récent
    collinfo = requests.get("https://index.commoncrawl.org/collinfo.json", timeout=15)
    collinfo.raise_for_status()
    latest_api = collinfo.json()[0]["cdx-api"]

    resp = requests.get(latest_api, params={
        "url": "*.{}".format(domain),
        "output": "json",
        "fl": "url",
        "limit": 5000,
    }, timeout=60)
    resp.raise_for_status()

    domains = []
    for line in resp.text.strip().splitlines():
        try:
            host = urlparse(json.loads(line).get("url", "")).hostname
            if host:
                domains.append(host.lower())
        except ValueError:
            continue
    return sorted(set(domains))
