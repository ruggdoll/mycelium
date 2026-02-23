import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("BEVIGIL_API_KEY")
    if not api_key:
        raise RuntimeError("BEVIGIL_API_KEY not set — skipping Bevigil")
    session = requests.session()
    session.headers = {"X-Access-Token": api_key, "User-Agent": "Mozilla/5.0"}
    url = "https://osint.bevigil.com/api/{}/subdomains/".format(domain)
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = json.loads(resp.text)
    return sorted(set(data.get("subdomains", [])))
