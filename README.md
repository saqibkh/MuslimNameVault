# MuslimNameVault 🌙

A comprehensive static website generator and database for Muslim baby names. This project creates a fast, SEO-friendly, and interactive dictionary website featuring native audio pronunciations, origin filtering, and deep meanings.

## 📂 Project Structure

This repository is organized as follows:

### 🐍 Core Scripts

* **`generate_site.py`**
    * **The Main Builder.** This script reads the JSON database, compiles the data, and generates the static HTML website in the `output/` folder. It creates the Index, Alphabetical pages, Name Detail pages, Sitemap, and the Global Search Index.

* **`generate_audio.py`**
    * **The Voice Engine.** This script iterates through the name database and uses Google Text-to-Speech (gTTS) to generate MP3 files for every name. It intelligently selects the correct accent (Arabic, Persian, Turkish) based on the name's origin.

* **`update_database.py`**
    * **The Data Manager.** This script takes raw input from `new_names.json` and intelligently merges it into the existing `names_data/` library. It handles deduplication, ID assignment, and alphabetical sorting.

### 🗂️ Data & Output

* **`names_data/`**
    * **The Database Source.** This folder contains the source of truth for all names. Data is split into smaller JSON files (e.g., `aa.json`, `kh.json`) based on the first two letters of the name to keep the dataset manageable.

* **`output/`**
    * **The Build Directory.** This contains the fully generated website ready for deployment.
        * `*.html`: The static web pages.
        * `audio/`: The generated MP3 pronunciation files.
        * `sitemap.xml` & `robots.txt`: SEO files.
        * `search_index.json`: Data for the search bar.
    * *Note: This is the folder you upload to GitHub Pages or your hosting provider.*

### ⚙️ Configuration

* **`new_names.json`**
    * **The Staging File.** This is where you paste lists of new names you wish to add to the database. The `update_database.py` script reads from here.
    * *Format:* `[{"name": "Ali", "gender": "Boy", "meaning": "High", "origin": "Arabic"}, ...]`

* **`requirements.txt`**
    * **Dependencies.** Lists the Python libraries required to run the tools (Jinja2 for templating, gTTS for audio).

---

## 🚀 Workflow: How to Update the Site

Follow these steps to add new names and rebuild the project:

### 1. Installation
Install the required Python libraries:
```bash
pip install -r requirements.txt
