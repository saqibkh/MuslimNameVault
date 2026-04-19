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

def generate_suggest_page():
    """Generates a simple suggestion page using Formspree to email results."""
    print("📝 Generating Suggestion Page...")

    template = env.from_string("""
    {% extends "base.html" %}
    {% block content %}
    <div class="max-w-2xl mx-auto py-16 px-4 min-h-screen">
        <div class="text-center mb-10">
            <span class="inline-block p-3 rounded-full bg-emerald-100 text-emerald-600 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
            </span>
            <h1 class="text-4xl md:text-5xl font-bold mb-4 font-heading text-slate-900">Suggest a Name</h1>
            <p class="text-slate-600 text-lg">Help us grow the vault! If you know a beautiful Muslim name we missed, submit it below.</p>
        </div>

        <form action="https://formspree.io/f/xaqdzewg" method="POST" class="bg-white p-8 rounded-2xl shadow-xl border border-slate-100 space-y-6">

            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Name *</label>
                <input type="text" name="Name" required placeholder="e.g. Zayd" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none transition">
            </div>

            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Meaning *</label>
                <textarea name="Meaning" required rows="3" placeholder="e.g. Abundance, Growth" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none transition"></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Gender</label>
                    <select name="Gender" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none transition">
                        <option value="Boy">Boy</option>
                        <option value="Girl">Girl</option>
                        <option value="Unisex">Unisex</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Origin (Optional)</label>
                    <input type="text" name="Origin" placeholder="e.g. Arabic" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none transition">
                </div>
            </div>

            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Your Email (Optional)</label>
                <input type="email" name="_replyto" placeholder="To notify you when it's added" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 outline-none transition">
            </div>

            <input type="hidden" name="_subject" value="New Name Suggestion for MuslimNameVault!">
            <input type="hidden" name="_next" value="https://muslimnamevault.com/">

            <button type="submit" class="w-full py-4 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition shadow-lg flex justify-center items-center gap-2">
                Send Suggestion
            </button>
        </form>
    </div>
    {% endblock %}
    """)

    folder_path = os.path.join(OUTPUT_DIR, 'suggest')
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(template.render(
            title="Suggest a Name | MuslimNameVault",
            description="Submit a new Muslim baby name to our database.",
            url=f"{SITE_URL}/suggest/"
        ))
    print("✅ Generated Suggestion Page")

def generate_collection_page(folder_name, title, description, name_list, all_names, is_letter_page=False, show_gender_filter=True):
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

        {% if show_gender_filter %}
        <div class="flex flex-wrap justify-center gap-3 mb-10">
            <button onclick="applyGenderFilter('All')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-emerald-500" data-filter="All">All</button>
            <button onclick="applyGenderFilter('Boy')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-blue-500" data-filter="Boy">Boys</button>
            <button onclick="applyGenderFilter('Girl')" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 hover:border-pink-500" data-filter="Girl">Girls</button>
        </div>
        {% endif %}

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
            {% if show_gender_filter %}
            const savedGender = localStorage.getItem('genderPreference') || 'All';
            applyGenderFilter(savedGender);
            {% endif %}
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
            quranic=quranic_set,     # PASSING DATA
            show_gender_filter=show_gender_filter
        ))

    print(f"✅ Generated Collection: {title} ({len(filtered_names)} names)")


