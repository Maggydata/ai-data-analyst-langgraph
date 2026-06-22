import pandas as pd

def load_dataframe(csv_path : str) -> pd.DataFrame:
    """Load a csv file into a pandas DataFrame"""
    try:
        return pd.read_csv(csv_path)
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, encoding='latin-1')