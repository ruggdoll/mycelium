import argparse
from lib.lib_mycelium import Mycelium
from lib.lib_graph import GraphVisualization

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    parser.add_argument("--CSV", help="Prints data in CSV format",action="store_true")
    parser.add_argument("--resolve", help="Performs a DNS resolution",action="store_true")
    parser.add_argument("--graph", help="Createsa IP-Domain graph named DOMAIN.TLD.html",action="store_true")
    args = parser.parse_args()

    mushroom = Mycelium(args.domain)
    mushroom.grow()

    if args.resolve:
        mylist=mushroom.resolve()
        if args.graph:
            G = GraphVisualization()
            for dom in mushroom.sub_list:
                try:
                    G.addEdge(dom,mylist[dom])
                except:
                    continue
            G.visualize(mushroom.domain)
        else:
            for res in mylist:
                print("{}: {}".format(res,mylist[res]))
    else: 
        if args.CSV:
            mushroom.Domain_CSV_output()
        else:
            mushroom.Domain_std_output()
