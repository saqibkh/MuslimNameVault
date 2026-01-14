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

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | MuslimNameVault</title>
    <meta name="description" content="{{ description }}">
    
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://saqibkh.github.io/MuslimNameVault/">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:image" content="https://via.placeholder.com/1200x630.png?text=MuslimNameVault">

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital@0;1&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .arabic-text { font-family: 'Amiri', serif; }
        /* Smooth fade for search filtering */
        .name-card { transition: all 0.3s ease; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 flex flex-col min-h-screen">

    <nav class="bg-emerald-700 text-white shadow-lg sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <a href="index.html" class="text-2xl font-bold tracking-tight flex items-center gap-2">
                <span>MuslimNameVault</span>
            </a>
            <div class="flex gap-6 items-center">
                <a href="index.html" class="hover:text-emerald-200 hidden md:block font-medium">Home</a>
                <a href="favorites.html" class="hover:text-emerald-200 font-medium flex items-center gap-1">
                    <span>❤️ My List</span>
                </a>
            </div>
        </div>
    </nav>

    <main class="flex-grow container mx-auto px-4 py-8">
        {{ content }}
    </main>

    <footer class="bg-slate-900 text-slate-400 py-8 text-center mt-auto border-t border-slate-800">
        <p>&copy; 2026 MuslimNameVault. Built with ❤️ and Python.</p>
    </footer>

</body>
</html>
"""

INDEX_CONTENT = """
<div class="text-center max-w-2xl mx-auto mb-16 mt-8">
    <h1 class="text-5xl font-bold text-slate-900 mb-6 tracking-tight">Find the Perfect Name</h1>
    <p class="text-xl text-slate-600 leading-relaxed">Explore our curated collection of beautiful, verified names from the Quran and Sunnah.</p>
    
    <div class="mt-8 flex justify-center gap-4">
        <a href="names-a.html" class="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition shadow-lg shadow-emerald-600/20">Start Browsing</a>
        <button onclick="randomName()" class="px-6 py-3 bg-white text-emerald-700 border border-emerald-200 rounded-lg font-semibold hover:bg-emerald-50 transition">Surprise Me 🎲</button>
    </div>
</div>

<div class="max-w-4xl mx-auto">
    <h2 class="text-2xl font-semibold mb-6 text-center text-slate-800">Browse by Letter</h2>
    <div class="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-9 gap-3">
        {% for letter in letters %}
        <a href="names-{{ letter|lower }}.html" 
           class="block bg-white hover:bg-emerald-600 hover:text-white transition-all transform hover:-translate-y-1 shadow-sm hover:shadow-md rounded-lg py-4 text-center text-xl font-bold border border-slate-200">
            {{ letter }}
        </a>
        {% endfor %}
    </div>
</div>

<script>
    function randomName() {
        const letters = {{ letters|tojson }};
        const randomLetter = letters[Math.floor(Math.random() * letters.length)];
        window.location.href = `names-${randomLetter.toLowerCase()}.html`;
    }
</script>
"""

LIST_CONTENT = """
<div class="flex flex-col md:flex-row justify-between items-center mb-8 border-b border-slate-200 pb-6 gap-4">
    <div>
        <h1 class="text-4xl font-bold text-slate-900">Letter <span class="text-emerald-600">{{ letter }}</span></h1>
        <a href="index.html" class="text-slate-500 hover:text-emerald-600 hover:underline text-sm mt-1 inline-block">&larr; Back to Home</a>
    </div>
    
    <div class="flex gap-3 w-full md:w-auto">
        <div class="relative w-full md:w-64">
            <input type="text" id="searchInput" placeholder="Search names..." 
                   class="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none w-full transition">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        </div>
        <select id="genderFilter" class="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none bg-white cursor-pointer">
            <option value="all">All Genders</option>
            <option value="Boy">Boys Only</option>
            <option value="Girl">Girls Only</option>
        </select>
    </div>
</div>

<div id="namesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for name in names %}
    <div class="name-card group bg-white rounded-xl shadow-sm border border-slate-200 p-6 relative hover:shadow-lg transition-all hover:border-emerald-500/50" data-name="{{ name.name|lower }}" data-gender="{{ name.gender }}">
        <button onclick="toggleFavorite(this, '{{ name.name }}', '{{ name.meaning|replace("'", "") }}', '{{ name.gender }}', '{{ name.arabic_spelling }}')" 
                class="fav-btn absolute top-5 right-5 text-slate-300 hover:text-red-500 transition focus:outline-none z-10 p-1 rounded-full hover:bg-red-50"
                data-fav-name="{{ name.name }}">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" stroke="none">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
        </button>

        <a href="name-{{ name.name|lower|replace(' ', '-') }}.html" class="block h-full flex flex-col">
            <div class="flex justify-between items-start pr-10 mb-2">
                <div>
                    <h2 class="text-2xl font-bold text-slate-900 group-hover:text-emerald-700 transition">{{ name.name }}</h2>
                    <p class="text-sm font-medium text-emerald-600/80">{{ name.transliteration }}</p>
                </div>
                <span class="arabic-text text-3xl text-slate-800">{{ name.arabic_spelling }}</span>
            </div>
            
            <p class="text-slate-600 mt-2 text-sm leading-relaxed line-clamp-2 flex-grow">{{ name.meaning }}</p>
            
            <div class="mt-5 pt-4 border-t border-slate-100 flex flex-wrap gap-2">
                <span class="px-2.5 py-1 bg-slate-100 text-xs rounded-md font-semibold text-slate-600 uppercase tracking-wide">{{ name.gender }}</span>
                {% for tag in name.tags[:2] %}
                <span class="px-2.5 py-1 bg-emerald-50 text-xs rounded-md font-medium text-emerald-700 border border-emerald-100">{{ tag }}</span>
                {% endfor %}
            </div>
        </a>
    </div>
    {% endfor %}
