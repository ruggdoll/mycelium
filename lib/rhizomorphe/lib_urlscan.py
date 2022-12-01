import requests
import re

 
def fetch_sub(domain):
    print("Fetching datas from : https://urlscan.io\n")
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

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

    return domains