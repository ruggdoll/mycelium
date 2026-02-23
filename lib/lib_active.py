import re
import socket
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
    ip_re  = re.compile(r"ip[46]:([\S]+)")

    for m in dom_re.findall(record):
        found.append(m.lstrip("="))
    # on ne suit pas les IPs mais on les ignore proprement

    # suivre récursivement les include: et redirect=
    includes = re.findall(r"(?:include|redirect)[:=]([^\s]+)", record, re.IGNORECASE)
    for inc in includes:
        for r in _query(inc, "TXT"):
            txt = r.to_text().strip('"')
            if "v=spf1" in txt.lower():
                found += _parse_spf(txt, depth + 1)
    return found


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
# DNS resolution + reverse DNS (déplacés ici depuis Mycelium)
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
