#ai_agent.py file

import os
from dotenv import load_dotenv
load_dotenv()  # this loads the .env file

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY=os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")


#LLM AND tools

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

openai_llm=ChatOpenAI(model="gpt-4o-min")
groq_llm=ChatGroq(model="llama-3.3-70b-versatile")

#search_tool =TavilySearchResults(max_results=2, tavily_api_key=TAVILY_API_KEY)


#setup ai agent 


from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage

system_promt="Act as an AI chatbot who is smart and friendly"

def get_response_from_ai_agent(llm_id, provider, query, allow_search ):
    if provider =="Groq":
        llm=ChatGroq(model=llm_id)
    if provider =="OpenAI":
        llm=ChatOpenAI(model=llm_id)

    tools=[TavilySearchResults(max_results=2)] if allow_search else []
    agent=create_react_agent(
        model=llm,
        tools=tools,
        #state_modifier= system_promt
    )

    #query ="Tell me about the trends job market"
    state={"messages":query}
    response=agent.invoke(state)
    #print(response)  
    messages=response.get("messages")
    ai_messages=[message.content for message in messages if isinstance(message, AIMessage)]
    return ai_messages[-1]

