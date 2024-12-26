import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error,precision_score, recall_score, mean_absolute_error

class ModelService:
    def __init__(self):
        self._df = None
       
    def load_data(self, file_path):
        if file_path.suffix == '.csv':
            self._df = pd.read_csv(file_path)
        elif file_path.suffix == '.xlsx':
            self._df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
     
    def train_linear_regression(self, feature_columns, target_column, test_size):
        try:
            if self._df is None:
                raise ValueError("No data loaded")
            
            if not isinstance(test_size, float) or not 0 < test_size < 1:
                raise ValueError("Test size must be a float between 0 and 1")
                
            X = self._df[feature_columns]
            y = self._df[target_column]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            mae = float(mean_absolute_error(y_test, y_pred))
            
            y_test_binary = y_test > y_test.median()
            y_pred_binary = y_pred > y_test.median()
            
            precision = float(precision_score(y_test_binary, y_pred_binary))
            recall = float(recall_score(y_test_binary, y_pred_binary))
            
            results = {
                'r2_score': float(r2_score(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'mae': mae,
                'precision': precision,
                'recall': recall,
                'feature_importance': dict(zip(feature_columns, model.coef_.tolist())),
                'model_intercept': float(model.intercept_),
                'samples': {
                    'train': len(X_train),
                    'test': len(X_test)
                }
            }
            
            return results
            
        except Exception as e:
            raise Exception(f"Model training failed: {str(e)}")