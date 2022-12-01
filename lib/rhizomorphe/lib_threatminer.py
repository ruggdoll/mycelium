import requests
import re
import json
 
def fetch_sub(domain):
    print("Fetching datas from : https://threatminer.org\n")
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

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

    return domains