import json
import glob
import os

def expand_variants():
    files = glob.glob('names_data/*.json')
    new_entries = []
    
    print("🚀 Generating Spelling Variants...")
    
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            for entry in data:
                name = entry['name']
                
                # Logic: Generate common variations automatically
                variants = []
                if 'oo' in name: variants.append(name.replace('oo', 'u'))
                if 'u' in name: variants.append(name.replace('u', 'oo'))
                if 'ee' in name: variants.append(name.replace('ee', 'i'))
                if 'i' in name: variants.append(name.replace('i', 'ee'))
                if name.endswith('a'): variants.append(name + 'h') # Amina -> Aminah
                
                for v in variants:
                    # Create a new entry for the variant pointing to the original meaning
                    new_entry = entry.copy()
                    new_entry['name'] = v
                    new_entry['id'] = entry['id'] + "_var"
                    new_entry['variant_of'] = name # Link back to main
                    new_entries.append(new_entry)

    # Save distinct new variants
    unique_new = {v['name']: v for v in new_entries}.values()
    print(f"✨ Generated {len(unique_new)} new unique variants!")
    
    with open('names_data/generated_variants.json', 'w') as f:
        json.dump(list(unique_new), f, indent=2)

if __name__ == "__main__":
    expand_variants()
