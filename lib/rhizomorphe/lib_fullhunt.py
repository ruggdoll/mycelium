import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("FULLHUNT_API_KEY")
    if not api_key:
        raise RuntimeError("FULLHUNT_API_KEY not set — skipping Fullhunt")
    session = requests.session()
    session.headers = {"X-API-KEY": api_key, "User-Agent": "Mozilla/5.0"}
    url = "https://fullhunt.io/api/v1/domain/{}/subdomains".format(domain)
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = json.loads(resp.text)
    return sorted(set(data.get("hosts", [])))
