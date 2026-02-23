import argparse
import os
from lib.lib_mycelium import Mycelium
from lib.lib_tools import GraphVisualization
from lib import lib_active


def load_keys(path="keys.conf"):
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and value and key not in os.environ:
                os.environ[key] = value


if __name__ == "__main__":
    load_keys()
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Domain name to analyse")
    parser.add_argument("--depth", help="Pivot depth on linked domains (default: 1)", type=int, default=1, metavar="N")
    parser.add_argument("--active", help="Enable active dissectors — disabled by default (TLP/PAP RED)", action="store_true")
    args = parser.parse_args()

    if args.depth < 1:
        parser.error("--depth must be >= 1")

    root = args.domain
    scanned_domains = {root}
    pending = [root]

    all_mushrooms = []
    all_mylist = {}
    pivot_domains = set()

    for current_depth in range(1, args.depth + 1):
        next_pending = []

        for target_domain in pending:
            if current_depth > 1:
                print("\n[Depth {}] Pivoting on: {}".format(current_depth, target_domain))
                pivot_domains.add(target_domain)

            m = Mycelium(target_domain)
            m.grow()

            if args.active:
                mylist = lib_active.resolve(m.sub_list + m.other_list)
                reverse = lib_active.reverse_resolve(mylist)
                m.handle_list(reverse, source="Reverse DNS")
                all_mylist.update(mylist)

            all_mushrooms.append((m, current_depth))

            if current_depth < args.depth:
                for dom in m.other_list:
                    if dom not in scanned_domains:
                        scanned_domains.add(dom)
                        next_pending.append(dom)

        pending = next_pending

    # Agréger les résultats passifs
    all_subs = {}
    all_others = {}
    for (m, depth_level) in all_mushrooms:
        for sub in m.sub_list:
            if sub not in all_subs:
                all_subs[sub] = m.domain
        for other in m.other_list:
            if other not in all_others:
                all_others[other] = m.domain

    # --- Dissecteurs actifs ---
    axfr_lines = []
    spf_lines  = []

    if args.active:
        print("\nActive dissectors\n")

        # DNS records (NS, MX, TXT, SOA, CAA)
        print("DNS records")
        rec_hosts, rec_lines = lib_active.dns_records(root)
        for l in rec_lines:
            print(l)
        for h in rec_hosts:
            if h.endswith("." + root) or h == root:
                all_subs.setdefault(h, "DNS records")
            else:
                all_others.setdefault(h, "DNS records")

        # SPF
        print("\nSPF")
        spf_hosts, spf_lines = lib_active.spf_harvest(root)
        if spf_lines:
            for l in spf_lines:
                print(l)
            for h in spf_hosts:
                if h.endswith("." + root) or h == root:
                    all_subs.setdefault(h, "SPF")
                else:
                    all_others.setdefault(h, "SPF")
        else:
            print("  (no SPF record)")

        # Zone transfer
        print("\nZone transfer")
        axfr_hosts, axfr_lines = lib_active.zone_transfer(root)
        for l in axfr_lines:
            print(l)
        for h in axfr_hosts:
            if h.endswith("." + root) or h == root:
                all_subs.setdefault(h, "AXFR")
            else:
                all_others.setdefault(h, "AXFR")

        # DNS resolutions
        print("\nDNS resolutions")
        seen_domains = set()
        for (m, depth_level) in all_mushrooms:
            if args.depth > 1:
                print("  -- depth {} : {} --".format(depth_level, m.domain))
            for dom in (m.sub_list + m.other_list):
                if dom in seen_domains:
                    continue
                seen_domains.add(dom)
                try:
                    for iplist in all_mylist[dom]:
                        for ip in iplist:
                            print("  {}  {}".format(dom, ip))
                except Exception:
                    continue

        new_linked = set()
        for (m, _) in all_mushrooms:
            for d in m.other_list:
                if d not in all_mylist:
                    new_linked.add(d)
        if new_linked:
            print("\nDiscovered via reverse DNS")
            for d in sorted(new_linked):
                print("  {}".format(d))

    # --- Security findings (mode --active) ---
    if args.active:
        print("\nSecurity findings\n")
        findings = lib_active.security_findings(
            root,
            list(all_subs.keys()),
            axfr_lines,
            spf_lines,
        )
        level_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2, "OK": 3}
        for level, msg in sorted(findings, key=lambda x: level_order.get(x[0], 9)):
            print("  [{:8s}] {}".format(level, msg))

    # --- Sortie console ---
    print("\nSubdomains ({})".format(len(all_subs)))
    for sub in sorted(all_subs):
        print("  {}".format(sub))
    if not all_subs:
        print("  (none)")

    print("\nLinked ({})".format(len(all_others)))
    for other in sorted(all_others):
        print("  {}".format(other))
    if not all_others:
        print("  (none)")

    # --- Sortie HTML (graphe + liste) ---
    G = GraphVisualization()
    for (m, depth_level) in all_mushrooms:
        for dom in m.sub_list:
            G.addLink(m.domain, dom, kind="subdomain")
        for dom in m.other_list:
            G.addLink(m.domain, dom, kind="other",
                      label=m.domain_sources.get(dom, ""))
        if args.active:
            for dom in (m.sub_list + m.other_list):
                if dom in all_mylist:
                    for iplist in all_mylist[dom]:
                        for ip in iplist:
                            G.addLink(dom, ip, kind="ip")

    G.visualize(root, pivot_domains=pivot_domains, all_subs=all_subs, all_others=all_others)
