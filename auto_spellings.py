import os
import json
import glob
import time
from deep_translator import GoogleTranslator

# Configuration
NAMES_DIR = 'names_data'

# The languages we want to translate to
TARGET_LANGUAGES = {
    'Arabic': 'ar',
    'Urdu': 'ur',
    'Persian': 'fa',
    'Turkish': 'tr',
    'Bengali': 'bn',
    'Indonesian': 'id',
    'Pashto': 'ps'
}

def generate_spellings():
    print("🌍 Starting Automatic Name Translation...")
    files = glob.glob(os.path.join(NAMES_DIR, '*.json'))
    
    total_updated = 0

    for file_path in files:
        print(f"Processing {file_path}...")
        updated = False
        
        # 1. Load the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Ensure data is a list
        names_list = data if isinstance(data, list) else [data]
        
        # 2. Process each name
        for name_entry in names_list:
            # Skip if spellings already exist
            if 'spellings' in name_entry and len(name_entry['spellings']) > 0:
                continue
                
            english_name = name_entry.get('name')
            if not english_name:
                continue
                
            spellings = {}
            print(f"  Translating: {english_name}...")
            
            try:
                # Fetch translations using deep-translator
                for lang_name, lang_code in TARGET_LANGUAGES.items():
                    translator = GoogleTranslator(source='en', target=lang_code)
                    translated_text = translator.translate(english_name)
                    spellings[lang_name] = translated_text
                
                # Add to the dictionary
                name_entry['spellings'] = spellings
                updated = True
                total_updated += 1
                
                # Sleep for half a second to avoid getting blocked by Google
                time.sleep(0.5) 
                
            except Exception as e:
                print(f"  ⚠️ Error translating {english_name}: {e}")
                # Save progress and pause if Google limits us
                time.sleep(5)
                
        # 3. Save the updated file back to the hard drive
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(data, dict):
                    json.dump(names_list[0], f, indent=4, ensure_ascii=False)
                else:
                    json.dump(names_list, f, indent=4, ensure_ascii=False)
                    
            print(f"✅ Saved updates to {file_path}")

    print(f"\n🎉 Finished! Successfully added translations for {total_updated} names.")

if __name__ == "__main__":
    generate_spellings()
