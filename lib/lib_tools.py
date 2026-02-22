import struct
from pyvis.network import Network
import socket


class GraphVisualization:

    def __init__(self):
        self.visual = []

    def addLink(self, a, b, kind="subdomain", label=""):
        self.visual.append({"from": a, "to": b, "kind": kind, "label": label})

    def visualize(self, domain):
        net = Network(height="100vh", width="100%", bgcolor="#0d1117", font_color="#c9d1d9")

        # Root domain — épinglé au centre
        net.add_node(domain, label=domain, shape="star", size=32,
            color={"background": "#e3b341", "border": "#f0c059",
                   "highlight": {"background": "#f0c059", "border": "#ffd77a"}},
            font={"size": 17, "color": "#ffffff"},
            x=0, y=0, physics=False)

        added_nodes = {domain}

        for link in self.visual:
            a, b, kind, label = link["from"], link["to"], link["kind"], link["label"]
            if a == b:
                continue

            if b not in added_nodes:
                NetObj = NetObject(b)
                if NetObj.isHost:
                    if b.endswith("." + domain) or b == domain:
                        short_label = b[: b.rfind("." + domain)]
                        net.add_node(b, label=short_label, title=b, shape="diamond", size=16,
                            color={"background": "#1f6feb", "border": "#58a6ff",
                                   "highlight": {"background": "#388bfd", "border": "#79c0ff"}},
                            font={"size": 13, "color": "#e6edf3"})
                    else:
                        net.add_node(b, label=b, shape="square", size=14,
                            color={"background": "#6e40c9", "border": "#bc8cff",
                                   "highlight": {"background": "#8957e5", "border": "#d2a8ff"}},
                            font={"size": 13, "color": "#e6edf3"})
                else:
                    if NetObj.isPrivateIP:
                        net.add_node(b, label=b, shape="dot", size=11,
                            color={"background": "#da3633", "border": "#f85149",
                                   "highlight": {"background": "#f85149", "border": "#ff7b72"}},
                            font={"size": 11, "color": "#e6edf3"})
                    else:
                        net.add_node(b, label=b, shape="dot", size=11,
                            color={"background": "#238636", "border": "#3fb950",
                                   "highlight": {"background": "#2ea043", "border": "#56d364"}},
                            font={"size": 11, "color": "#e6edf3"})
                added_nodes.add(b)

            if kind == "subdomain":
                net.add_edge(a, b, color={"color": "#58a6ff", "opacity": 0.7}, width=1.5)
            elif kind == "other":
                net.add_edge(a, b, color={"color": "#bc8cff", "opacity": 0.6},
                    width=1.2, dashes=True, title=label if label else "")
            else:  # ip
                net.add_edge(a, b, color={"color": "#484f58", "opacity": 0.6}, width=1)

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