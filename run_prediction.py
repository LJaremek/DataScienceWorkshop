import os
import glob
import sys
import argparse
from src.predictor.predictor import Predictor
from src.predictor.predictor import ModelClass


def process_directory(
    dir_path, model_type=ModelClass.LARGE, mask_threshold=0.5, mask_low_confidence=0.1
):
    """Process a single data directory if output files don't exist."""

    # Define expected output files by exact name
    vis_gm_path = os.path.join(dir_path, "visualization_gm.png")
    vis_osm_path = os.path.join(dir_path, "visualization_osm.png")

    # Check for prediction stats files using wildcard pattern
    stats_json_pattern = os.path.join(dir_path, "prediction_stats_*.json")
    stats_txt_pattern = os.path.join(dir_path, "prediction_stats_*.txt")

    # Check if output files already exist
    # vis_gm_exists = os.path.exists(vis_gm_path)
    # vis_osm_exists = os.path.exists(vis_osm_path)

    vis_gm_exists, vis_osm_exists = False, False # force to reprocess

    stats_json_exists = len(glob.glob(stats_json_pattern)) > 0
    stats_txt_exists = len(glob.glob(stats_txt_pattern)) > 0

    # Skip directory if all outputs already exist
    # if vis_gm_exists and vis_osm_exists and (stats_json_exists or stats_txt_exists):
    #     print(f"Skipping {dir_path} - all outputs already exist")
    # return False

    print(f"Processing {dir_path}...")

    try:
        # Check required input files exist
        required_files = ["gm.png", "osm.png", "osm_mask.png"]
        missing_files = [
            f for f in required_files if not os.path.exists(os.path.join(dir_path, f))
        ]

        if missing_files:
            print(
                f"Skipping {dir_path} - missing input files: {', '.join(missing_files)}"
            )
            return False

        # Initialize the predictor
        predictor = Predictor(
            img_data_folder=dir_path,
            image_gm="gm.png",
            image_osm="osm.png",
            parking_mask="osm_mask.png",
            model_type=model_type,
        )

        # Make predictions
        results = predictor.predict()

        # Generate GM visualization if it doesn't exist
        if not vis_gm_exists:
            print(f"Creating visualization_gm.png in {dir_path}")
            predictor.visualize(
                mask_threshold=mask_threshold,
                mask_low_confidence=mask_low_confidence,
                visualization_type="gm",
                save_path="visualization_gm.png",
            )
        else:
            print(f"visualization_gm.png already exists in {dir_path}")

        # Generate OSM visualization if it doesn't exist
        if not vis_osm_exists:
            print(f"Creating visualization_osm.png in {dir_path}")
            predictor.visualize(
                mask_threshold=mask_threshold,
                mask_low_confidence=mask_low_confidence,
                visualization_type="osm",
                save_path="visualization_osm.png",
            )
        else:
            print(f"visualization_osm.png already exists in {dir_path}")

        # Generate summary statistics if they don't exist
        if not stats_json_exists and not stats_txt_exists:
            print(f"Creating prediction stats in {dir_path}")
            predictor.summarize(
                mask_threshold=mask_threshold,
                mask_low_confidence=mask_low_confidence,
                save=True,
            )
        else:
            print(f"Prediction stats already exist in {dir_path}")

        print(f"Successfully processed {dir_path}")
        return True

    except Exception as e:
        print(f"Error processing {dir_path}: {e}")
        return False


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process parking data directories with YOLO model"
    )

    # Data directory
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Base directory containing numbered subdirectories with images (default: data)",
    )

    # Model type
    parser.add_argument(
        "--model-type",
        type=str,
        default="MEDIUM",
        choices=["NANO", "MEDIUM", "LARGE"],
        help="Model type to use (NANO, MEDIUM, or LARGE) (default: LARGE)",
    )

    # Thresholds
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Mask ratio threshold for high confidence (green boxes) (default: 0.5)",
    )

    parser.add_argument(
        "--low-threshold",
        type=float,
        default=0.1,
        help="Minimum mask ratio threshold for low confidence (red boxes) (default: 0.1)",
    )

    # Force reprocessing
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing of directories even if outputs already exist",
    )

    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_args()

    # Convert model type string to enum
    model_type_map = {
        "NANO": ModelClass.NANO,
        "MEDIUM": ModelClass.MEDIUM,
        "LARGE": ModelClass.LARGE,
    }
    model_type = model_type_map[args.model_type]

    print(f"Using model type: {model_type.value}")
    print(f"Using mask threshold: {args.threshold}")
    print(f"Using low mask threshold: {args.low_threshold}")

    # Find all subdirectories in the base directory
    data_dirs = glob.glob(os.path.join(args.data_dir, "*"))
    data_dirs = [d for d in data_dirs if os.path.isdir(d)]

    # Sort directories numerically
    data_dirs.sort(
        key=lambda x: (
            int(os.path.basename(x)) if os.path.basename(x).isdigit() else float("inf")
        )
    )

    print(f"Found {len(data_dirs)} directories to process")

    # Process each directory
    processed_count = 0
    for dir_path in data_dirs:
        if process_directory(
            dir_path,
            model_type=model_type,
            mask_threshold=args.threshold,
            mask_low_confidence=args.low_threshold,
        ):
            processed_count += 1

    print(
        f"Processing complete. {processed_count}/{len(data_dirs)} directories processed."
    )


if __name__ == "__main__":
    main()
