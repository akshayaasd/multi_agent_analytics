import os
import pandas as pd
import json
from datetime import datetime
from database.models import SessionLocal, CallRecord
from agents.state import PipelineState
from utils.logger import get_logger

logger = get_logger(__name__)

def simulate_llm_extraction(data):
    """
    In a production system, this function would send the 'events' transcript to an LLM 
    (like LangChain + OpenAI) to extract the intent and confidence.
    Here we simulate it using heuristics.
    """
    transcript = " ".join([event["text"].lower() for event in data.get("events", [])])
    
    intent = "unknown"
    if "lost my credit card" in transcript or "stolen" in transcript:
        intent = "report_lost_card"
    elif "move" in transcript or "transfer" in transcript:
        intent = "transfer_funds"
    elif "balance" in transcript or "how much money" in transcript:
        intent = "balance_inquiry"
    elif "mortgage" in transcript:
        intent = "mortgage_inquiry"
        
    fallback_count = transcript.count("didn't quite get that") + transcript.count("trouble understanding")
    
    start = datetime.fromisoformat(data["start_time"].replace('Z', '+00:00'))
    end = datetime.fromisoformat(data["end_time"].replace('Z', '+00:00'))
    duration = (end - start).total_seconds()
    
    routing = data.get("routing", {})
    disposition = "resolved"
    if routing.get("transferred_to_agent"):
        disposition = "transferred"
    elif routing.get("final_disposition") == "hangup_by_user" and fallback_count > 0:
        disposition = "abandoned"
        
    return {
        "id": data["call_id"],
        "timestamp": start.replace(tzinfo=None),
        "duration": duration,
        "disposition": disposition,
        "intent": intent,
        "confidence": 0.85, # Simulated confidence
        "fallback_count": fallback_count
    }

def table_agent(state: PipelineState) -> PipelineState:
    logger.info("--- TABLE AGENT START ---")
    mock_s3_path = "mock_s3"
    processed_files = state.get("files_processed", [])
    
    session = SessionLocal()
    new_files = []
    
    try:
        if not os.path.exists(mock_s3_path):
            logger.warning(f"Mock S3 path '{mock_s3_path}' does not exist.")
            return state

        for filename in os.listdir(mock_s3_path):
            if filename not in processed_files:
                filepath = os.path.join(mock_s3_path, filename)
                
                # Process CSV
                if filename.endswith(".csv"):
                    logger.info(f"Processing CSV file: {filename}")
                    df = pd.read_csv(filepath)
                    df = df.drop_duplicates(subset=['call_id'])
                    
                    added_count = 0
                    for _, row in df.iterrows():
                        exists = session.query(CallRecord).filter_by(id=row['call_id']).first()
                        if not exists:
                            timestamp = datetime.fromisoformat(row['timestamp'])
                            record = CallRecord(
                                id=row['call_id'], timestamp=timestamp, duration=float(row['duration']),
                                disposition=row['disposition'], intent=row['intent'],
                                confidence=float(row['confidence']), fallback_count=int(row['fallback_count'])
                            )
                            session.add(record)
                            added_count += 1
                    session.commit()
                    logger.info(f"Added {added_count} new records from CSV {filename}")
                    new_files.append(filename)

                # Process JSON Transcripts
                elif filename.endswith(".json"):
                    logger.info(f"Processing JSON transcript file: {filename}")
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    # 1. "LLM" Extraction Phase
                    extracted_row = simulate_llm_extraction(data)
                    
                    # 2. Database Insertion Phase
                    exists = session.query(CallRecord).filter_by(id=extracted_row['id']).first()
                    if not exists:
                        record = CallRecord(**extracted_row)
                        session.add(record)
                        session.commit()
                        logger.info(f"Successfully extracted and saved record for {extracted_row['id']}")
                    new_files.append(filename)
                
        state["files_processed"] = processed_files + new_files
        logger.info(f"--- TABLE AGENT END (Processed {len(new_files)} new files) ---")
    except Exception as e:
        logger.error(f"Table agent error: {e}", exc_info=True)
        state["errors"] = state.get("errors", []) + [str(e)]
    finally:
        session.close()
        
    return state
