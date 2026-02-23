import requests
import re

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://rapiddns.io/subdomain/{}?full=1".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    pattern = re.compile(r"<td>([a-zA-Z0-9][a-zA-Z0-9\-\.]*\." + re.escape(domain) + r")</td>")
    return sorted(set(re.findall(pattern, req.text)))
