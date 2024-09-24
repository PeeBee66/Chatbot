import pytesseract
from PIL import Image
import os

# Explicitly set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print(f"Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")

# Check if the file exists
if os.path.exists(pytesseract.pytesseract.tesseract_cmd):
    print("Tesseract executable found at the specified path.")
else:
    print("Tesseract executable NOT found at the specified path.")

try:
    print(f"Tesseract version: {pytesseract.get_tesseract_version()}")

    # Test with the debug screenshot
    image_path = 'debug_screenshot.png'
    if os.path.exists(image_path):
        text = pytesseract.image_to_string(Image.open(image_path))
        print(f"OCR result from debug_screenshot.png:\n{text}")
    else:
        print(f"Error: {image_path} not found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")