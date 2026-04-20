# MuslimNameVault - Static Site Generator

This project is a custom static site generator that builds **MuslimNameVault.com**. It takes a database of names (JSON files) and compiles them into a fast, SEO-optimized website with features like search, audio pronunciation, and smart filtering.

## 📂 Project Structure

Here is an overview of the key files you need to maintain:

### 🐍 Python Scripts (The Logic)

| File | Description |
| :--- | :--- |
| **`generate_site.py`** | **The Main Engine.** Run this script to rebuild the website. It reads the data, applies templates, generates all HTML pages (A-Z, details, collections, surprise), and builds the search index. |
| **`config.py`** | **The Curator.** Contains manual lists for special collections (e.g., `TRENDING_2026`, `PROPHET_NAMES`, `QURANIC_DIRECT`). **Update this file to change which names appear in the "Curated Lists" dropdown.** |
| **`update_database.py`** | **The Adder.** Safely adds new names to the dictionary. It reads incoming names from `new_names.json`, assigns them unique IDs, checks for duplicates, and categorizes them into their proper alphabetical JSON files. |
| **`export_master_list.py`** | **The Compiler.** Compiles all individual JSON files located in `names_data/` into one massive, alphabetically sorted file called `ALL_NAMES_MASTER.json` for backups, global searching, or migrations. |
| **`auto_spellings.py`** | **The Translator.** An automation script that uses the `deep-translator` library to automatically fetch and populate the "Global Spellings" (Arabic, Urdu, Persian, Turkish, Bengali, Indonesian, Pashto) for names in your database. |
| **`seo_utils.py`** | **The SEO Helper.** Handles the generation of the `sitemap.xml` file so Google can index all your pages correctly. |
| **`verify_links.py`** | **The Tester.** A QA script that scans all generated HTML files in the `docs/` directory to ensure there are no broken internal links before deploying. |
| **`generate_audio.py`** | *(Optional)* A utility script used to generate MP3 text-to-speech files for new names. Run this only when you add new names to the database. |


### 📄 Data & Content (The Database)

| Folder/File | Description |
| :--- | :--- |
| **`names_data/*.json`** | **The Name Database.** The names are split into multiple JSON files (e.g., `names_a.json`, `names_b.json`). <br>To add a new name, simply open the corresponding letter file and add a new JSON entry. |
| **`templates/`** | Contains `base.html` (the header/footer layout) and other HTML components. |
| **`docs/`** | **The Output.** This is the "public" folder. When you run the generator, it fills this folder with the final HTML files. **This is the folder you publish to the web.** |

---

## 🛠️ How to Add New Names

1.  Open the **`names_data/`** folder.
2.  Open the JSON file matching the letter (e.g., `names_a.json` for "Ali").
3.  Add a new entry inside the list following this format:
    ```json
    {
        "name": "Ali",
        "transliteration": "Ali",
        "meaning": "High, Exalted, Champion",
        "gender": "Boy",
        "origin": "Arabic",
        "arabic_spelling": "علي"
    }
    ```
4.  Save the file.
5.  Run the build script (see below).

---

## ⚙️ How to Update Curated Lists (Trending, Prophets, etc.)

1.  Open **`config.py`**.
2.  Find the list you want to update (e.g., `TRENDING_2026`).
3.  Add the **exact spelling** of the name as a string to the list.
    ```python
    TRENDING_2026 = [
        "Aaliyah",
        "Muhammad",
        "Zayn",
        "NewNameHere"  # <--- Add new name here
    ]
    ```
4.  Save and rebuild.

---

## 🚀 How to Build the Website

Whenever you make changes to data, config, or templates, you must rebuild the site.

1.  Open your terminal/command prompt.
2.  Navigate to the project folder.
3.  Run the following command:
    ```bash
    python generate_site.py
    ```
4.  You should see output like:
    ```text
    🚀 Starting Website Generation...
    ✅ Loaded 15,000 names.
    🌍 Top Origins found for Menu: ['Arabic', 'Persian', 'Urdu', ...]
    ✅ Generated Collection: Trending Muslim Names 2026
    ✅ Generated Surprise Page
    🎉 Site Generation Complete!
    ```

---

## 💻 Requirements

To run this project, you need Python installed along with the `Jinja2` library.

**Installation:**
```bash
pip install jinja2
```

### To view local changes, ru
```bash
python3 -m http.server 8000 -d docs
```
