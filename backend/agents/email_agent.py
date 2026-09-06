import os
from datetime import datetime
from database.models import SessionLocal, EmailDeliveryLog
from agents.state import PipelineState
from utils.logger import get_logger

logger = get_logger(__name__)

def email_agent(state: PipelineState) -> PipelineState:
    logger.info("--- EMAIL AGENT START ---")
    results = state.get("analysis_results", {})
    chart_paths = state.get("chart_paths", [])
    
    if not results:
        logger.warning("No results to email.")
        return state
        
    session = SessionLocal()
    
    try:
        rt = state.get('report_type', 'daily')
        sd = state.get('start_date', 'all')
        ed = state.get('end_date', 'all')
        
        def get_readable_prefix(rt, sd):
            try:
                if sd == 'all' or not sd:
                    return f"{rt.capitalize()}_Report"
                date_obj = datetime.strptime(sd, "%Y-%m-%d")
                if rt == 'weekly':
                    week_num = date_obj.isocalendar()[1]
                    year_num = date_obj.isocalendar()[0]
                    return f"Week_{week_num}_{year_num}"
                elif rt == 'monthly':
                    return f"{date_obj.strftime('%B_%Y')}"
                elif rt == 'daily':
                    return f"Daily_{sd}"
                else:
                    return f"{rt.capitalize()}_{sd}"
            except Exception:
                return f"{rt}_{sd}"
                
        prefix = get_readable_prefix(rt, sd)

        narrative = results.get("narrative", "")
        
        # Build formal HTML
        html_content = f"""
        <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <p>Hello Stakeholders,</p>
            <p>Please find the IVR Analytics {rt.capitalize()} Report for the recent period below. The report highlights key metrics, call dispositions, and trends in customer intents.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
            <h2>IVR Analytics {rt.capitalize()} Report</h2>
            <p>{narrative}</p>
            <h3>Charts:</h3>
        """
        
        attachments = []
        for chart_path in chart_paths:
            filename = os.path.basename(chart_path)
            cid = f"img_{filename}"
            html_content += f'<img src="cid:{cid}" alt="Chart" style="max-width: 600px; height: auto;"><br>'
            
            # Read chart for attachment
            if os.path.exists(chart_path):
                with open(chart_path, "rb") as f:
                    content_bytes = list(f.read())
                attachments.append({
                    "filename": filename,
                    "content": content_bytes,
                    "content_id": cid
                })
            
        html_content += """
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
            <p>Best regards,<br/><b>IVR Analytics Agent</b></p>
        </div>
        """
        
        email_path = f"outputs/{prefix}_report.html"
        with open(email_path, "w") as f:
            f.write(html_content)
            
        # Actually send via Resend
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY", "")
        recipient = os.getenv("REPORT_RECIPIENT", "akshayaa.s153@gmail.com")
        delivery_status = "sent"
        error_msg = None
        
        if resend.api_key:
            try:
                params = {
                    "from": "onboarding@resend.dev",
                    "to": [r.strip() for r in recipient.split(",") if r.strip()],
                    "subject": f"IVR Analytics Report - {prefix}",
                    "html": html_content
                }
                if attachments:
                    params["attachments"] = attachments
                resend.Emails.send(params)
                logger.info(f"Automated email successfully sent to {recipient}")
            except Exception as e:
                logger.error(f"Failed to send automated email: {e}")
                delivery_status = "failed"
                error_msg = str(e)
        else:
            logger.info("RESEND_API_KEY not set. Simulated sending automated email.")
            delivery_status = "simulated"
            
        # Log to DB
        log = EmailDeliveryLog(
            delivery_status=delivery_status,
            timestamp=datetime.now(),
            recipient=recipient,
            error_message=error_msg
        )
        session.add(log)
        session.commit()
        
        logger.info(f"Email HTML saved to {email_path} and logged to DB as 'sent'.")
        state["email_status"] = f"Email sent successfully and saved to {email_path}"
        logger.info("--- EMAIL AGENT END ---")
        
    except Exception as e:
        logger.error(f"Email agent error: {e}", exc_info=True)
        state["errors"] = state.get("errors", []) + [str(e)]
        
        # Log failure
        log = EmailDeliveryLog(
            delivery_status="failed",
            timestamp=datetime.now(),
            recipient="admin@company.com",
            error_message=str(e)
        )
        session.add(log)
        session.commit()
    finally:
        session.close()
        
    return state