def generate_favorites_page():
    """
    Generates the static /favorites/ page with URL-based Sharing Capabilities.
    """
    folder_path = os.path.join(OUTPUT_DIR, 'favorites')
    os.makedirs(folder_path, exist_ok=True)

    template = env.from_string("""
    {% extends "base.html" %}

    {% block content %}
    <div class="max-w-4xl mx-auto min-h-screen">
        <div class="text-center mb-10 mt-8">
            <h1 id="pageTitle" class="text-4xl font-bold text-slate-900 mb-2 font-heading">My Shortlist</h1>
            <p id="pageSubtitle" class="text-lg text-slate-600">Names you have saved for later.</p>
            
            <div id="sharedBanner" class="hidden mt-4 inline-block bg-indigo-50 border border-indigo-200 text-indigo-700 px-4 py-2 rounded-lg font-medium shadow-sm">
                👀 You are viewing a shared shortlist
            </div>
        </div>

        <div id="favEmptyState" class="hidden text-center py-20 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 id="emptyTitle" class="text-xl font-bold text-slate-700">No favorites yet</h3>
            <p id="emptyDesc" class="text-slate-500 mb-6">Start browsing and click the heart icon to add names here.</p>
            <a href="/names-a/" class="inline-block px-6 py-3 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 transition">Browse Names</a>
        </div>

        <div id="favList" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
        
        <div id="favActions" class="hidden mt-10 flex flex-wrap justify-center gap-4">
            <button onclick="showShareModal()" class="px-6 py-3 bg-emerald-600 border border-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 transition shadow-sm flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" /></svg>
                Share List
            </button>
            <button onclick="printList()" class="px-6 py-3 bg-white border border-slate-300 text-slate-700 font-bold rounded-lg hover:bg-slate-50 transition shadow-sm">
                Print List
            </button>
            <button onclick="clearFavorites()" class="px-6 py-3 bg-white border border-rose-200 text-rose-600 font-bold rounded-lg hover:bg-rose-50 transition shadow-sm">
                Clear All
            </button>
        </div>

        <div id="shareModal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 opacity-0 transition-opacity duration-300">
            <div class="bg-white rounded-2xl p-6 md:p-8 max-w-md w-full shadow-2xl transform scale-95 transition-transform duration-300 relative">
                <button onclick="closeShareModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
                
                <h3 class="text-2xl font-bold text-slate-900 mb-2 font-heading">Share Your Shortlist</h3>
                <p class="text-slate-600 mb-6 text-sm">Send this link to family and friends so they can see your favorite names.</p>
                
                <div class="flex items-center gap-2 mb-6">
                    <input type="text" id="shareUrlInput" readonly class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-600 outline-none focus:ring-2 focus:ring-emerald-500">
                    <button onclick="copyShareLink()" id="copyBtn" class="bg-slate-800 text-white px-5 py-3 rounded-lg font-bold text-sm hover:bg-slate-900 transition whitespace-nowrap">
                        Copy
                    </button>
                </div>

                <div class="grid grid-cols-2 gap-3 mb-2">
                    <button onclick="shareWhatsApp()" class="flex items-center justify-center gap-2 bg-[#25D366] text-white px-4 py-3 rounded-lg font-bold text-sm hover:bg-[#20bd5a] transition">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
                        WhatsApp
                    </button>
                    <button onclick="shareTwitter()" class="flex items-center justify-center gap-2 bg-black text-white px-4 py-3 rounded-lg font-bold text-sm hover:bg-slate-800 transition">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                        X (Twitter)
                    </button>

                    <button onclick="shareFacebook()" class="flex items-center justify-center gap-2 bg-[#1877F2] text-white px-4 py-3 rounded-lg font-bold text-sm hover:bg-[#166fe5] transition">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.469h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                        Facebook
                    </button>

                    <button onclick="shareTelegram()" class="flex items-center justify-center gap-2 bg-[#0088cc] text-white px-4 py-3 rounded-lg font-bold text-sm hover:bg-[#007ab8] transition">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0011.944 0zm6.67 8.248l-2.223 10.456c-.167.746-.61.928-1.233.578l-3.409-2.513-1.644 1.583c-.182.182-.336.335-.691.335l.245-3.486 6.345-5.733c.276-.246-.06-.382-.428-.137L5.734 14.18 2.36 13.12c-.733-.23-.746-.733.153-1.085l13.125-5.06c.607-.225 1.139.138.976 1.273z"/></svg>
                        Telegram
                    </button>
                </div>

                <button onclick="nativeShare()" class="w-full mt-2 flex items-center justify-center gap-2 bg-slate-100 text-slate-700 px-4 py-3 rounded-lg font-bold text-sm hover:bg-slate-200 transition border border-slate-200">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>
                    More Options (Instagram, SMS, Email)
                </button>
            </div>
        </div>

    </div>

    <script>
        // Create the HTML for a single name card
        function createCardHtml(n, isShared) {
            const isBoy = n.gender === 'Boy' || n.g === 'B';
            const isGirl = n.gender === 'Girl' || n.g === 'G';
            const genderLabel = isBoy ? 'Boy' : (isGirl ? 'Girl' : 'Unisex');
            const nameLink = n.link || n.s; // Handles both LocalStorage and search_index data structures
            const meaning = n.meaning || n.m;
            const nameStr = n.name || n.n;
            
            let badgeClass = 'text-purple-600 bg-purple-50 border-purple-100';
            if(isBoy) badgeClass = 'text-blue-600 bg-blue-50 border-blue-100';
            if(isGirl) badgeClass = 'text-pink-600 bg-pink-50 border-pink-100';

            // Only show the remove button if it is their personal list
            const removeBtnHtml = isShared ? '' : `
            <button onclick="removeFav('${nameStr}')" class="text-sm text-rose-500 font-semibold hover:text-rose-700 self-start flex items-center gap-1 mt-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                Remove
            </button>`;

            return `
            <div class="relative p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:border-emerald-400 transition group">
                <div>
                    <div class="flex justify-between items-start mb-2">
                        <a href="${nameLink}" class="text-2xl font-bold text-slate-800 group-hover:text-emerald-700 group-hover:underline">
                            ${nameStr}
                        </a>
                        <span class="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded border ${badgeClass}">${genderLabel}</span>
                    </div>
                    <p class="text-slate-600 text-sm">${meaning}</p>
                </div>
                ${removeBtnHtml}
            </div>`;
        }

        async function renderFavorites() {
            const list = document.getElementById('favList');
            const empty = document.getElementById('favEmptyState');
            const actions = document.getElementById('favActions');
            
            // Check if there is a "?list=" parameter in the URL
            const urlParams = new URLSearchParams(window.location.search);
            const sharedListParam = urlParams.get('list');

            list.innerHTML = '';

            // --- SCENARIO 1: VIEWING A SHARED LIST ---
            if (sharedListParam) {
                document.getElementById('pageTitle').innerText = "Shared Shortlist";
                document.getElementById('pageSubtitle').innerText = "Someone shared their favorite names with you.";
                document.getElementById('sharedBanner').classList.remove('hidden');
                
                const namesToFind = sharedListParam.split(',').map(n => n.toLowerCase().trim());
                
                try {
                    // Fetch the search index to get meanings and links for the shared names
                    const response = await fetch('/search_index.json');
                    const allNamesData = await response.json();
                    
                    const sharedNames = allNamesData.filter(item => namesToFind.includes(item.n.toLowerCase()));
                    
                    if (sharedNames.length === 0) {
                        empty.classList.remove('hidden');
                        document.getElementById('emptyTitle').innerText = "List Not Found";
                        document.getElementById('emptyDesc').innerText = "The shared link might be broken or empty.";
                        return;
                    }

                    sharedNames.forEach(n => {
                        list.insertAdjacentHTML('beforeend', createCardHtml(n, true));
                    });
                    
                    // Allow them to click a button to view their OWN list
                    actions.classList.remove('hidden');
                    actions.innerHTML = `
                        <a href="/favorites/" class="px-6 py-3 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 transition shadow-sm">
                            Create My Own List
                        </a>
                    `;

                } catch (e) {
                    console.error("Error loading shared list:", e);
                }
                return;
            }

            // --- SCENARIO 2: VIEWING PERSONAL LIST ---
            const favs = JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]');

            if (favs.length === 0) {
                empty.classList.remove('hidden');
                actions.classList.add('hidden');
                return;
            }

            empty.classList.add('hidden');
            actions.classList.remove('hidden');

            favs.forEach((n) => {
                list.insertAdjacentHTML('beforeend', createCardHtml(n, false));
            });
        }

        // Logic Functions
        function removeFav(nameStr) {
            let favs = JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]');
            favs = favs.filter(f => f.name !== nameStr); // Filter by name
            localStorage.setItem('muslimNamesFavs', JSON.stringify(favs));
            renderFavorites();
        }

        function clearFavorites() {
            if(confirm('Are you sure you want to delete all favorites?')) {
                localStorage.removeItem('muslimNamesFavs');
                renderFavorites();
            }
        }
        function printList() { window.print(); }

        // --- SHARING MODAL LOGIC ---
        function showShareModal() {
            const favs = JSON.parse(localStorage.getItem('muslimNamesFavs') || '[]');
            if(favs.length === 0) return;
            
            // Build the URL
            const namesOnly = favs.map(f => f.name).join(',');
            const shareUrl = window.location.origin + window.location.pathname + '?list=' + encodeURIComponent(namesOnly);
            
            document.getElementById('shareUrlInput').value = shareUrl;
            
            const modal = document.getElementById('shareModal');
            modal.classList.remove('hidden');
            // Slight delay for fade animation
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modal.children[0].classList.remove('scale-95');
            }, 10);
        }

        function closeShareModal() {
            const modal = document.getElementById('shareModal');
            modal.classList.add('opacity-0');
            modal.children[0].classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
                document.getElementById('copyBtn').innerText = 'Copy';
            }, 300); // Wait for animation
        }

        function copyShareLink() {
            const input = document.getElementById('shareUrlInput');
            input.select();
            document.execCommand('copy');
            const btn = document.getElementById('copyBtn');
            btn.innerText = 'Copied!';
            setTimeout(() => btn.innerText = 'Copy', 2000);
        }

        function shareWhatsApp() {
            const url = document.getElementById('shareUrlInput').value;
            const text = encodeURIComponent('Check out my favorite Muslim baby names shortlist! 👶❤️ \\n\\n') + encodeURIComponent(url);
            window.open('https://api.whatsapp.com/send?text=' + text, '_blank');
        }

        function shareTwitter() {
            const url = document.getElementById('shareUrlInput').value;
            const text = encodeURIComponent('Check out my shortlist of beautiful Muslim baby names! 👶✨');
            window.open(`https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(url)}`, '_blank');
        }

        function shareFacebook() {
            const url = document.getElementById('shareUrlInput').value;
            window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), '_blank');
        }

        function shareTelegram() {
            const url = document.getElementById('shareUrlInput').value;
            const text = encodeURIComponent('Check out my shortlist of beautiful Muslim baby names! 👶✨');
            window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${text}`, '_blank');
        }

        function nativeShare() {
            const url = document.getElementById('shareUrlInput').value;
            if (navigator.share) {
                navigator.share({
                    title: 'My MuslimNameVault Shortlist',
                    text: 'Check out my favorite Muslim baby names shortlist! 👶❤️',
                    url: url
                }).catch((error) => console.log('Error sharing:', error));
            } else {
                alert('Advanced sharing options are only supported on mobile devices or compatible browsers. Please use the Copy button instead!');
            }
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
    print(f"✅ Generated Favorites Page with Sharing UI")

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
    and display 20 random names, with Gender Filtering support.
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
            <p class="text-xl text-slate-600 max-w-2xl mx-auto">Discover random Muslim baby names for inspiration.</p>
            
            <div class="flex flex-wrap justify-center gap-3 mt-8 mb-8">
                <button onclick="setGender('All')" id="btn-All" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-transparent bg-indigo-600 text-white shadow-md">
                    All
                </button>
                <button onclick="setGender('Boy')" id="btn-Boy" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 bg-white hover:border-blue-400 hover:text-blue-600">
                    Boys
                </button>
                <button onclick="setGender('Girl')" id="btn-Girl" class="filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 bg-white hover:border-pink-400 hover:text-pink-600">
                    Girls
                </button>
            </div>

            <button onclick="loadRandomNames()" class="px-8 py-3 bg-slate-800 text-white font-bold rounded-full hover:bg-slate-900 hover:shadow-lg transition transform active:scale-95 flex items-center gap-2 mx-auto">
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
        let allNamesData = null;
        let currentGender = 'All';

        function setGender(gender) {
            currentGender = gender;
            
            // Update UI Buttons
            document.querySelectorAll('.filter-btn').forEach(btn => {
                // Reset to default style
                btn.className = 'filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-slate-200 text-slate-500 bg-white hover:border-slate-300';
            });

            // Set Active Style
            const activeBtn = document.getElementById('btn-' + gender);
            if(gender === 'All') {
                activeBtn.className = 'filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-transparent bg-indigo-600 text-white shadow-md';
            } else if (gender === 'Boy') {
                activeBtn.className = 'filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-blue-600 bg-blue-600 text-white shadow-md';
            } else if (gender === 'Girl') {
                activeBtn.className = 'filter-btn px-6 py-2 rounded-full font-bold transition-all border-2 border-pink-600 bg-pink-600 text-white shadow-md';
            }

            // Reload names with new filter
            loadRandomNames();
        }

        async function loadRandomNames() {
            const grid = document.getElementById('surpriseGrid');
            
            // Show Loading State if data isn't loaded yet
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

            // FILTER DATA BASED ON GENDER
            // 'B' = Boy, 'G' = Girl, 'U' = Unisex
            let filteredPool = allNamesData;
            
            if (currentGender === 'Boy') {
                filteredPool = allNamesData.filter(n => n.g === 'B' || n.g === 'U');
            } else if (currentGender === 'Girl') {
                filteredPool = allNamesData.filter(n => n.g === 'G' || n.g === 'U');
            }

            // Pick 20 Random Items from the FILTERED pool
            const randomSelection = [];
            const usedIndices = new Set();
            const total = filteredPool.length;
            const count = Math.min(20, total);

            if (total === 0) {
                grid.innerHTML = '<div class="col-span-full text-center py-10 text-slate-500">No names found for this filter.</div>';
                grid.style.opacity = '1';
                return;
            }

            while (randomSelection.length < count) {
                const idx = Math.floor(Math.random() * total);
                if (!usedIndices.has(idx)) {
                    usedIndices.add(idx);
                    randomSelection.push(filteredPool[idx]);
                }
            }

            // Render
            grid.innerHTML = '';
            grid.style.opacity = '1';
            
            randomSelection.forEach(item => {
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
        # Skip names with apostrophes or dots to prevent broken links
        if "'" in n.get('name', '') or "." in n.get('name', ''):
            continue

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

                {% if name.spellings %}
                <div class="mb-10 animate-fade-in-up">
                    <h3 class="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" /></svg>
                        Global Spellings
                    </h3>
                    <div class="flex flex-wrap gap-3">
                        {% for lang, script in name.spellings.items() %}
                        <div class="bg-white px-4 py-3 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3 hover:border-emerald-300 transition">
                            <span class="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">{{ lang }}</span>
                            <span class="text-2xl font-medium text-slate-800 {% if lang in ['Arabic', 'Urdu', 'Persian', 'Pashto'] %}arabic-text{% endif %}">
                                {{ script }}
                            </span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
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
        
        # --- NEW CODE: Remove redundant Latin spellings ---
        if 'spellings' in name_entry:
            cleaned_spellings = {}
            for lang, script in name_entry['spellings'].items():
                # Compare case-insensitively. Only keep it if it's actually different.
                if script.strip().lower() != name.strip().lower():
                    cleaned_spellings[lang] = script
            
            # If valid spellings remain, update it. Otherwise, remove the key entirely.
            if cleaned_spellings:
                name_entry['spellings'] = cleaned_spellings
            else:
                del name_entry['spellings']
        # --------------------------------------------------
        
        # Create Slug for Page
        slug = f"name-{name.strip().lower().replace(' ', '-')}"
        folder_path = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(folder_path, exist_ok=True)
        
        # --- AUDIO FILE CHECK ---
        # Logic from generate_audio.py: name.lower().strip().replace(' ', '-')
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

        filtered_names = [
            n for n in names
            if n['name'].startswith(char)
            and "'" not in n['name']
            and "." not in n['name']
        ]
        
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
   
    # --- ADD DEDICATED GENDER PAGES HERE ---
    boy_names = [n for n in names if n.get('gender', '').lower() in ['boy', 'unisex']]
    girl_names = [n for n in names if n.get('gender', '').lower() in ['girl', 'unisex']]

    generate_collection_page(
        "muslim-boy-names", 
        "Muslim Boy Names", 
        "A comprehensive collection of beautiful, strong, and meaningful Islamic names for boys.", 
        boy_names, 
        names, 
        is_letter_page=True,
        show_gender_filter=False
    )

    generate_collection_page(
        "muslim-girl-names", 
        "Muslim Girl Names", 
        "Explore our curated list of elegant, meaningful, and beautiful Islamic names for girls.", 
        girl_names, 
        names, 
        is_letter_page=True,
        show_gender_filter=False
    )
    # ---------------------------------------

    # 6a. Generate Thematic Pages
    generate_theme_collections(names)

    # 6b. Generate Origin Collections
    generate_origin_collections(names)

    # 6c. Generate Surprise Page
    generate_surprise_page()

    # 6d. Generate Favorites Page (NEW)
    generate_favorites_page()

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

    generate_suggest_page()

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
