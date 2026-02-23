import re
import socket
import ssl
import datetime
import ipaddress
import dns.resolver
import dns.zone
import dns.query
import dns.rdatatype
import dns.exception


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolver():
    r = dns.resolver.Resolver()
    r.timeout = 5
    r.lifetime = 10
    return r


def _query(domain, rdtype):
    try:
        return _resolver().resolve(domain, rdtype)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# DNS record enumeration — NS, MX, TXT, SOA, CAA
# ---------------------------------------------------------------------------

def dns_records(domain):
    """
    Retourne (hostnames, info_lines) :
    - hostnames : domaines/hôtes découverts dans les records
    - info_lines : lignes texte pour affichage console
    """
    found = []
    lines = []

    # NS
    for r in _query(domain, "NS"):
        h = str(r.target).rstrip(".")
        found.append(h)
        lines.append("  NS   {}".format(h))

    # MX
    for r in _query(domain, "MX"):
        h = str(r.exchange).rstrip(".")
        found.append(h)
        lines.append("  MX   {}".format(h))

    # SOA
    for r in _query(domain, "SOA"):
        ns   = str(r.mname).rstrip(".")
        mail = str(r.rname).rstrip(".").replace(".", "@", 1)
        found.append(ns)
        lines.append("  SOA  {}  ({})".format(ns, mail))

    # CAA
    for r in _query(domain, "CAA"):
        val = r.value.decode() if isinstance(r.value, bytes) else str(r.value)
        val = val.strip('"').split(";")[0].strip()
        found.append(val)
        lines.append("  CAA  {}".format(val))

    # TXT (brut + domaines extraits)
    txt_pattern = re.compile(r"([\w\d][\w\d\-\.]+\.[a-z]{2,})", re.IGNORECASE)
    for r in _query(domain, "TXT"):
        txt = r.to_text().strip('"')
        lines.append("  TXT  {}".format(txt))
        for m in txt_pattern.findall(txt):
            found.append(m.lower())

    return found, lines


# ---------------------------------------------------------------------------
# SPF recursive parsing
# ---------------------------------------------------------------------------

def _parse_spf(record, depth=0):
    """Extrait récursivement les domaines d'un enregistrement SPF."""
    if depth > 5:
        return []
    found = []
    dom_re = re.compile(r"(?:include|redirect|a|mx|exists|ptr):([^\s]+)", re.IGNORECASE)

    for m in dom_re.findall(record):
        found.append(m.lstrip("="))

    # suivre récursivement les include: et redirect=
    includes = re.findall(r"(?:include|redirect)[:=]([^\s]+)", record, re.IGNORECASE)
    for inc in includes:
        for r in _query(inc, "TXT"):
            txt = r.to_text().strip('"')
            if "v=spf1" in txt.lower():
                found += _parse_spf(txt, depth + 1)
    return found


def _count_spf_lookups(record, depth=0, visited=None):
    """Count DNS lookups required by SPF record (RFC 7208 §4.6.4 limit: 10)."""
    if visited is None:
        visited = set()
    if depth > 5:
        return 0

    # Mechanisms that each require one DNS lookup
    count = 0
    for term in record.split():
        t = term.lower().lstrip("+!~-")
        for mech in ("include", "a", "mx", "ptr", "exists", "redirect"):
            if (t == mech or t.startswith(mech + ":") or
                    t.startswith(mech + "=") or t.startswith(mech + "/")):
                count += 1
                break

    # Follow includes and redirects recursively
    for inc in re.findall(r"(?:include|redirect)[:=]([^\s]+)", record, re.IGNORECASE):
        if inc in visited:
            continue
        visited.add(inc)
        for r in _query(inc, "TXT"):
            txt = r.to_text().strip('"')
            if "v=spf1" in txt.lower():
                count += _count_spf_lookups(txt, depth + 1, visited)
    return count


def spf_harvest(domain):
    """
    Retourne (hostnames, info_lines) depuis les enregistrements SPF du domaine.
    """
    found = []
    lines = []
    for r in _query(domain, "TXT"):
        txt = r.to_text().strip('"')
        if txt.lower().startswith("v=spf1"):
            lines.append("  SPF  {}".format(txt))
            found += _parse_spf(txt)
    return found, lines


