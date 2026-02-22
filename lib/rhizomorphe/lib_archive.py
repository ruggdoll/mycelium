import requests
from urllib.parse import urlparse
import re
import json
 
def fetch_sub(domain):
    url = "http://web.archive.org/cdx/search/cdx?url=*.{}&output=json&fl=original&collapse=urlkey".format(domain)
    domains = []
    try:
        req = requests.get(url, timeout=20)
        urls = req.json()
        for item in urls:
            urlString = item[0]
            if domain in urlString:
                parsed_uri = urlparse(urlString)
                onlyDomain = "{uri.netloc}".format(uri=parsed_uri).split(":")[0]
                domains.append(onlyDomain)
    except requests.exceptions.RequestException as err:
        print("Oops: Something went wrong", err)
    return domains
