import os
import re
import requests
import json

def fetch_sub(domain):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set — skipping GitHub")
    session = requests.session()
    session.headers = {
        "Authorization": "token {}".format(token),
        "Accept": "application/vnd.github.v3.text-match+json",
        "User-Agent": "Mozilla/5.0",
    }
    url = "https://api.github.com/search/code?q={}&per_page=100".format(domain)
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = json.loads(resp.text)
    pattern = re.compile(r"([\w\d][\w\d\-\.]*\." + re.escape(domain) + r")", re.IGNORECASE)
    domains = set()
    for item in data.get("items", []):
        for match_obj in item.get("text_matches", []):
            for m in pattern.findall(match_obj.get("fragment", "")):
                domains.add(m.lower())
    return sorted(domains)
