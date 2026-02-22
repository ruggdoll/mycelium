import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"}
    url = "https://jldc.me/anubis/subdomains/{}".format(domain)
    domains = []
    try:
        req = session.get(url, timeout=20)
        req.raise_for_status()
        data = json.loads(req.text)
        if isinstance(data, list):
            domains = sorted(set(d for d in data if isinstance(d, str) and d.endswith(domain)))
    except (requests.exceptions.RequestException, ValueError) as err:
        print("Oops: Something went wrong", err)
    return domains
