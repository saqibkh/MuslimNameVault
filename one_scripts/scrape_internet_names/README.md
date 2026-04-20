```python?code_reference&code_event_index=2
readme_content = """# Local AI Muslim Name Generator

This project contains a Python script (`name_generator.py`) that uses a locally hosted Large Language Model (LLM) to generate a deduplicated list of authentic Muslim names. 

By running the AI locally via **Ollama**, this script takes full advantage of local GPU hardware (like an RTX 3080 Ti) to generate text for free, avoiding the need for expensive web scraping APIs or paid cloud AI services.

## 📋 What This Script Does

### **Inputs**
1. **Local System State:** The script checks for an existing `muslim_names_list.txt` file. If found, it loads all existing names into memory to prevent duplicates if the script was stopped and restarted.
2. **AI Prompts:** It continuously sends prompts to the local Ollama API (`http://localhost:11434/api/generate`), asking for batches of 50 names. It dynamically feeds the last 100 generated names into the prompt as a "negative list" to force the AI to think of new names.

### **Outputs**
1. **Console Output:** Real-time logging of how many unique names have been generated and added during the current session.
2. **`muslim_names_list.txt`**: The final output file. This is an automatically sorted, deduplicated text file containing the clean list of generated names. The script continuously saves to this file after every batch, ensuring no data is lost if the process is interrupted.

---

## 🛠️ Prerequisites

Before setting up the Python environment, you must install the local AI engine:

1. **Install Ollama:** Download from [ollama.com](https://ollama.com/) and install it on your system.
2. **Download the Model:** Open your terminal and run:
   ```
```text?code_stdout&code_event_index=2
README.md generated successfully.

```bash
   ollama run llama3
   ```
   *(This downloads the Meta Llama 3 model. You can type `/bye` to exit once it loads).*
3. **Ensure Ollama is Running:** Make sure the Ollama application is open and running in your system tray/background before starting the Python script.

---

## 🚀 Setup & Virtual Environment

It is best practice to run Python scripts in a Virtual Environment to keep dependencies isolated.

### 1. Create the Virtual Environment
Open your terminal, navigate to the folder containing `name_generator.py`, and run:
```bash
python -m venv ai_env
```

### 2. Activate the Environment
* **On Windows:**
  ```cmd
  ai_env\\Scripts\\activate
  ```
* **On macOS / Linux:**
  ```bash
  source ai_env/bin/activate
  ```
*(Your terminal prompt should now show `(ai_env)`).*

### 3. Install Dependencies
With the environment active, install the required HTTP library:
```bash
pip install requests
```

---

## ⚙️ How to Run

1. Verify that Ollama is running in the background.
2. Verify your virtual environment is active.
3. Execute the script:
   ```bash
   python name_generator.py
   ```

The script will engage your GPU, query the AI, and begin populating `muslim_names_list.txt`. 

### Stopping and Resuming
You can stop the script at any time by pressing `Ctrl + C`. Because it continuously saves to the text file, running the script again will simply load the existing names and pick up right where you left off.

When you are completely finished, you can exit the virtual environment by typing:
```bash
deactivate
```

---

## 🔧 Customization

You can easily modify the script's behavior by opening `name_generator.py` in a text editor and changing the variables at the top of the `main()` function:

* `target_name_count = 1000` — Change this number to generate more or fewer total names.
* `MODEL = "llama3"` — If you download a different model via Ollama (e.g., `mistral` or `phi3`), change this string to use the new model.
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)
    
print("README.md generated successfully.")

```
Your Markdown file is ready
[file-tag: code-generated-file-0-1776700330399113650]

I have created a comprehensive `README.md` file for your project. It fully documents the purpose of the script, details the inputs and outputs, and provides clear, step-by-step instructions on how to install the prerequisites, set up the virtual environment, and run the code.
