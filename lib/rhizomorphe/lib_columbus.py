import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://columbus.elmasy.com/api/lookup/{}".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    domains = []
    for item in data:
        if isinstance(item, str) and item:
            fqdn = item if (item.endswith("." + domain) or item == domain) else "{}.{}".format(item, domain)
            domains.append(fqdn)
    return sorted(set(domains))
