import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://crt.sh/?q=%25.{}&output=json".format(domain)
    req = session.get(url, timeout=30)
    req.raise_for_status()
    domains = []
    for entry in json.loads(req.text):
        for name in entry.get("name_value", "").split("\n"):
            name = name.strip().lstrip("*.")
            if name.endswith(domain):
                domains.append(name)
    return sorted(set(domains))
