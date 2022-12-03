import requests
import re

 
def fetch_sub(domain):
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    session.headers = {'User-Agent': ua}

    url = "https://urlscan.io/api/v1/search/?q={}".format(domain)
    pattern = r'url\": \"https://(.*?).'

    try:
        req = session.get(url,timeout=20)
        req.raise_for_status()
        hosts = sorted(set(re.findall(pattern+domain, req.text)))
        domains=[]
        for item in hosts:
            domains.append(item + "." + domain)

    except requests.exceptions.RequestException as err:
        print ("OOps: Something went wrong",err)
        if len(domains) > 0:
            return domains
        else:
            return []

    return domains