import os
import json
from jinja2 import Environment, FileSystemLoader
from config import INPUT_FOLDER, OUTPUT_FOLDER, SITE_URL
from src.data_manager import load_all_names, get_related_names, get_collection_data
from src.seo_utils import generate_search_index, generate_sitemap, generate_robots
from src.collections import PROPHETS, SAHABA, TRENDING_2025, QURANIC_DIRECT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def render_template(template_name, context, output_filename):
    try:
        template = env.get_template(template_name)
        if 'url' not in context:
            context['url'] = f"{SITE_URL}/{output_filename}"
        html_content = template.render(**context)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f"❌ Error rendering {template_name}: {e}")

def generate_website():
    print("🚀 Starting Website Generation...")
    
    # 1. Load Data
    data = load_all_names(INPUT_FOLDER)
    all_letters = sorted(data.keys())
    
    if not all_letters:
        print("❌ No data found!")
        return

    # 2. Generate Utility Files
    generate_search_index(data)
    generate_sitemap(data)
    generate_robots()

    # 3. Generate Index Page
    render_template('index.html', {
        'letters': all_letters,
        'letters_json': json.dumps(all_letters),
        'title': 'Muslim Name Vault - Meaningful Islamic Names Dictionary',
        'description': 'The most comprehensive collection of Muslim baby names.'
    }, 'index.html')
    print("✅ Generated index.html")

    # 4. Generate Favorites Page
    render_template('favorites.html', {
        'title': 'My Favorite Names',
        'description': 'Your shortlisted Muslim names.'
    }, 'favorites.html')
    print("✅ Generated favorites.html")

    # --- 5. Generate Collection Pages (NEW) ---
    
    collections = [
        {
            'filename': 'names-prophets.html',
            'list': PROPHETS,
            'title': 'Names of Prophets in Islam',
            'desc': 'A revered collection of names belonging to the Prophets (Anbiya) mentioned in the Quran and Sunnah.'
        },
        {
            'filename': 'names-sahaba.html',
            'list': SAHABA,
            'title': 'Names of the Sahaba (Companions)',
            'desc': 'Names of the noble Companions of Prophet Muhammad (ﷺ), known for their bravery, loyalty, and faith.'
        },
        {
            'filename': 'names-trending.html',
            'list': TRENDING_2025,
            'title': 'Trending Muslim Names 2025',
            'desc': 'The most popular and trending Muslim baby names for boys and girls this year.'
        },
        {
            'filename': 'names-quranic.html',
            'list': QURANIC_DIRECT,
            'title': 'Direct Quranic Names',
            'desc': 'Names that are explicitly mentioned in the Holy Quran.'
        }
    ]

    for col in collections:
        items = get_collection_data(data, col['list'])
        render_template('collection.html', {
            'names': items,
            'title': col['title'],
            'description': col['desc']
        }, col['filename'])
        print(f"✅ Generated {col['filename']} ({len(items)} names)")

    # 6. Generate Letter & Detail Pages
    for letter in all_letters:
        names = data[letter]
        
        # Letter Page
        render_template('list.html', {
            'letter': letter,
            'names': names,
            'title': f'Muslim Names Starting with {letter}',
            'description': f'Browse {len(names)} Muslim names starting with the letter {letter}.'
        }, f'names-{letter.lower()}.html')
        
        # Individual Name Pages
        for name_entry in names:
            safe_filename = f"name-{name_entry['name'].lower().replace(' ', '-')}.html"
            related = get_related_names(data, name_entry)
            
            schema = {
                "@context": "https://schema.org",
                "@type": "DefinedTerm",
                "name": name_entry['name'],
                "description": name_entry['meaning'],
                "inDefinedTermSet": "Muslim Names Dictionary"
            }
            
            render_template('detail.html', {
                'name': name_entry,
                'related_names': related,
                'schema_markup': f'<script type="application/ld+json">{json.dumps(schema)}</script>',
                'title': f"{name_entry['name']} Name Meaning & Origin",
                'description': f"What does {name_entry['name']} mean? Discover the meaning, origin ({name_entry['origin']}), and gender."
            }, safe_filename)
            
    print(f"\n✨ SUCCESS! Website generated in '{OUTPUT_FOLDER}' folder.")

if __name__ == "__main__":
    generate_website()
