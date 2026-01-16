import os

INPUT_FOLDER = 'names_data'
OUTPUT_FOLDER = 'output'
SITE_URL = "https://saqibkh.github.io/MuslimNameVault"

# Ensure output directory exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
