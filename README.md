# DataScienceWorkshop
Identification of the density of incorrectly parked vehicles from satellite images (e.g. on a lawn, garage driveway, etc.) - i.e. image analysis and classification. Objective: assessment of the difficulty of finding a parking space

### 1. Define and prepare the area you want to analyse
Using GPS coordinates (latitude and longitude) define tuples in `src/scraper/get_images.py` and run the code. The screenshots from Google Maps and Openstreet Map will then appear in the `data/` directory.

### 2. Align photos
If the image data needs to be aligned, this should be done using the prepared application `src/scraper/app.py`.

### 3. Generate masks
The prepared method for calculating metrics uses masks that we generate on the aligned images using an `src/preprocessing/parking_extractor.py` script.

### 4. 
