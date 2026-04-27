import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# NOTE: ce dissecteur effectue une connexion directe vers la cible (requête HTTPS).
# Il est classifié comme ACTIF et n'est appelé que via --active.
# Ne pas inclure dans la liste des dissecteurs passifs.

def fetch_sub(domain):
    """
    Lit le header Content-Security-Policy du domaine cible pour extraire
    les sous-domaines déclarés. Connexion directe → actif uniquement.
    """
    results = set()
    try:
        r = requests.get(
            "https://{}".format(domain),
            timeout=5,
            allow_redirects=True,
            verify=False,
        )
        csp_header = ""
        for h in r.headers:
            if h.lower() == "content-security-policy":
                csp_header = r.headers[h]
                break
        if csp_header:
            matches = re.findall(
                r"([\w\.-]+\." + re.escape(domain) + r")", csp_header
            )
            for m in matches:
                results.add(m.lower().strip("."))
    except requests.exceptions.RequestException:
        pass
    return sorted(results)
