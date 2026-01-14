import json
import os
import glob
from jinja2 import Environment, FileSystemLoader, Template

# --- CONFIGURATION ---
INPUT_FOLDER = 'names_data'
OUTPUT_FOLDER = 'output'

# Ensure output directory exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# --- TEMPLATES (HTML & CSS) ---
# We use Tailwind CSS via CDN for instant modern styling without extra files.

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | MuslimNameVault</title>
    <meta name="description" content="{{ description }}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital@0;1&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .arabic-text { font-family: 'Amiri', serif; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 flex flex-col min-h-screen">

    <nav class="bg-emerald-700 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <a href="index.html" class="text-2xl font-bold tracking-tight">MuslimNameVault</a>
            <div class="space-x-4 hidden md:block">
                <a href="index.html" class="hover:text-emerald-200">Home</a>
                <a href="#" class="hover:text-emerald-200">About</a>
                <a href="#" class="hover:text-emerald-200">Contact</a>
            </div>
        </div>
    </nav>

    <main class="flex-grow container mx-auto px-4 py-8">
        {{ content }}
    </main>

    <footer class="bg-slate-900 text-slate-400 py-8 text-center mt-auto">
        <p>&copy; 2024 MuslimNameVault. All rights reserved.</p>
    </footer>

</body>
</html>
"""

INDEX_CONTENT = """
<div class="text-center max-w-2xl mx-auto mb-12">
    <h1 class="text-4xl font-bold text-slate-900 mb-4">Find the Perfect Muslim Name</h1>
    <p class="text-lg text-slate-600">Browse our collection of verified, beautiful names from the Quran and Sunnah.</p>
</div>

<h2 class="text-2xl font-semibold mb-6 text-center">Browse by Letter</h2>
<div class="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-9 gap-4 max-w-4xl mx-auto">
    {% for letter in letters %}
    <a href="names-{{ letter|lower }}.html" 
       class="block bg-white hover:bg-emerald-600 hover:text-white transition shadow rounded-lg py-4 text-center text-xl font-bold border border-slate-200">
        {{ letter }}
    </a>
    {% endfor %}
</div>
"""


LIST_CONTENT = """
<div class="flex flex-col md:flex-row justify-between items-center mb-8 border-b border-slate-200 pb-4 gap-4">
    <div>
        <h1 class="text-3xl font-bold">Names starting with "{{ letter }}"</h1>
        <a href="index.html" class="text-emerald-600 hover:underline text-sm">&larr; Back to Home</a>
    </div>
    
    <div class="flex gap-2 w-full md:w-auto">
        <input type="text" id="searchInput" placeholder="Search names..." 
               class="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none w-full md:w-64">
        <select id="genderFilter" class="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none bg-white">
            <option value="all">All</option>
            <option value="Boy">Boys</option>
            <option value="Girl">Girls</option>
        </select>
    </div>
</div>

<div id="namesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for name in names %}
    <a href="name-{{ name.name|lower|replace(' ', '-') }}.html" class="name-card group block" data-name="{{ name.name|lower }}" data-gender="{{ name.gender }}">
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6 hover:shadow-md transition hover:border-emerald-500 relative overflow-hidden h-full">
            <div class="flex justify-between items-start">
                <div>
                    <h2 class="text-2xl font-bold text-slate-900 group-hover:text-emerald-700 transition">{{ name.name }}</h2>
                    <p class="text-sm text-slate-500 mb-2">{{ name.transliteration }}</p>
                </div>
                <span class="arabic-text text-3xl text-emerald-800">{{ name.arabic_spelling }}</span>
            </div>
            
            <p class="text-slate-700 mt-3 line-clamp-2 text-sm">{{ name.meaning }}</p>
            
            <div class="mt-4 flex flex-wrap gap-2">
                <span class="px-2 py-1 bg-slate-100 text-xs rounded-full font-medium text-slate-600 uppercase tracking-wide">{{ name.gender }}</span>
                {% for tag in name.tags[:2] %}
                <span class="px-2 py-1 bg-emerald-50 text-xs rounded-full text-emerald-700">{{ tag }}</span>
                {% endfor %}
            </div>
        </div>
    </a>
    {% endfor %}
</div>

