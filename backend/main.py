from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from agents.state import PipelineState
from agents.table_agent import table_agent
from agents.analysis_agent import analysis_agent
from agents.viz_agent import viz_agent
from agents.email_agent import email_agent
import time
from utils.logger import get_logger

logger = get_logger(__name__)

def build_pipeline():
    workflow = StateGraph(PipelineState)
    
    # Add nodes
    workflow.add_node("table_agent", table_agent)
    workflow.add_node("analysis_agent", analysis_agent)
    workflow.add_node("viz_agent", viz_agent)
    workflow.add_node("email_agent", email_agent)
    
    # Define edges (linear pipeline as per diagram)
    workflow.set_entry_point("table_agent")
    workflow.add_edge("table_agent", "analysis_agent")
    workflow.add_edge("analysis_agent", "viz_agent")
    workflow.add_edge("viz_agent", "email_agent")
    workflow.add_edge("email_agent", END)
    
    return workflow.compile()

if __name__ == "__main__":
    logger.info("Initializing Multi-Agent IVR Analytics Pipeline...")
    
    # Initial state
    initial_state = {
        "files_processed": [],
        "analysis_results": {},
        "chart_paths": [],
        "email_status": "",
        "errors": []
    }
    
    pipeline = build_pipeline()
    
    # Run the pipeline
    start_time = time.time()
    final_state = pipeline.invoke(initial_state)
    end_time = time.time()
    
    logger.info("--- Pipeline Execution Complete ---")
    logger.info(f"Time taken: {end_time - start_time:.2f} seconds")
    logger.info(f"Processed files: {final_state.get('files_processed')}")
    logger.info(f"Email status: {final_state.get('email_status')}")
    if final_state.get("errors"):
        logger.error(f"Errors encountered: {final_state.get('errors')}")

