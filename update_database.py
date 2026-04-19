import json
import os
import re
import glob

# --- CONFIGURATION ---
NAMES_DATA_DIR = 'names_data'
INPUT_FILE = 'new_names.json'

def load_json(file_path):
    """Safely loads a JSON file. Returns None if corrupt to prevent data loss."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"❌ CRITICAL: {file_path} is corrupt. Fix JSON syntax before updating.")
            return None
    return []

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_highest_id_number(prefix, existing_data):
    """Scans the file ONCE to find the highest existing ID number."""
    max_num = 0
    for entry in existing_data:
        id_str = entry.get('id', '')
        if id_str.startswith(prefix):
            try:
                num_part = id_str[len(prefix):].replace('_var', '')
                num = int(num_part)
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    return max_num

def get_compare_key(name):
    """
    Strips ALL spaces, dashes, and apostrophes and lowercases it. 
    This ensures "Ma'an", "Maan", and "Ma-an" are recognized as the same name.
    """
    return re.sub(r'[^a-z]', '', name.lower())

def update_database():
    print(f"🚀 Starting Database Update from '{INPUT_FILE}'...")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        try:
            new_entries = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error: '{INPUT_FILE}' is not valid JSON. {e}")
            return

    if not isinstance(new_entries, list):
        print("❌ Error: Input JSON must be a list of objects.")
        return

    # 1. BUILD A GLOBAL MEMORY BANK OF ALL EXISTING NAMES
    print("🔍 Scanning entire database to prevent cross-file duplicates...")
    global_existing_names = set()
    
    all_json_files = glob.glob(os.path.join(NAMES_DATA_DIR, '*.json'))
    for filepath in all_json_files:
        # Skip variants or master list to avoid false reads
        if 'generated_variants.json' in filepath or 'ALL_NAMES_MASTER.json' in filepath:
            continue
            
        data = load_json(filepath)
        if data:
            for entry in data:
                compare_key = get_compare_key(entry.get('name', ''))
                if compare_key:
                    global_existing_names.add(compare_key)

    print(f"🧠 Memorized {len(global_existing_names)} unique names.")

    updates_by_file = {}
    names_skipped = 0

    # 2. FILTER NEW NAMES AGAINST THE GLOBAL MEMORY BANK
    for entry in new_entries:
        name = entry.get('name', '').strip()
        if not name or len(name) < 2:
            print(f"⚠️ Skipping invalid name entry: {entry}")
            continue
            
        compare_key = get_compare_key(name)
        
        # If the name is ANYWHERE in the database, skip it immediately
        if compare_key in global_existing_names:
            print(f"⏩ Skipping '{name}' (Already exists in the database)")
            names_skipped += 1
            continue
            
        # Add to memory bank so we don't add duplicates from the new_names.json file itself!
        global_existing_names.add(compare_key)

        # Group by first two letters
        clean_name = re.sub(r'[^a-zA-Z]', '', name)
        prefix = clean_name[:2].lower()
        filename = f"{prefix}.json"

        if filename not in updates_by_file:
            updates_by_file[filename] = []
        updates_by_file[filename].append(entry)

    files_updated = 0
    names_added = 0
    
    # 3. PROCESS THE VALID, NON-DUPLICATE NAMES
    for filename, entries_to_add in updates_by_file.items():
        file_path = os.path.join(NAMES_DATA_DIR, filename)

        # Load existing data
        existing_data = load_json(file_path)
        
        if existing_data is None:
            print(f"🛑 Skipping updates for {filename} to prevent data wiping.")
            continue

        file_modified = False
        prefix = filename.replace('.json', '')
        current_max_id = get_highest_id_number(prefix, existing_data)

        for entry in entries_to_add:
            name = entry.get('name', '').strip()

            # Generate ID if missing using the fast memory counter
            if 'id' not in entry:
                current_max_id += 1
                entry['id'] = f"{prefix}{current_max_id}"

            if 'verified' not in entry: 
                entry['verified'] = True

            existing_data.append(entry)
            file_modified = True
            names_added += 1
            print(f"✅ Added '{name}' to {filename} (ID: {entry['id']})")

        if file_modified:
            # Sort alphabetically, ignoring case
            existing_data.sort(key=lambda x: x.get('name', '').lower())
            save_json(file_path, existing_data)
            files_updated += 1

    print("\n" + "="*30)
    print(f"🎉 Update Complete!")
    print(f"📂 Files Updated: {files_updated}")
    print(f"✅ Names Added:   {names_added}")
    print(f"⏩ Names Skipped: {names_skipped}")

if __name__ == "__main__":
    update_database()
