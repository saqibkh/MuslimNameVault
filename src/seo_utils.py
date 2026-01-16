import os
import json
from config import OUTPUT_FOLDER, SITE_URL

def generate_search_index(data):
    """Generates a lightweight JSON for the JS search bar."""
    print("🔍 Generating Global Search Index...")
    index = []
    for letter, names in data.items():
        for name in names:
            index.append({
                "n": name['name'],
                "s": f"name-{name['name'].lower().replace(' ', '-')}.html",
                "m": name['meaning'][:60], 
                "g": name['gender']
            })
    
    with open(os.path.join(OUTPUT_FOLDER, 'search_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f)
    print("✅ search_index.json created.")

def generate_sitemap(data):
    """Generates XML Sitemap."""
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

def generate_robots():
    """Generates robots.txt."""
    print("🤖 Generating robots.txt...")
    content = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(OUTPUT_FOLDER, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ robots.txt created.")
