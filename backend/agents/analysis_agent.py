import pandas as pd
from database.models import SessionLocal, CallRecord
from agents.state import PipelineState
from sqlalchemy import select
from utils.logger import get_logger

logger = get_logger(__name__)

def analysis_agent(state: PipelineState) -> PipelineState:
    logger.info("--- ANALYSIS AGENT START ---")
    session = SessionLocal()
    
    try:
        start_date_str = state.get("start_date")
        end_date_str = state.get("end_date")
        
        # Query all records
        query = select(CallRecord)
        if start_date_str:
            from datetime import datetime
            query = query.filter(CallRecord.timestamp >= datetime.fromisoformat(start_date_str))
        if end_date_str:
            from datetime import datetime
            query = query.filter(CallRecord.timestamp <= datetime.fromisoformat(end_date_str + 'T23:59:59' if len(end_date_str) == 10 else end_date_str))
            
        logger.info(f"EXECUTING QUERY: {query}")
        df = pd.read_sql(query, session.bind)
        
        if df.empty:
            logger.warning("No data available for analysis.")
            metrics = {
                "call_volume": 0,
                "avg_handle_time": 0,
                "containment_rate": 0,
                "fallback_rate": 0,
                "abandonment_rate": 0,
                "top_intents": []
            }
            state["analysis_results"] = {
                "call_volume": 0,
                "avg_handle_time": 0,
                "containment_rate": 0,
                "fallback_rate": 0,
                "abandonment_rate": 0,
                "top_intents": [],
                "narrative": "No data available for this period.",
                "raw_data_summary": []
            }
            return state
            
        # Summary numbers
        call_volume = len(df)
        avg_handle_time = df['duration'].mean()
        
        resolved_calls = len(df[df['disposition'] == 'resolved'])
        containment_rate = (resolved_calls / call_volume) * 100 if call_volume > 0 else 0
        
        fallback_calls = len(df[df['fallback_count'] > 0])
        fallback_rate = (fallback_calls / call_volume) * 100 if call_volume > 0 else 0
        
        abandoned_calls = len(df[df['disposition'] == 'abandoned'])
        abandonment_rate = (abandoned_calls / call_volume) * 100 if call_volume > 0 else 0
        
        top_intents = df['intent'].value_counts().head(3).to_dict()
        
        logger.debug(f"Computed metrics for {call_volume} calls. Containment: {containment_rate:.1f}%, Fallback: {fallback_rate:.1f}%")
        
        metrics = {
            "call_volume": call_volume,
            "avg_handle_time": avg_handle_time,
            "containment_rate": containment_rate,
            "fallback_rate": fallback_rate,
            "abandonment_rate": abandonment_rate,
            "top_intents": list(top_intents.keys())
        }
        
        import os
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        try:
            prompt = f"Write a detailed, comprehensive executive report for these IVR call center metrics: {metrics}. Include sections for Executive Summary, Key Insights, and Recommendations. Do not include a preamble."
            
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
                narrative = llm.invoke(prompt).content
            else:
                try:
                    from langchain_ollama import ChatOllama
                    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), temperature=0)
                    narrative = llm.invoke(prompt).content
                except Exception as ollama_err:
                    try:
                        from langchain_community.chat_models import ChatOllama
                        llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), temperature=0)
                        narrative = llm.invoke(prompt).content
                    except Exception:
                        raise ollama_err
                
            # Convert basic markdown to HTML since email_agent just puts it in <p> tags,
            import re
            narrative = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', narrative)
            narrative = narrative.replace('\n', '<br>')
                
        except Exception as e:
            logger.error(f"LLM narrative generation failed ({provider}): {e}")
            # Fallback narrative
            narrative = (
                f"<b>Executive Summary:</b><br>"
                f"Analysis of {call_volume} calls shows an average handle time of {avg_handle_time:.1f} seconds. "
                f"The containment rate is {containment_rate:.1f}% with an abandonment rate of {abandonment_rate:.1f}%.<br><br>"
                f"<b>Key Insights:</b><br>"
                f"- Fallback rate to human agents is {fallback_rate:.1f}%.<br>"
                f"- The top intents driving traffic are: {', '.join(top_intents.keys())}.<br><br>"
                f"<b>Recommendations:</b><br>"
                f"- Investigate the high fallback rate for complex intents.<br>"
                f"- Optimize the IVR flow for {list(top_intents.keys())[0] if top_intents else 'the most common issues'} to improve containment."
            )
        
        state["analysis_results"] = {
            "call_volume": call_volume,
            "avg_handle_time": avg_handle_time,
            "containment_rate": containment_rate,
            "fallback_rate": fallback_rate,
            "abandonment_rate": abandonment_rate,
            "top_intents": top_intents,
            "narrative": narrative,
            "raw_data_summary": df[['intent', 'duration', 'fallback_count', 'disposition']].to_dict(orient='records') # Simplified for viz
        }
        logger.info("--- ANALYSIS AGENT END ---")
        
    except Exception as e:
        logger.error(f"Analysis agent error: {e}", exc_info=True)
        state["errors"] = state.get("errors", []) + [str(e)]
    finally:
        session.close()
        
    return state
