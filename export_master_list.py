import os
import json
import glob

NAMES_DIR = 'names_data'
OUTPUT_FILE = 'ALL_NAMES_MASTER.json'

def export_all_names():
    print("📦 Starting Export...")
    
    all_names = []
    # Find all JSON files in the names_data folder
    files = glob.glob(os.path.join(NAMES_DIR, '*.json'))
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_names.extend(data)
                elif isinstance(data, dict):
                    all_names.append(data)
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")

    # Sort alphabetically
    all_names.sort(key=lambda x: x.get('name', ''))
    
    # Save to one big file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_names, f, indent=2, ensure_ascii=False)

    print(f"✅ Success! Exported {len(all_names)} names to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    export_all_names()
