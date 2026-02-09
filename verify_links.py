import os
from bs4 import BeautifulSoup

# CONFIG
DOCS_DIR = 'docs'
BASE_URL = 'https://muslimnamevault.com'

def verify_internal_links():
    print(f"🔍 Scanning {DOCS_DIR} for broken links...")
    
    html_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    print(f"📄 Found {len(html_files)} HTML files. Starting validation...")

    broken_links = []
    total_checked = 0

    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']
                
                # We only care about internal links starting with /
                if href.startswith('/') and not href.startswith('//'):
                    total_checked += 1
                    
                    # Construct the local path the link is pointing to
                    # Remove trailing slash and add /index.html
                    clean_href = href.strip('/')
                    target_path = os.path.join(DOCS_DIR, clean_href, 'index.html') if clean_href else os.path.join(DOCS_DIR, 'index.html')

                    if not os.path.exists(target_path):
                        broken_links.append({
                            'source': file_path,
                            'target': href
                        })

    print(f"✅ Checked {total_checked} internal links.")

    if broken_links:
        print(f"❌ Found {len(broken_links)} broken links:")
        for bug in broken_links[:20]: # Show first 20
            print(f"   - In {bug['source']} -> Points to: {bug['target']}")
        if len(broken_links) > 20:
            print(f"   ... and {len(broken_links) - 20} more.")
    else:
        print("🎉 All internal links are valid!")

if __name__ == "__main__":
    # You may need to install beautifulsoup4: pip install beautifulsoup4
    try:
        verify_internal_links()
    except ImportError:
        print("❌ Error: BeautifulSoup4 is required. Run: pip install beautifulsoup4")
