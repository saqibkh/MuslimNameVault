import os
import json
import glob
import random
from jinja2 import Environment, FileSystemLoader
from seo_utils import generate_sitemap
import config  # Ensure config.py exists in the same directory

# --- CONFIGURATION ---
NAMES_DATA_DIR = 'names_data'
OUTPUT_DIR = 'docs'
TEMPLATES_DIR = 'templates'
SITE_URL = "https://muslimnamevault.com"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Jinja2 Setup
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_robots_txt():
    content = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w') as f:
        f.write(content)
    print("✅ Generated robots.txt")

def generate_rich_description(name, meaning, gender, origin, transliteration):
    """
    Generates a unique, non-repetitive description for every name
    to prevent Google 'Duplicate Content' penalties.
    """
    # 1. Gender-specific Introductions
    intro_templates = []
    if gender == 'Boy':
        intro_templates = [
            f"If you are looking for a strong and significant name for your son, <strong>{name}</strong> is a standout choice.",
            f"The name <strong>{name}</strong> is a classic masculine title rooted in {origin} tradition.",
            f"For parents seeking a noble identity for their baby boy, <strong>{name}</strong> offers deep spiritual resonance."
        ]
    elif gender == 'Girl':
        intro_templates = [
            f"Graceful and timeless, the name <strong>{name}</strong> is a beautiful choice for a baby girl.",
            f"<strong>{name}</strong> is a feminine title rich in history, originating from {origin} roots.",
            f"Capturing elegance and depth, <strong>{name}</strong> stands out as a meaningful name for your daughter."
        ]
    else: # Unisex
        intro_templates = [
            f"<strong>{name}</strong> is a versatile and harmonious name suitable for both boys and girls.",
            f"With its {origin} roots, <strong>{name}</strong> is a unique unisex choice carrying profound meaning."
        ]

    # 2. Meaning Analysis
    meaning_lower = meaning.lower()
    meaning_text = ""
    if "god" in meaning_lower or "allah" in meaning_lower:
        meaning_text = f"It carries a divine connection, translating essentially to '<em>{meaning}</em>'. This bestows a sense of spiritual protection upon the bearer."
    elif "beautiful" in meaning_lower or "flower" in meaning_lower or "light" in meaning_lower:
        meaning_text = f"The literal meaning, '<em>{meaning}</em>', evokes imagery of nature and radiance, suggesting a personality full of life and positivity."
    elif "warrior" in meaning_lower or "brave" in meaning_lower or "lion" in meaning_lower:
        meaning_text = f"Meaning '<em>{meaning}</em>', this name carries a weight of authority, courage, and leadership."
    else:
        meaning_text = f"The name holds the profound meaning of '<em>{meaning}</em>', reflecting qualities that parents often wish to bestow upon their child."

    # 3. Cultural Context (Randomized variations)
    cultural_templates = [
        f"In {origin} culture, names are more than labels; they are prayers. {name} is widely respected for its positive connotations.",
        f"Pronounced as <em>{transliteration or name}</em>, it has a rhythmic flow that makes it memorable and distinct.",
        f"While popular in {origin} regions, {name} has a modern appeal that transcends borders."
    ]

    # 4. Closing Recommendation
    closing = "It is an excellent choice for a modern Muslim family honoring tradition."
    
    # Combine random selections
    paragraph_1 = f"{random.choice(intro_templates)} {meaning_text}"
    paragraph_2 = f"{random.choice(cultural_templates)} {closing}"
    
    return f"{paragraph_1} <br><br> {paragraph_2}"

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


