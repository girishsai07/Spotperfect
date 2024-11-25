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

# Calculate centrality measures
degree_centrality = nx.degree_centrality(G)
closeness_centrality = nx.closeness_centrality(G, distance='weight')
betweenness_centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)

# Print centrality measures
print("Degree Centrality:")
for city, centrality in degree_centrality.items():
    print(f"City {city}: {centrality:.4f}")

print("\nCloseness Centrality:")
for city, centrality in closeness_centrality.items():
    print(f"City {city}: {centrality:.4f}")

print("\nBetweenness Centrality:")
for city, centrality in betweenness_centrality.items():
    print(f"City {city}: {centrality:.4f}")

# Combine centrality measures with weights
weight_degree = 0.4
weight_closeness = 0.3
weight_betweenness = 0.3

combined_centrality = {
    city: (weight_degree * degree_centrality[city] +
           weight_closeness * closeness_centrality[city] +
           weight_betweenness * betweenness_centrality[city])
    for city in G.nodes()
}

# Rank nodes based on combined centrality
ranked_nodes = sorted(combined_centrality.items(), key=lambda item: item[1], reverse=True)

print("\nRanked Nodes by Combined Centrality:")
for city, centrality in ranked_nodes:
    print(f"City {city}: {centrality:.4f}")
