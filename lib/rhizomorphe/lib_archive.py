import requests
from urllib.parse import urlparse

def fetch_sub(domain):
    url = "https://web.archive.org/cdx/search/cdx?url=*.{}&output=json&fl=original&collapse=urlkey".format(domain)
    req = requests.get(url, timeout=30)
    req.raise_for_status()
    domains = []
    for item in req.json():
        host = urlparse(item[0]).netloc.split(":")[0].lower()
        if host and (host.endswith("." + domain) or host == domain):
            domains.append(host)
    return sorted(set(domains))
