import socket
import rhizomorphe.lib_alienvault
import rhizomorphe.lib_certspotter
import rhizomorphe.lib_crt
import rhizomorphe.lib_hackertarget
import rhizomorphe.lib_omnisint
import rhizomorphe.lib_rapiddns
import rhizomorphe.lib_riddler
import rhizomorphe.lib_threatminer
import rhizomorphe.lib_urlscan


# Freely inspired by :
# https://github.com/D3Ext/AORT
# https://github.com/gfek/Lepus
# https://github.com/ruggdoll/certific8

class Mycelium:
    def __init__(self, domain):
        self.domain=domain
        self.fqdn_list=[]
        self.additionnal_list=[]
#        self.handle_list({self.domain})

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

    def handle_list(self,list):
        for item in list:
            if item[-1]=='.':
                item = item[:-1]
            if item[:2]=="*.":
                item=item[2:]
            if self.check_forbidden(item.lower()):
                continue
            if self.check_ip(item):
                continue
            if item.endswith(self.domain):
                if item not in self.fqdn_list:
                    self.fqdn_list.append(item)
            elif (item.lower() not in self.additionnal_list):
                self.additionnal_list.append(item.lower())


    def grow(self):
#        self.handle_list(rhizomorphe.lib_alienvault.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_certspotter.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_crt.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_hackertarget.fetch_sub(self.domain))
        self.handle_list(rhizomorphe.lib_omnisint.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_rapiddns.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_riddler.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_threatminer.fetch_sub(self.domain))
#        self.handle_list(rhizomorphe.lib_urlscan.fetch_sub(self.domain))