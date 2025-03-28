#!/bin/bash
# filepath: c:/Users/szymo/WUT/Masters/DataScienceWorkshop/DataScienceWorkshop/extract_parking_from_data.sh

echo "Starting processing of cropped_gm.png files..."

# Find all cropped_osmcould.png files recursively in data directory
find "data" -name "cropped_osmcould.png" -type f | while read file; do
    echo "Processing: $file"
    python src/preprocessing/parking_extractor.py "$file"
    
    if [ $? -ne 0 ]; then
        echo "Error processing file: $file"
    else
        echo "Successfully processed: $file"
    fi
done

echo "Processing complete."