</div>

<div id="noResults" class="hidden text-center py-12">
    <p class="text-xl text-slate-400 font-medium">No names found matching your search.</p>
</div>

<script>
    // --- Search Logic ---
    const searchInput = document.getElementById('searchInput');
    const genderFilter = document.getElementById('genderFilter');
    const cards = document.querySelectorAll('.name-card');
    const noResults = document.getElementById('noResults');

    function filterNames() {
        const query = searchInput.value.toLowerCase().trim();
        const gender = genderFilter.value;
        let visibleCount = 0;

        cards.forEach(card => {
            const nameText = card.getAttribute('data-name');
            const cardGender = card.getAttribute('data-gender');
            
            const matchesSearch = nameText.includes(query);
            const matchesGender = gender === 'all' || cardGender === gender;

            if (matchesSearch && matchesGender) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/Hide "No Results" message
        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }

    searchInput.addEventListener('input', filterNames);
    genderFilter.addEventListener('change', filterNames);

    // --- Favorites Logic (Shared) ---
    function toggleFavorite(btn, name, meaning, gender, arabic) {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        const index = favorites.findIndex(f => f.name === name);
        
        if (index === -1) {
            favorites.push({ name, meaning, gender, arabic });
            btn.classList.add('text-red-500');
            btn.classList.remove('text-slate-300');
        } else {
            favorites.splice(index, 1);
            btn.classList.remove('text-red-500');
            btn.classList.add('text-slate-300');
        }
        localStorage.setItem('muslimNamesFavs', JSON.stringify(favorites));
    }

    // Initialize Heart Colors on Load
    document.addEventListener('DOMContentLoaded', () => {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        favorites.forEach(fav => {
            const btns = document.querySelectorAll(`button[data-fav-name="${fav.name}"]`);
            btns.forEach(btn => {
                btn.classList.add('text-red-500');
                btn.classList.remove('text-slate-300');
            });
        });
    });
</script>
"""

DETAIL_CONTENT = """
<div class="max-w-3xl mx-auto">
    <a href="names-{{ name.name[0]|lower }}.html" class="inline-flex items-center text-slate-500 hover:text-emerald-600 mb-6 transition font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to {{ name.name[0] }} Names
    </a>

    <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
        <div class="bg-gradient-to-r from-emerald-800 to-emerald-600 p-10 text-center text-white relative">
            <h1 class="text-6xl font-bold mb-2 tracking-tight">{{ name.name }}</h1>
            <p class="text-emerald-100 text-2xl font-light">{{ name.transliteration }}</p>
            <div class="arabic-text text-7xl mt-6 opacity-90">{{ name.arabic_spelling }}</div>
            
            {% if name.verified %}
            <div class="absolute top-6 right-6 bg-white/10 backdrop-blur-sm border border-white/20 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-emerald-200" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Verified
            </div>
            {% endif %}
        </div>

        <div class="p-8 md:p-10">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-y-8 gap-x-12 mb-10">
                <div class="border-b border-slate-100 pb-4">
                    <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Meaning</h3>
                    <p class="text-2xl text-slate-900 font-medium leading-snug">{{ name.meaning }}</p>
                </div>
                <div class="border-b border-slate-100 pb-4">
                    <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Gender</h3>
                    <p class="text-2xl text-slate-900 font-medium">{{ name.gender }}</p>
                </div>
                <div>
                    <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Origin</h3>
                    <p class="text-xl text-slate-800">{{ name.origin }}</p>
                </div>
                <div>
                    <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-2">Categories</h3>
                    <div class="flex flex-wrap gap-2">
                        {% for tag in name.tags %}
                        <span class="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium border border-emerald-100">{{ tag }}</span>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <div class="bg-slate-50 rounded-xl p-6 text-center border border-slate-100">
                <p class="text-slate-600 mb-4">Do you like this name?</p>
                <button onclick="toggleDetailFavorite()" id="detailFavBtn" class="inline-flex items-center gap-2 px-6 py-2.5 bg-white border border-slate-300 rounded-lg text-slate-700 hover:border-red-400 hover:text-red-500 transition font-semibold shadow-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" stroke="none">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                    </svg>
                    <span id="favBtnText">Add to Favorites</span>
                </button>
            </div>
        </div>
    </div>
</div>

<script>
    const currentName = "{{ name.name }}";
    const currentData = {
        name: "{{ name.name }}",
        meaning: "{{ name.meaning|replace('"', '') }}",
        gender: "{{ name.gender }}",
        arabic: "{{ name.arabic_spelling }}"
    };
    const btn = document.getElementById('detailFavBtn');
    const btnText = document.getElementById('favBtnText');

    function updateBtnState() {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        const isFav = favorites.some(f => f.name === currentName);
        
        if (isFav) {
            btn.classList.add('text-red-500', 'border-red-200');
            btn.classList.remove('text-slate-700', 'border-slate-300');
            btnText.textContent = "Saved to Favorites";
        } else {
            btn.classList.remove('text-red-500', 'border-red-200');
            btn.classList.add('text-slate-700', 'border-slate-300');
            btnText.textContent = "Add to Favorites";
        }
    }

    function toggleDetailFavorite() {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        const index = favorites.findIndex(f => f.name === currentName);

        if (index === -1) {
            favorites.push(currentData);
        } else {
            favorites.splice(index, 1);
        }
        localStorage.setItem('muslimNamesFavs', JSON.stringify(favorites));
        updateBtnState();
    }

    document.addEventListener('DOMContentLoaded', updateBtnState);
</script>
"""

FAVORITES_CONTENT = """
<div class="max-w-4xl mx-auto min-h-[60vh]">
    <div class="flex items-center justify-between mb-8">
        <h1 class="text-4xl font-bold text-slate-900">My Shortlist ❤️</h1>
        <button onclick="clearAll()" class="text-sm text-red-500 hover:bg-red-50 px-3 py-1 rounded-md transition" id="clearBtn">Clear All</button>
    </div>

    <div id="favGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        </div>

    <div id="emptyState" class="hidden flex flex-col items-center justify-center py-20 text-center">
        <div class="bg-slate-100 p-6 rounded-full mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
        </div>
        <h3 class="text-xl font-bold text-slate-800 mb-2">Your list is empty</h3>
        <p class="text-slate-500 mb-6">Start browsing and click the heart icon to save names.</p>
        <a href="index.html" class="px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition">Browse Names</a>
    </div>
</div>

<script>
    const grid = document.getElementById('favGrid');
    const emptyState = document.getElementById('emptyState');
    const clearBtn = document.getElementById('clearBtn');

    function renderFavorites() {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        grid.innerHTML = '';

        if (favorites.length === 0) {
            emptyState.classList.remove('hidden');
            clearBtn.classList.add('hidden');
        } else {
            emptyState.classList.add('hidden');
            clearBtn.classList.remove('hidden');
            
            favorites.forEach(fav => {
                const card = document.createElement('div');
                card.className = 'bg-white rounded-xl shadow-sm hover:shadow-md transition p-6 border border-slate-200 flex justify-between items-center relative overflow-hidden group';
                
                // Link wrapper
                const link = document.createElement('a');
                link.href = `name-${fav.name.toLowerCase().replace(' ', '-')}.html`;
                link.className = 'absolute inset-0 z-0';
                card.appendChild(link);

                card.innerHTML += `
                    <div class="z-10 relative pointer-events-none">
                        <div class="flex items-center gap-3">
                            <h2 class="text-xl font-bold text-slate-900">${fav.name}</h2>
                            <span class="px-2 py-0.5 bg-slate-100 text-[10px] rounded-full uppercase tracking-wide font-bold text-slate-500">${fav.gender}</span>
                        </div>
                        <p class="text-slate-600 text-sm mt-1 line-clamp-1">${fav.meaning}</p>
                    </div>
                    <div class="text-right z-10 relative pointer-events-auto">
                        <span class="arabic-text text-2xl text-emerald-800 block mb-2 pointer-events-none">${fav.arabic}</span>
                        <button onclick="removeFav('${fav.name}')" class="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition flex items-center gap-1 ml-auto">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 000-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                            Remove
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    }

    function removeFav(name) {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        favorites = favorites.filter(f => f.name !== name);
        localStorage.setItem('muslimNamesFavs', JSON.stringify(favorites));
        renderFavorites();
    }

    function clearAll() {
        if(confirm('Are you sure you want to clear your list?')) {
            localStorage.removeItem('muslimNamesFavs');
            renderFavorites();
        }
    }

    // Init
    renderFavorites();
</script>
"""

# --- HELPER FUNCTIONS ---

def load_all_names(folder):
    """Loads all json files into a dictionary keyed by letter."""
    data_by_letter = {}
    
    files = glob.glob(os.path.join(folder, '*.json'))
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                names_list = json.load(f)
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
    content_template = Template(template_str)
    inner_html = content_template.render(**context)
    
    layout_template = Template(BASE_LAYOUT)
    final_html = layout_template.render(
        title=context.get('title', 'Muslim Names'), 
        description=context.get('description', 'Find beautiful Muslim names'),
        content=inner_html
    )
    
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

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
        'title': 'Muslim Name Vault - Meaningful Islamic Names',
        'description': 'The most beautiful collection of Muslim boy and girl names with meanings, origins, and verification.'
    }, 'index.html')
    print("✅ Generated index.html")

    # 3. Generate Favorites Page
    render_page(FAVORITES_CONTENT, {
        'title': 'My Favorite Names',
        'description': 'View your shortlisted Muslim names.'
    }, 'favorites.html')
    print("✅ Generated favorites.html")

    # 4. Generate Letter Pages & Detail Pages
    for letter in all_letters:
        names = data[letter]
        
        # Letter Page
        render_page(LIST_CONTENT, {
            'letter': letter,
            'names': names,
            'title': f'Muslim Names Starting with {letter}',
            'description': f'Browse {len(names)} Muslim names starting with the letter {letter}, including meanings and origins.'
        }, f'names-{letter.lower()}.html')
        
        # Individual Name Pages
        for name_entry in names:
            safe_filename = f"name-{name_entry['name'].lower().replace(' ', '-')}.html"
            render_page(DETAIL_CONTENT, {
                'name': name_entry,
                'title': f"{name_entry['name']} - Meaning & Origin",
                'description': f"Meaning of the Muslim name {name_entry['name']}: {name_entry['meaning']}. Origin: {name_entry['origin']}."
            }, safe_filename)
            
    print(f"\n✨ Website generated successfully in the '{OUTPUT_FOLDER}' folder!")

if __name__ == "__main__":
    generate_website()
