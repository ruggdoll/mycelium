import argparse
from lib.lib_mycelium import Mycelium
from lib.lib_tools import GraphVisualization

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    parser.add_argument("--CSV", help="Prints data in CSV format",action="store_true")
    parser.add_argument("--resolve", help="Performs a DNS resolution",action="store_true")
    parser.add_argument("--graph", help="Creates a IP-Domain graph named DOMAIN.TLD.html",action="store_true")
    args = parser.parse_args()

    mushroom = Mycelium(args.domain)
    mushroom.grow()

    mylist = {}
    if args.resolve:
        mylist = mushroom.resolve()

    if args.graph:
        G = GraphVisualization()
        root = mushroom.domain

        for dom in mushroom.sub_list:
            G.addLink(root, dom, kind="subdomain")

        for dom in mushroom.other_list:
            source = mushroom.domain_sources.get(dom, "")
            G.addLink(root, dom, kind="other", label=source)

        for dom in (mushroom.sub_list + mushroom.other_list):
            try:
                for itemlist in mylist[dom]:
                    for item in itemlist:
                        G.addLink(dom, item, kind="ip")
            except:
                continue

        G.visualize(root)

    elif args.resolve:
        for dom in (mushroom.sub_list + mushroom.other_list):
            try:
                for itemlist in mylist[dom]:
                    for item in itemlist:
                        print("{}: {}".format(dom, item))
            except:
                continue

    elif args.CSV:
        mushroom.Domain_CSV_output()

    else:
        mushroom.Domain_std_output()
