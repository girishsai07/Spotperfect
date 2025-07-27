import pandas as pd
import folium
from folium.plugins import HeatMap


data1 = pd.read_csv('output1.csv')
locations = pd.read_csv('combined_data.csv')

# Merge the data on the 'location' column
merged_data = pd.merge(data1, locations, on='location')

# Check if merge is successful and data looks correct
print(merged_data.head())

# Prepare heatmap data
# Using 'suitability_score' for the heatmap value, you can change it as needed
heat_data = merged_data[['lats', 'longs', 'suitability_score']].values.tolist()

# Create a base map centered on India
india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Add heatmap layer
HeatMap(heat_data, radius=15, blur=10, min_opacity=0.5).add_to(india_map)

# Save map to HTML file
india_map.save('india_heatmap.html')

print("Heatmap generated and saved as 'india_heatmap.html'.")
