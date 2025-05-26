import os
import csv
from src.scraper.scrapers import GoogleMapsScraper, OpenStreetMapScraper
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

GRID_CSV = 'warsaw_grid.csv'
DATA_DIR = 'data'

# Thread-local storage for scraper instances
thread_local = threading.local()

def get_scrapers():
    if not hasattr(thread_local, 'google_scraper'):
        thread_local.google_scraper = GoogleMapsScraper(headless=True)
    if not hasattr(thread_local, 'osm_scraper'):
        thread_local.osm_scraper = OpenStreetMapScraper(headless=True)
    return thread_local.google_scraper, thread_local.osm_scraper

def process_cell(row):
    cell_id = row['cell_id']
    lat = float(row['center_lat'])
    lon = float(row['center_lon'])
    cell_dir = os.path.join(DATA_DIR, str(cell_id))
    os.makedirs(cell_dir, exist_ok=True)
    gm_path = os.path.join(cell_dir, 'gm.png')
    osm_path = os.path.join(cell_dir, 'osm.png')
    coords_path = os.path.join(cell_dir, 'coords.json')
    # Skip if already downloaded
    if os.path.exists(gm_path) and os.path.exists(osm_path):
        return f"Cell {cell_id}: images already exist, skipping."
    google_scraper, osm_scraper = get_scrapers()
    google_scraper.scrape((lat, lon), gm_path)
    osm_scraper.scrape((lat - 0.000009*7.5, lon), osm_path)
    with open(coords_path, 'w') as f:
        f.write(f'{{"latitude": {lat}, "longitude": {lon}}}')
    return f"Downloaded images for cell {cell_id} at ({lat}, {lon})"

def main():
    with open(GRID_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        grid = list(reader)

    max_workers = min(30, os.cpu_count())  # Adjust as needed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_cell, row) for row in grid]
        for f in tqdm(as_completed(futures), total=len(futures)):
            try:
                msg = f.result()
                if msg:
                    print(msg)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()