def generate_collection_page(folder_name, title, description, name_list, all_names, is_letter_page=False):
    """ 
    Generates a collection page with Gender Filtering.
    """
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    filtered_names = []
    if is_letter_page:
        filtered_names = name_list
    else:
        # Filter names: Find matches in our database
        target_names = {n.lower() for n in name_list}
        filtered_names = [n for n in all_names if n['name'].lower() in target_names]

    # Inline Template with Gender Filtering Logic
    template = env.from_string("""
    {% extends "base.html" %}

    {% block content %}
    <div class="max-w-6xl mx-auto">
        <div class="text-center mb-8 mt-8">
            <span class="inline-block py-1.5 px-4 rounded-full bg-emerald-100 text-emerald-800 text-sm font-bold mb-4 border border-emerald-200">
                {{ names|length }} Names Found
            </span>
            <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-6 font-heading">{{ title }}</h1>
            <p class="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">{{ description }}</p>
        </div>

        <div class="flex flex-wrap justify-center gap-3 mb-10" id="genderControls">
            <button onclick="applyGenderFilter('All')" 
                class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-emerald-500 hover:text-emerald-600" 
                data-filter="All">
                All
            </button>
            <button onclick="applyGenderFilter('Boy')" 
                class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-blue-500 hover:text-blue-600" 
                data-filter="Boy">
                Boys
            </button>
            <button onclick="applyGenderFilter('Girl')" 
                class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-pink-500 hover:text-pink-600" 
                data-filter="Girl">
                Girls
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="namesGrid">
            {% for n in names %}
            <a href="/name-{{ n.name|lower|replace(' ', '-') }}/" 
               class="name-card block p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-500 hover:shadow-lg transition group relative overflow-hidden"
               data-gender="{{ n.gender }}">
                
                <div class="flex justify-between items-start mb-2 relative z-10">
                    <h3 class="text-2xl font-bold text-slate-800 group-hover:text-emerald-700">{{ n.name }}</h3>
                    
                    {% if n.gender == 'Boy' %}
                        <span class="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100">{{ n.gender }}</span>
                    {% elif n.gender == 'Girl' %}
                        <span class="text-xs font-bold uppercase tracking-wider text-pink-600 bg-pink-50 px-2 py-1 rounded border border-pink-100">{{ n.gender }}</span>
                    {% else %}
                        <span class="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-50 px-2 py-1 rounded border border-slate-100">{{ n.gender }}</span>
                    {% endif %}
                </div>
                
                <p class="text-slate-600 line-clamp-2 relative z-10">{{ n.meaning }}</p>
            </a>
            {% endfor %}
        </div>

        <div id="emptyState" class="hidden text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
            <p class="text-slate-500 text-lg">No names found for this specific filter.</p>
            <button onclick="applyGenderFilter('All')" class="text-emerald-600 font-bold mt-2 inline-block hover:underline">Show All Names</button>
        </div>

        {% if names|length == 0 %}
        <div class="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
            <p class="text-slate-500 text-lg">We are adding more names to this collection soon!</p>
            <a href="/" class="text-emerald-600 font-bold mt-2 inline-block hover:underline">Return Home</a>
        </div>
        {% endif %}
    </div>

    <script>
        function applyGenderFilter(gender) {
            // 1. Save preference
            localStorage.setItem('genderPreference', gender);

            // 2. Update UI Buttons
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => {
                // Reset styling
                btn.classList.remove('bg-emerald-600', 'bg-blue-600', 'bg-pink-600', 'text-white', 'border-transparent');
                btn.classList.add('bg-white', 'text-slate-500', 'border-slate-200');
                
                // Apply Active Styling
                if (btn.dataset.filter === gender) {
                    btn.classList.remove('bg-white', 'text-slate-500', 'border-slate-200');
                    btn.classList.add('text-white', 'border-transparent');
                    if(gender === 'All') btn.classList.add('bg-emerald-600');
                    if(gender === 'Boy') btn.classList.add('bg-blue-600');
                    if(gender === 'Girl') btn.classList.add('bg-pink-600');
                }
            });

            // 3. Filter Grid Items
            const cards = document.querySelectorAll('.name-card');
            let visibleCount = 0;

            cards.forEach(card => {
                const cardGender = card.getAttribute('data-gender');
                let shouldShow = false;

                if (gender === 'All') {
                    shouldShow = true;
                } else if (gender === 'Boy') {
                    // Show Boys AND Unisex
                    if (cardGender === 'Boy' || cardGender === 'Unisex') shouldShow = true;
                } else if (gender === 'Girl') {
                    // Show Girls AND Unisex
                    if (cardGender === 'Girl' || cardGender === 'Unisex') shouldShow = true;
                }

                if (shouldShow) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // 4. Handle Empty State
            const emptyState = document.getElementById('emptyState');
            if (visibleCount === 0 && cards.length > 0) {
                emptyState.classList.remove('hidden');
            } else {
                emptyState.classList.add('hidden');
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            const savedGender = localStorage.getItem('genderPreference') || 'All';
            applyGenderFilter(savedGender);
        });
    </script>
    {% endblock %}
    """)

    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(template.render(
            title=f"{title} | MuslimNameVault",
            description=description,
            names=filtered_names,
            url=f"{SITE_URL}/{folder_name}/"
        ))

    print(f"✅ Generated Collection: {title} ({len(filtered_names)} names)")

