import warnings
import pandas as pd

from state import AnalysisState
from data_io import load_dataframe

def _round(value, ndigits = 2):
  """Round a float value to a given number of decimal places""" 
  try:
      return round(float(value), ndigits)
  except(TypeError, ValueError):
      return None
  
  
def profile_dataframe(df : pd.DataFrame) -> dict:
    """Profile a pandas DataFrame and return a summary of its contents"""
    
    # numeric columns
    numeric_cols = df.select_dtypes(include= "number").columns.tolist()
    other_cols = [c for c in df.columns if c not in numeric_cols]
    
    # distinguish between dates and categories columns
    datetime_cols, categorical_cols = [], []
    for col in other_cols:
        sample = df[col].dropna().head(1000)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed = pd.to_datetime(sample, errors = "coerce")
        if len(sample) > 0 and parsed.notna().mean() >= 0.8:
            datetime_cols.append(col)
        else:
            categorical_cols.append(col)
    
    #summarize a summary       
    summary = {
        "n_rows" : int(df.shape[0]), 
        "n_cols" : int(df.shape[1]),
        "columns" : df.columns.tolist(),
        "dtypes" : {c : str(t) for c, t in df.dtypes.items()},
        "missing_value" : {c : int(n) for c, n in df.isna().sum().items() if n > 0},
        "numerical_columns" : numeric_cols,
        "categorical_columns" : categorical_cols,
        "datetime_columns" : datetime_cols,
        "numeric_stats" : {},
        "categorical_preview" : {}
    }
    
    #Stats for each numerical columns
    for col in numeric_cols :
        s = df[col]
        summary["numeric_stats"][col] = {
            "min" : _round(s.min()), "max" : _round(s.max()),
            "mean" : _round(s.mean()), "median" : _round(s.median()),
            "std" : _round(s.std())
        }   
        
    
    #Overview of Each Categorical Column  
    for col in categorical_cols:
        vc = df[col].value_counts().head(5)
        summary["categorical_preview"][col] = {
            "n_unique" : int(df[col].nunique()),
            "top_values" : {str(k) : int(v) for k, v in vc.items()}
        }
        
    return summary

def explorer_node (state : AnalysisState) -> dict :
    
    df = load_dataframe(state["csv_path"])
    summary = profile_dataframe(df)
    print (f"[Explorer] {summary["n_rows"]} rows, {summary["n_cols"]} columns"
           f" | {len(summary["numerical_columns"])} numerical columns, "
           f" {len(summary["categorical_columns"])} categorical columns, "
           f" {len(summary["datetime_columns"])} dates columns")
    return {"data_summary" : summary}


if __name__ == "__main__" : 
    import json
    from config import CSV_PATH
    df = load_dataframe(CSV_PATH)
    print(json.dumps(profile_dataframe(df), indent = 2, ensure_ascii= False, default = str))