import json
import shutil

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from state import AnalysisState, initial_state
from config import get_llm
from execute import run_generated_code

FORCE_BUG_ON_FIRST_TRY = True

class GeneratedCode(BaseModel) : 
    """Forces the LLM to return plain code, without Markdown or explanations."""
    code : str = Field(
        description = "The complete, executable Python script,"
                      "no Markdown tags or explanatory text." 
    )
    

SYSTEM_PROMPT = """ You are an expert Python data analyst.
You write a SINGLE complete and executable Python script that performs the requested analyses
and generates Plotly charts.

STRICT REQUIREMENTS — your script MUST:
- Read the CSV from sys.argv[1] (NEVER a hard-coded path). Handle encoding:
  try utf-8, and fall back to latin-1 if a UnicodeDecodeError occurs.
- Use pandas (import pandas as pd) and Plotly (plotly.express as px
  and/or plotly.graph_objects as go).
- For EACH analysis in the plan, in order, create a Plotly figure and
  save it with fig.write_json(‘figN.json’), where N starts at 0 and increments
  (fig0.json for the first analysis, fig1.json for the second, etc.).
- Give each figure a clear TITLE.
- Parse the date columns using `pd.to_datetime` BEFORE creating any time-series plots.
- Use ONLY columns present in the provided profile.

STRICTLY PROHIBITED:
- No `fig.show()`, no `plt.show()`, no on-screen display.
- No network access (requests, urllib, etc.).
- No writing to or reading from files other than the output figN.json files.

The script must run from start to finish without errors. """

def _build_human_prompt(summary : dict, plan : list, attempts_log : list) -> str : 
    """Combine the variable data: the profile and the plan to be carried out."""
    prompt =(
        "DATASET PROFILE (available columns, types, statistics):\n"
        + json.dumps(summary, ensure_ascii = False, indent = 2)
        +"\n\nPLAN OF ANALYSES TO BE PERFORMED (one figure per task, in order):"
        + json.dumps(plan, ensure_ascii=False, indent=2)
    )
    #Check if an attempt failed
    failed = [a for a in attempts_log if a.get("error")]
    if failed :
        last = failed[-1]
        prompt += (
            "\n\n YOUR PREVIOUS ATTEMPT FAILED."
            "Analyze the error below and FIX your code.\n"
            "--- Previous CODE ---\n" + last["code"] +
            "\n--- ERROR OCCURRED ---\n" + last["error"] +
            "\n\nRéécris le script COMPLET et corrigé."
        )
    else : 
        prompt += "\n\nGenerates the complete Python script that complies with the contract."
    return prompt        
    
    
    
def coder_node(state : AnalysisState) -> dict : 
        """generates the code, runs it in a sandbox, and captures whether it succeeds or fails"""
        
        #Code generation
        llm = get_llm(temperature = 0)
        coder = llm.with_structured_output(GeneratedCode)
        
        system = SYSTEM_PROMPT
        
        #Force bug
        if FORCE_BUG_ON_FIRST_TRY and state["retry_count"] == 0 :
            system += ("\n\n[TEST MODE] In this script only, deliberately use "
                       "a 'Revenue' column that doesn't exist instead of 'Sale'"
                       "to cause an intentional error.")
        
        generated : GeneratedCode = coder.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content= _build_human_prompt(state["data_summary"], state["plan"], state["attempts_log"] ))
        ])
        code = generated.code
        
        #Execution in the isolated sandbox
        print(f"[Coder] code generated ({len(code)} characters ) -> sandbox execution ...")
        result = run_generated_code(code, state["csv_path"], timeout = 30)
        
        
        #Processing the Results
        if result.success :
            figures = []
            for path in result.figure_files:
                with open(path, "r", encoding="utf-8") as f:
                    figures.append(f.read())
            shutil.rmtree(result.workdir, ignore_errors=True)
            
            print(f"[Coder] success : {len(figures)} chart(s) producted")
            return{
                "generated_code" : code,
                "figures" : figures,
                "error" : None,
                "retry_count" : state["retry_count"] + 1,
                "attempts_log" : [{"code" : code, "error" : None}]
            }
        
        else:
            shutil.rmtree(result.workdir, ignore_errors=True)
            err = result.stderr.strip()
            print(f"[Coder] failed : {err[:150]}")
            return{
               " generated_code" : code,
               "figures" : [],
               "error" : err,
               "retry_count" : state["retry_count"] + 1,
               "attemps_log" : [{"code" : code, "error" : err}],
            }
            
#Test
if __name__ == "__main__":
    from config import CSV_PATH
    from data_io import load_dataframe
    from explorer import profile_dataframe
    from planner import planner_node
    
    summary = profile_dataframe(load_dataframe(CSV_PATH))
    plan = planner_node({"data_summary" : summary})["plan"]
    
    state = initial_state(CSV_PATH)
    state["data_summary"] = summary
    state["plan"] = plan
    
    result = coder_node(state)
    
    print("\n--- RESULTS ---")
    print("error       :", result["error"])
    print("figures     :", len(result["figures"]))
    print("retry_count :", result["retry_count"])
    
    with open("last_generated_code.py", "w", encoding="utf-8" ) as f:
            f.write(result["generated_code"])
    print(" Code generated writed in last_generated_code.py")        
            
    
    