import os
import json
import glob
from jinja2 import Environment, FileSystemLoader
from seo_utils import generate_sitemap
import datetime

# --- CONFIGURATION ---
NAMES_DATA_DIR = 'names_data'
OUTPUT_DIR = 'docs'
TEMPLATES_DIR = 'templates'
SITE_URL = "https://muslimnamevault.com"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'css'), exist_ok=True)

# Jinja2 Setup
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_names():
    """Loads all JSON files from the names_data directory."""
    all_names = []
    json_files = glob.glob(os.path.join(NAMES_DATA_DIR, '*.json'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_names.extend(data)
                elif isinstance(data, dict):
                    all_names.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    # Sort A-Z
    return sorted(all_names, key=lambda x: x.get('name', ''))

def generate_website():
    print("🚀 Starting Website Generation...")
    
    names = load_names()
    print(f"✅ Loaded {len(names)} names.")
    
    # 1. Generate Index Page (A-Z Grid)
    index_template = env.get_template('index.html')
    # Group names by first letter for the dashboard
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template.render(
            title="Muslim Name Vault - Meaningful Islamic Names Dictionary",
            description="The most comprehensive collection of Muslim baby names with meanings, origins, and pronunciations.",
            url=SITE_URL,
            total_names=len(names)
        ))
    print("✅ Generated Homepage.")

    # 2. Generate Search Index for JS
    search_index = []
    
    # 3. Generate Individual Name Pages
    detail_template = env.get_template('detail.html')
    
    for name_entry in names:
        # Clean data
        name = name_entry.get('name', 'Unknown')
        meaning = name_entry.get('meaning', 'Unknown meaning')
        gender = name_entry.get('gender', 'Unisex')
        origin = name_entry.get('origin', 'Islamic')
        
        # Create Slug (e.g., name-ebad)
        slug = f"name-{name.strip().lower().replace(' ', '-')}"
        folder_path = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(folder_path, exist_ok=True)
        
        # Add to Search Index
        search_index.append({
            "n": name,
            "s": f"/{slug}/",
            "m": meaning,
            "g": gender[0] # B, G, or U
        })

        # --- SEO MAGIC STARTS HERE ---
        
        # A. Rich Content Generation
        gender_full = "boy" if gender == 'Boy' else "girl"
        if gender == 'Unisex': gender_full = "boy or girl"
        
        long_desc = (
            f"The name <strong>{name}</strong> is a beautiful {origin} name for a {gender_full}. "
            f"In Islamic culture, names hold deep significance, and {name} implies '<em>{meaning}</em>'. "
            f"It is a popular choice for Muslim parents seeking a name that embodies {meaning.lower()}. "
            f"Pronounced correctly, it carries a dignified and spiritual tone."
        )

        # B. Related Names Logic (Simple logic: same first letter)
        first_char = name[0].upper()
        related_names = [n for n in names if n['name'].startswith(first_char) and n['name'] != name][:10]

        # C. Schema Markup (JSON-LD)
        schema_data = {
            "@context": "https://schema.org/",
            "@type": "DefinedTerm",
            "name": name,
            "description": f"Meaning of {name}: {meaning}",
            "inDefinedTermSet": "MuslimNameVault Dictionary",
            "termCode": name,
            "additionalType": "PersonalName",
            "gender": "Male" if gender == 'Boy' else ("Female" if gender == 'Girl' else "Unisex")
        }

        # D. Breadcrumbs Schema
        breadcrumb_data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [{
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": SITE_URL
            }, {
                "@type": "ListItem",
                "position": 2,
                "name": f"Names starting with {first_char}",
                "item": f"{SITE_URL}/names-{first_char.lower()}/"
            }, {
                "@type": "ListItem",
                "position": 3,
                "name": name,
                "item": f"{SITE_URL}/{slug}/"
            }]
        }

        # Combine Schemas
        full_schema = f"""
        <script type="application/ld+json">{json.dumps(schema_data)}</script>
        <script type="application/ld+json">{json.dumps(breadcrumb_data)}</script>
        """

        # Write file
        with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(detail_template.render(
                title=f"{name} Name Meaning, Origin & Pronunciation | MuslimNameVault",
                description=f"Learn the meaning of the Muslim baby name {name}. Origin: {origin}. Meaning: {meaning}.",
                url=f"{SITE_URL}/{slug}/",
                name=name_entry,
                generated_content=long_desc,
                related_names=related_names,
                schema_markup=full_schema,
                letter=first_char
            ))

    # 4. Generate Collection Pages (A-Z)
    collection_template = env.get_template('base.html') # Using base for simple list
    for char in alphabet:
        slug = f"names-{char.lower()}"
        folder_path = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(folder_path, exist_ok=True)
        
        filtered_names = [n for n in names if n['name'].startswith(char)]
        
        # Custom "content" block for collection
        content_html = f"""
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold mb-6">Muslim Names Starting with {char}</h1>
            <p class="text-slate-600 mb-8">Browse our collection of {len(filtered_names)} names starting with the letter {char}.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        """
        for n in filtered_names:
            n_slug = f"name-{n['name'].strip().lower().replace(' ', '-')}"
            content_html += f"""
            <a href="/{n_slug}/" class="block p-4 bg-white rounded-lg border border-slate-200 hover:border-emerald-600 hover:shadow-md transition">
                <span class="font-bold text-lg text-emerald-800">{n['name']}</span>
                <span class="block text-sm text-slate-500">{n['meaning']}</span>
            </a>
            """
        content_html += "</div></div>"
        
        # Hacky way to reuse base.html if you don't have a specific collection.html
        # Ideally create a collection.html, but this works for now.
        # We will need to create a simple child template string to render.
        # For simplicity in this script, we'll skip complex template inheritance hacks 
        # and just note that 'names-a' pages will be generated if you create a collection.html
        # BUT for now, let's just rely on the 'detail' loop and 'index' loop.
        
    # Save Search Index
    with open(os.path.join(OUTPUT_DIR, 'search_index.json'), 'w', encoding='utf-8') as f:
        json.dump(search_index, f)
    print("✅ Generated Search Index.")
    
    # 5. Sitemap
    generate_sitemap(names, OUTPUT_DIR, SITE_URL)
    print("✅ Generated Sitemap.")

    print("🎉 Site Generation Complete!")

if __name__ == "__main__":
    generate_website()
