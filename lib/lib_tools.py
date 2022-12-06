import matplotlib.pyplot as plt
from pyvis.network import Network
import socket


class GraphVisualization:

    def __init__(self):
        self.visual = []
            
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def visualize(self,domain):
        net = Network(notebook=True)
        for nodes in self.visual:
            if nodes[0]==nodes[1]:
                continue
            for node in nodes:
                NetObj = NetObject(node)
                if NetObj.isHost == True:
                    net.add_node(node,label=node,color="blue",shape="diamond",size=10)
                elif NetObj.isHost == False:
                    if NetObj.is_private_ip ==True:
                        net.add_node(node,label=node,color="red",size=10)
                    else:
                        net.add_node(node,label=node,color="green",size=10)
            net.add_edge(nodes[0],nodes[1])
        try:
            net.show(domain + ".html")
        except:
            print("File generation failed :(")
            pass
        print("Graph file {} generated successfuly YAY".format(domain + ".html"))



class NetObject:
        
    def __init__(self,NetObj):
        self.node=NetObj
        if self.is_ip(NetObj):
            self.isHost=False
            if self.is_private_ip(self.node):
                self.isPrivateIP=True
            else:
                self.isPrivateIP=False
        else :
            self.isHost=True
    
    def is_ip(self,candidate):
            try:
                socket.inet_aton(candidate)
                return(True)
            except socket.error:
                return(False)

    def is_private_ip(self,ip):
        networks = [
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.0.0.0/24",
        "192.0.2.0/24",
        "192.88.99.0/24",
        "192.168.0.0/16",
        "198.18.0.0/15",
        "198.51.100.0/24",
        "203.0.113.0/24",
        "240.0.0.0/4",
        "255.255.255.255/32",
        "224.0.0.0/4",
        ]

        for network in networks:
            try:
                ipaddr = struct.unpack(">I", socket.inet_aton(ip))[0]
                netaddr, bits = network.split("/")
                network_low = struct.unpack(">I", socket.inet_aton(netaddr))[0]
                network_high = network_low | 1 << (32 - int(bits)) - 1
                if ipaddr <= network_high and ipaddr >= network_low:
                    return True
            except Exception :
                continue
        return False