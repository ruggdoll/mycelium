import struct
from pyvis.network import Network
import socket


class GraphVisualization:

    def __init__(self):
        self.visual = []
            
    def addLink(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def visualize(self,domain):
        net = Network(height="100vh", width="100%", bgcolor="#0d1117", font_color="#c9d1d9")
        for nodes in self.visual:
            if nodes[0]==nodes[1]:
                continue
            for node in nodes:
                NetObj = NetObject(node)
                if NetObj.isHost == True:
                    net.add_node(node, label=node, shape="diamond", size=16,
                        color={"background":"#1f6feb","border":"#58a6ff",
                               "highlight":{"background":"#388bfd","border":"#79c0ff"}},
                        font={"size":13,"color":"#e6edf3"})
                elif NetObj.isHost == False:
                    if NetObj.isPrivateIP == True:
                        net.add_node(node, label=node, shape="dot", size=12,
                            color={"background":"#da3633","border":"#f85149",
                                   "highlight":{"background":"#f85149","border":"#ff7b72"}},
                            font={"size":11,"color":"#e6edf3"})
                    else:
                        net.add_node(node, label=node, shape="dot", size=12,
                            color={"background":"#238636","border":"#3fb950",
                                   "highlight":{"background":"#2ea043","border":"#56d364"}},
                            font={"size":11,"color":"#e6edf3"})
            net.add_edge(nodes[0], nodes[1], color={"color":"#484f58","opacity":0.8}, width=1.5)
        net.set_options("""
        {
          "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -80,
              "centralGravity": 0.01,
              "springLength": 130,
              "springConstant": 0.08,
              "damping": 0.4
            },
            "maxVelocity": 50,
            "stabilization": { "enabled": true, "iterations": 1000 }
          },
          "edges": { "smooth": { "type": "continuous" } },
          "interaction": { "hover": true, "tooltipDelay": 200 }
        }
        """)
        try:
            net.write_html(domain + ".html")
            print("Graph file {} generated successfully".format(domain + ".html"))
        except Exception as e:
            print("File generation failed :(", e)



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