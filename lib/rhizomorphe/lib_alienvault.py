import os
import requests
import re

def fetch_sub(domain):
    api_key = os.environ.get("OTX_API_KEY")
    if not api_key:
        raise RuntimeError("OTX_API_KEY not set — skipping Alienvault")
    session = requests.session()
    session.headers = {
        "X-OTX-API-KEY": api_key,
        "User-Agent": "Mozilla/5.0",
    }
    url = "https://otx.alienvault.com/api/v1/indicators/domain/{}/passive_dns".format(domain)
    pattern = re.compile(r'"hostname": "(.*?)"')
    domains = []
    try:
        req = session.get(url, timeout=20)
        req.raise_for_status()
        domains = sorted(set(re.findall(pattern, req.text)))
    except requests.exceptions.RequestException as err:
        print("Oops: Something went wrong", err)
    return domains
