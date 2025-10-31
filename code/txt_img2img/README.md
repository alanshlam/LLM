This folder archives the code for text to image or image to image generation powered by LLM and ComfyUI, and some regenerated image samples.

### index.html: index file for the web application
### server.py:  python code for analyzing and generating the images
### llm-img.conf: nginx config for the web application

To run the code:
uvicorn server:app --host 127.0.0.1 --port 9000 --log-level debug

### image_regenerated_in_ComfyUI.png :  Regenerated images in ConfyUI
<img src="./image_regenerated_in_ComfyUI.png" width="600">

### regenerated_image_sample (*).png :  Regenerated image samples
<img src="./regenerated_image_sample (3).png" width="600">
<img src="./regenerated_image_sample (2).png" width="600">
<img src="./regenerated_image_sample (1).png" width="600">
<img src="./regenerated_image_sample (4).png" width="600">
<img src="./regenerated_image_sample (5).png" width="600">
<img src="./regenerated_image_sample (6).png" width="600">
<img src="./regenerated_image_sample (7).png" width="600">
<img src="./regenerated_image_sample (8).png" width="600">



