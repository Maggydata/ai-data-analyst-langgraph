from typing import TypedDict, Annotated, Optional, Any
import operator

class AnalysisState(TypedDict):
    csv_path : str                  #CSV file path
    data_summary : dict[str, Any]   #product by the Explorer
    plan : list[dict]               #product by the Planner
    
    #product and update by the Coder
    generated_code : str            #last python code generated
    figures : list                  #plot of the last successful run
    error : Optional[str]           #last error message
    retry_count : int               #number of attempts
    attempts_log : Annotated[list, operator.add]         #history for auto-correction
    
    insights : str                  # product by the Writter
    
    

def initial_state(csv_path : str) -> AnalysisState:
    """Construct the initial state that will be passed to the graph"""
    return {
        "csv_path" : csv_path,
        "data_summary" : {},
        "plan" : [],
        "generated_code" : "",
        "figures" : [],
        "error" : None,
        "retry_count" : 0,
        "attempts_log" : [],
        "insights" : "",
    }