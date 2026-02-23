import struct
from pyvis.network import Network
import socket


class GraphVisualization:

    def __init__(self):
        self.visual = []
        self._edge_set = set()

    def addLink(self, a, b, kind="subdomain", label=""):
        key = (a, b, kind)
        if key not in self._edge_set:
            self._edge_set.add(key)
            self.visual.append({"from": a, "to": b, "kind": kind, "label": label})

    def _add_other_node(self, net, node_id):
        net.add_node(node_id, label=node_id, shape="square", size=14,
            color={"background": "#6e40c9", "border": "#bc8cff",
                   "highlight": {"background": "#8957e5", "border": "#d2a8ff"}},
            font={"size": 13, "color": "#e6edf3"})

    def _build_sidebar(self, domain, all_subs, all_others):
        def li(d, color):
            return (
                '<li style="padding:3px 0;word-break:break-all">'
                '<a href="http://{d}" target="_blank" style="color:{c};text-decoration:none;'
                'font-family:monospace;font-size:12px">{d}</a></li>'
            ).format(d=d, c=color)
        sub_items  = "".join(li(d, "#58a6ff") for d in sorted(all_subs))
        other_items = "".join(li(d, "#bc8cff") for d in sorted(all_others))
        return (
            '<div id="mycelium-sidebar" style="width:300px;min-width:300px;height:100vh;'
            'overflow-y:auto;background:#0d1117;border-left:1px solid #21262d;'
            'color:#c9d1d9;box-sizing:border-box;flex-shrink:0">'
            '<div style="padding:14px 16px;border-bottom:1px solid #21262d;position:sticky;'
            'top:0;background:#0d1117;z-index:10">'
            '<span style="color:#e3b341;font-size:16px;font-weight:bold">&#9733; {domain}</span>'
            '</div>'
            '<div style="padding:12px 16px">'
            '<div style="color:#58a6ff;font-size:12px;font-weight:600;margin-bottom:8px;'
            'text-transform:uppercase;letter-spacing:.5px">'
            'Subdomains <span style="color:#484f58;font-weight:normal">({nsub})</span></div>'
            '<ul style="margin:0;padding:0;list-style:none">{sub}</ul>'
            '</div>'
            '<div style="padding:12px 16px;border-top:1px solid #21262d">'
            '<div style="color:#bc8cff;font-size:12px;font-weight:600;margin-bottom:8px;'
            'text-transform:uppercase;letter-spacing:.5px">'
            'Linked <span style="color:#484f58;font-weight:normal">({nother})</span></div>'
            '<ul style="margin:0;padding:0;list-style:none">{other}</ul>'
            '</div>'
            '</div>'
        ).format(domain=domain, nsub=len(all_subs), nother=len(all_others),
                 sub=sub_items, other=other_items)

    def visualize(self, domain, pivot_domains=None, all_subs=None, all_others=None):
        if pivot_domains is None:
            pivot_domains = set()
        if all_subs is None:
            all_subs = {}
        if all_others is None:
            all_others = {}
        net = Network(height="100vh", width="100%", bgcolor="#0d1117", font_color="#c9d1d9")

        # Root domain — épinglé au centre
        net.add_node(domain, label=domain, shape="star", size=32,
            color={"background": "#e3b341", "border": "#f0c059",
                   "highlight": {"background": "#f0c059", "border": "#ffd77a"}},
            font={"size": 17, "color": "#ffffff"},
            x=0, y=0, physics=False)

        added_nodes = {domain}

        # Pré-insertion des nœuds pivots (triangles ambrés)
        for pdom in pivot_domains:
            if pdom not in added_nodes:
                net.add_node(pdom, label=pdom, title=pdom, shape="triangle", size=22,
                    color={"background": "#9e6a03", "border": "#e3b341",
                           "highlight": {"background": "#b08800", "border": "#f0c059"}},
                    font={"size": 14, "color": "#ffffff"})
                added_nodes.add(pdom)

        for link in self.visual:
            a, b, kind, label = link["from"], link["to"], link["kind"], link["label"]
            if a == b:
                continue

            # Garde : si 'a' n'est pas encore dans le graphe, on l'ajoute
            if a not in added_nodes:
                self._add_other_node(net, a)
                added_nodes.add(a)

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
                        self._add_other_node(net, b)
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
        css = (
            '<style>'
            'html,body{margin:0;padding:0;height:100%;overflow:hidden}'
            'body{display:flex!important;flex-direction:row;background:#0d1117}'
            '#mynetwork{flex:1!important;height:100vh!important;min-width:0}'
            '</style>'
        )
        sidebar = self._build_sidebar(domain, all_subs, all_others)
        try:
            html = net.generate_html()
            html = html.replace('</head>', css + '</head>', 1)
            html = html.replace('</body>', sidebar + '</body>', 1)
            with open(domain + ".html", "w") as f:
                f.write(html)
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