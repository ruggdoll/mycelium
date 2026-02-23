import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("VT_API_KEY")
    if not api_key:
        raise RuntimeError("VT_API_KEY not set — skipping VirusTotal")
    session = requests.session()
    session.headers = {"x-apikey": api_key, "User-Agent": "Mozilla/5.0"}
    url = "https://www.virustotal.com/api/v3/domains/{}/subdomains?limit=40".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    domains = [item["id"] for item in data.get("data", []) if item.get("id")]
    return sorted(set(domains))
