from setuptools import setup, find_packages

setup(
    name="src",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python",
        "torch",
        "ultralytics",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Parking space prediction using YOLO models",
    keywords="computer vision, object detection, parking",
    python_requires=">=3.9",
)
