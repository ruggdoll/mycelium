import requests
import re
 
def fetch_sub(domain):
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    session.headers = {'User-Agent': ua}

    url = "https://api.hackertarget.com/hostsearch/?q={}".format(domain)
    pattern = r'(.*?),'

    try:
        req = session.get(url,timeout=20)
        req.raise_for_status()
        domains = sorted(set(re.findall(pattern, req.text)))

    except requests.exceptions.RequestException as err:
        print ("OOps: Something went wrong",err)
        if len(domains) > 0:
            return domains
        else:
            return []

    return domains