import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_sub(domain):
    """Queries Subdomain Center API."""
    results = set()
    try:
        url = f"https://api.subdomain.center/?domain={domain}"
        r = requests.get(url, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            for sub in data:
                if sub.endswith(domain):
                    results.add(sub.lower())
    except:
        pass
    return list(results)
