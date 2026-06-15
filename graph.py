from langgraph.graph import StateGraph, START, END
from state import AnalysisState, initial_state

def explorer_node(state : AnalysisState) -> dict : 
    # Read the input of the system
    print(f"[Explorer] i inspected the CSV : {state['csv_path']}")
    
    # return result of dataset's inspection
    return{"data_summary" : {"n_rows" : 994, "columns" : ["Sales", "Profit"]}}


def planner_node(state: AnalysisState) -> dict:
    # Read what planner wrote in the state
    print(f"[Planner] i read the data summary : {state['data_summary']}")
    return{"plan" : [{"analysis" : "Sales by region ", "chart" : "bar"}]}

def coder_node(state : AnalysisState) -> dict: 
    # Read plan of planner
    print(f"[Coder] i read the plan : {state['plan']}")
    return{
        "generate_code" : "# active code",
        "figures" : ["<figure factice>"], 
        "error" : None, 
        "retry_count" : state["retry_count"] + 1,
        "attempts_log" : [{"code" : "# active code", "error" : None}]
        }
    
def writer_node (state : AnalysisState) - > dict:
    # Read charts product by the coder
    print(f"[Writer] i read the figures : {state['figures']}")
    return {"insights" : "Insights factices"}
    