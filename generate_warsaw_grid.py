import csv

# Warsaw bounding box (approximate)
# Latitude: 52.0975 (south) to 52.3680 (north)
# Longitude: 20.8512 (west) to 21.2712 (east)
LAT_MIN = 52.0975
LAT_MAX = 52.3680
LON_MIN = 20.8512
LON_MAX = 21.2712

# Grid size (degrees). Adjust for finer/coarser grid.
LAT_STEP = 0.003  # ~330 m
LON_STEP = 0.003  # ~220 m

output_csv = 'warsaw_grid.csv'

grid = []
cell_id = 0
lat = LAT_MIN
while lat < LAT_MAX:
    lon = LON_MIN
    while lon < LON_MAX:
        center_lat = lat + LAT_STEP / 2
        center_lon = lon + LON_STEP / 2
        grid.append({'cell_id': cell_id, 'center_lat': center_lat, 'center_lon': center_lon})
        cell_id += 1
        lon += LON_STEP
    lat += LAT_STEP

with open(output_csv, 'w', newline='') as csvfile:
    fieldnames = ['cell_id', 'center_lat', 'center_lon']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in grid:
        writer.writerow(row)

print(f"Generated {len(grid)} grid cells. Output: {output_csv}")
