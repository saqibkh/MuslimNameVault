import os

INPUT_FOLDER = 'names_data'
OUTPUT_FOLDER = 'docs'
SITE_URL = "https://muslimnamevault.com"

# Ensure output directory exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
