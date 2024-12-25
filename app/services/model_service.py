import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

class ModelService:
    def __init__(self):
        pass
        
    def train_linear_regression(self, df, feature_columns, target_column, test_size):
        try:
            if not isinstance(test_size, float) or not 0 < test_size < 1:
                raise ValueError("Test size must be a float between 0 and 1")
                
            X = df[feature_columns]
            y = df[target_column]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            results = {
                'r2_score': float(r2_score(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
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