
# Library Imports 
import os
from dotenv import load_dotenv

# psycopg2 is the PostgreSQL adapter for Python
import psycopg2
# Import the pooling utility to manage multiple database connections
from psycopg2 import pool  

# LangChain and LangGraph components for AI logic
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage, HumanMessage

# Load variables from the .env file into the environment
load_dotenv()

#  Configuration & API Keys 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

#  Database Connection Pool Setup 
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize a ConnectionPool to maintain open connections.
# This prevents the overhead of creating a new connection for every single message.
# minconn=1: Keep at least one connection open at all times.
# maxconn=10: Allow up to 10 simultaneous connections.
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10, DATABASE_URL, sslmode='require'
)

# Database Helper Functions 

def save_message(user_id, role, content):
    """
    Saves a single chat message (user or assistant) into the PostgreSQL database.
    """
    # Request a connection from the pool
    conn = db_pool.getconn() 
    try:
        cur = conn.cursor()
        # SQL query
        cur.execute(
            "INSERT INTO chatbotagent (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content),
        )
        # Commit to save permanent
        conn.commit()
        cur.close()
    finally:
        # return the connection to the pool, even if the query fails
        db_pool.putconn(conn)


def load_chat_history(user_id="user"):
    """
    Retrieves all past messages for a specific user and converts them 
    into LangChain message objects (HumanMessage or AIMessage).
    """
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        # Fetch messages oldest to newest
        cur.execute(
            "SELECT role, content FROM chatbotagent WHERE user_id = %s ORDER BY created_at ASC",
            (user_id,),
        )
        rows = cur.fetchall()
        cur.close()
        
        chat_history = []
        for role, content in rows:
            # Reconstruct the specific message objects required by the AI model
            if role == "user":
                chat_history.append(HumanMessage(content=content))
            elif role == "assistant":
                chat_history.append(AIMessage(content=content))
        return chat_history
    finally:
        # Return the connection to the pool for next request
        db_pool.putconn(conn)

# Main AI Agent Logic

def get_response_from_ai_agent(llm_id, provider, query, allow_search, user_id="user"):
    """
    Coordinates the full chat flow:
    1. Loads history from DB
    2. Updates history with the new user query
    3. Triggers the AI model (and optional search tools)
    4. Saves the AI's response back to the DB
    """
    
    # Load previous messages from database
    chat_history = load_chat_history(user_id)

    # Add current user queries to the history and save them to the DB
    for q in query:
        chat_history.append(HumanMessage(content=q))
        save_message(user_id, "user", q)

    #  Select the LLM provider based on the backend request
    if provider == "Groq":
        llm = ChatGroq(model=llm_id)
    elif provider == "OpenAI":
        llm = ChatOpenAI(model=llm_id)
    else:
        raise ValueError("Provider must be 'Groq' or 'OpenAI'")

    # web search tool
    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    #  ReAct Agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
    )

    # Run agent with combined history (Memory + New Query)
    state = {"messages": chat_history}
    response = agent.invoke(state)

    #  Parse the response to find the latest assistant message
    messages = response.get("messages", [])
    ai_messages = [m.content for m in messages if isinstance(m, AIMessage)]
    final_answer = ai_messages[-1] if ai_messages else "I'm sorry, I couldn't process that."

    # save AI's reply to the database for future context
    save_message(user_id, "assistant", final_answer)
    
    return final_answer