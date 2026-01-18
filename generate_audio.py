import json
import os
import glob
import time
from gtts import gTTS

# CONFIGURATION
INPUT_FOLDER = 'names_data'
# UPDATED: Save to 'assets' so they are not deleted during site generation
AUDIO_OUTPUT_FOLDER = 'docs/audio' 

# Create audio folder if not exists
if not os.path.exists(AUDIO_OUTPUT_FOLDER):
    os.makedirs(AUDIO_OUTPUT_FOLDER)
    print(f"📁 Created directory: {AUDIO_OUTPUT_FOLDER}")

def get_safe_filename(name):
    """Converts 'Ali ibn Abi Talib' to 'ali-ibn-abi-talib'"""
    # This must match the slug logic in generate_site.py
    return name.lower().strip().replace(' ', '-').replace("'", "")

def determine_lang(origin):
    """Decides which language code to use based on Origin."""
    origin = str(origin).lower()
    if 'turkish' in origin:
        return 'tr'
    # Default to Arabic for Persian/Urdu/Quranic as they share script
    # and Google's Arabic TTS is very high quality
    return 'ar' 

def generate_audio_files():
    print(f"🎙️  Starting Audio Generation into '{AUDIO_OUTPUT_FOLDER}'...")
    
    files = glob.glob(os.path.join(INPUT_FOLDER, '*.json'))
    total_generated = 0
    skipped = 0

    if not files:
        print("❌ No JSON files found in names_data!")
        return

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            names_list = json.load(f)

        for entry in names_list:
            name_english = entry['name']
            name_arabic = entry.get('arabic_spelling', '')
            origin = entry.get('origin', '')
            
            # Filename based on English name (e.g., omar.mp3)
            filename = f"{get_safe_filename(name_english)}.mp3"
            save_path = os.path.join(AUDIO_OUTPUT_FOLDER, filename)

            # Skip if already exists (Saves time on re-runs)
            if os.path.exists(save_path):
                skipped += 1
                # print(f"⏩ Skipping {name_english} (Exists)") # Uncomment to see skips
                continue

            # Text to speak: Prefer Arabic text, fallback to English
            text_to_speak = name_arabic if name_arabic else name_english
            lang_code = determine_lang(origin)

            try:
                # Generate Audio
                tts = gTTS(text=text_to_speak, lang=lang_code, slow=False)
                tts.save(save_path)
                print(f"✅ Generated: {filename} ({text_to_speak})")
                total_generated += 1
                
                # Polite delay to avoid Google API rate limits
                time.sleep(0.5) 
                
            except Exception as e:
                print(f"❌ Failed: {name_english} - {e}")

    print(f"\n🎉 Done! Generated: {total_generated}, Skipped: {skipped}")
    print(f"📂 Audio files are located in: {AUDIO_OUTPUT_FOLDER}")

if __name__ == "__main__":
    generate_audio_files()
