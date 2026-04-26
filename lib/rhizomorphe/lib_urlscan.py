import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://urlscan.io/api/v1/search/?q=domain:{}&size=100".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    domains = set()
    for result in data.get("results", []):
        page = result.get("page", {})
        hostname = page.get("domain", "")
        if hostname and (hostname.endswith("." + domain) or hostname == domain):
            domains.add(hostname.lower())
    return sorted(domains)
