import requests
import re
import json
 
def fetch_sub(domain):
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    session.headers = {'User-Agent': ua}

    url = "https://api.threatminer.org/v2/domain.php?q={}&rt=5".format(domain)
    pattern = re.compile(r'"common_name": "(.*?)"')
    try:
        req = session.get(url,timeout=20)
        req.raise_for_status()
        rawlist = json.loads(req.content)
        domains = rawlist['results']

    except requests.exceptions.RequestException as err:
        print ("OOps: Something went wrong",err)
        if len(domains) > 0:
            return domains
        else:
            return []

    return domains