import networkx as nx
import matplotlib.pyplot as plt

# Create an undirected graph
G = nx.Graph()

# Add nodes representing cities
cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
G.add_nodes_from(cities)

# Add weighted edges representing distances between cities
edges = [
    ('A', 'B', 4), ('A', 'C', 3), ('B', 'C', 2), ('B', 'D', 5), ('C', 'D', 7),
    ('C', 'E', 8), ('D', 'E', 6), ('D', 'F', 4), ('E', 'F', 1), ('E', 'G', 3), ('F', 'G', 2)
]
G.add_weighted_edges_from(edges)

# Draw the graph
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.title("Transportation Network Graph")
plt.show()

# Calculate betweenness centrality
betweenness_centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
print("Betweenness Centrality:")
for city, centrality in betweenness_centrality.items():
    print(f"City {city}: {centrality:.4f}")

# Identify critical nodes (bridges between regions)
# For simplicity, consider nodes with betweenness centrality higher than average as critical
average_centrality = sum(betweenness_centrality.values()) / len(betweenness_centrality)
critical_nodes = [node for node, centrality in betweenness_centrality.items() if centrality > average_centrality]

print(f"Critical nodes (bridges between regions): {critical_nodes}")
