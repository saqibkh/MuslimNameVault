import json
import os
import glob

# --- CONFIGURATION ---
NAMES_DATA_DIR = 'names_data'
INPUT_FILE = 'new_names.json'  # Put your new names here

def load_json(file_path):
    """Safely loads a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: {file_path} is corrupt or empty. Starting fresh.")
            return []
    return []

def save_json(file_path, data):
    """Saves data to JSON with pretty formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_id(prefix, existing_data):
    """Calculates the next available ID (e.g., 'aa101') based on existing data."""
    max_num = 0
    for entry in existing_data:
        id_str = entry.get('id', '')
        # Check if ID starts with our prefix (e.g., 'aa')
        if id_str.startswith(prefix):
            try:
                # Extract the number part
                num_part = id_str[len(prefix):]
                num = int(num_part)
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    return f"{prefix}{max_num + 1}"

def update_database():
    print(f"🚀 Starting Database Update from '{INPUT_FILE}'...")

    # 1. Load the new names
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
        print("❌ Error: Input JSON must be a list of objects (e.g., [ {...}, {...} ])")
        return

    # 2. Group new entries by their target file (e.g., 'aa.json')
    # This prevents opening/closing the same file multiple times
    updates_by_file = {}

    for entry in new_entries:
        name = entry.get('name', '').strip()
        if not name or len(name) < 2:
            print(f"⚠️ Skipping invalid name entry: {entry}")
            continue

        # Determine target file based on first 2 letters
        prefix = name[:2].lower()
        filename = f"{prefix}.json"
        
        if filename not in updates_by_file:
            updates_by_file[filename] = []
        
        updates_by_file[filename].append(entry)

    # 3. Process each file
    files_updated = 0
    names_added = 0
    names_skipped = 0

    for filename, entries_to_add in updates_by_file.items():
        file_path = os.path.join(NAMES_DATA_DIR, filename)
        
        # Load existing data
        existing_data = load_json(file_path)
        
        # Create a set of existing names for fast lookup (lowercase)
        existing_names_set = {x['name'].lower() for x in existing_data}
        
        file_modified = False
        prefix = filename.replace('.json', '')

        for entry in entries_to_add:
            name = entry['name']
            
            if name.lower() in existing_names_set:
                print(f"⏩ Skipping '{name}' (Already exists in {filename})")
                names_skipped += 1
                continue

            # Generate ID if missing
            if 'id' not in entry:
                entry['id'] = get_next_id(prefix, existing_data)
                # Add to existing_data immediately so next iteration sees the new ID count
                # (We append to list below, but get_next_id reads from the list)
            
            # Ensure other fields exist
            if 'verified' not in entry: entry['verified'] = True
            
            existing_data.append(entry)
            existing_names_set.add(name.lower()) # Prevent adding same new name twice
            file_modified = True
            names_added += 1
            print(f"✅ Added '{name}' to {filename} (ID: {entry['id']})")

        # 4. Save changes if modification happened
        if file_modified:
            # Sort alphabetically
            existing_data.sort(key=lambda x: x['name'])
            save_json(file_path, existing_data)
            files_updated += 1

    print("\n" + "="*30)
    print(f"🎉 Update Complete!")
    print(f"📂 Files Updated: {files_updated}")
    print(f"✅ Names Added:   {names_added}")
    print(f"⏩ Names Skipped: {names_skipped}")
    print("="*30)

if __name__ == "__main__":
    update_database()
