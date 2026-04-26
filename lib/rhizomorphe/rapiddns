import requests
import re

class RapidDNS:
    """
    Scraper pour RapidDNS.io.
    Trouve des records DNS historiques sans dépendre des logs CT.
    """
    def __init__(self, domain):
        self.domain = domain
        self.url = f"https://rapiddns.io/subdomain/{domain}#result"

    def get_data(self):
        results = set()
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Mycelium/1.0'}
            r = requests.get(self.url, headers=headers, timeout=15)
            if r.status_code == 200:
                # Extraction des domaines se terminant par la cible dans les cellules <td>
                pattern = re.compile(r'<td>([\w\.-]+\.' + re.escape(self.domain) + r')</td>')
                matches = pattern.findall(r.text)
                for m in matches:
                    results.add(m.lower())
        except:
            pass
        return list(results)
