import requests
import re

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    pattern = r"([\w\d][\w\d\-\.]*\.{})".format(re.escape(domain))
    return sorted(set(re.findall(pattern, req.text)))