def generate_rich_description(name, meaning, gender, origin, transliteration):
    """
    Generates a unique, non-repetitive description for every name
    to prevent Google 'Duplicate Content' penalties.
    """
    # 1. Gender-specific Introductions
    intro_templates = []
    if gender == 'Boy':
        intro_templates = [
            f"If you are looking for a strong and significant name for your son, <strong>{name}</strong> is a standout choice.",
            f"The name <strong>{name}</strong> is a classic masculine title rooted in {origin} tradition.",
            f"For parents seeking a noble identity for their baby boy, <strong>{name}</strong> offers deep spiritual resonance."
        ]
    elif gender == 'Girl':
        intro_templates = [
            f"Graceful and timeless, the name <strong>{name}</strong> is a beautiful choice for a baby girl.",
            f"<strong>{name}</strong> is a feminine title rich in history, originating from {origin} roots.",
            f"Capturing elegance and depth, <strong>{name}</strong> stands out as a meaningful name for your daughter."
        ]
    else: # Unisex
        intro_templates = [
            f"<strong>{name}</strong> is a versatile and harmonious name suitable for both boys and girls.",
            f"With its {origin} roots, <strong>{name}</strong> is a unique unisex choice carrying profound meaning."
        ]

    # 2. Meaning Analysis
    meaning_lower = meaning.lower() if meaning else ""
    meaning_text = ""
    if "god" in meaning_lower or "allah" in meaning_lower:
        meaning_text = f"It carries a divine connection, translating essentially to '<em>{meaning}</em>'. This bestows a sense of spiritual protection upon the bearer."
    elif "beautiful" in meaning_lower or "flower" in meaning_lower or "light" in meaning_lower:
        meaning_text = f"The literal meaning, '<em>{meaning}</em>', evokes imagery of nature and radiance, suggesting a personality full of life and positivity."
    elif "warrior" in meaning_lower or "brave" in meaning_lower or "lion" in meaning_lower:
        meaning_text = f"Meaning '<em>{meaning}</em>', this name carries a weight of authority, courage, and leadership."
    else:
        meaning_text = f"The name holds the profound meaning of '<em>{meaning}</em>', reflecting qualities that parents often wish to bestow upon their child."

    # 3. Cultural Context (Randomized variations)
    cultural_templates = [
        f"In {origin} culture, names are more than labels; they are prayers. {name} is widely respected for its positive connotations.",
        f"Pronounced as <em>{transliteration or name}</em>, it has a rhythmic flow that makes it memorable and distinct.",
        f"While popular in {origin} regions, {name} has a modern appeal that transcends borders."
    ]

    # 4. Closing Recommendation
    closing = "It is an excellent choice for a modern Muslim family honoring tradition."
    
    # Combine random selections
    # Ensure lists aren't empty to avoid errors
    p1 = random.choice(intro_templates) if intro_templates else f"The name <strong>{name}</strong> is a beautiful choice."
    p2 = random.choice(cultural_templates)
    
    return f"{p1} {meaning_text} <br><br> {p2} {closing}"