<script>
    const searchInput = document.getElementById('searchInput');
    const genderFilter = document.getElementById('genderFilter');
    const cards = document.querySelectorAll('.name-card');

    function filterNames() {
        const query = searchInput.value.toLowerCase();
        const gender = genderFilter.value;

        cards.forEach(card => {
            const nameText = card.getAttribute('data-name');
            const cardGender = card.getAttribute('data-gender');
            
            const matchesSearch = nameText.includes(query);
            const matchesGender = gender === 'all' || cardGender === gender;

            if (matchesSearch && matchesGender) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    searchInput.addEventListener('input', filterNames);
    genderFilter.addEventListener('change', filterNames);
</script>
"""

DETAIL_CONTENT = """
<div class="max-w-2xl mx-auto">
    <a href="names-{{ name.name[0]|lower }}.html" class="text-emerald-600 hover:underline mb-4 inline-block">&larr; Back to {{ name.name[0] }} Names</a>

    <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-slate-100">
        <div class="bg-emerald-700 p-8 text-center text-white">
            <h1 class="text-5xl font-bold mb-2">{{ name.name }}</h1>
            <p class="text-emerald-100 text-xl">{{ name.transliteration }}</p>
            <div class="arabic-text text-6xl mt-4">{{ name.arabic_spelling }}</div>
        </div>

        <div class="p-8">
            <div class="grid grid-cols-2 gap-6 mb-8">
                <div>
                    <h3 class="text-sm uppercase tracking-wide text-slate-500 font-bold mb-1">Meaning</h3>
                    <p class="text-xl text-slate-900">{{ name.meaning }}</p>
                </div>
                <div>
                    <h3 class="text-sm uppercase tracking-wide text-slate-500 font-bold mb-1">Gender</h3>
                    <p class="text-xl text-slate-900">{{ name.gender }}</p>
                </div>
                <div>
                    <h3 class="text-sm uppercase tracking-wide text-slate-500 font-bold mb-1">Origin</h3>
                    <p class="text-lg text-slate-900">{{ name.origin }}</p>
                </div>
                <div>
                    <h3 class="text-sm uppercase tracking-wide text-slate-500 font-bold mb-1">Status</h3>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {{ 'bg-green-100 text-green-800' if name.verified else 'bg-yellow-100 text-yellow-800' }}">
                        {{ 'Verified' if name.verified else 'Unverified' }}
                    </span>
                </div>
            </div>

            <div>
                <h3 class="text-sm uppercase tracking-wide text-slate-500 font-bold mb-2">Categories</h3>
                <div class="flex flex-wrap gap-2">
                    {% for tag in name.tags %}
                    <span class="px-3 py-1 bg-slate-100 rounded-full text-slate-700">{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
"""

# --- HELPER FUNCTIONS ---

def load_all_names(folder):
    """Loads all json files into a dictionary keyed by letter."""
    data_by_letter = {}
    
    # Get all json files
    files = glob.glob(os.path.join(folder, '*.json'))
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                names_list = json.load(f)
                # Determine letter from filename (e.g., 'a.json' -> 'A')
                filename = os.path.basename(file_path)
                letter = filename[0].upper()
                
                # Sort names alphabetically
                names_list.sort(key=lambda x: x['name'])
                data_by_letter[letter] = names_list
                print(f"Loaded {len(names_list)} names for letter {letter}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return data_by_letter

def render_page(template_str, context, output_filename):
    """Renders a page using Jinja2 and saves it."""
    # 1. Render the inner content
    content_template = Template(template_str)
    inner_html = content_template.render(**context)
    
    # 2. Render the base layout with the inner content injected
    layout_template = Template(BASE_LAYOUT)
    final_html = layout_template.render(
        title=context.get('title', 'Muslim Names'), 
        description=context.get('description', 'Find beautiful Muslim names'),
        content=inner_html
    )
    
    # 3. Save
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    # print(f"Generated {output_filename}")

# --- MAIN GENERATOR ---

def generate_website():
    print("🚀 Starting Website Generation...")
    
    # 1. Load Data
    data = load_all_names(INPUT_FOLDER)
    all_letters = sorted(data.keys())
    
    if not all_letters:
        print("❌ No data found! Make sure 'names_data' folder has .json files.")
        return

    # 2. Generate Index Page
    render_page(INDEX_CONTENT, {
        'letters': all_letters,
        'title': 'Home',
        'description': 'The best collection of Muslim boy and girl names.'
    }, 'index.html')
    print("✅ Generated index.html")

    # 3. Generate Letter Pages (e.g., names-a.html)
    for letter in all_letters:
        names = data[letter]
        render_page(LIST_CONTENT, {
            'letter': letter,
            'names': names,
            'title': f'Muslim Names Starting with {letter}',
            'description': f'Browse {len(names)} Muslim names starting with the letter {letter}.'
        }, f'names-{letter.lower()}.html')
        
        # 4. Generate Individual Name Pages (e.g., name-alyan.html)
        for name_entry in names:
            safe_filename = f"name-{name_entry['name'].lower().replace(' ', '-')}.html"
            render_page(DETAIL_CONTENT, {
                'name': name_entry,
                'title': f"{name_entry['name']} - Meaning & Origin",
                'description': f"Meaning of the Muslim name {name_entry['name']}: {name_entry['meaning']}."
            }, safe_filename)
            
    print(f"✅ Generated letter pages and individual name pages.")
    print(f"\n✨ Website generated successfully in the '{OUTPUT_FOLDER}' folder!")
    print(f"👉 Open '{OUTPUT_FOLDER}/index.html' in your browser to view it.")

if __name__ == "__main__":
    generate_website()
