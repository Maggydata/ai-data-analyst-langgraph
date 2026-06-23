import json
from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from state import AnalysisState
from config import get_llm

#Chart list
ChartType = Literal["bar", "line", "scatter", "histogram", "box", "pie"]

class AnalysisTask(BaseModel) : 
    """Analysis described in a way that the coder can use"""
    title : str = Field(description = "A short, clear title for the analysis")
    question : str = Field(description= "The business question addressed by the analysis")
    chart_type : ChartType = Field(description = "The most appropriate type of chart")
    columns : list[str] = Field (
        description = "The EXACT columns in the dataset used by this analysis"
    )
    rationale : str = Field(description = "Why this analysis is relevant here")
    

class AnalysisPlan(BaseModel) : 
    """The complete plan"""
    tasks : list[AnalysisTask] = Field( description = "3 to 5 relevant analyses")


SYSTEM_PROMPT = """You are an expert data analysis planner.
    You are provided with the FACTUAL PROFILE of a dataset (columns, types, stats).
    Your task: propose 3 to 5 relevant analyses, each with a visualization.

    STRICT RULES:
    - Use ONLY columns present in the profile. Never invent a column.
    - Choose the chart_type based on the column types:
        * time series (date column + numeric) -> line
        * comparison between categories -> bar
        * relationship between two numeric values -> scatter
        * distribution of a numeric value -> histogram or box plot
        * breakdown of a whole into parts -> pie
    - Prioritize analyses with business value (sales, profit, trends, segments).
    - Vary your perspectives: don’t present the same thing five times."""
    
def planner_node(state : AnalysisState) -> dict :
        """reads the Explorer's summary and drafts a sound plan"""
        summary = state["data_summary"]
        
        #Create an LLM that MUST respond in the AnalysisPlan format 
        llm = get_llm(temperature = 0)
        planner = llm.with_structured_output(AnalysisPlan)
        
        plan_obj : AnalysisPlan = planner.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content = "Here is the dataset profile:\n" + 
                         json.dumps(summary, ensure_ascii = False, indent = 2)),
        ])
        
        #Reject any task that references a nonexistent column
        valid_cols = set(summary["columns"])
        tasks = []
        for t in plan_obj.tasks : 
            unknown = [c for c in t.columns if c not in valid_cols]
            if unknown:
                print(f"[planner] ignored task (unknown columns {unknown}) : {t.title} ")
                continue
            tasks.append(t.model_dump()) #simple dict for state
            
        print(f"[planner] {len(tasks)} Scheduled analysis(es) : ")
        for t in tasks:
            print(f"        - {t['title']} [{t['chart_type']}] {t['columns']}")
        return {"plan" : tasks}
    

#Test
if __name__ == "__main__" : 
    from config import CSV_PATH
    from data_io import load_dataframe
    from explorer import profile_dataframe
    
    summary = profile_dataframe(load_dataframe(CSV_PATH))
    result = planner_node({"data_summary" : summary})
    print("\nRough Plan :", json.dumps(result, ensure_ascii=False, indent=2))
          