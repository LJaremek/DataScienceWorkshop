import os
import json
import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = 'data'
OUTPUT_CSV = 'warsaw_predictions_merged.csv'

def load_json_safe(file_path):
    """Safely load JSON file, return empty dict if file doesn't exist or is invalid."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return {}

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def main():
    data_rows = []
    
    # Get all subdirectories in data folder
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print(f"Error: {DATA_DIR} directory not found")
        return
    
    subdirs = [d for d in data_path.iterdir() if d.is_dir()]
    subdirs.sort(key=lambda x: int(x.name) if x.name.isdigit() else float('inf'))
    
    print(f"Processing {len(subdirs)} folders...")
    
    for subdir in subdirs:
        cell_id = subdir.name
        coords_file = subdir / 'coords.json'
        stats_file = subdir / 'prediction_stats.json'
        
        # Initialize row with cell_id
        row = {'cell_id': cell_id}
        
        # Load coordinates
        coords_data = load_json_safe(coords_file)
        if coords_data:
            row['latitude'] = coords_data.get('latitude')
            row['longitude'] = coords_data.get('longitude')
        else:
            row['latitude'] = None
            row['longitude'] = None
        
        # Load prediction stats
        stats_data = load_json_safe(stats_file)
        if stats_data:
            # Extract stats section
            stats = stats_data.get('stats', {})
            
            # Flatten nested dictionaries (like mask_ratio_distribution, class_distribution)
            flattened_stats = flatten_dict(stats)
            
            # Add parameters
            parameters = stats_data.get('parameters', {})
            for param_key, param_value in parameters.items():
                row[f'param_{param_key}'] = param_value
            
            # Add all flattened stats
            row.update(flattened_stats)
            
            # Add counts of high/low confidence boxes
            high_conf_boxes = stats_data.get('high_confidence_boxes', [])
            low_conf_boxes = stats_data.get('low_confidence_boxes', [])
            
            row['high_conf_boxes_count'] = len(high_conf_boxes)
            row['low_conf_boxes_count'] = len(low_conf_boxes)
            
            # Calculate additional metrics if boxes exist
            if high_conf_boxes:
                high_confs = [box['conf'] for box in high_conf_boxes if 'conf' in box]
                high_mask_ratios = [box['mask_ratio'] for box in high_conf_boxes if 'mask_ratio' in box]
                
                if high_confs:
                    row['high_conf_std_confidence'] = np.std(high_confs)
                if high_mask_ratios:
                    row['high_conf_std_mask_ratio'] = np.std(high_mask_ratios)
            
            if low_conf_boxes:
                low_confs = [box['conf'] for box in low_conf_boxes if 'conf' in box]
                low_mask_ratios = [box['mask_ratio'] for box in low_conf_boxes if 'mask_ratio' in box]
                
                if low_confs:
                    row['low_conf_std_confidence'] = np.std(low_confs)
                if low_mask_ratios:
                    row['low_conf_std_mask_ratio'] = np.std(low_mask_ratios)
        
        # Add file existence flags
        row['has_coords'] = coords_file.exists()
        row['has_prediction_stats'] = stats_file.exists()
        row['has_images'] = (subdir / 'gm.png').exists() and (subdir / 'osm.png').exists()
        
        data_rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Reorder columns to put important ones first
    priority_cols = ['cell_id', 'latitude', 'longitude', 'has_coords', 'has_prediction_stats', 
                     'has_images', 'total_detections', 'high_confidence_boxes', 'low_confidence_boxes',
                     'mask_coverage_pct', 'high_conf_mask_coverage_pct', 'avg_confidence', 
                     'avg_mask_ratio']
    
    # Get remaining columns
    remaining_cols = [col for col in df.columns if col not in priority_cols]
    
    # Reorder
    new_order = [col for col in priority_cols if col in df.columns] + remaining_cols
    df = df[new_order]
    
    # Fill NaN values for numeric columns with 0, and object columns with empty string or appropriate defaults
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Save to CSV
    df.to_csv(OUTPUT_CSV, index=False)
    
    # Print summary
    print(f"\nDataFrame created with {len(df)} rows and {len(df.columns)} columns")
    print(f"Saved to: {OUTPUT_CSV}")
    
    print(f"\nSummary:")
    print(f"- Folders with coordinates: {df['has_coords'].sum()}")
    print(f"- Folders with prediction stats: {df['has_prediction_stats'].sum()}")
    print(f"- Folders with images: {df['has_images'].sum()}")
    print(f"- Folders with detections > 0: {(df['total_detections'] > 0).sum()}")
    
    print(f"\nFirst few rows:")
    print(df.head())
    
    print(f"\nColumn list:")
    for i, col in enumerate(df.columns):
        print(f"{i+1:2d}. {col}")
    
    return df

if __name__ == '__main__':
    df = main()
