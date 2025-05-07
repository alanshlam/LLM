from flask import Flask, request, send_file, render_template_string
from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image
from PIL import Image
import torch
import os
import logging
from datetime import datetime
import sys
import traceback
import gc
import pynvml  # For NVIDIA GPU memory querying

app = Flask(__name__)

# Configure logging
log_file = f"flask_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Log uncaught exceptions
def log_uncaught_exceptions(exctype, value, tb):
    logger.error("Uncaught exception:", exc_info=(exctype, value, tb))
    with open("crash_details.log", "a") as f:
        f.write(f"Uncaught exception at {datetime.now()}:\n")
        traceback.print_exception(exctype, value, tb, file=f)

sys.excepthook = log_uncaught_exceptions

logger.info("Starting Flask app...")

# Set PyTorch CUDA memory allocation configuration to avoid fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Function to select an available GPU
def select_available_gpu(min_free_memory_mb=20000):  # Require at least ~20GB free
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        logger.info(f"Found {device_count} GPUs")
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            free_memory_mb = mem_info.free // 1024 // 1024  # Convert bytes to MiB
            logger.info(f"GPU {i}: Free memory = {free_memory_mb} MiB")
            
            if free_memory_mb >= min_free_memory_mb:
                pynvml.nvmlShutdown()
                logger.info(f"Selected GPU {i} with {free_memory_mb} MiB free memory")
                return i
        pynvml.nvmlShutdown()
        logger.warning("No GPU found with sufficient free memory")
        return None
    except Exception as e:
        logger.error(f"Error selecting GPU: {str(e)}")
        return None

# Set the CUDA device before loading pipelines
selected_gpu = select_available_gpu()
if selected_gpu is not None:
    os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_gpu)
    logger.info(f"Set CUDA_VISIBLE_DEVICES to GPU {selected_gpu}")
else:
    logger.warning("No suitable GPU found, falling back to default GPU selection")
    # Optionally, you could exit here or fall back to CPU:
    # sys.exit("No available GPU with sufficient memory")

# Pipeline loading functions
def load_text2image_pipeline():
    pipeline = AutoPipelineForText2Image.from_pretrained(
        "./flux1-dev",
        torch_dtype=torch.bfloat16,
        use_safetensors=True
    )
    pipeline.enable_sequential_cpu_offload()
    pipeline.enable_model_cpu_offload()
    return pipeline

def load_image2image_pipeline():
    pipeline = AutoPipelineForImage2Image.from_pretrained(
        "./flux1-dev",
        torch_dtype=torch.bfloat16,
        use_safetensors=True
    )
    pipeline.enable_sequential_cpu_offload()
    pipeline.enable_model_cpu_offload()
    return pipeline

# LoRA weights path
GHIBLI_LORA_PATH = "openfree/flux-chatgpt-ghibli-lora"
GHIBLI_LORA_WEIGHT = "flux-chatgpt-ghibli-lora.safetensors"

logger.info("Pipeline functions defined, will load on demand.")

# HTML template (unchanged)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ghibli Image Generator</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        textarea { width: 400px; height: 100px; }
        button { padding: 10px 20px; margin-top: 10px; }
        .slider { width: 300px; }
    </style>
