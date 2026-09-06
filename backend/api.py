from asyncio import selector_events
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time

from main import build_pipeline

app = FastAPI(title="IVR Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

def run_daily_report():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Triggering scheduled daily report for {yesterday}")
    try:
        pipeline = build_pipeline()
        initial_state = {
            "files_processed": [],
            "analysis_results": {},
            "chart_paths": [],
            "email_status": "",
            "errors": [],
            "start_date": yesterday,
            "end_date": yesterday,
            "report_type": "daily"
        }
        pipeline.invoke(initial_state)
    except Exception as e:
        print(f"Scheduled pipeline error: {e}")

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Trigger at 6:00 AM every day
    scheduler.add_job(run_daily_report, CronTrigger(hour=6, minute=0))
    scheduler.start()
    print("Background scheduler started. Daily report set for 6:00 AM.")

# Ensure outputs directory exists
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "time": time.time()}

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PipelineRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    report_type: Optional[str] = 'daily'

class ChatRequest(BaseModel):
    query: str

@app.post("/api/run-pipeline")
def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    def run(req: PipelineRequest):
        try:
            pipeline = build_pipeline()
            initial_state = {
                "files_processed": [],
                "analysis_results": {},
                "chart_paths": [],
                "email_status": "",
                "errors": [],
                "start_date": req.start_date or "",
                "end_date": req.end_date or "",
                "report_type": req.report_type or "daily"
            }
            pipeline.invoke(initial_state)
        except Exception as e:
            print(f"Pipeline error: {e}")

    background_tasks.add_task(run, request)
    return {"status": "Pipeline triggered successfully"}

class EmailRequest(BaseModel):
    email: str
    subject: Optional[str] = None
    content: Optional[str] = None

@app.post("/api/send-email")
def send_email(request: EmailRequest):
    import resend
    
    # Try to read Resend API key from environment
    resend.api_key = os.getenv("RESEND_API_KEY", "")
    
    if not resend.api_key:
        return {"status": f"Simulated: Email to {request.email} logged. Add RESEND_API_KEY to .env to send real emails."}
        
    body_content = request.content if request.content else "This is an automated report from the IVR Analytics platform."
    subject = request.subject if request.subject else "IVR Analytics Report"
    
    import re
    
    attachments = []
    
    # Find all <img src="filename.png"> and embed them using CID so Gmail renders them inline
    def embed_image(match):
        src = match.group(1)
        filename = os.path.basename(src)
        filepath = os.path.join("outputs", filename)
        
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                content_bytes = list(f.read())
            
            # Create a unique CID for this image
            cid = f"img_{filename}"
            
            attachments.append({
                "filename": filename,
                "content": content_bytes,
                "content_id": cid
            })
            return f'<img src="cid:{cid}" alt="Chart" style="max-width: 600px; height: auto;">'
            
        return '' # if file not found, remove the img tag
        
    body_content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', embed_image, body_content)
            
    try:
        # Support multiple comma-separated emails
        to_emails = [e.strip() for e in request.email.split(",") if e.strip()]
        
        params = {
            "from": "onboarding@resend.dev",
            "to": to_emails,
            "subject": subject,
            "html" if "<" in body_content and ">" in body_content else "text": body_content,
        }
        if attachments:
            params["attachments"] = attachments
            
        email_res = resend.Emails.send(params)
        return {"status": f"Email successfully sent to {request.email}."}
    except Exception as e:
        return {"error": f"Failed to send email via Resend: {e}"}

from fastapi.responses import FileResponse

@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("outputs", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}

@app.get("/api/reports")
def get_reports():
    reports = []
    if os.path.exists("outputs"):
        for file in os.listdir("outputs"):
            if file.endswith(".html") or file.endswith(".png"):
                reports.append({
                    "name": file,
                    "url": f"http://localhost:8000/outputs/{file}",
                    "type": "image" if file.endswith(".png") else "document"
                })
    return {"reports": reports}

from database.models import SessionLocal, CallRecord
from sqlalchemy import func

@app.get("/api/records")
def get_records(start_date: Optional[str] = None, end_date: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(CallRecord)
        if start_date:
            query = query.filter(CallRecord.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(CallRecord.timestamp <= datetime.fromisoformat(end_date + 'T23:59:59' if len(end_date) == 10 else end_date))
            
        records = query.order_by(CallRecord.timestamp.desc()).limit(100).all()
        return {"records": [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "duration": r.duration,
                "disposition": r.disposition,
                "intent": r.intent,
                "confidence": r.confidence,
                "fallback_count": r.fallback_count
            } for r in records
        ]}
    finally:
        session.close()

@app.get("/api/analytics")
def get_analytics(start_date: Optional[str] = None, end_date: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(CallRecord)
        if start_date:
            query = query.filter(CallRecord.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(CallRecord.timestamp <= datetime.fromisoformat(end_date + 'T23:59:59' if len(end_date) == 10 else end_date))
            
        total_calls = query.count()
        if total_calls == 0:
            return {"total_calls": 0, "avg_duration": 0, "containment_rate": 0, "abandonment_rate": 0, "intent_distribution": []}
            
        avg_duration = session.query(func.avg(CallRecord.duration)).filter(CallRecord.id.in_(query.with_entities(CallRecord.id))).scalar() or 0
        resolved_calls = query.filter(CallRecord.disposition == 'resolved').count()
        abandoned_calls = query.filter(CallRecord.disposition == 'abandoned').count()
        
        containment_rate = (resolved_calls / total_calls) * 100
        abandonment_rate = (abandoned_calls / total_calls) * 100
        
        # Intents breakdown
        intents = session.query(CallRecord.intent, func.count(CallRecord.id)).filter(CallRecord.id.in_(query.with_entities(CallRecord.id))).group_by(CallRecord.intent).all()
        intent_data = [{"name": i[0], "value": i[1]} for i in intents]
        
        return {
            "total_calls": total_calls,
            "avg_duration": round(avg_duration, 1),
            "containment_rate": round(containment_rate, 1),
            "abandonment_rate": round(abandonment_rate, 1),
            "intent_distribution": intent_data
        }
    finally:
        session.close()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
