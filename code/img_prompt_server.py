import json
import uuid
import websocket
import logging
import os
import copy
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("comfyui-api")

app = FastAPI(title="ComfyUI API Proxy")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
server_address = "127.0.0.1:8190"
workflow_path = "workflow01.json"
ollama_address = "http://localhost:11438"

# Load workflow
def load_workflow():
    try:
        with open(workflow_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load workflow")

workflow = load_workflow()

class WorkflowRequest(BaseModel):
    positive_prompt: str
    negative_prompt: str = ""
    ckpt_name: str = "RealVisXL_V5.0_Lightning_fp32.safetensors"
    use_ollama: bool = False
    ollama_model: Optional[str] = None

def open_websocket_connection():
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()
    try:
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        logger.info("WebSocket connected successfully")
        return ws, client_id
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"ComfyUI server connection error: {str(e)}")

def queue_prompt(prompt: Dict, client_id: str) -> Dict:
    try:
        response = requests.post(
            f"http://{server_address}/prompt",
            json={"prompt": prompt, "client_id": client_id}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to queue prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue prompt: {str(e)}")

def track_progress(ws: websocket.WebSocket, prompt_id: str):
    while True:
        try:
            message = json.loads(ws.recv())
            if message.get("type") == "executed" and message.get("data", {}).get("prompt_id") == prompt_id:
                break
        except Exception as e:
            logger.error(f"WebSocket error during progress tracking: {str(e)}")
            raise HTTPException(status_code=500, detail="Error tracking progress")

def get_images(prompt_id: str) -> List[Dict]:
    try:
        response = requests.get(f"http://{server_address}/history/{prompt_id}")
        response.raise_for_status()
        history = response.json()
        outputs = history.get(prompt_id, {}).get("outputs", {})
        result = []
        for node_id, output in outputs.items():
            for unit in output.get("images", []):
                image_response = requests.get(f"http://{server_address}/view?filename={unit['filename']}&type=output")
                image_response.raise_for_status()
                import base64
                result.append({
                    "node_id": node_id,
                    "data": base64.b64encode(image_response.content).decode("utf-8"),
                    "format": "image/png"
                })
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {str(e)}")

def get_ollama_models() -> List[str]:
    try:
        response = requests.get(f"{ollama_address}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        models = [model["name"] for model in data.get("models", [])]
        if not models:
            logger.warning("No Ollama models found")
        return models
    except requests.exceptions.ConnectionError:
        logger.error(f"Ollama server not reachable at {ollama_address}")
        return []
    except Exception as e:
        logger.error(f"Failed to fetch Ollama models: {str(e)}")
        return []

def enhance_prompt_with_ollama(prompt: str, model: str) -> str:
    try:
        response = requests.post(
            f"{ollama_address}/api/generate",
            json={
                "model": model,
                "prompt": f"Refine the following prompt for high-quality image generation, making it more detailed and descriptive while keeping the core idea intact, skip the explanation, just give the best option: '{prompt}'",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", prompt)
    except requests.exceptions.ConnectionError:
        logger.warning(f"Ollama server not reachable at {ollama_address}")
        return prompt
    except requests.exceptions.HTTPError as e:
        logger.warning(f"Ollama HTTP error: {str(e)}")
        return prompt
    except Exception as e:
        logger.warning(f"Failed to enhance prompt with Ollama: {str(e)}")
        return prompt

def generate_follow_up_with_ollama(prompt: str, images: List[Dict], model: str) -> str:
    try:
        response = requests.post(
            f"{ollama_address}/api/generate",
            json={
                "model": model,
                "prompt": f"Based on the following prompt used for image generation: '{prompt}', provide a detailed description of the expected visual elements in the generated images and suggest improvements for future iterations. Note that {len(images)} image(s) were generated.",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No follow-up description available.")
    except requests.exceptions.ConnectionError:
        logger.warning(f"Ollama server not reachable at {ollama_address}")
        return "Ollama server not reachable."
    except requests.exceptions.HTTPError as e:
        logger.warning(f"Ollama HTTP error: {str(e)}")
        return f"Ollama error: {str(e)}"
    except Exception as e:
        logger.warning(f"Failed to generate follow-up with Ollama: {str(e)}")
        return "No follow-up description available due to an error."

@app.get("/checkpoints")
async def get_checkpoints():
    try:
        response = requests.get(f"http://{server_address}/object_info/CheckpointLoaderSimple", timeout=5)
        if not response.ok:
            logger.error(f"ComfyUI returned HTTP {response.status_code}: {response.text}")
            raise HTTPException(status_code=503, detail=f"ComfyUI server error: HTTP {response.status_code}")
        data = response.json()
        checkpoints = data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])[0]
        if not checkpoints:
            logger.warning("No checkpoints found in ComfyUI response")
            raise HTTPException(status_code=404, detail="No checkpoints available")
        return {"checkpoints": checkpoints}
    except requests.exceptions.ConnectionError:
        logger.error(f"ComfyUI server not reachable at {server_address}")
        raise HTTPException(status_code=503, detail=f"ComfyUI server not reachable at {server_address}")
    except Exception as e:
        logger.error(f"Failed to fetch checkpoints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch checkpoints: {str(e)}")

@app.get("/ollama_health")
async def ollama_health():
    try:
        response = requests.get(f"{ollama_address}/api/tags", timeout=5)
        response.raise_for_status()
        return {"status": "Ollama server is running", "models": response.json().get("models", [])}
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return {"status": "Ollama server not reachable", "error": str(e)}

@app.get("/ollama_models")
async def get_ollama_models_endpoint():
    models = get_ollama_models()
    if not models:
        raise HTTPException(status_code=503, detail="No Ollama models available or server not reachable")
    return {"models": models}

@app.post("/run")
async def run_workflow(request: WorkflowRequest):
    try:
        # Validate checkpoint name
        response = requests.get(f"http://{server_address}/object_info/CheckpointLoaderSimple", timeout=5)
        response.raise_for_status()
        data = response.json()
        checkpoints = data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])[0]
        
        if request.ckpt_name not in checkpoints:
            raise HTTPException(status_code=400, detail="Invalid checkpoint name")

        # Validate Ollama model if use_ollama is true
        final_positive_prompt = request.positive_prompt
        if request.use_ollama:
            if not request.ollama_model or request.ollama_model == "undefined":
                raise HTTPException(status_code=400, detail="Ollama model must be specified when use_ollama is true")
            
            available_models = get_ollama_models()
            if not available_models:
                logger.warning("No Ollama models available; falling back to original prompt")
                request.use_ollama = False
            elif request.ollama_model not in available_models:
                raise HTTPException(status_code=400, detail=f"Invalid Ollama model: {request.ollama_model}. Available models: {available_models}")
            else:
                final_positive_prompt = enhance_prompt_with_ollama(request.positive_prompt, request.ollama_model)
                logger.info(f"Enhanced prompt: {final_positive_prompt}")

        # Create a copy of the workflow
        prompt = copy.deepcopy(workflow)
        
        # Update prompts
        id_to_class_type = {id: details["class_type"] for id, details in prompt.items()}
        k_sampler_id = [key for key, value in id_to_class_type.items() if value == "KSampler"][0]
        positive_input_id = prompt[k_sampler_id]["inputs"]["positive"][0]
        negative_input_id = prompt[k_sampler_id]["inputs"]["negative"][0]
        
        # Update seed for each run
        prompt[k_sampler_id]["inputs"]["seed"] = int.from_bytes(os.urandom(8), "big") % (10**15)
        prompt[positive_input_id]["inputs"]["text"] = final_positive_prompt
        if request.negative_prompt:
            prompt[negative_input_id]["inputs"]["text"] = request.negative_prompt

        # Update checkpoint name
        checkpoint_loader_id = [key for key, value in id_to_class_type.items() if value == "CheckpointLoaderSimple"][0]
        prompt[checkpoint_loader_id]["inputs"]["ckpt_name"] = request.ckpt_name

        # Connect to WebSocket and queue prompt
        ws, client_id = open_websocket_connection()
        try:
            prompt_id = queue_prompt(prompt, client_id)["prompt_id"]
            track_progress(ws, prompt_id)
            images = get_images(prompt_id)
            
            # Generate follow-up description with Ollama if requested
            follow_up = ""
            if request.use_ollama and available_models:
                follow_up = generate_follow_up_with_ollama(final_positive_prompt, images, request.ollama_model)
            
            return {
                "status": "success",
                "result": images,
                "enhanced_prompt": final_positive_prompt,
                "follow_up": follow_up
            }
        finally:
            ws.close()
    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
