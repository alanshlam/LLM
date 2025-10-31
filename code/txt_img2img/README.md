This folder archives the code for text to image or image to image generation powered by LLM and ComfyUI

### index.html: index file for the web application
### server.py:  python code for analyzing and generating the images
### llm-img.conf: nginx config for the web application

To run the code:
uvicorn server:app --host 127.0.0.1 --port 9000 --log-level debug

