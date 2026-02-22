import socket,sys,time
from lib.rhizomorphe import lib_alienvault
from lib.rhizomorphe import lib_archive
from lib.rhizomorphe import lib_certspotter
from lib.rhizomorphe import lib_crt
from lib.rhizomorphe import lib_hackertarget
from lib.rhizomorphe import lib_jldc
from lib.rhizomorphe import lib_rapiddns
from lib.rhizomorphe import lib_urlscan


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
            'ovh.net'
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
    
    def print_progress(self,list,text):
        self.handle_list(list, source=text)
        print(">> {} :done".format(text))

    def grow(self):
        print("Data aquisition started")
        try:
            self.print_progress(lib_alienvault.fetch_sub(self.domain),"Alienvault")
        except:
            print("worker Alienvault failed!\n")
            pass
        try:
            self.print_progress(lib_archive.fetch_sub(self.domain),"Archive.org")
        except:
            print("worker Archive.org failed!\n")
            pass
        try:
            self.print_progress(lib_certspotter.fetch_sub(self.domain),"Certspotter")
        except:
            print("worker Certspotter failed!\n")
            pass
        try:
            self.print_progress(lib_crt.fetch_sub(self.domain),"CRT.sh")
        except:
            print("worker CRT.sh failed!\n")
            pass
        try:
            self.print_progress(lib_hackertarget.fetch_sub(self.domain),"Hackertarget")
        except:
            print("worker Hackertarget failed!\n")
            pass
        try:
            self.print_progress(lib_jldc.fetch_sub(self.domain),"JLDC")
        except:
            print("worker JLDC failed!\n")
            pass
        try:
            self.print_progress(lib_rapiddns.fetch_sub(self.domain),"Rapiddns")
        except:
            print("worker Rapiddns failed!\n")
            pass
        try:
            self.print_progress(lib_urlscan.fetch_sub(self.domain),"Urlscan")
        except:
            print("worker urlscan failed!\n")
            pass
        print("Data acquisition finished.\n")

    def Domain_CSV_output(self):
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
    
    def Domain_std_output(self):
        print("\nFound {} subdomains and {} linked domains".format(
            len(self.sub_list),
            len(self.other_list)
            ))
        for sub in self.sub_list:
            print("Subdomain : {}".format(sub))
        for other in self.other_list:
            print("Linked : {}".format(other))

    def resolve(self):
        print("Performing DNS resolution, please wait...")
        
        domain_list = {}
        for dom in (self.sub_list + self.other_list):
            try:
                datas=socket.gethostbyname_ex(dom)
                ips=[]
                for i in range(1,len(datas)):
                    if (''.join(datas[i]) != '') and (dom != ''.join(datas[i])):
                        ips.append(datas[i])
                domain_list[dom]=ips
            except:
                continue
        print("DNS resolutions finished.")
        return domain_list
