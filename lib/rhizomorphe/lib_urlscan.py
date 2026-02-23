import requests
import re

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://urlscan.io/api/v1/search/?q={}".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    pattern = r'url\": \"https://(.*?)\.' + re.escape(domain)
    hosts = sorted(set(re.findall(pattern, req.text)))
    return [h + "." + domain for h in hosts]
