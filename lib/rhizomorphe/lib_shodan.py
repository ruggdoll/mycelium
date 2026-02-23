import os
import requests
import json

def fetch_sub(domain):
    api_key = os.environ.get("SHODAN_API_KEY")
    if not api_key:
        raise RuntimeError("SHODAN_API_KEY not set — skipping Shodan")
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://api.shodan.io/dns/domain/{}?key={}".format(domain, api_key)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    domains = ["{}.{}".format(sub, domain) for sub in data.get("subdomains", [])]
    return sorted(set(domains))