def generate_website():
    print("🚀 Starting Website Generation...")
    
    names = load_names()
    print(f"✅ Loaded {len(names)} names.")
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # 1. Generate Index Page (Homepage)
    index_template = env.get_template('index.html')
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template.render(
            title="Muslim Name Vault - Meaningful Islamic Names Dictionary",
            description="The most comprehensive collection of Muslim baby names with meanings, origins, and pronunciations.",
            url=SITE_URL,
            total_names=len(names),
            alphabet=list(alphabet)
        ))
    print("✅ Generated Homepage.")

    # 2. Initialize Search Index
    search_index = []
    
    # 3. Generate Individual Name Pages
    detail_template = env.get_template('detail.html')
    
    for name_entry in names:
        # Data Cleaning
        name = name_entry.get('name', 'Unknown')
        meaning = name_entry.get('meaning', 'Unknown meaning')
        gender = name_entry.get('gender', 'Unisex')
        origin = name_entry.get('origin', 'Islamic')
        
        # Create Slug
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

        # --- SEO CONTENT GENERATION ---
        
        # A. Rich Description
        gender_full = "boy" if gender == 'Boy' else "girl"
        if gender == 'Unisex': gender_full = "boy or girl"
        
        long_desc = generate_rich_description(name, meaning, gender, origin, name_entry.get('transliteration'))

        # B. Related Names (Same starting letter)
        first_char = name[0].upper()
        related_names = [n for n in names if n.get('origin') == origin and n['name'] != name]
        
        # 2. Fallback: If not enough origin matches, find names with same Gender
        if len(related_names) < 5:
            related_names += [n for n in names if n.get('gender') == gender and n['name'] != name]
            
        # 3. Shuffle and pick 10
        import random
        random.shuffle(related_names)
        related_names = related_names[:12] # Show 12 related names

        # C. JSON-LD Schema
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

        # Render Page
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

    # 4. Generate A-Z Collection Pages
    for char in alphabet:
        slug = f"names-{char.lower()}"
        filtered_names = [n for n in names if n['name'].startswith(char)]
        
        generate_collection_page(
            slug,
            f"Muslim Names Starting with {char}",
            f"Browse our comprehensive collection of {len(filtered_names)} Islamic names starting with the letter {char}. Find the perfect name with deep meaning.",
            filtered_names,
            names,
            is_letter_page=True
        )

    # 5. Generate Special Collections (Trending, Prophets, etc.)
    generate_collection_page(
        "names-trending", 
        "Trending Muslim Names 2026", 
        "The most popular and trending Muslim baby names for boys and girls in 2026.",
        config.TRENDING_2026, names, is_letter_page=False
    )
    generate_collection_page(
        "names-prophets", 
        "Names of Prophets", 
        "Honorable names of the Prophets (AS) mentioned in Islam.",
        config.PROPHET_NAMES, names, is_letter_page=False
    )
    generate_collection_page(
        "names-sahaba", 
        "Names of Sahaba & Sahabiyat", 
        "Names of the noble Companions of Prophet Muhammad (SAW).",
        config.SAHABA_NAMES, names, is_letter_page=False
    )
    generate_collection_page(
        "names-quranic", 
        "Direct Quranic Names", 
        "Names directly mentioned in the Holy Quran.",
        config.QURANIC_DIRECT, names, is_letter_page=False
    )

    # 6. Generate Finder Page
    finder_template = env.from_string("""
    {% extends "base.html" %}
    {% block content %}
    <div class="max-w-4xl mx-auto py-12 text-center">
        <h1 class="text-4xl font-bold mb-6 font-heading text-slate-900">Name Finder</h1>
        <p class="text-slate-600 mb-8 text-lg">Use our advanced search to find the perfect name by spelling, meaning, or origin.</p>
        
        <div class="bg-white p-8 rounded-2xl shadow-xl border border-slate-100">
            <div class="relative">
                <input type="text" id="finderInput" placeholder="Type a name, meaning, or origin..." 
                       class="w-full text-lg px-6 py-4 pl-12 rounded-xl bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none mb-4 transition">
                <span class="absolute left-4 top-4 text-2xl">🔍</span>
            </div>
            <div id="finderResults" class="text-left grid gap-2 max-h-[500px] overflow-y-auto"></div>
        </div>
    </div>
    <script>
        const fInput = document.getElementById('finderInput');
        const fResults = document.getElementById('finderResults');
        let fData = [];
        
        // Load the full search index
        fetch('/search_index.json').then(r=>r.json()).then(d=>{fData=d});
        
        fInput.addEventListener('input', (e)=>{
            const q = e.target.value.toLowerCase().trim();
            fResults.innerHTML = '';
            
            if(q.length < 2) return;
            
            // Search logic (matches name OR meaning)
            const res = fData.filter(i => 
                i.n.toLowerCase().includes(q) || 
                i.m.toLowerCase().includes(q)
            ).slice(0, 50); // Limit to 50 results
            
            if(res.length === 0) {
                 fResults.innerHTML = '<div class="p-4 text-slate-500 text-center">No names found matching that query.</div>';
                 return;
            }

            res.forEach(r => {
                fResults.innerHTML += `
                <a href="${r.s}" class="block p-4 hover:bg-emerald-50 border-b border-slate-100 last:border-0 transition rounded-lg">
                    <div class="flex justify-between items-center">
                        <div>
                            <span class="font-bold text-lg text-slate-800">${r.n}</span>
                            <span class="block text-sm text-slate-500">${r.m}</span>
                        </div>
                        <span class="text-xs font-bold uppercase px-2 py-1 bg-slate-100 rounded text-slate-600">${r.g}</span>
                    </div>
                </a>`;
            });
        });
    </script>
    {% endblock %}
    """)
    
    folder_path = os.path.join(OUTPUT_DIR, 'finder')
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(finder_template.render(
            title="Name Finder | MuslimNameVault", 
            description="Search for Muslim Names by meaning, origin, or gender.", 
            url=f"{SITE_URL}/finder/"
        ))
    print("✅ Generated Finder Page")

    # 7. Save Search Index
    with open(os.path.join(OUTPUT_DIR, 'search_index.json'), 'w', encoding='utf-8') as f:
        json.dump(search_index, f)
    print("✅ Generated Search Index.")

    # 8. Generate Sitemap
    generate_sitemap(names, OUTPUT_DIR, SITE_URL)
    print("✅ Generated Sitemap.")

    print("🎉 Site Generation Complete!")

if __name__ == "__main__":
    generate_website()
