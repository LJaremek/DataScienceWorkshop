import os
import csv
from src.scraper.scrapers import GoogleMapsScraper, OpenStreetMapScraper
from tqdm import tqdm

GRID_CSV = 'warsaw_grid.csv'
DATA_DIR = 'data'

def main():
    # Read grid
    with open(GRID_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        grid = list(reader)

    # Initialize scrapers
    google_scraper = GoogleMapsScraper(headless=True)
    osm_scraper = OpenStreetMapScraper(headless=True)

    try:
        for row in tqdm(grid):
            cell_id = row['cell_id']
            lat = float(row['center_lat'])
            lon = float(row['center_lon'])
            cell_dir = os.path.join(DATA_DIR, str(cell_id))
            os.makedirs(cell_dir, exist_ok=True)
            gm_path = os.path.join(cell_dir, 'gm.png')
            osm_path = os.path.join(cell_dir, 'osm.png')
            # Skip if already downloaded
            if os.path.exists(gm_path) and os.path.exists(osm_path):
                print(f"Cell {cell_id}: images already exist, skipping.")
                continue
            print(f"Downloading images for cell {cell_id} at ({lat}, {lon})...")
            google_scraper.scrape((lat, lon), gm_path)
            osm_scraper.scrape((lat, lon), osm_path)

            # save a json with the coordinates
            coords_path = os.path.join(cell_dir, 'coords.json')
            with open(coords_path, 'w') as f:
                f.write(f'{{"latitude": {lat}, "longitude": {lon}}}')
    finally:
        google_scraper.driver.quit()
        osm_scraper.driver.quit()

if __name__ == '__main__':
    main()
