from typing import TypedDict, List, Dict, Any

class PipelineState(TypedDict):
    files_processed: List[str]
    analysis_results: Dict[str, Any]
    chart_paths: List[str]
    email_status: str
    errors: List[str]
    start_date: str
    end_date: str
    report_type: str
