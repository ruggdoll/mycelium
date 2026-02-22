import requests
import re

def fetch_sub(domain):
    session = requests.session()
    session.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"}
    url = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names".format(domain)
    pattern = r"([\w\d][\w\d\-\.]*\.{0})".format(re.escape(domain))
    domains = []
    try:
        req = session.get(url, timeout=20)
        req.raise_for_status()
        domains = sorted(set(re.findall(pattern, req.text)))
    except requests.exceptions.RequestException as err:
        print("Oops: Something went wrong", err)
    return domains