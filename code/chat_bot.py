import streamlit as st
import requests
import json

# API Configuration
API_URL = "http://localhost:8080/api/chat/completions"
API_KEY = "My_API"  # Replace with your actual API key
MODELS_URL = "http://localhost:8080/api/models"


# Web UI
st.set_page_config(page_title="Chatbot for Tech Team")

st.title("Chatbot for Tech Team")

# Instructions
st.markdown(
    """
    **Instructions:**
    - Choose the model you want to chat from the pull-down menu
    - Type your message in the input field below and press Enter.
    - This is an experimental chatbot interface. Responses may not always be accurate. Please use the responses as a reference. 
    """
)

# Disclaimer
st.warning(
    """
    **Disclaimer:** This chatbot is for testing purposes only. Do not share sensitive or personal information.
    The responses generated are AI-based and may not always be accurate or reliable. Please use the responses as a reference.
    """
)


# Fetch available models with proper parsing
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(MODELS_URL, headers=headers)

if response.status_code == 200:
    try:
        models_data = response.json().get("data", [])
        available_models = [model.get("name", "Unknown Model") for model in models_data]
    except json.JSONDecodeError:
        available_models = ["Error: Invalid JSON response"]
elif response.status_code == 403:
    available_models = ["Access Forbidden - Check API Key Permissions"]
else:
    available_models = ["report01"]  # Fallback option

# Model selection
MODEL_NAME = st.selectbox("Select a model:", available_models)

# Initialize chat history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input field
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Prepare API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": st.session_state.messages
    }
    
    # Send request to Open Web-UI API
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
    else:
        reply = f"Error: {response.status_code} - {response.text}"
    
    # Add assistant message to session state
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    with st.chat_message("assistant"):
        st.markdown(reply)
