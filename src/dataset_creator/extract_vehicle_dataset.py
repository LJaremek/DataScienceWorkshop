import os
import shutil
import numpy as np
from tqdm import tqdm
import yaml
import argparse

def extract_vehicle_dataset(source_base, target_base, train_count=1000, val_count=250):
    """
    Extract vehicle images and labels from DOTA dataset.
    Keep only labels 9 (large-vehicle) and 10 (small-vehicle) and relabel them as 0 and 1.
    
    Args:
        source_base: Base directory of the original DOTA dataset
        target_base: Base directory for the new vehicle dataset
        train_count: Number of training images to extract
        val_count: Number of validation images to extract
    """
    # Create target directories
    os.makedirs(target_base, exist_ok=True)
    
    splits = {
        'train': train_count,
        'val': val_count,
    }
    
    for split, count in splits.items():
        print(f"Processing {split} split...")
        
        # Create directories for this split
        os.makedirs(os.path.join(target_base, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(target_base, 'labels', split), exist_ok=True)
        
        # Get source directories
        source_img_dir = os.path.join(source_base, 'images', split)
        source_label_dir = os.path.join(source_base, 'labels', split)
        
        # Skip if source directories don't exist
        if not os.path.exists(source_img_dir) or not os.path.exists(source_label_dir):
            print(f"Skipping {split} - source directories not found")
            continue
        
        # Get all image files
        image_files = [f for f in os.listdir(source_img_dir) if f.endswith('.jpg') or f.endswith('.png')]
        
        # Track how many we've processed
        processed = 0
        
        # Process each image
        for img_file in tqdm(image_files):
            if processed >= count:
                break
                
            img_basename = os.path.splitext(img_file)[0]
            label_file = f"{img_basename}.txt"
            label_path = os.path.join(source_label_dir, label_file)
            
            # Skip if label file doesn't exist
            if not os.path.exists(label_path):
                continue
                
            # Read label file
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            # Filter for vehicle classes (9 and 10) and convert to new labels (0 and 1)
            vehicle_lines = []
            has_vehicles = False
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 6:  # Skip invalid lines
                    continue
                    
                # Check if class is 9 (large-vehicle) or 10 (small-vehicle)
                try:
                    class_id = int(parts[0])
                    if class_id == 9:  # large-vehicle -> 0
                        parts[0] = "0"
                        vehicle_lines.append(" ".join(parts) + "\n")
                        has_vehicles = True
                    elif class_id == 10:  # small-vehicle -> 1
                        parts[0] = "1"
                        vehicle_lines.append(" ".join(parts) + "\n")
                        has_vehicles = True
                except ValueError:
                    continue
            
            # Skip image if no vehicles found
            if not has_vehicles:
                continue
                
            # Copy image and create new label file
            shutil.copy(
                os.path.join(source_img_dir, img_file),
                os.path.join(target_base, 'images', split, img_file)
            )
            
            with open(os.path.join(target_base, 'labels', split, label_file), 'w') as f:
                f.writelines(vehicle_lines)
                
            processed += 1
        
        print(f"Processed {processed} images for {split} split")
    
    # Create YAML file for the dataset
    yaml_content = {
        'path': os.path.join("..", "datasets", "DOTAv1-vehicles"),
        'train': os.path.join('images', 'train'),
        'val': os.path.join('images', 'val'),
        'nc': 2,
        'names': ['large-vehicle', 'small-vehicle']
    }
    
    with open(os.path.join(os.path.dirname(target_base), 'DOTAv1-vehicles.yaml'), 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    print(f"Dataset created at {target_base}")
    print(f"YAML configuration file created at {os.path.join(os.path.dirname(target_base), 'DOTAv1-vehicles.yaml')}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract vehicle dataset from DOTA dataset")
    parser.add_argument('--train-count', type=int, default=1000, 
                        help='Number of training images to extract (default: 1000)')
    parser.add_argument('--val-count', type=int, default=250, 
                        help='Number of validation images to extract (default: 250)')
    parser.add_argument('--source-dir', type=str, default=None,
                        help='Source directory for the DOTA dataset (optional)')
    parser.add_argument('--target-dir', type=str, default=None,
                        help='Target directory for the vehicle dataset (optional)')
    
    args = parser.parse_args()
    
    # Source base as directory from which this script is run
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Use provided paths or defaults
    source_base = args.source_dir if args.source_dir else os.path.join(dir_path, "datasets", "DOTAv1")
    target_base = args.target_dir if args.target_dir else os.path.join(dir_path, "datasets", "DOTAv1-vehicles")
    
    print(f"Source directory: {source_base}")
    print(f"Target directory: {target_base}")
    print(f"Training count: {args.train_count}")
    print(f"Validation count: {args.val_count}")
    
    extract_vehicle_dataset(source_base, target_base, args.train_count, args.val_count)
