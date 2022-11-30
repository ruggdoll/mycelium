import requests
import json
 
def fetch_sub(domain):
    print("Fetching datas from : https://omnisint.io\n")
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    session.headers = {'User-Agent': ua}

    url = "https://sonar.omnisint.io/subdomains/{}".format(domain)
    pattern = r"([\w\d][\w\d\-\.]*\.{0})"
    domains=[]
    try:
        req = session.get(url,timeout=20)
        req.raise_for_status()

        if req.status_code == 200 and req.text.strip() != "null":
            data = json.loads(req.text)
            for d in data:
                domains.append(d)

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

    return domains