import streamlit as st
import requests
import json
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import streamlit.components.v1 as components
from duckduckgo_search import DDGS

# API Configuration
API_URL = "http://localhost:8080/api/chat/completions"
API_KEY = "Your_API_key"  # Replace with your actual API key
MODELS_URL = "http://localhost:8080/api/models"

# Web UI
st.set_page_config(page_title="Chatbot for Tech Team powered by VLLM and Ollama")

st.title("Chatbot for Tech Team powered by VLLM and Ollama")

# Instructions
st.markdown(
    """
    **Instructions:**
    - Choose the model and AI role from the pull-down menu or define your own custom role.
    - Predefined roles include:
      - **General Assistant** (default): A versatile assistant for general-purpose personal assistance.
      - **Secretary**: Assists with drafting documents, proofreading, and managing text-based tasks.
      - **Programmer**: Skilled in writing, debugging, and explaining code across various languages.
      - **Data Analyzer**: Proficient in extracting, analyzing, and interpreting data from various formats.
      - **Teacher**: Prepares course materials, explains concepts, and aids in education.
      - **Trip Advisor**: Specializes in planning trips, suggesting itineraries, and providing travel advice.
    - For a custom role (e.g., "Fitness Trainer"), enter a name and description (e.g., "You are a fitness trainer skilled in creating workout plans...").
    - Upload a file to provide data (optional). Supported formats: TXT, MD, CSV, JSON, PDF, DOCX, XLSX.
    - Use the 'Toggle Web Search' button above the input prompt, like the file uploader, to enable or disable DuckDuckGo web results for your prompt (optional).
    - Type your message in the input field below and press Enter to instruct the chatbot.
    - Use the "Copy" button to copy the assistant's response to your clipboard (works best in Chrome; may require permissions in Firefox).
    - This is an experimental chatbot interface. Responses may not always be accurate. Please use as a reference.
    """
)

# Disclaimer
st.warning(
    """
    **Disclaimer:** This chatbot is for testing purposes only. Do not share sensitive or personal information.
    The responses generated are AI-based and may not always be accurate or reliable. Please use as a reference.
    """
)

# Fetch available models
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
    available_models = ["Qwen/Qwen2.5-VL-32B-Instruct"]  # Fallback option

# Model selection
MODEL_NAME = st.selectbox("Select a model:", available_models)

# Predefined AI Roles
AI_ROLES = {
    "General Assistant": "You are a versatile assistant designed for general-purpose personal assistance, helping with a wide range of tasks and questions.",
    "Secretary": "You are a secretary assisting with drafting documents, proofreading, and managing text-based tasks.",
    "Programmer": "You are a programmer skilled in writing, debugging, and explaining code across various languages.",
    "Data Analyzer": "You are a data analyst proficient in extracting, analyzing, and interpreting data from various formats.",
    "Teacher": "You are a teacher tasked with preparing course materials, explaining concepts, and aiding in education.",
    "Trip Advisor": "You are a trip advisor specializing in planning trips, suggesting itineraries, and providing travel advice."
}

# AI Role selection with custom option, defaulting to "General Assistant"
role_option = st.selectbox(
    "Select AI Role or Choose Custom:",
    list(AI_ROLES.keys()) + ["Custom Role"],
    index=list(AI_ROLES.keys()).index("General Assistant")  # Set default to "General Assistant"
)

# Custom Role Input
custom_role_name = ""
custom_role_desc = ""
if role_option == "Custom Role":
    custom_role_name = st.text_input("Enter Custom Role Name (e.g., Fitness Trainer):", "")
    custom_role_desc = st.text_area(
        "Describe the Custom Role (e.g., 'You are a fitness trainer skilled in creating workout plans...'):",
        ""
    )
    SELECTED_ROLE = custom_role_name if custom_role_name else "Custom Role"
    SELECTED_ROLE_DESC = custom_role_desc if custom_role_desc else "You are a helpful assistant with a custom role."
else:
    SELECTED_ROLE = role_option
    SELECTED_ROLE_DESC = AI_ROLES[role_option]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None
if "enable_web_search" not in st.session_state:
    st.session_state.enable_web_search = False

# Display chat messages from history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Add copy button for assistant messages only
        if message["role"] == "assistant":
            # Use a hidden textarea and JavaScript for copying
            components.html(
                f"""
                <textarea id="copy-text-{i}" style="display:none;">{message['content'].replace('`', '\\`').replace('"', '"')}</textarea>
                <button onclick="copyToClipboard('copy-text-{i}')">Copy</button>
                <script>
                function copyToClipboard(elementId) {{
                    var text = document.getElementById(elementId).value;
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(text).then(
                            function() {{ console.log('Copy successful'); }},
                            function(err) {{ 
                                console.error('Clipboard API failed:', err);
                                fallbackCopy(text);
                            }}
                        );
                    }} else {{
                        fallbackCopy(text);
                    }}
                }}
                function fallbackCopy(text) {{
                    var tempInput = document.createElement('textarea');
                    tempInput.value = text;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    try {{
                        document.execCommand('copy');
                        console.log('Fallback copy successful');
                    }} catch (err) {{
                        console.error('Fallback copy failed:', err);
                        alert('Copy failed. Please copy manually.');
                    }}
                    document.body.removeChild(tempInput);
                }}
                </script>
                """,
                height=50
            )

