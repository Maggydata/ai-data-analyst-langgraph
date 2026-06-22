from langgraph.graph import StateGraph, START, END
from state import AnalysisState, initial_state
from explorer import explorer_node


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
    
def writer_node (state : AnalysisState) -> dict:
    # Read charts product by the coder
    print(f"[Writer] i read the figures : {state['figures']}")
    return {"insights" : "Insights factices"}


# Graph Construction

def build_graph() : 
    
    builder = StateGraph(AnalysisState)
    
    # registration of nodes
    builder.add_node("explorer", explorer_node)
    builder.add_node("planner", planner_node)
    builder.add_node("coder", coder_node)
    builder.add_node("writer", writer_node)
    
    # registration of edges
    builder.add_edge(START, "explorer")
    builder.add_edge("explorer", "planner")
    builder.add_edge("planner", "coder")
    builder.add_edge("coder", "writer")
    builder.add_edge("writer", END)
    
    return builder.compile()

if __name__ == "__main__":
    
    app = build_graph()
    print(app.get_graph().draw_mermaid())
    
    final_state = app.invoke(initial_state("Data/Sample - Superstore.csv"))
    print("\n--- Final State ---")
    for key, value in final_state.items():
       print(f"{key} : {value}")