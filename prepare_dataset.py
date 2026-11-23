import random
import shutil
import csv
from pathlib import Path
from PIL import Image

# Original dataset location
SOURCE_DIR = Path(
    r"C:\Users\priya\Downloads\archive\plantvillage dataset\color"
)

# CropCare dataset location
OUTPUT_DIR = Path("dataset")

IMAGE_DIR = OUTPUT_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Supported image formats
extensions = {".jpg", ".jpeg", ".png"}

# Find images in all disease categories
all_images = []

for category_folder in SOURCE_DIR.iterdir():

    if category_folder.is_dir():

        for image_path in category_folder.iterdir():

            if image_path.suffix.lower() in extensions:
                all_images.append((image_path, category_folder.name))

print("Total images found:", len(all_images))

# Check availability
if len(all_images) < 600:
    raise ValueError("Dataset contains fewer than 600 images!")

# Random selection
random.seed(42)
selected_images = random.sample(all_images, 600)

# Copy images and create labels
csv_data = []

for index, (image_path, label) in enumerate(selected_images, start=1):

    new_name = f"image_{index:04d}{image_path.suffix.lower()}"

    destination = IMAGE_DIR / new_name

    shutil.copy2(image_path, destination)

    csv_data.append([new_name, label])

# Save CSV file
with open(OUTPUT_DIR / "labels.csv", "w", newline="",
          encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow(["image_name", "label"])
    writer.writerows(csv_data)

print("\nDataset preparation completed!")
print("Selected images:", len(selected_images))
print("Output folder:", OUTPUT_DIR)
print("Labels saved in:", OUTPUT_DIR / "labels.csv")