# File upload with extended file types
uploaded_file = st.file_uploader(
    "Upload a file (optional)", 
    type=["txt", "md", "csv", "json", "pdf", "docx", "xlsx"]
)

# Web search toggle button above user input
if st.button("Toggle Web Search", help="Enable or disable DuckDuckGo web results for your prompt"):
    st.session_state.enable_web_search = not st.session_state.enable_web_search
st.write(f"Web Search: {'Enabled' if st.session_state.enable_web_search else 'Disabled'}")

# Function to extract content from different file types
def extract_file_content(file):
    file_extension = file.name.split(".")[-1].lower()
    try:
        if file_extension in ["txt", "md"]:
            return file.getvalue().decode("utf-8")
        elif file_extension == "csv":
            df = pd.read_csv(file)
            return df.to_string(index=False)
        elif file_extension == "json":
            return json.dumps(json.load(file))
        elif file_extension == "pdf":
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif file_extension == "docx":
            doc = Document(file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        elif file_extension == "xlsx":
            df = pd.read_excel(file)
            return df.to_string(index=False)
        else:
            return "Unsupported file format."
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Process uploaded file
if uploaded_file is not None:
    st.session_state.file_content = extract_file_content(uploaded_file)
    with st.expander("View Uploaded File Content"):
        st.text(st.session_state.file_content)

# User input field
user_input = st.chat_input("Type your message...")

if user_input:
    # Perform web search if enabled
    web_search_results = ""
    if st.session_state.enable_web_search:
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(user_input, max_results=3)]
                if results:
                    web_search_results = "\n\n[Web Search Results]:\n"
                    for i, result in enumerate(results, 1):
                        web_search_results += (
                            f"{i}. {result['title']}\n"
                            f"   {result['body']}\n"
                            f"   Source: {result['href']}\n"
                        )
                else:
                    web_search_results = "\n\n[Web Search Results]: No relevant results found."
        except Exception as e:
            web_search_results = f"\n\n[Web Search Results]: Error performing web search: {str(e)}"

    # Prepare the full user message
    full_user_message = user_input
    if st.session_state.file_content:
        full_user_message += (
            f"\n\n[Uploaded Data]:\n{st.session_state.file_content}\n"
            "Please use the uploaded data above to process my request."
        )
    if web_search_results:
        full_user_message += web_search_results
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": full_user_message})
    with st.chat_message("user"):
        st.markdown(full_user_message)
    
    # Prepare API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # System message with selected AI role
    system_prompt = (
        f"{SELECTED_ROLE_DESC} "
        "You are a helpful assistant. If the user provides uploaded data or web search results in their message, "
        "use them to answer their question or follow their instructions. "
        "Do not ask for additional data, links, or search results if they are already provided. "
        "If web search results are included, prioritize them for up-to-date information."
    )
    
    messages = [
        {"role": "system", "content": system_prompt}
    ] + st.session_state.messages
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }
    
    # Send request to API
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
        if st.session_state.file_content and ("please provide" in reply.lower() or "input data" in reply.lower() or "link" in reply.lower()):
            reply += (
                "\n\n**Note:** The uploaded data was provided in the message. "
                "Please use it to respond. If I misunderstood, clarify your request!"
            )
        if web_search_results and ("please provide" in reply.lower() or "search results" in reply.lower() or "web information" in reply.lower()):
            reply += (
                "\n\n**Note:** Web search results were provided in the message. "
                "Please use them to respond. If I misunderstood, clarify your request!"
            )
    else:
        reply = f"Error: {response.status_code} - {response.text}"
    
    # Add assistant message to session state
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    with st.chat_message("assistant"):
        st.markdown(reply)
        # Add copy button for the new assistant message
        components.html(
            f"""
            <textarea id="copy-text-latest" style="display:none;">{reply.replace('`', '\\`').replace('"', '"')}</textarea>
            <button onclick="copyToClipboard('copy-text-latest')">Copy</button>
            <script>
            function copyToClipboard(elementId) {{
                var text = document.getElementById(elementId).value;
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(text).then(
                        function() {{ console.log('Copy successful'); }},
                        function(err) {{ 
                            console.error('Clipboard API failed:', err);
                            fallbackCopy(text);
                        }}
                    );
                }} else {{
                    fallbackCopy(text);
                }}
            }}
            function fallbackCopy(text) {{
                var tempInput = document.createElement('textarea');
                tempInput.value = text;
                document.body.appendChild(tempInput);
                tempInput.select();
                try {{
                    document.execCommand('copy');
                    console.log('Fallback copy successful');
                }} catch (err) {{
                    console.error('Fallback copy failed:', err);
                    alert('Copy failed. Please copy manually.');
                }}
                document.body.removeChild(tempInput);
            }}
            </script>
            """,
            height=50
        )

