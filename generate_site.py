import os
import json
from jinja2 import Environment, FileSystemLoader
from config import INPUT_FOLDER, OUTPUT_FOLDER, SITE_URL
from src.data_manager import load_all_names, get_related_names
from src.seo_utils import generate_search_index, generate_sitemap, generate_robots

# Setup Jinja2 Environment (Load templates from filesystem)
env = Environment(loader=FileSystemLoader('templates'))

def render_template(template_name, context, output_filename):
    """Renders a template and saves the file."""
    template = env.get_template(template_name)
    
    # Add common SEO tags to context
    if 'url' not in context:
        context['url'] = f"{SITE_URL}/{output_filename}"
        
    html_content = template.render(**context)
    
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

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

    # 5. Generate Letter & Detail Pages
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
