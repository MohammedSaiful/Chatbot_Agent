# LangGraph AI Agent with PostgreSQL Memory

An intelligent, stateful chatbot built using **LangGraph**, **FastAPI**, and **Streamlit**. This agent uses a **ReAct (Reasoning + Acting)** logic flow to answer queries, search the web via Tavily, and maintain long-term conversation history in a **Supabase (PostgreSQL)** database using connection pooling.



##  Features
* **Dual LLM Support:** Switch between **Groq** (Llama 3) and **OpenAI** (GPT-4o) on the fly.
* **Persistent Memory:** Conversations are saved in a PostgreSQL database and reloaded automatically.
* **Web Search:** Integrated with **Tavily Search** for real-time information retrieval.
* **Efficient Database Handling:** Uses `psycopg2` connection pooling to handle multiple requests without lag.
* **Modern UI:** Clean and interactive interface built with Streamlit.

---

##  Project Structure
* `ai_agent.py`: The core logic. Defines the LangGraph agent, tools, and database helper functions.
* `Backend.py`: A FastAPI server that acts as the bridge between the UI and the AI logic.
* `Frontend.py`: The Streamlit web application for the user interface.
* `.env`: (Not included in repo) Contains API keys and Database URL.

---
## Usage
Step 1: Start the Backend
* python Backend.py
The API will start running at http://127.0.0.1:9999.

Step 2: Start the Frontend
Open a new terminal and run:
* streamlit run Frontend.py

## How Works
1. Request: The Frontend sends a JSON payload to the FastAPI /chat endpoint.
2. Memory: The Agent fetches past messages from PostgreSQL for the specific user_id.
3. Thought: The LLM decides if it needs to search the web based on the user's query.
4.  Action: If needed, the Tavily tool is triggered.
5. Response & Save: The final answer is sent to the user and both user/assistant messages are saved to the DB.