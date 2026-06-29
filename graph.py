from langgraph.graph import StateGraph, START, END

from state import AnalysisState, initial_state
from explorer import explorer_node
from planner import planner_node
from coder import coder_node
from writer import writer_node
from config import MAX_CODE_ATTEMPTS


def route_after_coder(state : AnalysisState) -> str:
    """A conditional branch that determines what happens after the Coder, depending on the state."""
    
    if state["error"] is None:
        print(f"[Route] success in {state['retry_count']} attemp(s) ")
        return "success"
    
    if state["retry_count"] >= MAX_CODE_ATTEMPTS :
        print(f"[Route] failed after {state['retry_count']} attemp(s)"
              f"(max atteint) -> we continue with writer")
        return "give up"
    print(f"[Route] failed (attemp {state['retry_count']}) -> we retry with coder")
    return "retry"

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
    builder.add_conditional_edges("coder", route_after_coder, {
        "success" : "writer",
        "give up" : "writer",
        "retry" : "coder", 
    })
    builder.add_edge("writer", END)
    
    return builder.compile()

if __name__ == "__main__":
    
    app = build_graph()
    print(app.get_graph().draw_mermaid())
    
    final_state = app.invoke(initial_state("Data/Sample - Superstore.csv"))
    print("\n--- Final State ---")
    #for key, value in final_state.items():
       #print(f"{key} : {value}")