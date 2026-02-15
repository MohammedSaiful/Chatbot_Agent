
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import requests

#  Streamlit 
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("Chatbot Agent")

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

# Provider selection
provider = st.radio("Select Provider:", ("Groq", "OpenAI"))
if provider == "Groq":
    selected_model = st.selectbox("Select Groq:", MODEL_NAMES_GROQ)
else:
    selected_model = st.selectbox("Select OpenAI:", MODEL_NAMES_OPENAI)

# Web search option
allow_web_search = st.checkbox("Allow Web Search")

# User input
user_query = st.text_area("Write your thoughts", height=150, placeholder="Ask Me Anything!")

API_URL = "http://127.0.0.1:9999/chat"

#  Button to get AI response 
if st.button("Answer"):
    if not user_query.strip():
        st.warning("Please type a question or message!")
    else:
        payload = {
            "model_name": selected_model,
            "model_provider": provider,
            "messages": [user_query],
            "allow_search": allow_web_search
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data:
                    st.error(response_data["error"])
                else:
                    st.subheader("Agent Response")
                    st.markdown(f"**Response:** {response_data['response']}")
            else:
                st.error(f"Server returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to backend: {e}")
