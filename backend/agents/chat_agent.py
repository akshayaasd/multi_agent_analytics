import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from utils.logger import get_logger

logger = get_logger(__name__)

def ask_database(query: str) -> str:
    logger.info(f"Chat Agent querying DB with: {query}")
    try:
        from database.models import DATABASE_URL
        db = SQLDatabase.from_uri(DATABASE_URL)
        
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        else:
            from langchain_community.chat_models import ChatOllama
            llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), temperature=0)
            
        agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools" if provider == "openai" else "zero-shot-react-description", verbose=True)
        response = agent_executor.invoke({"input": query})
        return response.get("output", "Sorry, I couldn't process your request.")
    except Exception as e:
        logger.error(f"Chat Agent error: {e}")
        return f"An error occurred while answering your query: {str(e)}"
