import os
import numpy as np
from PIL import Image

def create_color_mask(image_path):
    """
    Creates a binary mask where pixels with RGBA(238,238,238,255) are white and everything else is black.
    
    Args:
        image_path: Path to the input image
    
    Returns:
        Saves the mask image in the same folder with '_mask' suffix
    """
    # Load the image with PIL
    img = Image.open(image_path)
    
    # Convert to RGBA if it's not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Convert to numpy array for easier processing
    img_array = np.array(img)
    
    # Target color to find (R=238, G=238, B=238, A=255)
    target_color = np.array([238, 238, 238, 255])
    
    # Create mask where all values match the target color (255 for match, 0 for non-match)
    # All 4 channels must match
    mask = np.all(img_array == target_color, axis=2).astype(np.uint8) * 255
    
    # Create mask image
    mask_img = Image.fromarray(mask, mode='L')  # 'L' mode for 8-bit grayscale
    
    # Construct output filename with _mask suffix
    base_name = os.path.splitext(image_path)[0]
    mask_path = f"{base_name}_mask{os.path.splitext(image_path)[1]}"
    
    # Save the mask image
    mask_img.save(mask_path)
    
    print(f"Mask saved to: {mask_path}")
    return mask_path

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python create_mask.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    create_color_mask(image_path)
