import os
import json
import glob

NAMES_DIR = 'names_data'

def organize_names():
    print("🧹 Starting Database Cleanup...")
    
    # 1. Load ALL existing names
    all_names = {}
    files = glob.glob(os.path.join(NAMES_DIR, '*.json'))
    
    print(f"📂 Found {len(files)} files. Reading...")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        # Use name as key to remove duplicates automatically
                        # clean up whitespace and standardize capitalization
                        clean_name = entry['name'].strip().title()
                        entry['name'] = clean_name
                        all_names[clean_name] = entry
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")

    total_unique = len(all_names)
    print(f"✨ Total Unique Names Found: {total_unique}")
    
    # 2. Group by First Letter
    sorted_names = sorted(all_names.values(), key=lambda x: x['name'])
    grouped = {}
    
    for name in sorted_names:
        first_char = name['name'][0].upper()
        if not first_char.isalpha():
            first_char = 'Other'
        
        if first_char not in grouped:
            grouped[first_char] = []
        grouped[first_char].append(name)
        
    # 3. Wipe Directory (Optional but recommended to keep it clean)
    # Be careful: This deletes old json files to replace them with sorted ones
    for f in files:
        os.remove(f)
        
    # 4. Save New Split Files
    print("💾 Saving organized files...")
    for letter, names_list in grouped.items():
        filename = f"names_{letter.lower()}.json"
        save_path = os.path.join(NAMES_DIR, filename)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(names_list, f, indent=2, ensure_ascii=False)
            
        print(f"   -> {filename}: {len(names_list)} names")

    print("✅ Database successfully organized!")

if __name__ == "__main__":
    organize_names()
