#!/usr/bin/env python3
# extract_network_info_multi_model.py

import os
import base64
import json
import argparse
from pathlib import Path

import requests

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"

# Supported models (display name → Ollama tag)
SUPPORTED_MODELS = {
    "llama3.2-vision:11b": "llama3.2-vision:11b",
    "llama3.2-vision:90b": "llama3.2-vision:90b",
    "qwen3-vl:32b":        "qwen3-vl:32b",
    "gemma3:27b":          "gemma3:27b",
}

INPUT_FOLDER   = "network_diagrams"   # put your images here
OUTPUT_FOLDER  = "network_info"       # extracted text files go here
ALLOWED_EXT    = {".png", ".jpg", ".jpeg", ".bmp"}

# Prompt that is sent to every model
SYSTEM_PROMPT = """
Analyze the network diagram and extract the following information in a structured, easy-to-read format:

1. **Network components** (routers, switches, firewalls, servers, etc.)
2. **Connections** (e.g., Router1 → Switch1)
3. **IP addresses / subnets** (if visible)
4. **Protocols / services** (if indicated)
5. **Labels / annotations**

Return the result as plain text, using markdown headers and bullet points where appropriate.
"""

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def encode_image(image_path: Path) -> str | None:
    """Read an image file and return its base64 representation."""
    try:
        return base64.b64encode(image_path.read_bytes()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding {image_path.name}: {e}")
        return None


def query_ollama(model: str, b64_image: str) -> str | None:
    """Send the image + prompt to Ollama and return the model's reply."""
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": SYSTEM_PROMPT,
                "images": [b64_image],
            }
        ],
    }

    try:
        resp = requests.post(
            OLLAMA_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "No response")
    except requests.RequestException as e:
        print(f"Request error for model {model}: {e}")
        return None


def save_output(content: str, out_path: Path):
    """Write the extracted text to disk."""
    try:
        out_path.write_text(content, encoding="utf-8")
        print(f"Saved → {out_path}")
    except Exception as e:
        print(f"Failed to write {out_path}: {e}")


# --------------------------------------------------------------------------- #
# Main processing
# --------------------------------------------------------------------------- #
def process_folder(model_tag: str):
    input_path = Path(INPUT_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(exist_ok=True)

    if not input_path.is_dir():
        raise FileNotFoundError(f"Input folder '{INPUT_FOLDER}' not found.")

    images = [
        p for p in input_path.iterdir()
        if p.suffix.lower() in ALLOWED_EXT and p.is_file()
    ]

    if not images:
        print("No supported images found in the input folder.")
        return

    print(f"Using model: **{model_tag}**")
    print(f"Found {len(images)} image(s) to process.\n")

    for img_path in images:
        print(f"Processing {img_path.name} …")
        b64 = encode_image(img_path)
        if not b64:
            continue

        extracted = query_ollama(model_tag, b64)
        if extracted is None:
            print(f"Skipping {img_path.name} (model error).")
            continue

        # Build output filename:  original_stem + _ + model_tag + .txt
        safe_model_name = model_tag.replace(":", "-")   # avoid colons in filenames
        out_name = f"{img_path.stem}_{safe_model_name}.txt"
        out_file = output_path / out_name

        save_output(extracted, out_file)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_cli():
    parser = argparse.ArgumentParser(
        description="Extract network-diagram information using a chosen Ollama vision model."
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=list(SUPPORTED_MODELS.keys()),
        required=True,
        help="Vision model to use (required).",
    )
    parser.add_argument(
        "-i",
        "--input",
        default=INPUT_FOLDER,
        help=f"Folder containing diagram images (default: {INPUT_FOLDER})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_FOLDER,
        help=f"Folder for extracted text files (default: {OUTPUT_FOLDER})",
    )
    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    global INPUT_FOLDER, OUTPUT_FOLDER
    INPUT_FOLDER = args.input
    OUTPUT_FOLDER = args.output

    chosen_model = SUPPORTED_MODELS[args.model]

    process_folder(chosen_model)


if __name__ == "__main__":
    main()

