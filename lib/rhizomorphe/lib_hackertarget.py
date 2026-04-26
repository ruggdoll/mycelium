import requests
import re

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://api.hackertarget.com/hostsearch/?q={}".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    text = req.text.strip()
    if not text or text.lower().startswith("error"):
        raise RuntimeError("HackerTarget: {}".format(text))
    return sorted(set(re.findall(r"([\w\d][\w\d\-\.]*\.{}),".format(re.escape(domain)), text)))