# ---------------------------------------------------------------------------
# Zone transfer (AXFR)
# ---------------------------------------------------------------------------

def zone_transfer(domain):
    """
    Tente un AXFR sur chaque nameserver du domaine.
    Retourne (hostnames, info_lines).
    """
    found = []
    lines = []

    ns_records = _query(domain, "NS")
    if not ns_records:
        return found, lines

    for ns_rdata in ns_records:
        ns = str(ns_rdata.target).rstrip(".")
        try:
            ns_ip = socket.gethostbyname(ns)
            z = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=10))
            count = 0
            for name in z.nodes.keys():
                fqdn = "{}.{}".format(name, domain) if str(name) != "@" else domain
                found.append(fqdn)
                count += 1
            lines.append("  AXFR {} -> {} records".format(ns, count))
        except dns.exception.FormError:
            lines.append("  AXFR {} -> refused".format(ns))
        except Exception as e:
            lines.append("  AXFR {} -> failed ({})".format(ns, type(e).__name__))

    return found, lines


# ---------------------------------------------------------------------------
# DNS resolution + reverse DNS
# ---------------------------------------------------------------------------

def resolve(domains):
    """Résout une liste de domaines. Retourne {domain: [[ip, ...], ...]}"""
    domain_list = {}
    for dom in domains:
        try:
            datas = socket.gethostbyname_ex(dom)
            ips = []
            for i in range(1, len(datas)):
                if (''.join(datas[i]) != '') and (dom != ''.join(datas[i])):
                    ips.append(datas[i])
            domain_list[dom] = ips
        except Exception:
            continue
    return domain_list


def reverse_resolve(domain_list):
    """Reverse DNS sur les IPs résolues. Retourne une liste de hostnames."""
    unique_ips = set()
    for ips_lists in domain_list.values():
        for iplist in ips_lists:
            for ip in iplist:
                unique_ips.add(ip)
    found = []
    for ip in unique_ips:
        try:
            found.append(socket.gethostbyaddr(ip)[0])
        except socket.herror:
            continue
    return found


# ---------------------------------------------------------------------------
# Security findings — helpers
# ---------------------------------------------------------------------------

# Fingerprints de services cloud dont un subdomain orphelin peut être revendiqué
_TAKEOVER_FINGERPRINTS = [
    ("github.io",             "There isn't a GitHub Pages site here"),
    ("herokuapp.com",         "No such app"),
    ("s3.amazonaws.com",      "NoSuchBucket"),
    ("blob.core.windows.net", "404 Web Site not found"),
    ("netlify.app",           "Not Found"),
    ("netlify.com",           "Not Found"),
    ("myshopify.com",         "Sorry, this shop is currently unavailable"),
    ("fastly.net",            "Fastly error: unknown domain"),
    ("cargo.site",            "If you're moving your domain away from Cargo"),
    ("readme.io",             "Project doesnt exist"),
    ("helpscoutdocs.com",     "No settings were found for this company"),
    ("ghost.io",              "The thing you were looking for is no longer here"),
    ("surge.sh",              "project not found"),
    ("bitbucket.io",          "Repository not found"),
    ("smartling.com",         "Domain is not configured"),
    ("uservoice.com",         "This UserVoice subdomain is currently available"),
    ("zendesk.com",           "Help Center Closed"),
    ("statuspage.io",         "You are being redirected"),
]


def _get_cname(subdomain):
    """Retourne la cible CNAME finale d'un subdomain, ou None."""
    try:
        answers = _resolver().resolve(subdomain, "CNAME")
        return str(answers[0].target).rstrip(".")
    except Exception:
        return None


def _check_takeover(subdomain):
    """
    Vérifie si un subdomain est candidat au takeover.
    Retourne (cname, service) ou None.
    """
    import requests as req
    cname = _get_cname(subdomain)
    if not cname:
        return None
    for (pattern, fingerprint) in _TAKEOVER_FINGERPRINTS:
        if pattern in cname:
            try:
                r = req.get("http://{}".format(subdomain), timeout=8,
                            allow_redirects=True)
                if fingerprint.lower() in r.text.lower():
                    return (cname, pattern)
            except Exception:
                return (cname, pattern + " (no response)")
    return None


