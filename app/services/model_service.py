import pandas as pd
import numpy as np
from pathlib import Path
import logging
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    precision_score, recall_score
)
from app.utils.exceptions import ValidationError, DataProcessingError

logger = logging.getLogger('yugen')

class ModelService:
    def __init__(self):
        self._df = None
        self._model = None
        self._train_results = {}
        
    def load_data(self, file_path: Path) -> None:
        """Load data from file"""
        try:
            if not file_path.exists():
                raise ValidationError(f"File not found: {file_path}")
                
            if file_path.suffix == '.csv':
                self._df = pd.read_csv(file_path)
            elif file_path.suffix == '.xlsx':
                self._df = pd.read_excel(file_path)
            else:
                raise ValidationError(f"Unsupported file type: {file_path.suffix}")
                
            logger.info(f"Data loaded successfully from {file_path}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise DataProcessingError(f"Failed to load data: {str(e)}")
    
    def train_linear_regression(self, feature_columns, target_column, test_size=0.2):
        """Train a linear regression model"""
        try:
            if self._df is None:
                raise ValidationError("No data loaded")
                
            if not target_column:
                raise ValidationError("Target column must be specified")
                
            if not feature_columns or len(feature_columns) == 0:
                raise ValidationError("At least one feature column must be selected")
                
            # Validate columns exist in dataframe
            all_columns = feature_columns + [target_column]
            for col in all_columns:
                if col not in self._df.columns:
                    raise ValidationError(f"Column not found in dataset: {col}")
            
            # Create feature matrix and target vector
            X = self._df[feature_columns]
            y = self._df[target_column]
            
            # Handle missing values
            X = X.fillna(X.mean())
            mask = ~y.isna()
            X = X[mask]
            y = y[mask]
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Train the model
            self._model = LinearRegression()
            self._model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self._model.predict(X_test)
            
            # Calculate metrics
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            # For binary classification metrics (approximating with median threshold)
            y_test_binary = y_test > y_test.median()
            y_pred_binary = y_pred > y_test.median()
            precision = precision_score(y_test_binary, y_pred_binary)
            recall = recall_score(y_test_binary, y_pred_binary)
            
            # Get feature importance
            feature_importance = dict(zip(feature_columns, self._model.coef_))
            
            # Store results
            self._train_results = {
                'model_type': 'LinearRegression',
                'feature_columns': feature_columns,
                'target_column': target_column,
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'precision': float(precision),
                'recall': float(recall),
                'feature_importance': {k: float(v) for k, v in feature_importance.items()},
                'samples': {
                    'train': len(X_train),
                    'test': len(X_test)
                }
            }
            
            logger.info(f"Model trained successfully. R² Score: {r2:.4f}")
            return self._train_results
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise DataProcessingError(f"Failed to train model: {str(e)}")
    
    def predict(self, data):
        """Make predictions using the trained model"""
        if self._model is None:
            raise ValidationError("No model trained")
            
        try:
            predictions = self._model.predict(data)
            return predictions
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise DataProcessingError(f"Failed to make predictions: {str(e)}")
    
    def get_training_results(self):
        """Get the results from the last training session"""
        if not self._train_results:
            raise ValidationError("No training results available")
            
        return self._train_results