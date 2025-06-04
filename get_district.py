# pip install geopandas shapely requests

import geopandas as gpd
from shapely.geometry import Point
import os
import requests

url_geojson = "https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson"
local_folder = "data_districts"
local_geojson = os.path.join(local_folder, "warszawa-dzielnice.geojson")

# Ensure local folder exists
os.makedirs(local_folder, exist_ok=True)

# Download if not present
if not os.path.isfile(local_geojson):
    print("Downloading GeoJSON file...")
    r = requests.get(url_geojson)
    r.raise_for_status()
    with open(local_geojson, "wb") as f:
        f.write(r.content)
    print("Downloaded.")

gdf = gpd.read_file(local_geojson)

print("CRS granic dzielnic:", gdf.crs)

gdf = gdf[gdf["name"] != "Warszawa"].reset_index(drop=True)

def check_district(lat, lon):
    punkt = Point(lon, lat)
    for _, row in gdf.iterrows():
        if row["geometry"].contains(punkt):
            return row["name"]
    return None

test_points = [
    (52.2297, 21.0122),  # Śródmieście
    (52.1550, 20.9920),  # Ursynów
    (52.4000, 21.2000),  # poza Warszawą
]

for lat, lon in test_points:
    district = check_district(lat, lon)
    if district:
        print(f"Punkt ({lat:.4f}, {lon:.4f}) → dzielnica: {district}")
    else:
        print(f"Punkt ({lat:.4f}, {lon:.4f}) → poza granicami dzielnic Warszawy.")