def _check_dangling_cnames(subdomains):
    """Check for CNAMEs pointing to non-existent targets (NXDOMAIN)."""
    findings = []
    for sub in subdomains:
        cname = _get_cname(sub)
        if not cname:
            continue
        try:
            socket.gethostbyname(cname)
        except socket.gaierror:
            findings.append(("CRITICAL",
                "Dangling CNAME: {} -> {} (target NXDOMAIN)".format(sub, cname)))
    return findings


def _check_dnssec(domain):
    """Check if DNSSEC is configured (DNSKEY present at zone apex)."""
    if list(_query(domain, "DNSKEY")):
        return ("OK", "DNSSEC configured (DNSKEY present)")
    return ("WARNING", "DNSSEC not configured — no DNSKEY record")


def _check_dkim(domain):
    """Check common DKIM selectors."""
    selectors = [
        "default", "selector1", "selector2", "google", "mail",
        "k1", "dkim", "smtp", "s1", "s2", "mimecast", "postmark",
    ]
    found = []
    for sel in selectors:
        name = "{}._domainkey.{}".format(sel, domain)
        for r in _query(name, "TXT"):
            txt = r.to_text().strip('"')
            if "v=dkim1" in txt.lower() or "k=rsa" in txt.lower() or "p=" in txt.lower():
                found.append(sel)
                break
    if found:
        return [("OK", "DKIM configured (selectors: {})".format(", ".join(found)))]
    return [("WARNING", "No DKIM record found (checked {} common selectors)".format(len(selectors)))]


def _check_mta_sts(domain):
    """Check MTA-STS policy record."""
    for r in _query("_mta-sts.{}".format(domain), "TXT"):
        txt = r.to_text().strip('"')
        if "v=sts1" in txt.lower():
            return ("OK", "MTA-STS configured")
    return ("WARNING", "No MTA-STS record — no SMTP transport security policy")


def _check_ns_diversity(domain):
    """Check if all nameservers share the same /24 subnet (SPOF risk)."""
    ns_ips = []
    for r in _query(domain, "NS"):
        ns = str(r.target).rstrip(".")
        try:
            ip = socket.gethostbyname(ns)
            ns_ips.append(ip)
        except Exception:
            continue
    if len(ns_ips) < 2:
        return None
    prefixes = set()
    for ip in ns_ips:
        try:
            net = ipaddress.ip_network("{}/24".format(ip), strict=False)
            prefixes.add(str(net))
        except Exception:
            continue
    if len(prefixes) == 1:
        return ("WARNING",
            "All nameservers in same /24 ({}) — single point of failure".format(
                list(prefixes)[0]))
    return ("OK", "Nameservers distributed across {} /24 subnets".format(len(prefixes)))


