import requests
import re

def fetch_sub(domain):
    """
    Read Content-Security-Policy (CSP) headers to find linked subdomains.
    """
    results = set()
    try:
        # On tente de récupérer les headers sur le domaine racine
        # allow_redirects=True est crucial car bcp de domaines redirigent vers www
        r = requests.get(f"https://{domain}", timeout=5, allow_redirects=True, verify=False)
        
        # On cherche le header CSP (insensible à la casse)
        csp_header = ""
        for h in r.headers:
            if h.lower() == 'content-security-policy':
                csp_header = r.headers[h]
                break
        
        if csp_header:
            # Extraction de tous les domaines appartenant à la cible listés dans le CSP
            matches = re.findall(r'([\w\.-]+\.' + re.escape(domain) + r')', csp_header)
            for m in matches:
                results.add(m.lower().strip('.'))
    except:
        pass
    return list(results)
