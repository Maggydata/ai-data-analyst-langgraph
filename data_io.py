import pandas as pd



class DataLoadError(Exception):
    """ To generate a clear, specific error message when the CSV file cannot be processed"""
    pass


def load_dataframe(csv_path : str) -> pd.DataFrame:
    """Load a csv file into a pandas DataFrame"""
    try:
        try:
            df = pd.read_csv(csv_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding='latin-1')
    except Exception as e:
        #Clear Message for "pandas error" and "corrupted file"
        raise DataLoadError(f"Impossible de lire le CSV : {e}")
    
    #Validation
    if df.shape[0] == 0 :
        raise DataLoadError("Le CSV ne contient aucune lignes ")
    if df.shape[1] == 0:
        raise DataLoadError("Le CSV ne contient aucune colonne")
    return df
    
            