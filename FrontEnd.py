#FrontEnd.py

from dotenv import load_dotenv
load_dotenv()


#Setup UI with streamlit
import streamlit as st

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("Chatbot Agent")

#system_prompt=st.text_area("Define The Search Field: ", height=70, 
 #                          placeholder="Type your system prompt here...")

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider=st.radio("Select Provider:", ("Groq", "OpenAI"))

if provider == "Groq":
    selected_model = st.selectbox("Select Groq:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.selectbox("Select OpenAI:", MODEL_NAMES_OPENAI)

allow_web_search=st.checkbox("Allow Web Search")

user_query=st.text_area("Write your thoughts", height=150, placeholder="Ask Me Anything!")

API_URL="http://127.0.0.1:9999/chat"

if st.button("Answer"):
    if user_query.strip():

# Connect with backend by URL
        import requests

        payload={
            "model_name": selected_model,
            "model_provider": provider,
            "messages": [user_query],
            "allow_search": allow_web_search
        }

        response=requests.post(API_URL, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            if "error" in response_data:
                st.error(response_data["error"])
            else:
                st.subheader("Agent Response")
                st.markdown(f"**Response:** {response_data}")