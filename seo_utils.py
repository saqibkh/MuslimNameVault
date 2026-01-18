import os
import datetime

def generate_sitemap(names, output_dir, site_url):
    """
    Generates a sitemap.xml file for Google Search Console.
    Includes the homepage, collection pages, and every single name page.
    """
    sitemap_path = os.path.join(output_dir, 'sitemap.xml')
    
    # Current date for Last-Modified header
    today = datetime.date.today().isoformat()
    
    xml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # 1. Add Homepage
    xml_content.append(f"""
    <url>
        <loc>{site_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """)

    # 2. Add Collection Pages (A-Z)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for char in alphabet:
        xml_content.append(f"""
        <url>
            <loc>{site_url}/names-{char.lower()}/</loc>
            <lastmod>{today}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.8</priority>
        </url>
        """)

    # 3. Add Individual Name Pages
    for name_entry in names:
        # Create the clean slug exactly like generate_site.py does
        clean_name = name_entry['name'].strip().lower().replace(' ', '-')
        slug = f"name-{clean_name}"
        
        xml_content.append(f"""
        <url>
            <loc>{site_url}/{slug}/</loc>
            <lastmod>{today}</lastmod>
            <changefreq>monthly</changefreq>
            <priority>0.6</priority>
        </url>
        """)

    xml_content.append('</urlset>')
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_content))

    print(f"   └── Sitemap generated at: {sitemap_path}")
