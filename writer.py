import json
import plotly.io as pio
import base64
import numpy as np

from langchain_core.messages import SystemMessage, HumanMessage

from state import AnalysisState
from config import get_llm


def _fmt(v):
    """Formats a number; otherwise, returns it as is"""
    try : 
        return f"{float(v) : , .Of}".replace(",", " ")
    except(TypeError, ValueError):
        return str(v)
    
    
def _decode(v):
    """Decode a binary-encoded Plotly array into a list"""
    if isinstance(v, dict) and "bdata" in v:
        raw = base64.b64decode(v["bdata"])
        return np.frombuffer(raw, dtype=np.dtype(v["dtype"])).tolist()
    if v is None:
        return []
    return list(v)    
    


def describe_figure(fig_json : str, max_points : int = 40) -> str :
    """Converts a Plotly figure (JSON) into a concise, numbered textual summary."""
    try :
        fig = pio.from_json(fig_json)
    except Exception:
        return "Unreadable figure"
    
    
    title = fig.layout.title.text if (fig.layout.title and fig.layout.title.text) else "No title"
    out = [f'Figure : "{title}"']
    
    for tr in fig.data : 
        ttype = tr.type or "?"
        name = tr.name or ""
        x = _decode(getattr(tr, "x", None) )
        y = _decode(getattr(tr, "y", None)) 
        labels = _decode(getattr(tr, "labels", None) )
        values = _decode(getattr(tr, "values", None))
        
        if labels and values:                                                       #Camembert
            pairs = ";".join(f"{l} : {_fmt(v)}" for l,v in zip(labels, values))
            out.append(f"   (pie) {pairs}")
        elif x and y and len(x) <= max_points:                                      #bar / small series
            pairs = ";".join(f"{a} : {_fmt(b)}" for a, b in zip(x, y))
            out.append(f"   ({ttype}) {name} {pairs}".rstrip())
        elif x and y:                                                               #big series -> summary
            try:
                ynum = [float(v) for v in y if v is not None]
                out.append(f"({ttype}) {name} {len(x)} points ;"
                           f"beginning {_fmt(y[0])}, end {_fmt(y[-1])}, "
                           f"min {_fmt(min(ynum))}, max {_fmt(max(ynum))}".rstrip()) 
            except Exception :
                out.append(f"   ({ttype}) {name} {len(x)} points")
            
        elif x:                                                                      #histogram    
            out.append(f"   ({ttype}) {len(x)} values")
    return "\n ".join(out) 

SYSTEM_PROMPT = """You are a data analyst. Based on DESCRIPTIONS of charts
(titles + numerical data), you write clear and useful insights in French.

RULES:
- Base your work SOLELY on the numbers provided. Do NOT make up ANY data.
- For each chart: 1 to 2 concrete insights (what we LEARN, not a description).
- Be precise (mention key categories/values) but concise.
- End with a short general summary (2–3 sentences).
- Your writing should be professional and accessible."""

def writer_node(state : AnalysisState) -> dict : 
    """The node extracts the key points, then asks the LLM to write the insights."""
    
    #no figures + an earlier error
    if state.get("error") and not state.get("fugures") :
        last = state["error"].splitlines()[-1] if state ["error"] else ""
        msg = (f" The automatic analysis failed: The code failed after "
               f"{state["retry_count"]} attemp(s), No figures were produced. \n"
               f"last error is {last}")
        print("[Writer] failed, no figures")
        return {"insights" : msg}
    
    
    #If there are figures, we analyze each one and then write up the results
    digests = [describe_figure(f) for f in state["figures"]]
    digest_text = "\n\n".join(digests)
    
    print("=== DIGEST ENVOYÉ AU WRITER ===")
    print(digest_text)
    print("=== FIN DIGEST ===")
    
    llm = get_llm(temperature= 0.5)
    resp = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="Here are the generated charts : \n\n" + digest_text)
    ])
    insights = resp.content
    print(f"[Writer] written insights ({len(insights)}) caracters")
    return{"insights" : insights}


if __name__ == "__main__":
    
    # first test : failed
    fail_state = {"error": "KeyError: 'Revenue'", "figures": [], "retry_count" : 3}
    print("=== Failed test ===")
    print(writer_node(fail_state)["insights"])
    
    #second test : success
    fake_fig = json.dumps({
        "data": [{"type": "bar",
                  "x": ["West", "East", "Central", "South"],
                  "y": [725458, 678781, 501240, 391722]}],
        "layout": {"title": {"text": "Ventes par région"}},
    })
    print("\n === Success Test === ")
    ok_state = {"error" : None, "figures" : [fake_fig], "retry_count" : 1}
    print(writer_node(ok_state)["insights"])
    
                      
               