def _check_cert_expiry(domain):
    """Check TLS certificate validity and days until expiry."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                not_after_str = cert.get("notAfter", "")
                not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                days_left = (not_after - datetime.datetime.utcnow()).days
                if days_left < 0:
                    return ("CRITICAL", "TLS certificate EXPIRED {} days ago".format(-days_left))
                elif days_left < 14:
                    return ("CRITICAL", "TLS certificate expires in {} days".format(days_left))
                elif days_left < 30:
                    return ("WARNING", "TLS certificate expires in {} days".format(days_left))
                else:
                    return ("OK", "TLS certificate valid for {} more days".format(days_left))
    except ssl.SSLCertVerificationError as e:
        return ("CRITICAL", "TLS certificate invalid: {}".format(str(e)[:80]))
    except Exception:
        return None  # Not reachable on 443, skip silently


# ---------------------------------------------------------------------------
# Security findings — main
# ---------------------------------------------------------------------------

def security_findings(domain, subdomains, axfr_lines, spf_lines):
    """
    Retourne une liste de (level, message) :
      level : 'CRITICAL' | 'WARNING' | 'OK'
    """
    findings = []

    # --- AXFR ---
    for line in axfr_lines:
        if "records" in line and "refused" not in line and "failed" not in line:
            ns = line.strip().split()[1]
            findings.append(("CRITICAL", "Zone transfer open on {}".format(ns)))
    if all("refused" in l or "failed" in l for l in axfr_lines) and axfr_lines:
        findings.append(("OK", "Zone transfer refused on all nameservers"))

    # --- SPF policy ---
    spf_found = False
    for line in spf_lines:
        if "v=spf1" in line.lower():
            spf_found = True
            if "+all" in line:
                findings.append(("CRITICAL", "SPF +all — anyone can spoof this domain"))
            elif "?all" in line:
                findings.append(("WARNING", "SPF ?all — neutral policy, no protection"))
            elif "~all" in line:
                findings.append(("WARNING", "SPF ~all — softfail, spoofing may go undetected"))
            elif "-all" in line:
                findings.append(("OK", "SPF -all — strict policy"))
            else:
                findings.append(("WARNING", "SPF has no 'all' directive"))
    if not spf_found:
        findings.append(("CRITICAL", "No SPF record — email spoofing unprotected"))

    # --- SPF lookup count (RFC 7208 limit: 10) ---
    for r in _query(domain, "TXT"):
        txt = r.to_text().strip('"')
        if txt.lower().startswith("v=spf1"):
            n = _count_spf_lookups(txt)
            if n > 10:
                findings.append(("CRITICAL",
                    "SPF lookup count {} > 10 — permerror, SPF will always fail".format(n)))
            elif n > 7:
                findings.append(("WARNING",
                    "SPF lookup count {} (approaching 10-lookup RFC limit)".format(n)))
            break

    # --- DMARC ---
    dmarc_found = False
    for r in _query("_dmarc.{}".format(domain), "TXT"):
        txt = r.to_text().strip('"')
        if "v=dmarc1" in txt.lower() and not dmarc_found:
            dmarc_found = True
            m = re.search(r"p=(\w+)", txt, re.IGNORECASE)
            policy = m.group(1).lower() if m else "unknown"
            if policy == "none":
                findings.append(("WARNING", "DMARC p=none — monitoring only, no enforcement"))
            elif policy in ("quarantine", "reject"):
                findings.append(("OK", "DMARC p={} — enforced".format(policy)))
            else:
                findings.append(("WARNING", "DMARC policy unknown: {}".format(txt)))
            if "rua=" not in txt.lower():
                findings.append(("WARNING", "DMARC: no rua= aggregate reporting configured"))
    if not dmarc_found:
        findings.append(("CRITICAL", "No DMARC record — spoofed emails reach inbox"))

    # --- DKIM ---
    findings.extend(_check_dkim(domain))

    # --- MTA-STS ---
    findings.append(_check_mta_sts(domain))

    # --- CAA ---
    if not list(_query(domain, "CAA")):
        findings.append(("WARNING", "No CAA record — any CA can issue certificates"))

    # --- DNSSEC ---
    findings.append(_check_dnssec(domain))

    # --- NS diversity ---
    ns_div = _check_ns_diversity(domain)
    if ns_div:
        findings.append(ns_div)

    # --- Wildcard DNS ---
    import random
    import string
    rand = ''.join(random.choices(string.ascii_lowercase, k=12))
    wild_test = "{}.{}".format(rand, domain)
    try:
        socket.gethostbyname(wild_test)
        findings.append(("WARNING", "Wildcard DNS — *.{} resolves".format(domain)))
    except socket.gaierror:
        findings.append(("OK", "No wildcard DNS"))

    # --- Certificate expiry ---
    cert = _check_cert_expiry(domain)
    if cert:
        findings.append(cert)

    # --- Dangling CNAMEs ---
    findings.extend(_check_dangling_cnames(subdomains))

    # --- Subdomain takeover ---
    for sub in subdomains:
        result = _check_takeover(sub)
        if result:
            cname, service = result
            findings.append(("CRITICAL",
                "Subdomain takeover candidate: {} -> {} ({})".format(sub, cname, service)))

    return findings
