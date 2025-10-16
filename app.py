from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import networkx as nx
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from networkx.algorithms.community import greedy_modularity_communities, modularity
from typing import List

app = FastAPI(title="Dynamic Community Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Utility Functions ----
def read_graph_from_csv(file: UploadFile):
    df = pd.read_csv(file.file)
    G = nx.from_pandas_edgelist(df, source="source", target="target")
    return G

def extract_features(G, prev_G=None):
    deg = dict(G.degree())
    clust = nx.clustering(G)
    features = {}
    for n in G.nodes():
        d = deg[n]; c = clust[n]
        delta_d = delta_c = 0
        if prev_G is not None and prev_G.has_node(n):
            delta_d = d - prev_G.degree(n)
            delta_c = c - nx.clustering(prev_G, n)
        features[n] = [d, c, delta_d, delta_c]
    return features

def hybrid_detection(snapshots: List[nx.Graph]):
    results = []
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    prev_G = None
    prev_labels = None

    for t, G in enumerate(snapshots):
        features = extract_features(G, prev_G)
        X = np.array(list(features.values()))
        nodes = list(features.keys())

        if t == 0:
            # Initialize static detection
            comms = list(greedy_modularity_communities(G))
            labels = {n: i for i, c in enumerate(comms) for n in c}
            y = np.array([labels[n] for n in nodes])
            clf.fit(X, y)
        else:
            y_pred = clf.predict(X)
            labels = {nodes[i]: int(y_pred[i]) for i in range(len(nodes))}

        comms = [set([n for n, lbl in labels.items() if lbl == c]) for c in set(labels.values())]
        mod = modularity(G, comms)
        results.append({
            "snapshot": t + 1,
            "modularity": round(mod, 4),
            "communities": {int(k): int(v) for k, v in labels.items()}
        })

        prev_G = G
        prev_labels = labels

    return results

# ---- API Routes ----
@app.post("/analyze/")
async def analyze_snapshots(files: List[UploadFile]):
    snapshots = []
    for f in files:
        G = read_graph_from_csv(f)
        snapshots.append(G)

    results = hybrid_detection(snapshots)
    return {"results": results}
