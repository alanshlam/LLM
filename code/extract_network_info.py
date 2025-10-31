import os
import base64
import requests
import json
from pathlib import Path

# Configuration
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
MODEL = "llama3.2-vision:90b"
INPUT_FOLDER = "network_diagrams"  # Folder containing network diagram images
OUTPUT_FOLDER = "network_info"      # Folder to save extracted info
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'}

# Prompt for extracting network diagram information
SYSTEM_PROMPT = """
Analyze the network diagram and extract the following information in a structured format:
1. Network components (e.g., routers, switches, servers, firewalls)
2. Connections between components (e.g., Router1 -> Switch1)
3. IP addresses or subnets (if visible)
4. Protocols or services (if indicated)
5. Any labels or annotations
Provide the output in a clear, structured text format.
"""

def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def extract_info(image_path):
    """Extract information from a network diagram using Llama 3.2 Vision."""
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return None

    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": SYSTEM_PROMPT,
                "images": [base64_image]
            }
        ]
    }

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get('message', {}).get('content', 'No response received')
    except requests.RequestException as e:
        print(f"Error processing {image_path}: {e}")
        return None

def save_to_file(content, output_path):
    """Save extracted information to a text file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved extracted info to {output_path}")
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")

def main():
    # Create output folder if it doesn't exist
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    # Process each image in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        file_path = os.path.join(INPUT_FOLDER, filename)
        if Path(file_path).suffix.lower() in ALLOWED_EXTENSIONS:
            print(f"Processing {filename}...")
            
            # Extract information
            extracted_info = extract_info(file_path)
            if extracted_info:
                # Save to output file (same name as image but with .txt extension)
                output_filename = Path(filename).stem + '.txt'
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                save_to_file(extracted_info, output_path)
            else:
                print(f"Failed to extract info from {filename}")

if __name__ == "__main__":
    main()


