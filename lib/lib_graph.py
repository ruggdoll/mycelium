import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


class GraphVisualization:
    
    def __init__(self):
        self.visual = []
            
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def visualize(self,domain):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        net = Network(notebook=True)
        net.from_nx(G)
        GraphName=domain + ".html"
        try:
            net.show(GraphName)
        except:
            print("File generation failed :(")
            pass
        print("Graph file {} generated successfuly YAY".format(GraphName))
