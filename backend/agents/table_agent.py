import os
import pandas as pd
import json
import uuid
from datetime import datetime
from database.models import SessionLocal, CallRecord
from agents.state import PipelineState
from utils.logger import get_logger

logger = get_logger(__name__)

def resolve_mock_s3_path() -> str:
    """Finds the absolute path for mock_s3 directory across various execution contexts."""
    possible_paths = [
        "mock_s3",
        "backend/mock_s3",
        os.path.join(os.path.dirname(__file__), "..", "mock_s3"),
        os.path.join(os.path.dirname(__file__), "..", "..", "backend", "mock_s3")
    ]
    for p in possible_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p) and os.path.isdir(abs_p):
            return abs_p
    return os.path.abspath("mock_s3")

def parse_iso_datetime(dt_val) -> datetime:
    """Safely converts ISO datetime string or object into timezone-naive datetime."""
    if not dt_val:
        return datetime.now()
    if isinstance(dt_val, datetime):
        return dt_val.replace(tzinfo=None)
    dt_str = str(dt_val).replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.replace(tzinfo=None)
    except Exception:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(dt_str[:19], fmt)
            except Exception:
                pass
        return datetime.now()

def simulate_llm_extraction(data: dict) -> dict:
    """
    Ingests a raw JSON call log transcript and converts it into a structured
    dictionary matching the CallRecord database schema.
    """
    call_id = data.get("call_id") or data.get("id") or str(uuid.uuid4())
    
    events = data.get("events", [])
    if isinstance(events, list):
        transcript_texts = [
            event.get("text", "").lower()
            for event in events
            if isinstance(event, dict) and "text" in event
        ]
        transcript = " ".join(transcript_texts)
    else:
        transcript = str(events).lower()
    
    intent = data.get("intent")
    if not intent or intent == "unknown":
        if "lost my credit card" in transcript or "stolen" in transcript or "freeze" in transcript:
            intent = "report_lost_card"
        elif "move" in transcript or "transfer" in transcript:
            intent = "transfer_funds"
        elif "balance" in transcript or "how much money" in transcript:
            intent = "balance_inquiry"
        elif "mortgage" in transcript or "escrow" in transcript:
            intent = "mortgage_inquiry"
        else:
            intent = "general_inquiry"
            
    fallback_count = data.get("fallback_count")
    if fallback_count is None:
        fallback_count = transcript.count("didn't quite get that") + transcript.count("trouble understanding") + transcript.count("sorry")
    
    start_str = data.get("start_time") or data.get("timestamp")
    start = parse_iso_datetime(start_str) if start_str else datetime.now()
    
    duration = data.get("duration")
    if duration is None:
        end_str = data.get("end_time")
        if end_str:
            end = parse_iso_datetime(end_str)
            duration = max(0.0, (end - start).total_seconds())
        else:
            duration = 60.0
    else:
        duration = float(duration)
        
    routing = data.get("routing", {})
    if not isinstance(routing, dict):
        routing = {}
        
    disposition = data.get("disposition")
    if not disposition:
        if routing.get("transferred_to_agent") or routing.get("final_disposition") == "transferred":
            disposition = "transferred"
        elif routing.get("final_disposition") == "hangup_by_user" and fallback_count > 0:
            disposition = "abandoned"
        else:
            disposition = "resolved"
            
    confidence = float(data.get("confidence", 0.85))
    
    return {
        "id": str(call_id),
        "timestamp": start,
        "duration": duration,
        "disposition": disposition,
        "intent": intent,
        "confidence": confidence,
        "fallback_count": int(fallback_count)
    }

def table_agent(state: PipelineState) -> PipelineState:
    logger.info("--- TABLE AGENT START ---")
    mock_s3_path = resolve_mock_s3_path()
    processed_files = state.get("files_processed", [])
    
    session = SessionLocal()
    new_files = []
    
    try:
        if not os.path.exists(mock_s3_path):
            logger.warning(f"Mock S3 path '{mock_s3_path}' does not exist.")
            return state

        logger.info(f"Scanning mock S3 directory at: {mock_s3_path}")
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
                            timestamp = parse_iso_datetime(row['timestamp'])
                            record = CallRecord(
                                id=str(row['call_id']),
                                timestamp=timestamp,
                                duration=float(row['duration']),
                                disposition=str(row['disposition']),
                                intent=str(row['intent']),
                                confidence=float(row['confidence']),
                                fallback_count=int(row['fallback_count'])
                            )
                            session.add(record)
                            added_count += 1
                    session.commit()
                    logger.info(f"Added {added_count} new records from CSV {filename}")
                    new_files.append(filename)

                # Process JSON Transcripts / JSON Call logs into Table records
                elif filename.endswith(".json"):
                    logger.info(f"Processing JSON transcript file: {filename}")
                    with open(filepath, "r", encoding="utf-8") as f:
                        raw_content = json.load(f)
                    
                    # Handle single object or list of call objects
                    json_items = raw_content if isinstance(raw_content, list) else [raw_content]
                    
                    added_count = 0
                    for item in json_items:
                        if isinstance(item, dict):
                            extracted_row = simulate_llm_extraction(item)
                            exists = session.query(CallRecord).filter_by(id=extracted_row['id']).first()
                            if not exists:
                                record = CallRecord(**extracted_row)
                                session.add(record)
                                added_count += 1
                    
                    if added_count > 0:
                        session.commit()
                    logger.info(f"Successfully extracted and saved {added_count} table records from {filename}")
                    new_files.append(filename)
                
        state["files_processed"] = processed_files + new_files
        logger.info(f"--- TABLE AGENT END (Processed {len(new_files)} new files) ---")
    except Exception as e:
        logger.error(f"Table agent error: {e}", exc_info=True)
        state["errors"] = state.get("errors", []) + [str(e)]
    finally:
        session.close()
        
    return state

