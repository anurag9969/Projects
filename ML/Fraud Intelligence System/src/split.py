from sklearn.model_selection import train_test_split 
import pandas as pd 

def train_val_split(X: pd.DataFrame,y: pd.Series, test_size = 0.2):
    """
        Creates stratified train / validation split
    """

    X_train,X_test,y_train,y_test = train_test_split(
        X, 
        y, 
        test_size=test_size, 
        stratify=y, 
        random_state=42
    )
    return X_train,X_test,y_train,y_test