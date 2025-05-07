### This folder contains the programs to faciliate knowledge base building powered by LLM

**app_3090.py**: Image generator can be with Ghibli-Style, powered by
black-forest-labs/FLUX.1-dev,
openfree/flux-chatgpt-ghibli-lora, and
flux-chatgpt-ghibli-lora.safetensors 

**chat_bot_up15.py**: Streamlit UI program for building a Chatbot accessing available models in Open WebU. This version allows user upload file with differnet document format, choose AI roles, and copy response to clipborad.

**chat_bot_up15_ws.py**: include the functions in chat_bot_up15.py plus web search function by duckduckgo

**chat_bot.py**: Streamlit UI program for building a Chatbot accessing available models in Open WebU

**extract_network_info.py**: Extract network information from network diagram in the network_diagrams folder by using llama3.2-vision:90b in Ollama.

**extract_text_from_eml.py**: program to extract mail body texts from mailbox in eml format

**extract_and_group_emails.py**: Progam to extract plain text from mail body and group the output mails with same subject tilte. 

**img_prompt_server.py**: Program connected to ollama LLM and ComfyUI image model to generate image 