</head>
<body>
    <h1>Ghibli-Style Image Generator</h1>
    <form method="POST" action="/" enctype="multipart/form-data">
        <textarea name="prompt" placeholder="Enter your prompt (e.g., A serene forest with a small wooden house)"></textarea><br>
        <input type="file" name="image" accept="image/*" style="margin-top: 10px;"><br>
        <label><input type="checkbox" name="use_ghibli"> Use Ghibli Style</label><br>
        <p> Besides Ghibli Style, you can specify other styles in the prompt window above,<br> such as Van Gogh, Claude Monet, or Gothic<p>
        <label>Strength (0.1 = keep more original, 1.0 = more transformation):</label><br>
        <input type="range" name="strength" min="0.1" max="1.0" step="0.05" value="0.75" class="slider" oninput="this.nextElementSibling.value = this.value">
        <output>0.75</output><br>
        <label>Number of Inference Steps (10–350, higher = better quality):</label><br>
        <input type="range" name="num_steps" min="10" max="350" step="1" value="30" class="slider" oninput="this.nextElementSibling.value = this.value">
        <output>30</output><br>
        <label>Guidance Scale (1.0–15.0, higher = stronger prompt):</label><br>
        <input type="range" name="guidance" min="1.0" max="15.0" step="0.5" value="7.5" class="slider" oninput="this.nextElementSibling.value = this.value">
        <output>7.5</output><br>
        <label>Image Size (256–1024 pixels, square):</label><br>
        <input type="range" name="image_size" min="256" max="1024" step="64" value="512" class="slider" oninput="this.nextElementSibling.value = this.value + 'x' + this.value">
        <output>512x512</output><br>
        <button type="submit">Generate Image</button>
    </form>
    {% if image_path %}
        <h3>Generated Image:</h3>
        <img src="{{ image_path }}" alt="Generated Image" style="max-width: 80%;">
        <br><a href="{{ image_path }}" download="ghibli_image.png">Download Image</a>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def generate_image():
    image_path = None
    if request.method == "POST":
        prompt = request.form.get("prompt", "A serene forest with a small wooden house")
        uploaded_file = request.files.get("image")
        use_ghibli = request.form.get("use_ghibli") == "on"
        strength = float(request.form.get("strength", 0.75))
        num_steps = int(request.form.get("num_steps", 30))
        guidance = float(request.form.get("guidance", 7.5))
        image_size = int(request.form.get("image_size", 512))

        if use_ghibli and "ghibli" not in prompt.lower():
            prompt = f"{prompt}, Ghibli style"
        logger.info(f"Received prompt: {prompt}, Use Ghibli: {use_ghibli}, Strength: {strength}, Steps: {num_steps}, Guidance: {guidance}, Size: {image_size}x{image_size}")

        try:
            if torch.cuda.is_available():
                logger.info(f"Using GPU {torch.cuda.current_device()}")
                logger.info(f"GPU Memory before generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB allocated, {torch.cuda.memory_reserved() / 1024**2:.2f} MiB reserved")

            pipeline = load_image2image_pipeline() if uploaded_file else load_text2image_pipeline()
            if use_ghibli:
                pipeline.load_lora_weights(GHIBLI_LORA_PATH, weight_name=GHIBLI_LORA_WEIGHT)

            static_dir = os.path.join(app.root_path, "static")
            os.makedirs(static_dir, exist_ok=True)
            image_path = os.path.join(static_dir, "generated_image.png")

            with torch.no_grad():
                if uploaded_file:
                    logger.info("Processing uploaded image...")
                    init_image = Image.open(uploaded_file).convert("RGB").resize((image_size, image_size))
                    image = pipeline(
                        prompt=prompt,
                        image=init_image,
                        strength=strength,
                        num_inference_steps=num_steps,
                        guidance_scale=guidance,
                        height=image_size,
                        width=image_size
                    ).images[0]
                else:
                    logger.info("Generating from text prompt only...")
                    image = pipeline(
                        prompt,
                        height=image_size,
                        width=image_size,
                        num_inference_steps=num_steps,
                        guidance_scale=guidance
                    ).images[0]

                logger.info(f"Generated image size: {image.size[0]}x{image.size[1]}")
                if image.size != (image_size, image_size):
                    logger.warning(f"Output size {image.size} does not match requested {image_size}x{image_size}, resizing...")
                    image = image.resize((image_size, image_size), Image.LANCZOS)

            image.save(image_path)
            image_path = "/static/generated_image.png"
            logger.info("Image generated and saved successfully.")

            del pipeline
            gc.collect()
            torch.cuda.empty_cache()
            logger.info(f"GPU Memory after cleanup: {torch.cuda.memory_allocated() / 1024**2:.2f} MiB allocated, {torch.cuda.memory_reserved() / 1024**2:.2f} MiB reserved")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            gc.collect()
            torch.cuda.empty_cache()
            return f"Error: {str(e)}", 500

    return render_template_string(HTML_TEMPLATE, image_path=image_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


