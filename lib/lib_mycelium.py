import socket,sys,time
from lib.rhizomorphe import lib_alienvault
from lib.rhizomorphe import lib_archive
from lib.rhizomorphe import lib_certspotter
from lib.rhizomorphe import lib_crt
from lib.rhizomorphe import lib_hackertarget
from lib.rhizomorphe import lib_rapiddns
from lib.rhizomorphe import lib_riddler
from lib.rhizomorphe import lib_threatminer
from lib.rhizomorphe import lib_urlscan


class Mycelium:
    def __init__(self, domain):
        self.domain = domain
        self.sub_list = []
        self.other_list = []

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
        forbidden = (
            'googlemail.com',
            'google.com',
            'cloudflaressl.com',
            'ovh.net'
            )
        if candidate.endswith(forbidden):
            return True
        else:
            return False

    def handle_list(self,list):
        for item in list:
            if item[-1] == '.':
                item = item[:-1]
            if item[:2] == "*.":
                item=item[2:]
            if self.check_forbidden(item.lower()):
                continue
            if self.check_ip(item):
                continue
            if item.endswith(self.domain):
                if item not in self.sub_list:
                    self.sub_list.append(item)
            elif (item.lower() not in self.other_list):
                self.other_list.append(item.lower())
    
    def print_progress(self,list,text):
        for i in range(0, 101, 10):
            print("\r>> {} :{}%".format(text,i), end='')
            sys.stdout.flush()
            self.handle_list(list)

    def grow(self):
        print("Working please wait.")
        self.print_progress(lib_alienvault.fetch_sub(self.domain),"Alienvault")
        self.print_progress(lib_archive.fetch_sub(self.domain),"Archive.org")
        self.print_progress(lib_certspotter.fetch_sub(self.domain),"Certspotter")
        self.print_progress(lib_crt.fetch_sub(self.domain),"CRT.sh")
        self.print_progress(lib_hackertarget.fetch_sub(self.domain),"Hackertarget")
        self.print_progress(lib_rapiddns.fetch_sub(self.domain),"Rapiddns")
        self.print_progress(lib_riddler.fetch_sub(self.domain),"Riddler")
        self.print_progress(lib_threatminer.fetch_sub(self.domain),"Threatminer")
        self.print_progress(lib_urlscan.fetch_sub(self.domain),"Urlscan")
        print("\r",end='')
        sys.stdout.flush()

    def CSV_output(self):
        print("\n----8<----CSV_STARTS_HERE----8<----")
        print("\"Index\";\"Domain\";\"Type\";")
        i=1
        for sub in self.sub_list:
            print("\"{}\";\"{}\";\"subdomain\";".format(i,sub))
            i += 1 
        for other in self.other_list:
            print("\"{}\";\"{}\";\"other\";".format(i,other))
            i += 1
        print("----8<----CSV_STOPS_HERE----8<----")
    
    def std_output(self):
        print("\nFound {} subdomains and {} linked domains".format(
            len(self.sub_list),
            len(self.other_list)
            ))
        for sub in self.sub_list:
            print("Subdomain : {}".format(sub))
        for other in self.other_list:
            print("Linked : {}".format(other))
