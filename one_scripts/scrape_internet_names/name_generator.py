import requests
import time
import os
import json

# Ollama local API endpoint (Runs locally, 100% free)
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3" # Utilizing the model we downloaded

def get_names_from_ai(existing_names, batch_size=50):
    """Asks the local GPU-powered AI to generate a batch of names."""
    
    # We pass a sample of existing names so the AI knows what to avoid
    avoid_list = ", ".join(list(existing_names)[-100:]) if existing_names else "None"
    
    prompt = (
        f"Generate a list of {batch_size} authentic Muslim names (mix of male and female). "
        f"Do NOT include any of these names: {avoid_list}. "
        "Respond ONLY with a comma-separated list of names. Do not include any explanations, bullet points, or extra text."
    )

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False # We want the full response at once
    }

    try:
        response = requests.post(OLLAMA_API, json=payload)
        response.raise_for_status()
        result = response.json()["response"]

        # Clean and split the AI's response into a list
        raw_names = result.split(',')
        
        # Remove whitespace, trailing periods, and convert to Title Case
        cleaned_names = [name.strip().rstrip('.').title() for name in raw_names]
        
        # Remove any empty strings or weird AI formatting artifacts
        return [n for n in cleaned_names if n and len(n) < 20 and "\n" not in n]
    
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: Is Ollama running? ({e})")
        return []

def load_master_names(filepath="ALL_NAMES_MASTER.json"):
    """Loads the master JSON file and returns a set of existing names."""
    master_names = set()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # Extract the name and standardize it to Title Case for accurate matching
                    if "name" in item:
                        master_names.add(item["name"].strip().title())
            print(f"Loaded {len(master_names)} master names from {filepath}.")
        except json.JSONDecodeError:
            print(f"Error reading {filepath}. Ensure it is valid JSON.")
    else:
        print(f"Master file {filepath} not found. Proceeding without it.")
    
    return master_names

def main():
    target_name_count = 20000 # Set how many unique names you want
    unique_names = set()
    output_file = "muslim_names_list.txt"

    # 1. Load the master list to check against
    master_names_set = load_master_names()

    # 2. Load existing names if the script was stopped and restarted
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                unique_names.add(line.strip())
        print(f"Loaded {len(unique_names)} existing names from {output_file}.")

    print(f"Firing up the 3080 Ti... Generating up to {target_name_count} names.")

    while len(unique_names) < target_name_count:
        print(f"Current count: {len(unique_names)}. Asking AI for more...")
        
        new_names = get_names_from_ai(unique_names)
        
        added_this_round = 0
        for name in new_names:
            # Prevent duplicates in the current session list AND skip names already in the master JSON
            if name not in unique_names and name not in master_names_set:
                unique_names.add(name)
                added_this_round += 1

        print(f" -> Added {added_this_round} new unique names.")

        # Save to file continuously so you don't lose data if you stop the script
        with open(output_file, "w", encoding="utf-8") as f:
            for name in sorted(unique_names):
                f.write(name + "\n")

        # Brief pause to keep the loop stable
        time.sleep(1)

    print(f"\nDone! Successfully saved {len(unique_names)} unique names to {output_file}.")

if __name__ == "__main__":
    main()
