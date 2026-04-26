import requests
import re

class PivotsCSP:
    """
    Extracts subdomains from Content-Security-Policy (CSP) headers.
    High-fidelity source: if a domain is in the CSP, it's almost certainly active.
    """
    def __init__(self, domain):
        self.domain = domain
        self.url = f"https://{domain}"

    def get_data(self):
        results = set()
        try:
            # On fait un HEAD pour ne pas charger toute la page
            r = requests.head(self.url, timeout=5, allow_redirects=True)
            csp = r.headers.get('Content-Security-Policy', '')
            
            # Extraction de tout ce qui ressemble à un sous-domaine de la cible
            matches = re.findall(r'([\w\.-]+\.' + re.escape(self.domain) + r')', csp)
            for m in matches:
                results.add(m.lower().strip('.'))
        except:
            pass
        return list(results)
