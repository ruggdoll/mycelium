import requests
import re
 
def fetch_sub(domain):
    print("Fetching datas from : https://hackertarget.com\n")
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

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

    return domains