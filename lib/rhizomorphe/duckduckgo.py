import requests
import re

class DuckDuckGo:
    """
    Exploitation des résultats de recherche DuckDuckGo pour trouver des sous-domaines indexés.
    """
    def __init__(self, domain):
        self.domain = domain
        self.url = f"https://duckduckgo.com/html/?q=site%3A{domain}"

    def get_data(self):
        results = set()
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(self.url, headers=headers, timeout=10)
            if r.status_code == 200:
                # Regex pour isoler les domaines dans les snippets/liens
                pattern = re.compile(r'([\w\.-]+\.' + re.escape(self.domain) + r')')
                matches = pattern.findall(r.text)
                for m in matches:
                    results.add(m.lower())
        except:
            pass
        return list(results)
