import json
import os
import glob
import random

def load_all_names(input_folder):
    """Loads all json files and merges them by first letter."""
    data_by_letter = {}
    files = glob.glob(os.path.join(input_folder, '*.json'))
    print(f"📂 Found {len(files)} JSON files to process...")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content: continue
                names_list = json.loads(content)
                
                # Get letter from filename (e.g., 'aa.json' -> 'A')
                filename = os.path.basename(file_path)
                letter = filename[0].upper()
                
                if letter not in data_by_letter: 
                    data_by_letter[letter] = []
                data_by_letter[letter].extend(names_list)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    # Sort names alphabetically
    for letter in data_by_letter:
        data_by_letter[letter].sort(key=lambda x: x['name'])
            
    return data_by_letter

def get_related_names(all_data, current_name_obj, count=3):
    """Finds names with same Gender or Origin."""
    candidates = []
    target_gender = current_name_obj.get('gender')
    target_origin = current_name_obj.get('origin')
    
    # Flatten data safely to search through everything
    for names in all_data.values():
        for n in names:
            if n['name'] == current_name_obj['name']: continue
            if n.get('gender') == target_gender or n.get('origin') == target_origin:
                candidates.append(n)
                
    if len(candidates) >= count:
        return random.sample(candidates, count)
    return candidates

def get_collection_data(all_data, name_list):
    """
    Fetches full name objects for a given list of strings.
    Example: ['Adam', 'Nuh'] -> [{'name': 'Adam', ...}, {'name': 'Nuh', ...}]
    """
    collection_items = []
    # Create a lookup set for faster checking (lowercase)
    target_names = {n.lower() for n in name_list}

    for names in all_data.values():
        for n in names:
            if n['name'].lower() in target_names:
                collection_items.append(n)

    # Sort them to match the order of the input list (optional, but good for curation)
    # Or just sort alphabetically:
    collection_items.sort(key=lambda x: x['name'])

    return collection_items
