from langgraph.graph import StateGraph, START, END

from state import AnalysisState, initial_state
from explorer import explorer_node
from planner import planner_node
from coder import coder_node 
    
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