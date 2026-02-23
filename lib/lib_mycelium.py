import socket,sys,time
from lib.rhizomorphe import lib_alienvault
from lib.rhizomorphe import lib_archive
from lib.rhizomorphe import lib_certspotter
from lib.rhizomorphe import lib_chaos
from lib.rhizomorphe import lib_columbus
from lib.rhizomorphe import lib_crt
from lib.rhizomorphe import lib_hackertarget
from lib.rhizomorphe import lib_jldc
from lib.rhizomorphe import lib_rapiddns
from lib.rhizomorphe import lib_robtex
from lib.rhizomorphe import lib_securitytrails
from lib.rhizomorphe import lib_shodan
from lib.rhizomorphe import lib_threatminer
from lib.rhizomorphe import lib_urlscan
from lib.rhizomorphe import lib_virustotal


class Mycelium:
    def __init__(self, domain):
        self.domain=domain
        self.sub_list=[]
        self.other_list=[]
        self.domain_sources={}

    def check_ip(self,candidate):
        try:
            socket.inet_aton(candidate)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, candidate)
                return True
            except socket.error:
                return False
                
    def check_forbidden(self,candidate):
        forbidden=(
            'googlemail.com',
            'google.com',
            'cloudflaressl.com',
            'ovh.net',
            'ovh.fr',
            'wanadoo.fr',
            'orangecustomers.net',
            'sfr.net',
            'bbox.fr',
            'free.fr',
            'numericable.fr',
            'fbxos.fr',
            'abo.wanadoo.fr',
            )
        if candidate.endswith(forbidden):
            return True
        else:
            return False

    def handle_list(self,list,source=""):
        for item in list:
            if item[-1]=='.':
                item = item[:-1]
            if item[:2]=="*.":
                item=item[2:]
            if self.check_forbidden(item.lower()):
                continue
            if self.check_ip(item):
                continue
            if item == self.domain:
                continue
            if item.endswith(self.domain):
                if item not in self.sub_list:
                    self.sub_list.append(item)
                    if source:
                        self.domain_sources[item] = source
            elif (item.lower() not in self.other_list):
                self.other_list.append(item.lower())
                if source:
                    self.domain_sources[item.lower()] = source
    
    def _run_worker(self, worker_fn, name):
        try:
            results = worker_fn(self.domain)
            self.handle_list(results, source=name)
            print("  [+] {:20s} ({} found)".format(name, len(results)))
        except RuntimeError:
            print("  [-] {:20s} no API key".format(name))
        except Exception:
            print("  [!] {:20s} unavailable".format(name))

    def grow(self):
        print("\n[ {} ]\n".format(self.domain))
        self._run_worker(lib_alienvault.fetch_sub,     "Alienvault")
        self._run_worker(lib_archive.fetch_sub,        "Archive.org")
        self._run_worker(lib_certspotter.fetch_sub,    "Certspotter")
        self._run_worker(lib_crt.fetch_sub,            "CRT.sh")
        self._run_worker(lib_hackertarget.fetch_sub,   "Hackertarget")
        self._run_worker(lib_jldc.fetch_sub,           "JLDC")
        self._run_worker(lib_rapiddns.fetch_sub,       "Rapiddns")
        self._run_worker(lib_urlscan.fetch_sub,        "Urlscan")
        self._run_worker(lib_columbus.fetch_sub,       "Columbus")
        self._run_worker(lib_threatminer.fetch_sub,    "ThreatMiner")
        self._run_worker(lib_robtex.fetch_sub,         "Robtex")
        self._run_worker(lib_virustotal.fetch_sub,     "VirusTotal")
        self._run_worker(lib_securitytrails.fetch_sub, "SecurityTrails")
        self._run_worker(lib_chaos.fetch_sub,          "Chaos")
        self._run_worker(lib_shodan.fetch_sub,         "Shodan")
        print()

    def reverse_resolve(self, domain_list):
        unique_ips = set()
        for ips_lists in domain_list.values():
            for iplist in ips_lists:
                for ip in iplist:
                    unique_ips.add(ip)
        found = []
        for ip in unique_ips:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                found.append(hostname)
            except socket.herror:
                continue
        self.handle_list(found, source="Reverse DNS")

    def resolve(self):
        domain_list = {}
        for dom in (self.sub_list + self.other_list):
            try:
                datas = socket.gethostbyname_ex(dom)
                ips = []
                for i in range(1, len(datas)):
                    if (''.join(datas[i]) != '') and (dom != ''.join(datas[i])):
                        ips.append(datas[i])
                domain_list[dom] = ips
            except:
                continue
        return domain_list
