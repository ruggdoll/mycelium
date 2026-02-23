import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    domains = []

    # Étape 1 : récupérer les IPs historiques du domaine (forward passive DNS)
    req = session.get("https://freeapi.robtex.com/pdns/forward/{}".format(domain), timeout=20)
    req.raise_for_status()
    ips = set()
    for line in req.text.strip().splitlines():
        try:
            entry = json.loads(line)
            if entry.get("rrtype") in ("A", "AAAA"):
                ip = entry.get("rrdata", "").strip()
                if ip:
                    ips.add(ip)
        except ValueError:
            continue

    # Étape 2 : reverse lookup sur chaque IP pour trouver les hostnames liés
    for ip in list(ips)[:5]:  # limite pour éviter le rate limiting
        try:
            rev = session.get("https://freeapi.robtex.com/pdns/reverse/{}".format(ip), timeout=20)
            rev.raise_for_status()
            for line in rev.text.strip().splitlines():
                try:
                    entry = json.loads(line)
                    rrname = entry.get("rrname", "").rstrip(".")
                    if rrname.endswith("." + domain) or rrname == domain:
                        domains.append(rrname)
                except ValueError:
                    continue
        except requests.exceptions.RequestException:
            continue

    return sorted(set(domains))
