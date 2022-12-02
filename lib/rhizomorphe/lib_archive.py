import requests
from urllib.parse import urlparse
import re
import json
 
def fetch_sub(domain):
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    session.headers = {'User-Agent': ua}
    url = "http://web.archive.org/cdx/search/cdx?url=*.{}&output=json&fl=original&collapse=urlkey".format(domain)
    domains = []
    try:
        req = requests.get(url, timeout = 20)
        urls = req.json()
        for item in urls:
            urlString = item[0]
            if domain in urlString:
                parsed_uri = urlparse(urlString)
                onlyDomain = "{uri.netloc}".format(uri=parsed_uri).split(":")[0]
                domains.append(onlyDomain)
            else:
                pass
#        domains = set(domains)
        return domains


        req = session.get(url,timeout=20)
        req.raise_for_status()
        rawlist = json.dumps(json.loads(req.text),indent=4)
        domains = sorted(set(re.findall(pattern, rawlist)))

    except requests.exceptions.RequestException as err:
        print ("OOps: Something went wrong",err)
        if len(domains) > 0:
            return domains
        else:
            return []

    return domains
