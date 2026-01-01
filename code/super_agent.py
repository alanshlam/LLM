
import os
import sys
import subprocess
import requests
import json
import readline  # This enables the "Up Arrow" history functionality
import atexit
import logging

# --- CONFIGURATION ---
# Use environment variables for configuration
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
HISTORY_FILE = "chat_history.json"

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- HELPER: Enable Up-Arrow History ---
# This saves your typed command history to a hidden file for the session
histfile = os.path.join(os.path.expanduser("~"), ".python_agent_history")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)

# --- HELPER: Model Management ---
def get_models():
    try:
        url = f"{OLLAMA_BASE}/api/tags"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        models = [m['name'] for m in resp.json()['models']]
        return models
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching models from {OLLAMA_BASE}: {e}")
        return []

def select_model():
    models = get_models()
    if not models:
        print("No models found. Defaulting to 'qwen2.5-coder:14b'")
        return "qwen2.5-coder:14b"
    
    print("\n--- Available Models ---")
    for i, m in enumerate(models):
        print(f"{i + 1}. {m}")
    
    while True:
        choice = input(f"\nSelect model (1-{len(models)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            return models[int(choice)-1]

# --- TOOLS ---
def read_file(path):
    if not os.path.exists(path): return f"Error: File {path} not found."
    try:
        with open(path, 'r') as f:
            return f"--- FILE: {path} ---\n{f.read()}\n--- END FILE ---"
    except Exception as e:
        logging.error(f"Error reading file {path}: {e}")
        return f"Error reading file: {e}"

def write_file(path, content):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        logging.error(f"Error writing to file {path}: {e}")
        return f"Error writing file: {e}"

def run_shell(command):
    print(f"  [EXEC] {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output if output.strip() else "(No Output)"
    except Exception as e:
        logging.error(f"Error running shell command {command}: {e}")
        return f"Execution Error: {e}"

# --- CORE LOGIC ---
SYSTEM_PROMPT = """You are a Local System Agent. 
You can execute commands. To do so, output exactly:
ACTION: run_shell
ARGS: <command>

To read a file:
ACTION: read_file
ARGS: <path>

To write a file:
ACTION: write_file
ARGS: <path>
CONTENT:
<content>
END_CONTENT

Do not use markdown blocks for actions. Just plain text.
"""

def chat_with_ollama(messages, model):
    url = f"{OLLAMA_BASE}/v1/chat/completions"
    payload = {"model": model, "messages": messages, "temperature": 0.0}
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"API Error: {e}")
        return f"API Error: {e}"

def main():
    # 1. Select Model
    model = select_model()
    print(f"\nUsing Model: {model}")

    # 2. Load History
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    if os.path.exists(HISTORY_FILE):
        load = input(f"Found saved history in {HISTORY_FILE}. Load it? (y/n): ").lower()
        if load == 'y':
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            print("  -> History loaded.")

    print("\n--- System Ready (Type 'exit' to quit, 'save' to save history) ---")
    
    while True:
        try:
            user_input = input("\n> ")
        except KeyboardInterrupt:
            break # Handle Ctrl+C

        if user_input.lower() in ['exit', 'quit']:
            break
        
        if user_input.lower() == 'save':
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)
            print(f"  -> History saved to {HISTORY_FILE}")
            continue

        history.append({"role": "user", "content": user_input})
        
        print("Thinking...")
        response = chat_with_ollama(history, model)
        print(f"\nAI: {response}")
        history.append({"role": "assistant", "content": response})

        # Tool Parsing Logic
        if "ACTION:" in response:
            lines = response.split('\n')
            action, args = None, None
            content_mode = False
            file_content = []

            for line in lines:
                if line.startswith("ACTION:"): action = line.replace("ACTION:", "").strip()
                elif line.startswith("ARGS:"): args = line.replace("ARGS:", "").strip()
                elif line.startswith("CONTENT:"): content_mode = True
                elif line.startswith("END_CONTENT"): content_mode = False
                elif content_mode: file_content.append(line)

            tool_result = ""
            if action == "run_shell" and args:
                tool_result = run_shell(args)
            elif action == "read_file" and args:
                tool_result = read_file(args)
            elif action == "write_file" and args:
                tool_result = write_file(args, "\n".join(file_content))

            if tool_result:
                print(f"  -> Output: {tool_result}") # Removed truncation
                history.append({"role": "user", "content": f"Tool Output: {tool_result}"})
                # Auto-reply after tool
                follow_up = chat_with_ollama(history, model)
                print(f"\nAI: {follow_up}")
                history.append({"role": "assistant", "content": follow_up})

            # Auto-save after every turn for safety
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)

if __name__ == "__main__":
    main()
