import pickle
from pathlib import Path
import networkx as nx

class GraphStore:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.graph_path = (base_dir.parent / "data" / "graph"/ "trend_graph.pkl")
        self.graph_path.parent.mkdir(parents=True,exist_ok=True)

    def load(self):
        if self.graph_path.exists():
            with open(self.graph_path,"rb") as f:
                return pickle.load(f)
        return nx.Graph()

    def save(self, graph):
        with open(self.graph_path,"wb") as f:
            pickle.dump(graph,f,protocol=pickle.HIGHEST_PROTOCOL)