import requests
import re

def fetch_sub(domain):
    """
    Scrape DuckDuckGo (HTML version) for indexed subdomains.
    """
    results = set()
    try:
        # L'endpoint /html/ est plus simple à parser sans JS
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'}
        url = f"https://duckduckgo.com/html/?q=site%3A{domain}"
        
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # Extraction des patterns qui matchent <sub.domain.tld>
            matches = re.findall(r'([\w\.-]+\.' + re.escape(domain) + r')', r.text)
            for m in matches:
                # Nettoyage basique pour éviter les résidus HTML
                clean_m = m.lower().strip('.')
                if clean_m.endswith(domain):
                    results.add(clean_m)
    except:
        pass
    return list(results)
