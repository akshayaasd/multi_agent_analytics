import matplotlib
matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt
import seaborn as sns
from agents.state import PipelineState
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

def viz_agent(state: PipelineState) -> PipelineState:
    logger.info("--- VIZ AGENT START ---")
    results = state.get("analysis_results", {})
    if not results:
        logger.warning("No analysis results to visualize.")
        return state
        
    try:
        # Create output dir if not exists
        os.makedirs("outputs", exist_ok=True)
        rt = state.get('report_type', 'daily')
        sd = state.get('start_date', 'all')
        ed = state.get('end_date', 'all')
        
        from datetime import datetime
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
        chart_paths = []
        
        # 1. Bar chart for intent distribution
        top_intents = results.get("top_intents", {})
        if top_intents:
            plt.figure(figsize=(8, 5))
            sns.barplot(x=list(top_intents.keys()), y=list(top_intents.values()))
            plt.title('Top Call Intents')
            plt.xlabel('Intent')
            plt.ylabel('Call Volume')
            plt.tight_layout()
            intent_chart_path = f"outputs/{prefix}_intent_distribution.png"
            plt.savefig(intent_chart_path)
            plt.close()
            chart_paths.append(intent_chart_path)
            logger.debug(f"Saved intent distribution chart to {intent_chart_path}")
            
        # 2. Add other charts if needed (e.g., fallback rate trend)
        raw_data = results.get("raw_data_summary", [])
        if raw_data:
            df = pd.DataFrame(raw_data)
            
            # Disposition pie chart
            if "disposition" in df.columns:
                plt.figure(figsize=(6, 6))
                disp_counts = df['disposition'].value_counts()
                plt.pie(disp_counts, labels=disp_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
                plt.title('Call Disposition Distribution')
                disp_chart_path = f"outputs/{prefix}_disposition_distribution.png"
                plt.savefig(disp_chart_path)
                plt.close()
                chart_paths.append(disp_chart_path)
                logger.debug(f"Saved disposition distribution chart to {disp_chart_path}")
            
            # Duration by intent boxplot
            if "duration" in df.columns and "intent" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.boxplot(x='intent', y='duration', data=df)
                plt.title('Call Duration Distribution by Intent')
                plt.xlabel('Intent')
                plt.ylabel('Duration (s)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                duration_chart_path = f"outputs/{prefix}_duration_by_intent.png"
                plt.savefig(duration_chart_path)
                plt.close()
                chart_paths.append(duration_chart_path)
                logger.debug(f"Saved duration chart to {duration_chart_path}")
                
        state["chart_paths"] = chart_paths
        logger.info(f"--- VIZ AGENT END (Generated {len(chart_paths)} charts) ---")
        
    except Exception as e:
        logger.error(f"Viz agent error: {e}", exc_info=True)
        state["errors"] = state.get("errors", []) + [str(e)]
        
    return state
