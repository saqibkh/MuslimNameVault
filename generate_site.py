import json
import os
import glob
import random
from datetime import datetime
from jinja2 import Template

# --- CONFIGURATION ---
INPUT_FOLDER = 'names_data'
OUTPUT_FOLDER = 'output'
SITE_URL = "https://saqibkh.github.io/MuslimNameVault"  # Change this to your real URL

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
    <meta property="og:url" content="{{ url }}">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:image" content="https://via.placeholder.com/1200x630.png?text=MuslimNameVault">
    
    {{ schema_markup if schema_markup else '' }}

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .arabic-text { font-family: 'Amiri', serif; }
        .name-card { transition: all 0.3s ease; }
        /* Custom Scrollbar for Search Results */
        .search-results::-webkit-scrollbar { width: 6px; }
        .search-results::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 flex flex-col min-h-screen">

    <nav class="bg-emerald-800 text-white shadow-lg sticky top-0 z-50">
        <div class="container mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center justify-between w-full md:w-auto">
                <a href="index.html" class="text-2xl font-bold tracking-tight flex items-center gap-2 hover:text-emerald-100 transition">
                    <span>MuslimNameVault</span>
                </a>
                <div class="flex md:hidden gap-4">
                    <a href="favorites.html" class="text-white hover:text-emerald-200">❤️</a>
                </div>
            </div>

            <div class="relative w-full md:w-96 group">
                <div class="relative">
                    <input type="text" id="globalSearch" placeholder="Search any name..." 
                           class="w-full pl-10 pr-4 py-2 rounded-lg text-slate-800 bg-emerald-50 focus:bg-white focus:ring-2 focus:ring-emerald-400 outline-none transition shadow-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-700 absolute left-3 top-2.5 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <div id="globalSearchResults" class="hidden absolute top-full left-0 right-0 bg-white mt-2 rounded-lg shadow-xl border border-slate-200 max-h-80 overflow-y-auto search-results z-50"></div>
            </div>

            <div class="hidden md:flex gap-6 items-center">
                <a href="index.html" class="hover:text-emerald-200 font-medium opacity-90 hover:opacity-100">Home</a>
                <a href="favorites.html" class="hover:text-emerald-200 font-medium flex items-center gap-1 opacity-90 hover:opacity-100">
                    <span>❤️ My List</span>
                </a>
            </div>
        </div>
    </nav>

    <main class="flex-grow container mx-auto px-4 py-8">
        {{ content }}
    </main>

    <footer class="bg-slate-900 text-slate-400 py-10 text-center mt-auto border-t border-slate-800">
        <div class="container mx-auto px-4">
            <p class="mb-4">&copy; 2026 MuslimNameVault. A comprehensive collection of Islamic names.</p>
            <div class="flex justify-center gap-4 text-sm">
                <a href="index.html" class="hover:text-white transition">Home</a>
                <span>&bull;</span>
                <a href="favorites.html" class="hover:text-white transition">Favorites</a>
            </div>
        </div>
    </footer>

    <script>
        // Global Search Logic
        const globalSearchInput = document.getElementById('globalSearch');
        const resultsContainer = document.getElementById('globalSearchResults');
        let searchIndex = [];

        // Fetch the search index once
        fetch('search_index.json')
            .then(response => response.json())
            .then(data => { searchIndex = data; })
            .catch(err => console.error("Error loading search index:", err));

        globalSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            resultsContainer.innerHTML = '';
            
            if (query.length < 2) {
                resultsContainer.classList.add('hidden');
                return;
            }

            const results = searchIndex.filter(item => item.n.toLowerCase().startsWith(query) || item.n.toLowerCase().includes(query)).slice(0, 10);

            if (results.length > 0) {
                resultsContainer.classList.remove('hidden');
                results.forEach(item => {
                    const div = document.createElement('a');
                    div.href = item.s;
                    div.className = "block px-4 py-3 hover:bg-emerald-50 border-b border-slate-100 last:border-0 transition flex justify-between items-center";
                    div.innerHTML = `
                        <div>
                            <span class="font-bold text-slate-800 block">${item.n}</span>
                            <span class="text-xs text-slate-500 truncate block max-w-[200px]">${item.m}</span>
                        </div>
                        <span class="text-xs font-semibold px-2 py-1 bg-slate-100 rounded text-slate-500">${item.g || 'U'}</span>
                    `;
                    resultsContainer.appendChild(div);
                });
            } else {
                resultsContainer.classList.remove('hidden');
                resultsContainer.innerHTML = '<div class="px-4 py-3 text-slate-500 text-sm">No names found.</div>';
            }
        });

        // Close search when clicking outside
        document.addEventListener('click', (e) => {
            if (!globalSearchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

INDEX_CONTENT = """
<div class="text-center max-w-2xl mx-auto mb-16 mt-8">
    <span class="inline-block py-1 px-3 rounded-full bg-emerald-100 text-emerald-800 text-sm font-semibold mb-4 border border-emerald-200">✨ Discover 2,000+ Islamic Names</span>
    <h1 class="text-5xl md:text-6xl font-bold text-slate-900 mb-6 tracking-tight leading-tight">Find a Name with <span class="text-emerald-700">Meaning</span></h1>
    <p class="text-xl text-slate-600 leading-relaxed mb-8">Explore our curated collection of beautiful, verified names from the Quran, Sunnah, and Islamic history.</p>
    
    <div class="flex flex-col sm:flex-row justify-center gap-4">
        <a href="names-a.html" class="px-8 py-3.5 bg-emerald-700 text-white rounded-lg font-semibold hover:bg-emerald-800 transition shadow-lg shadow-emerald-700/20 text-lg">Start Browsing A-Z</a>
        <button onclick="randomName()" class="px-8 py-3.5 bg-white text-emerald-800 border border-emerald-200 rounded-lg font-semibold hover:bg-emerald-50 transition text-lg flex items-center justify-center gap-2">
            <span>Surprise Me</span> 
            <span>🎲</span>
        </button>
    </div>
</div>

<div class="max-w-5xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
    <h2 class="text-2xl font-bold mb-6 text-slate-800 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" /></svg>
        Browse Dictionary by Letter
    </h2>
    <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-9 gap-3">
        {% for letter in letters %}
        <a href="names-{{ letter|lower }}.html" 
           class="group block bg-slate-50 hover:bg-emerald-600 hover:text-white transition-all transform hover:-translate-y-1 rounded-lg py-4 text-center border border-slate-100 hover:border-emerald-600">
            <span class="text-xl font-bold block">{{ letter }}</span>
        </a>
        {% endfor %}
    </div>
</div>

<script>
    function randomName() {
        const letters = {{ letters_json }};
        if (letters.length > 0) {
            const randomLetter = letters[Math.floor(Math.random() * letters.length)];
            window.location.href = `names-${randomLetter.toLowerCase()}.html`;
        }
    }
</script>
"""

LIST_CONTENT = """
<div class="flex flex-col md:flex-row justify-between items-center mb-8 border-b border-slate-200 pb-6 gap-4">
    <div>
        <h1 class="text-4xl font-bold text-slate-900">Names starting with <span class="text-emerald-700">'{{ letter }}'</span></h1>
        <div class="flex items-center gap-2 mt-2">
            <a href="index.html" class="text-slate-500 hover:text-emerald-600 hover:underline text-sm font-medium transition">&larr; Back to Home</a>
            <span class="text-slate-300">|</span>
            <span class="text-sm text-slate-500">{{ names|length }} names found</span>
        </div>
    </div>
    
    <div class="flex gap-3 w-full md:w-auto">
        <div class="relative w-full md:w-64">
            <input type="text" id="searchInput" placeholder="Filter current page..." 
                   class="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none w-full transition bg-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
        </div>
        <select id="genderFilter" class="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none bg-white cursor-pointer text-slate-700">
            <option value="all">All Genders</option>
            <option value="Boy">Boys</option>
            <option value="Girl">Girls</option>
            <option value="Unisex">Unisex</option>
        </select>
    </div>
</div>

<div id="namesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for name in names %}
    <div class="name-card group bg-white rounded-xl shadow-sm border border-slate-200 p-6 relative hover:shadow-lg transition-all hover:border-emerald-400" data-name="{{ name.name|lower }}" data-gender="{{ name.gender }}">
        <button onclick="toggleFavorite(this, '{{ name.name }}', '{{ name.meaning|replace("'", "") }}', '{{ name.gender }}', '{{ name.arabic_spelling }}')" 
                class="fav-btn absolute top-5 right-5 text-slate-300 hover:text-red-500 transition focus:outline-none z-10 p-2 rounded-full hover:bg-red-50"
                data-fav-name="{{ name.name }}" title="Add to Favorites">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" stroke="none">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
        </button>

        <a href="name-{{ name.name|lower|replace(' ', '-') }}.html" class="block h-full flex flex-col">
            <div class="flex justify-between items-start pr-12 mb-2">
                <div>
                    <h2 class="text-2xl font-bold text-slate-900 group-hover:text-emerald-700 transition">{{ name.name }}</h2>
                    <p class="text-sm font-medium text-emerald-600/80">{{ name.transliteration }}</p>
                </div>
                <span class="arabic-text text-3xl text-slate-700 group-hover:text-emerald-800 transition">{{ name.arabic_spelling }}</span>
            </div>
            
            <p class="text-slate-600 mt-2 text-sm leading-relaxed line-clamp-2 flex-grow">{{ name.meaning }}</p>
            
            <div class="mt-5 pt-4 border-t border-slate-100 flex flex-wrap gap-2">
                <span class="px-2.5 py-1 text-xs rounded-md font-bold uppercase tracking-wide
                    {% if name.gender == 'Boy' %}bg-blue-50 text-blue-700{% elif name.gender == 'Girl' %}bg-pink-50 text-pink-700{% else %}bg-purple-50 text-purple-700{% endif %}">
                    {{ name.gender }}
                </span>
                {% for tag in name.get('tags', [])[:2] %}
                <span class="px-2.5 py-1 bg-emerald-50 text-xs rounded-md font-medium text-emerald-700 border border-emerald-100">{{ tag }}</span>
                {% endfor %}
            </div>
        </a>
    </div>
    {% endfor %}
</div>

<div id="noResults" class="hidden flex flex-col items-center justify-center py-20">
    <div class="bg-slate-100 p-4 rounded-full mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
    </div>
    <p class="text-xl text-slate-500 font-medium">No names found matching your filter.</p>
    <button onclick="document.getElementById('searchInput').value=''; filterNames()" class="mt-4 text-emerald-600 font-medium hover:underline">Clear search</button>
</div>

<script>
    // Local Page Filtering Logic
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
        
        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }

    if(searchInput) searchInput.addEventListener('input', filterNames);
    if(genderFilter) genderFilter.addEventListener('change', filterNames);

    // Favorite Logic (Shared)
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
<div class="max-w-4xl mx-auto">
    <nav class="flex text-sm font-medium text-slate-500 mb-6">
        <a href="index.html" class="hover:text-emerald-600 transition">Home</a>
        <span class="mx-2">/</span>
        <a href="names-{{ name.name[0]|lower }}.html" class="hover:text-emerald-600 transition">{{ name.name[0] }} Names</a>
        <span class="mx-2">/</span>
        <span class="text-slate-900">{{ name.name }}</span>
    </nav>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div class="md:col-span-2 space-y-6">
            <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
                <div class="bg-gradient-to-br from-emerald-900 to-emerald-700 p-10 text-center text-white relative overflow-hidden">
                    <div class="absolute top-0 left-0 w-full h-full opacity-10 bg-[url('https://www.transparenttextures.com/patterns/arabesque.png')]"></div>
                    
                    <h1 class="text-5xl md:text-6xl font-bold mb-2 tracking-tight relative z-10">{{ name.name }}</h1>
                    <p class="text-emerald-100 text-2xl font-light relative z-10">{{ name.transliteration }}</p>
                    
                    <div class="flex items-center justify-center gap-4 mt-6 relative z-10">
                        <div class="arabic-text text-6xl md:text-7xl opacity-90" id="arabicText">{{ name.arabic_spelling }}</div>
                        <button onclick="speakName('{{ name.name }}')" class="bg-white/20 hover:bg-white/30 p-2 rounded-full transition text-white" title="Listen to pronunciation">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                            </svg>
                        </button>
                    </div>
                    
                    {% if name.verified %}
                    <div class="absolute top-6 right-6 bg-emerald-500/30 backdrop-blur-md border border-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1 shadow-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                        Verified
                    </div>
                    {% endif %}
                </div>

                <div class="p-8 md:p-10">
                    <div class="mb-8">
                        <h3 class="text-sm uppercase tracking-widest text-emerald-600 font-bold mb-3">Detailed Meaning</h3>
                        <p class="text-2xl text-slate-800 font-medium leading-relaxed">{{ name.meaning }}</p>
                    </div>

                    <div class="grid grid-cols-2 gap-6 mb-8">
                        <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
                            <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">Gender</h3>
                            <p class="text-lg font-semibold text-slate-700 flex items-center gap-2">
                                {{ name.gender }}
                                {% if name.gender == 'Boy' %}♂{% elif name.gender == 'Girl' %}♀{% else %}⚥{% endif %}
                            </p>
                        </div>
                        <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
                            <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">Origin</h3>
                            <p class="text-lg font-semibold text-slate-700">{{ name.origin }}</p>
                        </div>
                    </div>

                    <div class="border-t border-slate-100 pt-6">
                        <h3 class="text-xs uppercase tracking-widest text-slate-400 font-bold mb-3">Categories & Tags</h3>
                        <div class="flex flex-wrap gap-2">
                            {% for tag in name.get('tags', []) %}
                            <span class="px-3 py-1 bg-white text-emerald-700 rounded-full text-sm font-medium border border-emerald-100 shadow-sm">{{ tag }}</span>
                            {% else %}
                            <span class="text-slate-400 italic text-sm">No tags available</span>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button onclick="toggleDetailFavorite()" id="detailFavBtn" class="flex justify-center items-center gap-2 px-6 py-4 bg-white border border-slate-200 rounded-xl text-slate-700 hover:border-red-400 hover:text-red-500 transition font-bold shadow-sm group">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 transition-transform group-hover:scale-110" fill="currentColor" viewBox="0 0 24 24" stroke="none"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" /></svg>
                    <span id="favBtnText">Save Name</span>
                </button>
                <button onclick="copyData()" class="flex justify-center items-center gap-2 px-6 py-4 bg-white border border-slate-200 rounded-xl text-slate-700 hover:border-emerald-400 hover:text-emerald-600 transition font-bold shadow-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                    Copy Details
                </button>
            </div>
        </div>

        <div class="md:col-span-1 space-y-6">
            <div class="bg-slate-50 p-6 rounded-xl border border-slate-200">
                <h3 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                    Similar Names
                </h3>
                <div class="space-y-3">
                    {% for related in related_names %}
                    <a href="name-{{ related.name|lower|replace(' ', '-') }}.html" class="block bg-white p-4 rounded-lg shadow-sm border border-slate-100 hover:border-emerald-400 transition hover:shadow-md">
                        <div class="flex justify-between items-center mb-1">
                            <span class="font-bold text-slate-800">{{ related.name }}</span>
                            <span class="text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-500">{{ related.gender }}</span>
                        </div>
                        <p class="text-xs text-slate-500 line-clamp-1">{{ related.meaning }}</p>
                    </a>
                    {% else %}
                    <p class="text-sm text-slate-400">No related names found.</p>
                    {% endfor %}
                </div>
            </div>
            
            <div class="bg-emerald-50 p-6 rounded-xl border border-emerald-100 text-center">
                <h3 class="text-emerald-800 font-bold mb-2">Need Help?</h3>
                <p class="text-sm text-emerald-600 mb-4">Finding the perfect name is a spiritual journey. Make dua and consult with family.</p>
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
            btn.classList.add('text-red-500', 'border-red-200', 'bg-red-50');
            btn.classList.remove('text-slate-700', 'border-slate-200', 'bg-white');
            btnText.textContent = "Saved";
        } else {
            btn.classList.remove('text-red-500', 'border-red-200', 'bg-red-50');
            btn.classList.add('text-slate-700', 'border-slate-200', 'bg-white');
            btnText.textContent = "Save Name";
        }
    }

    function toggleDetailFavorite() {
        let favorites = JSON.parse(localStorage.getItem('muslimNamesFavs')) || [];
        const index = favorites.findIndex(f => f.name === currentName);

        if (index === -1) {
            favorites.push(currentData);
            showToast("Added to Favorites ❤️");
        } else {
            favorites.splice(index, 1);
            showToast("Removed from Favorites");
        }
        localStorage.setItem('muslimNamesFavs', JSON.stringify(favorites));
        updateBtnState();
    }

    function copyData() {
        const text = `Name: ${currentData.name}\\nMeaning: ${currentData.meaning}\\nArabic: ${currentData.arabic}`;
        navigator.clipboard.writeText(text).then(() => {
            showToast("Copied to clipboard! 📋");
        });
    }

    function speakName(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; // Using English approximation usually works better for names than forcing Arabic locale which might change pronunciation drastically
        window.speechSynthesis.speak(utterance);
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-slate-900 text-white px-6 py-3 rounded-full shadow-2xl font-medium text-sm transition-all duration-300 z-50 translate-y-10 opacity-0';
        toast.innerText = message;
        document.body.appendChild(toast);
        
        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        });

        setTimeout(() => {
            toast.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    document.addEventListener('DOMContentLoaded', updateBtnState);
</script>
"""

FAVORITES_CONTENT = """
<div class="max-w-4xl mx-auto min-h-[60vh]">
    <div class="flex items-center justify-between mb-8">
        <h1 class="text-4xl font-bold text-slate-900">My Shortlist ❤️</h1>
        <button onclick="clearAll()" class="text-sm text-red-500 hover:bg-red-50 px-4 py-2 rounded-lg transition font-medium border border-transparent hover:border-red-100" id="clearBtn">Clear All</button>
    </div>

    <div id="favGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        </div>

    <div id="emptyState" class="hidden flex flex-col items-center justify-center py-20 text-center">
        <div class="bg-slate-100 p-6 rounded-full mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
        </div>
        <h3 class="text-2xl font-bold text-slate-800 mb-2">Your list is empty</h3>
        <p class="text-slate-500 mb-8 max-w-sm mx-auto">Start browsing the dictionary and click the heart icon to save names you love.</p>
        <a href="index.html" class="px-8 py-3 bg-emerald-700 text-white rounded-lg font-medium hover:bg-emerald-800 transition shadow-lg shadow-emerald-700/20">Browse Names</a>
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
                    <div class="text-right z-10 relative pointer-events-auto flex flex-col items-end">
                        <span class="arabic-text text-2xl text-emerald-800 block mb-3 pointer-events-none">${fav.arabic}</span>
                        <button onclick="removeFav('${fav.name}')" class="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-3 py-1.5 rounded transition flex items-center gap-1 border border-red-100 hover:border-red-200">
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

    renderFavorites();
</script>
"""

# --- HELPER FUNCTIONS ---

def load_all_names(folder):
    """Loads all json files and merges them."""
    data_by_letter = {}
    files = glob.glob(os.path.join(folder, '*.json'))
    print(f"📂 Found {len(files)} JSON files to process...")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content: continue
                names_list = json.loads(content)
                filename = os.path.basename(file_path)
                letter = filename[0].upper()
                if letter not in data_by_letter: data_by_letter[letter] = []
                data_by_letter[letter].extend(names_list)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    for letter in data_by_letter:
        data_by_letter[letter].sort(key=lambda x: x['name'])
            
    return data_by_letter

def generate_search_index(data):
    """Generates a lightweight JSON for the JS search bar."""
    print("🔍 Generating Global Search Index...")
    index = []
    for letter, names in data.items():
        for name in names:
            index.append({
                "n": name['name'],
                "s": f"name-{name['name'].lower().replace(' ', '-')}.html",
                "m": name['meaning'][:60], # truncated for size
                "g": name['gender']
            })
    
    with open(os.path.join(OUTPUT_FOLDER, 'search_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f)
    print("✅ search_index.json created.")

def generate_sitemap(data):
    """Generates XML Sitemap for SEO."""
    print("🗺️ Generating Sitemap...")
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>',
                       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    # Static pages
    for page in ['index.html', 'favorites.html']:
        sitemap_content.append(f"""<url><loc>{SITE_URL}/{page}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>""")

    # Detail pages
    for letter, names in data.items():
        for name in names:
            slug = f"name-{name['name'].lower().replace(' ', '-')}.html"
            sitemap_content.append(f"""<url><loc>{SITE_URL}/{slug}</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>""")
            
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(OUTPUT_FOLDER, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))
    print("✅ sitemap.xml created.")

def get_related_names(all_data, current_name_obj, count=3):
    """Finds names with same Gender or Origin."""
    candidates = []
    target_gender = current_name_obj.get('gender')
    target_origin = current_name_obj.get('origin')
    
    # Flatten data safely
    for names in all_data.values():
        for n in names:
            if n['name'] == current_name_obj['name']: continue
            if n.get('gender') == target_gender or n.get('origin') == target_origin:
                candidates.append(n)
                
    if len(candidates) >= count:
        return random.sample(candidates, count)
    return candidates

def render_page(template_str, context, output_filename):
    """Renders a page using Jinja2."""
    template = Template(template_str)
    inner_html = template.render(**context)
    
    # Dynamic Meta Tags Construction
    page_title = context.get('title', 'Muslim Names Dictionary')
    page_desc = context.get('description', 'Discover beautiful Islamic names with meanings.')
    
    layout_template = Template(BASE_LAYOUT)
    final_html = layout_template.render(
        title=page_title, 
        description=page_desc,
        url=f"{SITE_URL}/{output_filename}",
        content=inner_html,
        schema_markup=context.get('schema_markup', '')
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
        print("❌ No data found!")
        return

    # 2. Generate Utility Files
    generate_search_index(data)
    generate_sitemap(data)

    # 3. Generate Index Page
    render_page(X_CONTENT, {
        'letters': all_letters,
        'letters_json': json.dumps(all_letters),
        'title': 'Muslim Name Vault - Meaningful Islamic Names Dictionary',
        'description': 'The most comprehensive collection of Muslim baby names with meanings, origins, and pronunciation.'
    }, 'index.html')

    # 4. Generate Favorites Page
    render_page(FAVORITES_CONTENT, {
        'title': 'My Favorite Names',
        'description': 'Your shortlisted Muslim names.'
    }, 'favorites.html')

    # 5. Generate Letter & Detail Pages
    for letter in all_letters:
        names = data[letter]
        
        # Letter Page
        render_page(LIST_CONTENT, {
            'letter': letter,
            'names': names,
            'title': f'Muslim Names Starting with {letter}',
            'description': f'Browse {len(names)} Muslim names starting with the letter {letter}.'
        }, f'names-{letter.lower()}.html')
        
        # Individual Name Pages
        for name_entry in names:
            safe_filename = f"name-{name_entry['name'].lower().replace(' ', '-')}.html"
            
            # Get Related Names
            related = get_related_names(data, name_entry)
            
            # Create Schema.org JSON-LD
            schema = {
                "@context": "https://schema.org",
                "@type": "DefinedTerm",
                "name": name_entry['name'],
                "description": name_entry['meaning'],
                "inDefinedTermSet": "Muslim Names Dictionary"
            }
            
            render_page(DETAIL_CONTENT, {
                'name': name_entry,
                'related_names': related,
                'schema_markup': f'<script type="application/ld+json">{json.dumps(schema)}</script>',
                'title': f"{name_entry['name']} Name Meaning & Origin",
                'description': f"What does {name_entry['name']} mean? Discover the meaning, origin ({name_entry['origin']}), and gender of this Muslim name."
            }, safe_filename)
            
    print(f"\n✨ SUCCESS! Website generated in '{OUTPUT_FOLDER}' folder.")

if __name__ == "__main__":
    generate_website()
