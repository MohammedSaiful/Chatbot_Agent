
# Library Imports 
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file immediately
load_dotenv()

import os
import psycopg2
from psycopg2 import pool 

# FastAPI framework for creating the API endpoints
from fastapi import FastAPI
from ai_agent import get_response_from_ai_agent

#  Database Connection Pool Setup 
DATABASE_URL = os.getenv("DATABASE_URL")


db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 5, DATABASE_URL, sslmode='require'
)

def save_message(user_id, role, content):
    """
    Manually saves a message to the database if needed at the API level.
    Uses the pool to get and return a connection safely.
    """
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chatbotagent (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content),
        )
        conn.commit()
        cur.close()
    finally:
        # Return connection back to the pool to avoid "leaks"
        db_pool.putconn(conn)

#  Request Schema (Data Validation) =====
class RequestState(BaseModel):
    """
    Defines the expected structure of the incoming JSON request.
    Pydantic will automatically validate types (e.g., ensuring allow_search is a boolean).
    """
    model_name: str
    model_provider: str
    messages: List[str]
    allow_search: bool

#  FastAPI App Configuration 
MODEL_NAMES = [
    "lama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
    "gpt-4o-mini",
]

# FastAPI application
app = FastAPI(title="LangGraph AI Agent")

# API Endpoints 

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    Main endpoint for the chatbot.
    Receives user messages, validates the model, and calls the AI agent logic.
    """
    # Validate that the requested model is supported
    if request.model_name not in MODEL_NAMES:
        return {"error": f"Invalid model name: {request.model_name}"}

    # Extract data from the validated request object
    llm_id = request.model_name
    query = request.messages
    allow_search = request.allow_search
    provider = request.model_provider

    # Placeholder for user identification (can be expanded for multi-user support)
    user_id = "user" 

    try:
        # Forward the request to the agent logic in ai_agent.py
        response = get_response_from_ai_agent(
            llm_id, provider, query, allow_search, user_id=user_id
        )
    except Exception as e:
        # Catch any errors (API failures, DB issues, etc.) and return as JSON
        return {"error": str(e)}

    # Return the final AI response to the client
    return {"response": response}

#  Server Execution 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)