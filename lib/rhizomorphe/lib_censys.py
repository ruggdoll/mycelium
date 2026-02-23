import os
import requests
import json

def fetch_sub(domain):
    api_id     = os.environ.get("CENSYS_API_ID")
    api_secret = os.environ.get("CENSYS_API_SECRET")
    if not api_id or not api_secret:
        raise RuntimeError("CENSYS_API_ID / CENSYS_API_SECRET not set — skipping Censys")
    url = "https://search.censys.io/api/v2/subdomains/{}".format(domain)
    resp = requests.get(url, auth=(api_id, api_secret), timeout=20)
    resp.raise_for_status()
    data = json.loads(resp.text)
    subs = data.get("result", {}).get("subdomains", [])
    return sorted(set("{}.{}".format(s, domain) for s in subs if s))
