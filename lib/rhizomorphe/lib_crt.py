import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"}
    url = "https://crt.sh/?q=%25.{}&output=json".format(domain)
    domains = []
    try:
        req = session.get(url, timeout=30)
        req.raise_for_status()
        for entry in json.loads(req.text):
            for name in entry.get("name_value", "").split("\n"):
                name = name.strip().lstrip("*.")
                if name.endswith(domain):
                    domains.append(name)
        domains = sorted(set(domains))
    except (requests.exceptions.RequestException, ValueError) as err:
        print("Oops: Something went wrong", err)
    return domains
