import pandas as pd 

def load_data(path: str) -> pd.DataFrame: 
    """
    Loads raw transaction data and performs basic validation.
    """
    df = pd.read_csv(path)

    # Basic sanity checks 
    if df.empty: 
        raise ValueError("Dataset is empty")
    
    if df.isnull().sum().sum():
        print("Warning: Missing values detected")

    return df 