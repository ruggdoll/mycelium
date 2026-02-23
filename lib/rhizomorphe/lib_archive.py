import requests
from urllib.parse import urlparse

def fetch_sub(domain):
    url = "http://web.archive.org/cdx/search/cdx?url=*.{}&output=json&fl=original&collapse=urlkey".format(domain)
    req = requests.get(url, timeout=20)
    domains = []
    for item in req.json():
        host = urlparse(item[0]).netloc.split(":")[0]
        if host:
            domains.append(host)
    return domains
