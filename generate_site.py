import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from config import INPUT_FOLDER, OUTPUT_FOLDER, SITE_URL
from src.data_manager import load_all_names, get_related_names, get_collection_data
# Added generate_cname to imports
from src.seo_utils import generate_search_index, generate_sitemap, generate_robots, generate_cname
# Updated TRENDING_2025 to TRENDING_2026 to match your collections.py
from src.collections import PROPHETS, SAHABA, TRENDING_2026, QURANIC_DIRECT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def copy_assets():
    """Copies static assets (audio) to the output folder."""
    print("📦 Copying assets...")
    
    # Source path (where you generated audio)
    src_audio = os.path.join(BASE_DIR, 'assets', 'audio')
    
    # Destination path (public website folder)
    dest_audio = os.path.join(OUTPUT_FOLDER, 'audio')
    
    # 1. Check if source exists
    if not os.path.exists(src_audio):
        print(f"⚠️ Warning: Source audio folder not found at {src_audio}")
        print("   -> Did you run 'python3 generate_audio.py' first?")
        return

    # 2. Create destination if missing
    if not os.path.exists(dest_audio):
        os.makedirs(dest_audio)

    # 3. Copy files
    files = os.listdir(src_audio)
    count = 0
    for f in files:
        if f.endswith('.mp3'):
            shutil.copy2(os.path.join(src_audio, f), os.path.join(dest_audio, f))
            count += 1
            
    print(f"✅ Copied {count} audio files to {dest_audio}")

def generate_nojekyll():
    """Tells GitHub Pages not to process files with Jekyll (Fixes audio 404s)."""
    nojekyll_path = os.path.join(OUTPUT_FOLDER, '.nojekyll')
    with open(nojekyll_path, 'w') as f:
        f.write('')
    print("✅ .nojekyll file created.")

def render_template(template_name, context, slug):
    """
    Renders pages using the Directory Index method for clean URLs.
    slug: The identifier (e.g., 'names-a', 'index', 'about')
    """
    try:
        template = env.get_template(template_name)
        
        # Handle Root Index specially
        if slug == 'index':
            output_path = os.path.join(OUTPUT_FOLDER, 'index.html')
            clean_url = f"{SITE_URL}/"
        else:
            # Create a folder for the slug and put index.html inside
            folder_path = os.path.join(OUTPUT_FOLDER, slug)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            output_path = os.path.join(folder_path, 'index.html')
            clean_url = f"{SITE_URL}/{slug}/"

        # Ensure canonical URL is set in context
        if 'url' not in context:
            context['url'] = clean_url
            
        html_content = template.render(**context)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    except Exception as e:
        print(f"❌ Error rendering {slug}: {e}")

def generate_website():
    print("🚀 Starting Website Generation (Clean URLs)...")
    
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
    generate_cname()     # Keeps your domain connected
    generate_nojekyll()  # Fixes the audio loading issue
    copy_assets()        # Copies the MP3 files

    # 3. Generate Index Page
    render_template('index.html', {
        'letters': all_letters,
        'letters_json': json.dumps(all_letters),
        'title': 'Muslim Name Vault - Meaningful Islamic Names Dictionary',
        'description': 'The most comprehensive collection of Muslim baby names.'
    }, 'index')
    print("✅ Generated index")

    # 4. Generate Favorites Page
    render_template('favorites.html', {
        'title': 'My Favorite Names',
        'description': 'Your shortlisted Muslim names.'
    }, 'favorites')
    print("✅ Generated favorites")

    # 5. Generate Finder Page
    render_template('finder.html', {
        'title': 'Advanced Name Finder',
        'description': 'Filter Muslim names by starting letter, ending letter, gender, and meaning.'
    }, 'finder')
    print("✅ Generated finder")

    # 6. Generate Collection Pages
    collections = [
        {'filename': 'names-prophets', 'list': PROPHETS, 'title': 'Names of Prophets', 'desc': 'Names of Prophets in Islam.'},
        {'filename': 'names-sahaba', 'list': SAHABA, 'title': 'Names of Sahaba', 'desc': 'Names of the Companions.'},
        # Updated variable to TRENDING_2026
        {'filename': 'names-trending', 'list': TRENDING_2026, 'title': 'Trending Names 2026', 'desc': 'Popular Muslim names.'},
        {'filename': 'names-quranic', 'list': QURANIC_DIRECT, 'title': 'Quranic Names', 'desc': 'Direct Quranic names.'}
    ]

    for col in collections:
        items = get_collection_data(data, col['list'])
        render_template('collection.html', {
            'names': items,
            'title': col['title'],
            'description': col['desc']
        }, col['filename'])
        print(f"✅ Generated {col['filename']}")

    # 7. Generate Letter & Detail Pages
    for letter in all_letters:
        names = data[letter]
        
        # Letter Page
        render_template('list.html', {
            'letter': letter,
            'names': names,
            'title': f'Muslim Names Starting with {letter}',
            'description': f'Browse {len(names)} Muslim names starting with {letter}.'
        }, f'names-{letter.lower()}')
        
        # Individual Name Pages
        for name_entry in names:
            safe_slug = f"name-{name_entry['name'].lower().replace(' ', '-')}"
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
                'description': f"Meaning of {name_entry['name']}: {name_entry['meaning']}."
            }, safe_slug)
            
    print(f"\n✨ SUCCESS! Website generated in '{OUTPUT_FOLDER}' folder.")

if __name__ == "__main__":
    generate_website()
