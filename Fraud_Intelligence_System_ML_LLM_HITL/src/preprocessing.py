import pandas as pd 

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data cleaning layer: 
    - Drop rows with missing target 
    - Final NaN validation
    """

    initial_rows = df.shape[0]

    # Drop rows where target is missing (critical rule)
    df = df.dropna(subset=["Class"])

    dropped_rows = initial_rows - df.shape[0]
    print(f"Dropped {dropped_rows} corrupted rows")

    # Hard Safety Check 
    total_missing = df.isnull().sum().sum()
    if total_missing != 0: 
        raise ValueError(
            f"Data Cleaning contains {total_missing} missing values after cleaning"
        )
    return df 