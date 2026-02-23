import requests
import json

def fetch_sub(domain):
    session = requests.session()
    session.headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://api.threatminer.org/v2/domain.php?q={}&rt=5".format(domain)
    req = session.get(url, timeout=20)
    req.raise_for_status()
    data = json.loads(req.text)
    if data.get("status_code") == "200":
        return sorted(set(data.get("results", [])))
    return []
