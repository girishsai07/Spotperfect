import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Create an undirected graph
G = nx.Graph()

# Add nodes
nodes = [1, 2, 3, 4, 5,6,7,8]
G.add_nodes_from(nodes)

# Add edges
edges = [(1, 2), (1, 3), (3, 4), (4, 5),(5,8),(6,7),(3,6),(4,8),(1,8)]
G.add_edges_from(edges)

# Draw the graph
plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15)
plt.title("Undirected Graph Visualization")
plt.show()

# Display the adjacency matrix
adj_matrix = nx.adjacency_matrix(G).todense()
print("Adjacency Matrix:")
print(adj_matrix)


# Calculate degree centrality
degree_centrality = nx.degree_centrality(G)
print("Degree Centrality:")
for node, centrality in degree_centrality.items():
    print(f"Node {node}: {centrality:.2f}")

# Identify the node with the highest degree centrality
max_centrality_node = max(degree_centrality, key=degree_centrality.get)
print(f"Node with the highest degree centrality: {max_centrality_node} (Centrality: {degree_centrality[max_centrality_node]:.2f})")
