import dns.resolver

# NOTE: ce dissecteur génère des requêtes DNS directes vers les nameservers de la
# cible. Il est classifié comme ACTIF et n'est appelé que via --active.

_WORDLIST = [
    # Infrastructure générique
    "www", "mail", "smtp", "pop", "pop3", "imap", "imap4", "ftp", "sftp",
    "webmail", "mx", "mx1", "mx2", "relay", "exchange",
    "ns1", "ns2", "ns3", "ns4", "dns", "dns1", "dns2",
    # Accès distant / VPN
    "vpn", "vpn1", "vpn2", "remote", "ras", "rdp", "citrix", "anyconnect",
    # Développement / CI
    "api", "api2", "api-v2", "rest", "graphql",
    "dev", "develop", "development", "staging", "stage", "preprod",
    "test", "uat", "qa", "sandbox", "demo", "beta", "alpha",
    "git", "gitlab", "github", "svn", "repo", "ci", "jenkins", "build",
    # Applications métier
    "app", "apps", "portal", "extranet", "intranet", "internal", "corp",
    "confluence", "jira", "wiki", "sharepoint", "helpdesk", "support", "crm",
    "erp", "sap", "sfdc", "salesforce",
    # Admin / Hébergement
    "admin", "panel", "dashboard", "mgmt", "manage",
    "cpanel", "whm", "plesk", "directadmin",
    # Auth / SSO
    "login", "auth", "sso", "sts", "adfs", "idp", "oauth",
    # Web / Média / CDN
    "blog", "shop", "store", "media", "static", "cdn", "assets", "img",
    "images", "files", "upload", "download", "share", "s3",
    "m", "mobile", "wap", "secure", "ssl",
    # Observabilité
    "monitoring", "monitor", "grafana", "prometheus", "kibana", "elastic",
    "splunk", "datadog", "nagios", "zabbix", "prtg",
    # Bases de données (accès externe rare mais ça arrive)
    "db", "db1", "db2", "database", "mysql", "postgres", "redis", "mongo",
    # Messagerie / Collab
    "autodiscover", "autoconfig", "meet", "calendar", "teams",
    # Backup / Infra
    "backup", "bak", "proxy", "fw", "firewall", "gw", "gateway",
    "lb", "loadbalancer", "haproxy", "nginx",
]


def fetch_sub(domain):
    """
    Résolution DNS directe sur une liste de préfixes communs.
    Requête A uniquement — rapide et suffisant pour confirmer l'existence.
    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    found = []
    for word in _WORDLIST:
        candidate = "{}.{}".format(word, domain)
        try:
            resolver.resolve(candidate, "A")
            found.append(candidate)
        except Exception:
            continue
    return sorted(found)
