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
    Generates a collection page with Gender Filtering, Favorites, AND Badges.
    """
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    filtered_names = []
    if is_letter_page:
        filtered_names = name_list
    else:
        target_names = {n.lower() for n in name_list}
        filtered_names = [n for n in all_names if n['name'].lower() in target_names]

    # PASS LISTS TO TEMPLATE
    # We use sets for faster lookup O(1)
    trending_set = set(config.TRENDING_2026)
    quranic_set = set(config.QURANIC_DIRECT) if hasattr(config, 'QURANIC_DIRECT') else set()

    template = env.from_string("""
    {% extends "base.html" %}

    {% block content %}
    <div class="max-w-6xl mx-auto">
        <div class="text-center mb-8 mt-8">
            <span class="inline-block py-1.5 px-4 rounded-full bg-emerald-100 text-emerald-800 text-sm font-bold mb-4 border border-emerald-200">
                {{ names|length }} Names Found
            </span>
            <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-6 font-heading">{{ title }}</h1>
            
            <div class="flex justify-center gap-4 mb-6">
                <a href="/favorites/" class="inline-flex items-center text-rose-600 font-bold hover:text-rose-700 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                    </svg>
                    View Favorites (<span id="favCountBadge">0</span>)
                </a>
            </div>

            <p class="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">{{ description }}</p>
        </div>

        <div class="flex flex-wrap justify-center gap-3 mb-10">
            <button onclick="applyGenderFilter('All')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-emerald-500" data-filter="All">All</button>
            <button onclick="applyGenderFilter('Boy')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-blue-500" data-filter="Boy">Boys</button>
            <button onclick="applyGenderFilter('Girl')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-pink-500" data-filter="Girl">Girls</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="namesGrid">
            {% for n in names %}
            {% set safe_slug = n.name|lower|replace(' ', '-')|replace("'", "") %}
            <div class="name-card relative group" data-gender="{{ n.gender|capitalize }}" data-name="{{ n.name }}">
                
                <a href="/name-{{ safe_slug }}/" class="block p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-500 hover:shadow-lg transition h-full">
                    
                    <div class="flex flex-wrap gap-2 mb-3">
                        {% if n.name in trending %}
                        <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 border border-amber-100 text-amber-700 text-xs font-bold uppercase tracking-wider">
                            🔥 Trending
                        </span>
                        {% endif %}
                        {% if n.name in quranic %}
                        <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-bold uppercase tracking-wider">
                            📖 Quranic
                        </span>
                        {% endif %}
                    </div>

                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-2xl font-bold text-slate-800 group-hover:text-emerald-700">{{ n.name }}</h3>
                        {% if n.gender|capitalize == 'Boy' %}
                            <span class="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100">{{ n.gender }}</span>
                        {% elif n.gender|capitalize == 'Girl' %}
                            <span class="text-xs font-bold uppercase tracking-wider text-pink-600 bg-pink-50 px-2 py-1 rounded border border-pink-100">{{ n.gender }}</span>
                        {% else %}
                            <span class="text-xs font-bold uppercase tracking-wider text-purple-600 bg-purple-50 px-2 py-1 rounded border border-purple-100">{{ n.gender }}</span>
                        {% endif %}
                    </div>
                    <p class="text-slate-600 line-clamp-2 pr-8">{{ n.meaning }}</p>
                </a>

                <button onclick="toggleFavorite(this, '{{ n.name }}', '{{ n.gender }}', '{{ n.meaning|escape }}', '/name-{{ safe_slug }}/')"
                    class="fav-btn absolute bottom-6 right-6 p-2 rounded-full bg-slate-50 hover:bg-rose-50 text-slate-300 hover:text-rose-500 transition border border-slate-100 z-20"
                    aria-label="Add to favorites">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 heart-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </button>
            </div>
            {% endfor %}
        </div>
        
        <div id="emptyState" class="hidden text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
            <p class="text-slate-500 text-lg">No names match this filter.</p>
        </div>
    </div>
    
    <script>
        function applyGenderFilter(gender) {
            localStorage.setItem('genderPreference', gender);
            updateFilterButtons(gender);
            const cards = document.querySelectorAll('.name-card');
            let visible = 0;
            cards.forEach(card => {
                const g = card.dataset.gender;
                const show = (gender === 'All') || (g === gender) || (g === 'Unisex') || (gender === 'Boy' && g === 'Unisex') || (gender === 'Girl' && g === 'Unisex');
                card.style.display = show ? 'block' : 'none';
                if(show) visible++;
            });
            document.getElementById('emptyState').classList.toggle('hidden', visible > 0);
        }
        function updateFilterButtons(gender) {
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.className = `filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500`;
                if(btn.dataset.filter === gender) {
                    btn.classList.add('text-white', 'border-transparent');
                    if(gender === 'All') btn.classList.add('bg-emerald-600');
                    if(gender === 'Boy') btn.classList.add('bg-blue-600');
                    if(gender === 'Girl') btn.classList.add('bg-pink-600');
                } else {
                    btn.classList.add('bg-white');
                }
            });
        }
        function getFavorites() { return JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]'); }
        function toggleFavorite(btn, name, gender, meaning, link) {
            let favs = getFavorites();
            const index = favs.findIndex(f => f.name === name);
            if (index > -1) { favs.splice(index, 1); animateHeart(btn, false); } 
            else { favs.push({ name, gender, meaning, link, date: new Date().getTime() }); animateHeart(btn, true); }
            localStorage.setItem('muslimNamesFavs', JSON.stringify(favs));
            updateFavCount();
        }
        function animateHeart(btn, isFav) {
            const icon = btn.querySelector('.heart-icon');
            if (isFav) {
                btn.classList.add('text-rose-600'); btn.classList.remove('text-slate-300'); icon.setAttribute('fill', 'currentColor');
                btn.style.transform = 'scale(1.2)'; setTimeout(() => btn.style.transform = 'scale(1)', 200);
            } else {
                btn.classList.remove('text-rose-600'); btn.classList.add('text-slate-300'); icon.setAttribute('fill', 'none');
            }
        }
        function initFavoritesUI() {
            const favs = getFavorites();
            const favNames = new Set(favs.map(f => f.name));
            document.querySelectorAll('.fav-btn').forEach(btn => {
                const card = btn.closest('.name-card');
                if (favNames.has(card.dataset.name)) animateHeart(btn, true);
            });
            updateFavCount();
        }
        function updateFavCount() {
            const badge = document.getElementById('favCountBadge');
            if(badge) badge.innerText = getFavorites().length;
        }
        document.addEventListener('DOMContentLoaded', () => {
            const savedGender = localStorage.getItem('genderPreference') || 'All';
            applyGenderFilter(savedGender);
            initFavoritesUI();
        });
    </script>
    {% endblock %}
    """)

    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(template.render(
            title=f"{title} | MuslimNameVault",
            description=description,
            names=filtered_names,
            url=f"{SITE_URL}/{folder_name}/",
            trending=trending_set,  # PASSING DATA
            quranic=quranic_set     # PASSING DATA
        ))

    print(f"✅ Generated Collection: {title} ({len(filtered_names)} names)")

def generate_favorites_page():
    """
    Generates the static /favorites/ page.
    The content is populated client-side via localStorage.
    """
    folder_path = os.path.join(OUTPUT_DIR, 'favorites')
    os.makedirs(folder_path, exist_ok=True)

    template = env.from_string("""
    {% extends "base.html" %}

    {% block content %}
    <div class="max-w-4xl mx-auto min-h-screen">
        <div class="text-center mb-10 mt-8">
            <h1 class="text-4xl font-bold text-slate-900 mb-2 font-heading">My Shortlist</h1>
            <p class="text-lg text-slate-600">Names you have saved for later.</p>
        </div>

        <div id="favEmptyState" class="hidden text-center py-20 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 class="text-xl font-bold text-slate-700">No favorites yet</h3>
            <p class="text-slate-500 mb-6">Start browsing and click the heart icon to add names here.</p>
            <a href="/names-a/" class="inline-block px-6 py-3 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 transition">Browse Names</a>
        </div>

        <div id="favList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            </div>
        
        <div id="favActions" class="hidden mt-10 text-center flex justify-center gap-4">
             <button onclick="printList()" class="px-6 py-3 bg-white border border-slate-300 text-slate-700 font-bold rounded-lg hover:bg-slate-50 transition shadow-sm">
                Print List
            </button>
            <button onclick="clearFavorites()" class="px-6 py-3 bg-white border border-rose-200 text-rose-600 font-bold rounded-lg hover:bg-rose-50 transition shadow-sm">
                Clear All
            </button>
        </div>
    </div>

    <script>
        function renderFavorites() {
            const favs = JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]');
            const list = document.getElementById('favList');
            const empty = document.getElementById('favEmptyState');
            const actions = document.getElementById('favActions');

            list.innerHTML = '';

            if (favs.length === 0) {
                empty.classList.remove('hidden');
                actions.classList.add('hidden');
                return;
            }

            empty.classList.add('hidden');
            actions.classList.remove('hidden');

            favs.forEach((n, index) => {
                const isBoy = n.gender === 'Boy';
                const isGirl = n.gender === 'Girl';
                
                // Determine colors
                let badgeClass = 'text-purple-600 bg-purple-50 border-purple-100';
                if(isBoy) badgeClass = 'text-blue-600 bg-blue-50 border-blue-100';
                if(isGirl) badgeClass = 'text-pink-600 bg-pink-50 border-pink-100';

                const html = `
                <div class="relative p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start mb-2">
                            <a href="${n.link}" class="text-2xl font-bold text-slate-800 hover:text-emerald-700 hover:underline">
                                ${n.name}
                            </a>
                            <span class="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded border ${badgeClass}">${n.gender}</span>
                        </div>
                        <p class="text-slate-600 text-sm mb-4">${n.meaning}</p>
                    </div>
                    
                    <button onclick="removeFav(${index})" class="text-sm text-rose-500 font-semibold hover:text-rose-700 self-start flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                        Remove
                    </button>
                </div>
                `;
                list.insertAdjacentHTML('beforeend', html);
            });
        }

        function removeFav(index) {
            let favs = JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]');
            favs.splice(index, 1);
            localStorage.setItem('muslimNamesFavs', JSON.stringify(favs));
            renderFavorites();
        }

        function clearFavorites() {
            if(confirm('Are you sure you want to delete all favorites?')) {
                localStorage.removeItem('muslimNamesFavs');
                renderFavorites();
            }
        }
        
        function printList() {
            window.print();
        }

        document.addEventListener('DOMContentLoaded', renderFavorites);
    </script>
    {% endblock %}
    """)

    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(template.render(
            title="My Favorites | MuslimNameVault",
            description="Your shortlisted Muslim baby names.",
            url=f"{SITE_URL}/favorites/"
        ))
    print(f"✅ Generated Favorites Page")

def get_related_names(current_name_entry, all_names, limit=6):
    """
    Finds related names based on:
    1. Rhyming (same last 3 letters)
    2. Same Origin + Gender
    3. Same Starting Letter + Gender
    """
    scores = []
    target_name = current_name_entry['name']
    target_suffix = target_name[-3:].lower() # Last 3 chars for rhyming
    target_origin = current_name_entry.get('origin', 'Unknown')
    target_gender = current_name_entry.get('gender', 'Unisex')

    for other in all_names:
        # Skip self
        if other['name'] == target_name:
            continue
            
        score = 0
        
        # 1. Gender Match (High Priority) - Parents usually want recommendations for the same gender
        if other.get('gender') == target_gender:
            score += 10
        elif target_gender == 'Unisex' or other.get('gender') == 'Unisex':
             score += 5
        else:
            continue # Skip opposite gender recommendations usually
            
        # 2. Rhyming Match (Very High Priority)
        # e.g. Rayyan & Ayaan
        if other['name'].lower().endswith(target_suffix):
            score += 20
            
        # 3. Origin Match
        if other.get('origin') == target_origin:
            score += 5
            
        # 4. Starting Letter Match
        if other['name'][0] == target_name[0]:
            score += 3

        # Only add if relevant
        if score > 10:
            scores.append((score, other))

    # Sort by score (descending) and take top N
    scores.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scores[:limit]]

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


def generate_surprise_page():
    """
    Generates a static page that uses Client-Side JS to fetch 
    and display 20 random names from the search index.
    """
    print("🎲 Generating Surprise Page...")
    
    template = env.from_string("""
    {% extends "base.html" %}
    {% block content %}
    <div class="max-w-6xl mx-auto min-h-screen">
        <div class="text-center mb-10 mt-8">
            <div class="inline-block p-3 rounded-full bg-indigo-100 text-indigo-600 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
            </div>
            <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-4 font-heading">Surprise Me!</h1>
            <p class="text-xl text-slate-600 max-w-2xl mx-auto">Here are 20 random names for inspiration.</p>
            
            <button onclick="loadRandomNames()" class="mt-8 px-8 py-3 bg-indigo-600 text-white font-bold rounded-full hover:bg-indigo-700 hover:shadow-lg transition transform active:scale-95 flex items-center gap-2 mx-auto">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Shuffle Again
            </button>
        </div>

        <div id="surpriseGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            </div>
    </div>

    <script>
        // Store data globally to avoid re-fetching
        let allNamesData = null;

        async function loadRandomNames() {
            const grid = document.getElementById('surpriseGrid');
            
            // Show Loading State
            if (!allNamesData) {
                grid.innerHTML = '<div class="col-span-full text-center py-20 text-slate-400">Loading name database...</div>';
            } else {
                grid.style.opacity = '0.5';
            }

            // Fetch Data (Once)
            if (!allNamesData) {
                try {
                    const response = await fetch('/search_index.json');
                    allNamesData = await response.json();
                } catch (e) {
                    grid.innerHTML = '<div class="col-span-full text-center text-red-500">Error loading names. Please refresh.</div>';
                    return;
                }
            }

            // Pick 20 Random Items
            const randomSelection = [];
            const usedIndices = new Set();
            const total = allNamesData.length;
            
            // Safety check if database is small
            const count = Math.min(20, total);

            while (randomSelection.length < count) {
                const idx = Math.floor(Math.random() * total);
                if (!usedIndices.has(idx)) {
                    usedIndices.add(idx);
                    randomSelection.push(allNamesData[idx]);
                }
            }

            // Render
            grid.innerHTML = '';
            grid.style.opacity = '1';
            
            randomSelection.forEach(item => {
                // Determine styling based on gender
                let badgeClass = 'bg-slate-100 text-slate-600';
                if(item.g === 'B') badgeClass = 'bg-blue-50 text-blue-600 border-blue-100';
                if(item.g === 'G') badgeClass = 'bg-pink-50 text-pink-600 border-pink-100';
                if(item.g === 'U') badgeClass = 'bg-purple-50 text-purple-600 border-purple-100';
                
                const genderLabel = item.g === 'B' ? 'Boy' : (item.g === 'G' ? 'Girl' : 'Unisex');

                const card = `
                <a href="${item.s}" class="block p-6 bg-white rounded-xl border border-slate-200 hover:border-indigo-400 hover:shadow-lg transition group animate-fade-in-up">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-2xl font-bold text-slate-800 group-hover:text-indigo-700">${item.n}</h3>
                        <span class="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded border ${badgeClass}">${genderLabel}</span>
                    </div>
                    <p class="text-slate-600 line-clamp-2">${item.m}</p>
                </a>
                `;
                grid.insertAdjacentHTML('beforeend', card);
            });
        }

        // Run on page load
        document.addEventListener('DOMContentLoaded', loadRandomNames);
    </script>
    
    <style>
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
            animation: fadeInUp 0.5s ease-out forwards;
        }
    </style>
    {% endblock %}
    """)

    folder_path = os.path.join(OUTPUT_DIR, 'surprise')
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(template.render(
            title="Surprise Me | MuslimNameVault",
            description="Generate random Muslim baby names for inspiration.",
            url=f"{SITE_URL}/surprise/"
        ))
    print("✅ Generated Surprise Page")

def generate_theme_collections(all_names):
    """
    Scans name meanings and generates collection pages for specific themes.
    """
    themes = {
        "Light": ["light", "shine", "bright", "radiant", "glow", "nur", "luminous", "sun", "moon", "star"],
        "Strength": ["strong", "brave", "warrior", "power", "mighty", "lion", "sword", "leader"],
        "Beauty": ["beauty", "beautiful", "pretty", "lovely", "grace", "elegant"],
        "Nature": ["flower", "rose", "garden", "river", "ocean", "tree", "mountain", "sky", "cloud"],
        "Wisdom": ["wise", "knowledge", "intellect", "intelligent", "mind", "learn"],
        "Faith": ["faith", "god", "allah", "worship", "divine", "holy", "religion", "pious"],
        "Happiness": ["happy", "joy", "bliss", "smile", "laugh", "cheerful"]
    }
    
    print("🎨 Generating Theme Pages...")
    
    for theme_name, keywords in themes.items():
        slug = f"names-meaning-{theme_name.lower()}"
        
        filtered_names = []
        for n in all_names:
            meaning_text = n.get('meaning', '').lower()
            if any(k in meaning_text for k in keywords):
                filtered_names.append(n)
                
        if filtered_names:
            # FIX: Added is_letter_page=True
            # This tells the function: "filtered_names is already a list of dicts, don't try to look them up again."
            generate_collection_page(
                slug,
                f"Muslim Names Meaning {theme_name}",
                f"Browse our collection of {len(filtered_names)} Muslim baby names associated with {theme_name.lower()}.",
                filtered_names,
                all_names,
                is_letter_page=True 
            )

def generate_origin_collections(all_names):
    """
    Groups names by their origin (e.g., Arabic, Persian, Turkish) 
    and generates specific collection pages.
    """
    print("🌍 Generating Origin Pages...")
    
    # 1. Identify all unique origins
    origin_groups = {}
    
    for n in all_names:
        # Split complex origins like "Arabic, Persian" into separate entries
        raw_origins = n.get('origin', 'Unknown').replace('/', ',').split(',')
        
        for origin in raw_origins:
            clean_origin = origin.strip()
            if len(clean_origin) < 3: continue # Skip abbreviations or empty
            
            if clean_origin not in origin_groups:
                origin_groups[clean_origin] = []
            origin_groups[clean_origin].append(n)
            
    # 2. Generate a page for each major origin
    for origin, names in origin_groups.items():
        if len(names) < 5: continue # Skip origins with too few names
        
        slug = f"names-origin-{origin.lower().replace(' ', '-')}"
        
        generate_collection_page(
            slug,
            f"{origin} Muslim Names",
            f"Browse our collection of {len(names)} Muslim baby names of {origin} origin.",
            names,
            all_names,
            is_letter_page=True # Treat as a pre-filtered list
        )

def generate_website():
    print("🚀 Starting Website Generation...")
    
    names = load_names()
    print(f"✅ Loaded {len(names)} names.")
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    origin_counts = {}
    for n in names:
        # Handle "Arabic, Persian"
        raw_origins = n.get('origin', 'Unknown').replace('/', ',').split(',')
        for origin in raw_origins:
            clean = origin.strip()
            if len(clean) >= 3: # Skip empty/short
                origin_counts[clean] = origin_counts.get(clean, 0) + 1
    
    # Get Top 10 Origins by count
    top_origins = sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Pass to ALL templates globally
    env.globals['nav_origins'] = top_origins
    print(f"🌍 Top Origins found for Menu: {[o[0] for o in top_origins]}")
    # -----------------------------------------------------

    # 1. Generate Index Page (Homepage)
    try:
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
    except Exception as e:
        print(f"⚠️ Warning: Could not generate homepage (missing index.html?): {e}")

    # 2. Initialize Search Index
    search_index = []
    
    # 3. Define INLINE Detail Template
    detail_template_str = """
    {% extends "base.html" %}
    {% block content %}
    <div class="max-w-4xl mx-auto py-10 px-4">
        
        <nav class="text-sm text-slate-500 mb-6">
            <a href="/" class="hover:text-emerald-600">Home</a> &rsaquo; 
            <a href="/names-{{ letter|lower }}/" class="hover:text-emerald-600">Names starting with {{ letter }}</a> &rsaquo;
            <span class="text-slate-800 font-bold">{{ name.name }}</span>
        </nav>

        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
            <div class="bg-emerald-600 p-8 text-white text-center relative">
                <h1 class="text-5xl md:text-6xl font-bold font-heading mb-2">{{ name.name }}</h1>
                
                <div class="flex items-center justify-center gap-3 mt-2">
                    <p class="text-emerald-100 text-xl">{{ name.transliteration }}</p>
                    
                    {% if audio_file %}
                    <button onclick="document.getElementById('nameAudio').play()" 
                            class="bg-white/20 hover:bg-white/40 text-white p-2 rounded-full transition shadow-sm backdrop-blur-sm" 
                            title="Listen to native pronunciation"
                            aria-label="Play pronunciation">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.828M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                    </button>
                    <audio id="nameAudio" src="/audio/{{ audio_file }}" preload="none"></audio>
                    {% endif %}
                </div>
                
                <div class="absolute top-4 right-4 bg-white/20 backdrop-blur px-3 py-1 rounded text-sm font-bold">
                    {{ name.gender }}
                </div>
            </div>

            <div class="p-8 md:p-12">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                    <div class="bg-slate-50 p-6 rounded-xl border border-slate-100">
                        <h3 class="text-xs font-bold uppercase text-slate-400 tracking-wider mb-1">Meaning</h3>
                        <p class="text-2xl font-serif text-slate-800 leading-snug">{{ name.meaning }}</p>
                    </div>
                    <div class="bg-slate-50 p-6 rounded-xl border border-slate-100">
                        <h3 class="text-xs font-bold uppercase text-slate-400 tracking-wider mb-1">Origin</h3>
                        <p class="text-2xl font-serif text-slate-800">{{ name.origin }}</p>
                    </div>
                </div>

                <div class="prose prose-lg text-slate-600 max-w-none mb-12">
                    {{ generated_content|safe }}
                </div>
                
                <div class="flex justify-between items-center py-6 border-t border-slate-100">
                    {% if prev_name %}
                    <a href="/name-{{ prev_name.name|lower|replace(' ', '-') }}/" class="group flex items-center text-slate-600 hover:text-emerald-600 transition">
                        <span class="text-2xl mr-2">&larr;</span>
                        <div class="text-left">
                            <span class="block text-xs text-slate-400 uppercase">Previous</span>
                            <span class="font-bold group-hover:underline">{{ prev_name.name }}</span>
                        </div>
                    </a>
                    {% else %}
                    <div></div>
                    {% endif %}

                    {% if next_name %}
                    <a href="/name-{{ next_name.name|lower|replace(' ', '-') }}/" class="group flex items-center text-right text-slate-600 hover:text-emerald-600 transition">
                        <div class="text-right">
                            <span class="block text-xs text-slate-400 uppercase">Next</span>
                            <span class="font-bold group-hover:underline">{{ next_name.name }}</span>
                        </div>
                        <span class="text-2xl ml-2">&rarr;</span>
                    </a>
                    {% endif %}
                </div>

            </div>
        </div>

        <div class="mt-16">
            <h3 class="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <svg class="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                Similar Names & Suggestions
            </h3>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {% for rel in related_names %}
                <a href="/name-{{ rel.name|lower|replace(' ', '-') }}/" class="group block p-4 rounded-xl border border-slate-200 bg-white hover:border-emerald-500 hover:shadow-md transition">
                    <div class="flex justify-between items-center mb-1">
                        <span class="font-bold text-slate-800 group-hover:text-emerald-700">{{ rel.name }}</span>
                        {% if rel.gender == 'Boy' %}
                            <span class="text-[10px] font-bold uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ rel.gender }}</span>
                        {% elif rel.gender == 'Girl' %}
                            <span class="text-[10px] font-bold uppercase text-pink-600 bg-pink-50 px-2 py-0.5 rounded">{{ rel.gender }}</span>
                        {% endif %}
                    </div>
                    <p class="text-xs text-slate-500 line-clamp-1">{{ rel.meaning }}</p>
                </a>
                {% endfor %}
            </div>
        </div>
        
    </div>
    {{ schema_markup|safe }}
    {% endblock %}
    """
    
    detail_template = env.from_string(detail_template_str)

    for i, name_entry in enumerate(names):
        # Data Cleaning
        name = name_entry.get('name', 'Unknown')
        meaning = name_entry.get('meaning', 'Unknown meaning')
        gender = name_entry.get('gender', 'Unisex')
        origin = name_entry.get('origin', 'Islamic')
        
        # Create Slug for Page
        slug = f"name-{name.strip().lower().replace(' ', '-')}"
        folder_path = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(folder_path, exist_ok=True)
        
        # --- AUDIO FILE CHECK ---
        # Logic from generate_audio.py: name.lower().strip().replace(' ', '-').replace("'", "")
        safe_audio_name = name.lower().strip().replace(' ', '-').replace("'", "")
        audio_filename = f"{safe_audio_name}.mp3"
        audio_file_path = os.path.join(OUTPUT_DIR, 'audio', audio_filename)
        
        # Only pass the filename if the file actually exists
        has_audio = None
        if os.path.exists(audio_file_path):
            has_audio = audio_filename

        # Add to Search Index
        search_index.append({
            "n": name,
            "s": f"/{slug}/",
            "m": meaning,
            "g": gender[0] # B, G, or U
        })

        # --- SEO CONTENT GENERATION ---
        long_desc = generate_rich_description(name, meaning, gender, origin, name_entry.get('transliteration'))

        # SMART RELATED NAMES
        related_names = get_related_names(name_entry, names)

        # NEXT / PREV LOGIC
        prev_name = names[i-1] if i > 0 else None
        next_name = names[i+1] if i < len(names) - 1 else None

        # SCHEMAS
        first_char = name[0].upper()
        
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

        breadcrumb_data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [{
                "@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL
            }, {
                "@type": "ListItem", "position": 2, "name": f"Names starting with {first_char}",
                "item": f"{SITE_URL}/names-{first_char.lower()}/"
            }, {
                "@type": "ListItem", "position": 3, "name": name, "item": f"{SITE_URL}/{slug}/"
            }]
        }

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
                letter=first_char,
                prev_name=prev_name,
                next_name=next_name,
                audio_file=has_audio  # PASS AUDIO TO TEMPLATE
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

    # 5. Generate Special Collections
    # Ensure config vars exist, fallback to empty list if not
    trending_list = getattr(config, 'TRENDING_2026', [])
    prophet_names = getattr(config, 'PROPHET_NAMES', [])
    sahaba_names = getattr(config, 'SAHABA_NAMES', [])
    quranic_direct = getattr(config, 'QURANIC_DIRECT', [])

    generate_collection_page("names-trending", "Trending Muslim Names 2026", "The most popular and trending Muslim baby names for boys and girls in 2026.", trending_list, names)
    generate_collection_page("names-prophets", "Names of Prophets", "Honorable names of the Prophets (AS) mentioned in Islam.", prophet_names, names)
    generate_collection_page("names-sahaba", "Names of Sahaba & Sahabiyat", "Names of the noble Companions of Prophet Muhammad (SAW).", sahaba_names, names)
    generate_collection_page("names-quranic", "Direct Quranic Names", "Names directly mentioned in the Holy Quran.", quranic_direct, names)
    
    # 6a. Generate Thematic Pages
    generate_theme_collections(names)

    # 6b. Generate Origin Collections
    generate_origin_collections(names)

    # 6c. Generate Surprise Page
    generate_surprise_page()

    # 7. Generate Finder Page
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
        fetch('/search_index.json').then(r=>r.json()).then(d=>{fData=d});
        fInput.addEventListener('input', (e)=>{
            const q = e.target.value.toLowerCase().trim();
            fResults.innerHTML = '';
            if(q.length < 2) return;
            const res = fData.filter(i => i.n.toLowerCase().includes(q) || i.m.toLowerCase().includes(q)).slice(0, 50); 
            if(res.length === 0) { fResults.innerHTML = '<div class="p-4 text-slate-500 text-center">No names found.</div>'; return; }
            res.forEach(r => {
                fResults.innerHTML += `
                <a href="${r.s}" class="block p-4 hover:bg-emerald-50 border-b border-slate-100 last:border-0 transition rounded-lg">
                    <div class="flex justify-between items-center">
                        <div><span class="font-bold text-lg text-slate-800">${r.n}</span><span class="block text-sm text-slate-500">${r.m}</span></div>
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

    # 8. Save Search Index
    with open(os.path.join(OUTPUT_DIR, 'search_index.json'), 'w', encoding='utf-8') as f:
        json.dump(search_index, f)
    print("✅ Generated Search Index.")

    # 9. Generate Sitemap
    generate_sitemap(names, OUTPUT_DIR, SITE_URL)
    print("✅ Generated Sitemap.")

    print("🎉 Site Generation Complete!")

if __name__ == "__main__":
    generate_website()
