import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import pickle
from flask import Flask, render_template, request, jsonify
import folium
import json
import requests
from googleapiclient.discovery import build
import time
from bs4 import BeautifulSoup
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")
# Suppress scikit-learn version warnings
import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

app = Flask(__name__)
api_key = ''

# Function to get location details from latitude and longitude
import requests

def get_location_from_lat_lng(lat, lng):
    """
    Fetch city and state from latitude and longitude using OpenStreetMap's Nominatim API.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
    headers = {
        "User-Agent": "YourAppName/1.0 (your@email.com)"  # Add a custom user-agent
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        address = data.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village")
        state = address.get("state")
        
        return city, state
    except requests.RequestException as e:
        print(f"An error occurred while fetching location: {e}")
        return None, None

# Function to get the first Google search result link
def get_top_google_link(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    query = query.replace(' ', '+')
    url = f'https://www.google.com/search?q={query}'
    
    # Configure retry strategy
    session = requests.Session()
    retries = Retry(
        total=5,  # Total number of retries
        backoff_factor=1,  # Delay between retries
        status_forcelist=[500, 502, 503, 504],  # Retry on these status codes
        allowed_methods=["GET"]  # Only retry on GET requests
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        # Add a random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        response = session.get(url, headers=headers, timeout=30)  # Increased timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first search result link
        search_result = soup.find('div', class_='yuRUbf')
        if search_result:
            link = search_result.find('a')['href']
            return link
        else:
            return None
    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

# Load the model and scaler
current_dir = os.getcwd()
model_path = os.path.join(current_dir, 'model.pkl')
scaler_path = os.path.join(current_dir, 'scaler.pkl')

model = pickle.load(open(model_path, 'rb'))
scaler = pickle.load(open(scaler_path, 'rb'))

@app.route('/')
def ind():
    return render_template('index1')

@app.route('/home', methods=['GET', 'POST'])
def index():
    locations = []
    if request.method == 'POST':
        # Extract form data
        print(request.form)
        population = float(request.form['population'])
        dist_road_qual = float(request.form['dist_road_qual'])
        tier_value = int(request.form['tier_value'])
        edi = float(request.form['edi'])
        literacy_rate = float(request.form['literacy_rate'])
        railways_count = int(request.form['railways_count'])
        average_land_price = float(request.form['average_land_price'])
        airport_proximity = float(request.form['airport_proximity'])

        # Prepare the input array for prediction
        new_input = np.array([
            [population, dist_road_qual, tier_value, edi, literacy_rate, railways_count, average_land_price, airport_proximity]
        ])
        new_input = scaler.transform(new_input)
        predicted_score = model.predict(new_input)[0]

        # Load data
        output_df = pd.read_csv('output1.csv')
        cleaned_df = pd.read_csv('combined_data.csv')

        # Clean and prepare the location data
        for df in [output_df, cleaned_df]:
            df['location'] = df['location'].str.lstrip(',').str.strip()
            df['location'] = df['location'].str.replace(r'\(.*\)', '', regex=True).str.strip()
            df['location'] = df['location'].apply(lambda x: ', '.join([part.strip() for part in x.split(',')]) if isinstance(x, str) else x)

        # Merge the data based on city names
        merged_df = pd.merge(output_df, cleaned_df[['location', 'lats', 'longs']], on='location', how='left')

        # Classification function
        def classify_location(row):
            if (row['population'] > 1000000 and row['dist_road_qual'] > 800000 and row['tier_value'] in [1, 2] and
                (row['airport_proximity'] > 20 or row['airport_proximity'] < 50) or (row['literacy_rate'] > 7 and row['railways_count'] < 6) and
                (row['edi'] > 25000 and row['edi'] < 70000) and (row['average_land_price'] > 2000 and row['average_land_price'] < 5000)):
                return 'Cross-Docking Center'
            elif ((row['population'] > 500000 and row['population'] < 3000000) or row['dist_road_qual'] > 800000 or
                  row['tier_value'] in [2, 3] and (row['airport_proximity'] > 30 and row['airport_proximity'] < 80) and
                  (row['literacy_rate'] > 7 and row['railways_count'] > 5 and row['railways_count'] < 11) and
                  (row['edi'] > 15000 and row['edi'] < 50000) and (row['average_land_price'] > 2000 and row['average_land_price'] < 5000)):
                return 'Warehouse'
            else:
                return 'Cross-Docking Center'

        merged_df['classification'] = merged_df.apply(classify_location, axis=1)
        
        merged_df['suitability_diff'] = abs(merged_df['suitability_score'] - predicted_score)
        top_10_cities = merged_df.nsmallest(10, 'suitability_diff')
        valid_cities = top_10_cities.dropna(subset=['lats', 'longs'])

        # Generate map
        map_center = [valid_cities['lats'].mean(), valid_cities['longs'].mean()]
        m = folium.Map(location=map_center, zoom_start=5, tiles='CartoDB positron')

        color_scheme = {
            'Cross-Docking Center': 'red',
            'Warehouse': 'blue',
            'Unclassified': 'gray'
        }

        for idx, row in valid_cities.iterrows():
            lat = row['lats']
            lng = row['longs']
            city, state = get_location_from_lat_lng(lat, lng)
    
            # Generate Google search query and get top link
            search_query = f"commercial land for sale in {city}, {state}"
            top_link = get_top_google_link(search_query)

            locations.append({
                'name': row['location'],
                'lat': row['lats'],
                'lng': row['longs'],
                'classification': row['classification'],
                'population': row['population'],
                'roadQuality': row['dist_road_qual'],
                'tierValue': row['tier_value'],
                'literacyRate': row['literacy_rate'],
                'railwaysCount': row['railways_count'],
                'landPrice': row['average_land_price'],
                'airportProximity': row['airport_proximity'],
                'color': color_scheme[row['classification']],
                'link':  f"https://www.99acres.com/commercial-land-in-{city}-ffid"
            })

        # Save map to HTML
        if not os.path.exists('static'):
            os.makedirs('static')
        map_html_path = os.path.join('static', 'map.html')
        m.save(map_html_path)

        # Generate parameter comparison plots
        fig_paths = []
        parameters = {
            'Population': 'population',
            'Road Quality': 'dist_road_qual',
            'Tier Value': 'tier_value',
            'Literacy Rate': 'literacy_rate',
            'Railways Count': 'railways_count',
            'Economic Development Index': 'edi',
            'Average Land Price (per acre)': 'average_land_price',
            'Airport Proximity': 'airport_proximity'
        }

        for param_name, param_column in parameters.items():
            fig, ax = plt.subplots(figsize=(10, 5))
            has_data = False
            for classification in valid_cities['classification'].unique():
                data = valid_cities[valid_cities['classification'] == classification]
                if not data.empty:
                    ax.barh(data['location'], data[param_column],
                            label=classification,
                            color=color_scheme[classification],
                            alpha=0.7)
                    has_data = True
            if has_data:
                ax.set_title(f'{param_name} Across Top Locations')
                ax.set_xlabel(param_name)
                ax.set_ylabel('Location')
                ax.tick_params(axis='y', labelsize=10)
                ax.legend()
                plt.tight_layout()
                fig_path = os.path.join('static', f'{param_name}.png')
                plt.savefig(fig_path)
                plt.close(fig)
                fig_paths.append(f'{param_name}.png')

        # Pass data to the template
        return render_template('results.html',
                               predicted_score=predicted_score,
                               data=json.dumps(locations),
                               fig_paths=fig_paths)
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)