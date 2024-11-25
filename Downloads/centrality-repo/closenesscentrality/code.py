import networkx as nx
import matplotlib.pyplot as plt

# Create an undirected graph
G = nx.Graph()

# Add nodes representing cities
cities = ['Chennai', 'Bangalore', 'Mumbai', 'Hyderabad', 'Kochi']
G.add_nodes_from(cities)

# Add edges representing distances between cities
edges = [('Chennai', 'Bangalore', 380), ('Chennai', 'Mumbai', 1300), ('Bangalore', 'Mumbai', 980), ('Bangalore', 'Hyderabad', 570), ('Mumbai', 'Hyderabad', 700), ('Hyderabad', 'Kochi', 1100),('Chennai','Kochi',700),('Kochi','Bangalore',530)]
G.add_weighted_edges_from(edges)

# Draw the graph
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.title("Graph of Cities and Distances")
plt.show()

# Calculate closeness centrality
closeness_centrality = nx.closeness_centrality(G, distance='weight')
print("Closeness Centrality:")
for city, centrality in closeness_centrality.items():
    print(f"City {city}: {centrality:.4f}")

# Identify the city with the highest closeness centrality (most reachable)
most_reachable_city = max(closeness_centrality, key=closeness_centrality.get)
print(f"The most reachable city is: {most_reachable_city} (Closeness Centrality: {closeness_centrality[most_reachable_city]:.4f})")
