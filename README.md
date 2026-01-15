Here is a professional README.md file for your repository. It explains the purpose of every file and folder and provides a clear workflow for using the tools.

MuslimNameVault 🌙
A static website generator and database for a comprehensive collection of Muslim baby names. This project generates a fast, SEO-friendly, and interactive dictionary website with native audio pronunciations, origin filtering, and meaning details.

📂 Project Structure
Here is a breakdown of the core files and directories in this repository:

🐍 Python Scripts
generate_site.py

The Main Engine. This script reads all JSON files from names_data/, compiles them, and generates the static HTML website in the output/ folder.

It creates the Index, Letter pages, Detail pages, Sitemap, and the Search Index.

Run this last to build the website.

generate_audio.py

The Pronunciation Engine. This script iterates through the name database and uses Google Text-to-Speech (gTTS) to generate MP3 files for every name.

It detects the name's origin (Arabic, Persian, Turkish) to select the correct accent/dialect.

Saves files to output/audio/.

update_database.py

The Data Manager. This script takes new names from new_names.json and intelligently merges them into the existing names_data/ library.

It prevents duplicates, assigns unique IDs, sorts names alphabetically, and categorizes them into the correct letter files (e.g., aa.json, sh.json).

📁 Directories
names_data/

The Database. Contains the source of truth. The data is split into multiple small JSON files (e.g., aa.json, mu.json) based on the first two letters of the names to keep the data manageable.

output/

The Build Folder. This is the generated website ready for deployment.

Contains index.html, all name-*.html pages, the audio/ folder, sitemap.xml, and search_index.json.

This folder is what you upload to GitHub Pages or your hosting provider.

📄 Configuration & Input
new_names.json

The Staging Area. This is where you paste raw lists of new names you want to add to the database.

Format: A JSON list of objects containing name, gender, meaning, and origin.

Used as input for update_database.py.

requirements.txt

Dependencies. Lists the Python libraries required to run the scripts (e.g., jinja2, gTTS).

🚀 Workflow: How to Update the Site
Follow this order to add names and rebuild the site:

1. Installation
First, ensure you have the required libraries:

Bash

pip install -r requirements.txt
2. Add New Names
Paste your new name entries into new_names.json, then run:

Bash

python3 update_database.py
This will merge the new names into names_data/ and clear duplicates.

3. Generate Audio
Create pronunciation files for the new names:

Bash

python3 generate_audio.py
This will skip existing audio files and only generate new ones.

4. Build Website
Generate the HTML pages and search index:

Bash

python3 generate_site.py
5. Deploy
Push the contents of the output/ folder (or the whole repo) to GitHub.

🛠️ Requirements
Python 3.x

Jinja2 (Templating engine)

gTTS (Google Text-to-Speech API)

Plaintext

jinja2
gTTS
