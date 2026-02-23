import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("CHAOS_API_KEY")
    if not api_key:
        raise RuntimeError("CHAOS_API_KEY not set — skipping Chaos")
    session = requests.session()
    session.headers = {"Authorization": api_key, "User-Agent": "Mozilla/5.0"}
    url = "https://dns.projectdiscovery.io/dns/{}/subdomains".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    domains = ["{}.{}".format(sub, domain) for sub in data.get("subdomains", [])]
    return sorted(set(domains))
