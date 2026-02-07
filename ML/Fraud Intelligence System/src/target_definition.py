import pandas as pd 

def audit_missing_values(df: pd.DataFrame):
    """
    Prints missing value summary.
    """

    missing = df.isnull().sum()
    missing = missing[missing>0]

    if len(missing) == 0: 
        print("No missing values found")
    else: 
        print("Missing values detected:")
        print(missing)

def split_features_target(df: pd.DataFrame):
    """
    Separates features and target variable.
    """
    if "Class" not in df.columns: 
        raise ValueError("Target column 'Class' not found")
    
    X = df.drop(columns=["Class"])
    y = df["Class"]

    return X,y