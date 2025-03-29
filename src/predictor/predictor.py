import os
import cv2
import numpy as np
import torch
from enum import Enum
from ultralytics import YOLO


class ModelClass(Enum):
    NANO = "nano"
    MEDIUM = "med"
    LARGE = "large"


class Predictor:
    def __init__(self, img_data_folder, image_gm, image_osm, parking_mask, model_type):
        """
        Initialize the predictor with paths and model type.

        Args:
            img_data_folder (str): Folder with image data (e.g., "data/0/")
            image_gm (str): Name of Google Maps image (e.g., "cropped_gm.png")
            image_osm (str): Name of OpenStreetMap image (e.g., "cropped_osm.png")
            parking_mask (str): Name of mask image (e.g., "cropped_osm_mask.png")
            model_type (ModelClass): Type of model to use (NANO, MEDIUM, LARGE)
        """
        self.img_data_folder = img_data_folder
        self.image_gm_path = os.path.join(img_data_folder, image_gm)
        self.image_osm_path = os.path.join(img_data_folder, image_osm)
        self.parking_mask_path = os.path.join(img_data_folder, parking_mask)
        self.model_type = model_type

        # Determine device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load model
        model_name = f"./runs/obb/train_{model_type.value}/weights/best.pt"
        self.model = YOLO(model_name)
        self.model.to(self.device)

        self.results = None

    def load_images(self):
        """Load input images and mask."""
        self.img_gm = cv2.imread(self.image_gm_path)
        self.img_osm = cv2.imread(self.image_osm_path)
        self.mask = cv2.imread(self.parking_mask_path, cv2.IMREAD_GRAYSCALE)

    def is_in_mask(self, box_points):
        """
        Check if a bounding box is within the masked area.

        Args:
            box_points: Array of (x,y) points defining the bounding box
            threshold: Minimum percentage of box area that should be in masked area

        Returns:
            float: Ratio of box points in masked area
        """
        # Convert tensor to numpy array if needed
        if isinstance(box_points, torch.Tensor):
            box_points = box_points.cpu().numpy()

        # Create a polygon mask from the box points
        box_mask = np.zeros_like(self.mask)
        points = box_points.reshape((-1, 1, 2)).astype(np.int32)
        cv2.fillPoly(box_mask, [points], 255)

        # Count pixels in box that are also in mask
        intersection = cv2.bitwise_and(box_mask, self.mask)
        box_area = np.sum(box_mask > 0)
        intersection_area = np.sum(intersection > 0)

        # Return ratio of intersection area to box area
        return intersection_area / box_area if box_area > 0 else 0

    def predict(self):
        """
        Make predictions on the loaded images.

        Returns:
            list: List of results from the model prediction
        """
        self.load_images()

        # Make prediction on Google Maps image
        self.results = self.model.predict(self.img_gm, device=self.device)

        return self.results

    def visualize(
        self,
        mask_threshold=0.7,
        mask_low_confidence=0.1,
        visualization_type="gm",
        save_path=None,
    ):
        """
        Create visualization.

        Args:
            confidence_threshold: Threshold for high confidence (green boxes)
            low_confidence: Minimum threshold for low confidence (red boxes)

        Returns:
            numpy.ndarray: Visualization image with colored boxes
        """

        # Create a visualization image (copy of the original)
        assert visualization_type in ["gm", "osm"], "Invalid visualization type"
        if visualization_type == "gm":
            vis_img = self.img_gm.copy()
        else:
            vis_img = self.img_osm.copy()

        # Process each detected object
        for result in self.results:
            if hasattr(result, "obb") and result.obb is not None:
                for i, box in enumerate(result.obb.xyxyxyxy):
                    conf = float(result.obb.conf[i])

                    # Convert tensor to numpy if needed
                    if isinstance(box, torch.Tensor):
                        box = box.cpu().numpy()

                    # Check if box is in masked area and get ratio
                    mask_ratio = self.is_in_mask(box)

                    # Only process boxes with sufficient confidence and mask overlap
                    if mask_ratio >= mask_low_confidence:
                        # Choose color based on confidence
                        if mask_ratio >= mask_threshold:
                            color = (0, 255, 0)  # Green for high confidence
                        else:
                            color = (0, 0, 255)  # Red for low confidence

                        # Draw the oriented bounding box
                        points = box.reshape((-1, 1, 2)).astype(np.int32)
                        cv2.polylines(
                            vis_img, [points], isClosed=True, color=color, thickness=2
                        )

                        # Get the minimum x and y for text positioning
                        box_reshaped = box.reshape(4, 2)
                        min_x = int(np.min(box_reshaped[:, 0]))
                        min_y = int(np.min(box_reshaped[:, 1]))
                        text_pos = (min_x, min_y - 10)

                        # Add confidence score text
                        cv2.putText(
                            vis_img,
                            f"{conf:.2f}",
                            text_pos,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            color,
                            2,
                        )

        # Save the visualization image if a path is provided
        if save_path:
            cv2.imwrite(os.path.join(self.img_data_folder, save_path), vis_img)
            print(f"Visualization saved to {save_path}")

        # Return the visualization image
        return vis_img

    def summarize(self, mask_threshold=0.7, mask_low_confidence=0.1, save=False):
        """
        Print summary of predictions with detailed statistics.

        Args:
            mask_threshold: Threshold for high confidence (green boxes)
            mask_low_confidence: Minimum threshold for low confidence (red boxes)
            save: Whether to save the stats to JSON and TXT files

        Returns:
            dict: Dictionary containing summary statistics
        """
        if self.results is None:
            print("No results to summarize. Please run predict() first.")
            return {}

        stats = {}
        all_confs = []
        all_mask_ratios = []
        high_conf_boxes = []  # Boxes with mask_ratio >= mask_threshold
        low_conf_boxes = (
            []
        )  # Boxes with mask_ratio between mask_low_confidence and mask_threshold

        # Create a mask to represent all boxes
        all_boxes_mask = np.zeros_like(self.mask)
        high_conf_boxes_mask = np.zeros_like(self.mask)

        # Collect data from all boxes
        for result in self.results:
            if hasattr(result, "obb") and result.obb is not None:
                for i, box in enumerate(result.obb.xyxyxyxy):
                    conf = float(result.obb.conf[i])

                    # Convert tensor to numpy if needed
                    if isinstance(box, torch.Tensor):
                        box = box.cpu().numpy()

                    # Get mask ratio
                    mask_ratio = self.is_in_mask(box)

                    if mask_ratio >= mask_low_confidence:
                        all_confs.append(conf)
                        all_mask_ratios.append(mask_ratio)

                        # Add box to appropriate boxes list
                        box_data = {
                            "box": box,
                            "conf": conf,
                            "mask_ratio": mask_ratio,
                            "cls": (
                                int(result.obb.cls[i])
                                if hasattr(result.obb, "cls")
                                else None
                            ),
                        }

                        # Create a box mask for area coverage calculation
                        points = box.reshape((-1, 1, 2)).astype(np.int32)
                        cv2.fillPoly(all_boxes_mask, [points], 255)

                        if mask_ratio >= mask_threshold:
                            high_conf_boxes.append(box_data)
                            cv2.fillPoly(high_conf_boxes_mask, [points], 255)
                        else:
                            low_conf_boxes.append(box_data)

        # Calculate mask coverage statistics
        total_mask_area = np.sum(self.mask > 0)
        if total_mask_area > 0:
            # Calculate area covered by all boxes
            all_boxes_in_mask = cv2.bitwise_and(all_boxes_mask, self.mask)
            covered_area = np.sum(all_boxes_in_mask > 0)
            stats["mask_coverage_pct"] = (covered_area / total_mask_area) * 100

            # Calculate area covered by high confidence boxes
            high_conf_in_mask = cv2.bitwise_and(high_conf_boxes_mask, self.mask)
            high_conf_covered_area = np.sum(high_conf_in_mask > 0)
            stats["high_conf_mask_coverage_pct"] = (
                high_conf_covered_area / total_mask_area
            ) * 100

        # Basic counts
        stats["total_detections"] = len(all_confs)
        stats["high_confidence_boxes"] = len(high_conf_boxes)
        stats["low_confidence_boxes"] = len(low_conf_boxes)

        # Confidence statistics
        if all_confs:
            stats["avg_confidence"] = float(
                np.mean(all_confs)
            )  # Convert numpy types to Python native types for JSON serialization
            stats["min_confidence"] = float(np.min(all_confs))
            stats["max_confidence"] = float(np.max(all_confs))
            stats["median_confidence"] = float(np.median(all_confs))

        # Mask ratio statistics
        if all_mask_ratios:
            stats["avg_mask_ratio"] = float(np.mean(all_mask_ratios))
            stats["min_mask_ratio"] = float(np.min(all_mask_ratios))
            stats["max_mask_ratio"] = float(np.max(all_mask_ratios))

        # High confidence box statistics
        if high_conf_boxes:
            high_confs = [box["conf"] for box in high_conf_boxes]
            high_mask_ratios = [box["mask_ratio"] for box in high_conf_boxes]
            stats["high_conf_avg_confidence"] = float(np.mean(high_confs))
            stats["high_conf_avg_mask_ratio"] = float(np.mean(high_mask_ratios))

        # Low confidence box statistics
        if low_conf_boxes:
            low_confs = [box["conf"] for box in low_conf_boxes]
            low_mask_ratios = [box["mask_ratio"] for box in low_conf_boxes]
            stats["low_conf_avg_confidence"] = float(np.mean(low_confs))
            stats["low_conf_avg_mask_ratio"] = float(np.mean(low_mask_ratios))

        # Distribution of mask ratios
        if all_mask_ratios:
            bins = [0, 0.25, 0.5, 0.75, 1.0]
            hist, _ = np.histogram(all_mask_ratios, bins=bins)
            stats["mask_ratio_distribution"] = {
                "0-25%": int(hist[0]),
                "25-50%": int(hist[1]),
                "50-75%": int(hist[2]),
                "75-100%": int(hist[3]),
            }

        # Class statistics (if available)
        if high_conf_boxes and high_conf_boxes[0]["cls"] is not None:
            classes = {}
            for box in high_conf_boxes + low_conf_boxes:
                cls_id = int(box["cls"])  # Convert to int for JSON serialization
                if cls_id not in classes:
                    classes[cls_id] = {"count": 0, "high_conf": 0, "low_conf": 0}

                classes[cls_id]["count"] += 1
                if box["mask_ratio"] >= mask_threshold:
                    classes[cls_id]["high_conf"] += 1
                else:
                    classes[cls_id]["low_conf"] += 1

            stats["class_distribution"] = classes

        # Format the summary text
        summary_text = "\n===== Detection Summary =====\n"
        summary_text += f"Total detections: {stats['total_detections']}\n"
        summary_text += f"High confidence boxes (mask ratio ≥ {mask_threshold}): {stats['high_confidence_boxes']}\n"
        summary_text += f"Low confidence boxes ({mask_low_confidence} ≤ mask ratio < {mask_threshold}): {stats['low_confidence_boxes']}\n"

        # Add mask coverage
        if "mask_coverage_pct" in stats:
            summary_text += f"\n--- Mask Coverage ---\n"
            summary_text += (
                f"Total parking area covered: {stats['mask_coverage_pct']:.1f}%\n"
            )
            summary_text += f"Parking area covered by high confidence boxes: {stats['high_conf_mask_coverage_pct']:.1f}%\n"

        if all_confs:
            summary_text += f"\n--- Confidence Statistics ---\n"
            summary_text += f"Average confidence: {stats['avg_confidence']:.3f}\n"
            summary_text += f"Confidence range: {stats['min_confidence']:.3f} - {stats['max_confidence']:.3f}\n"

        if all_mask_ratios:
            summary_text += f"\n--- Mask Overlap Statistics ---\n"
            summary_text += f"Average mask overlap: {stats['avg_mask_ratio']:.3f}\n"
            summary_text += f"Mask overlap range: {stats['min_mask_ratio']:.3f} - {stats['max_mask_ratio']:.3f}\n"

            if "mask_ratio_distribution" in stats:
                summary_text += f"\n--- Mask Ratio Distribution ---\n"
                for range_name, count in stats["mask_ratio_distribution"].items():
                    summary_text += f"  {range_name}: {count} boxes\n"

        if "class_distribution" in stats:
            summary_text += f"\n--- Class Distribution ---\n"
            for cls_id, data in stats["class_distribution"].items():
                summary_text += f"Class {cls_id}: {data['count']} total ({data['high_conf']} high conf, {data['low_conf']} low conf)\n"

        summary_text += "=============================\n"

        # Print the summary
        print(summary_text)

        # Save to files if requested
        if save:
            import json

            # Generate base filename with timestamp
            base_path = os.path.join(self.img_data_folder, f"prediction_stats")

            # Save as JSON (excluding non-serializable numpy arrays from boxes)
            json_stats = {k: v for k, v in stats.items() if k != "boxes"}

            # Remove any non-JSON serializable items (numpy types are handled above)
            for box in high_conf_boxes + low_conf_boxes:
                if "box" in box:
                    del box["box"]

            json_path = f"{base_path}.json"
            with open(json_path, "w") as f:
                json.dump(
                    {
                        "stats": json_stats,
                        "parameters": {
                            "mask_threshold": mask_threshold,
                            "mask_low_confidence": mask_low_confidence,
                        },
                        "high_confidence_boxes": high_conf_boxes,
                        "low_confidence_boxes": low_conf_boxes,
                    },
                    f,
                    indent=2,
                )

            # Save the summary text
            txt_path = f"{base_path}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(summary_text)

            print(f"Stats saved to {json_path} and {txt_path}")

        return stats
