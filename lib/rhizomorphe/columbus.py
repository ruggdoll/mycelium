import requests

class Columbus:
    """
    Query Columbus API (Project Discovery).
    Fast, open, and reliable alternative to crt.sh.
    """
    def __init__(self, domain):
        self.domain = domain
        self.url = f"https://columbus.elmasy.com/api/lookup/{domain}"

    def get_data(self):
        try:
            r = requests.get(self.url, timeout=10)
            if r.status_code == 200:
                # Columbus renvoie souvent une liste simple de sous-domaines
                data = r.json()
                return [d for d in data if d.endswith(self.domain)]
        except:
            pass
        return []
