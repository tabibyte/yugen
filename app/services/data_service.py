from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import logging
from app.utils.exceptions import DataProcessingError, ValidationError

logger = logging.getLogger('yugen')

class DataService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._original_df: Optional[pd.DataFrame] = None
        self._transformation_history: List[Dict[str, Any]] = []
        
    # app/services/data_service.py
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process uploaded file and return data info"""
        logger.info(f"Processing file: {file_path}")
        
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                raise ValidationError(f"File not found: {file_path}")

            if file_path.suffix == '.csv':
                logger.info("Reading CSV file")
                self._df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.suffix == '.xlsx':
                logger.info("Reading Excel file")
                self._df = pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file type: {file_path.suffix}")
                raise ValidationError(f"Unsupported file type: {file_path.suffix}")
                
            self._original_df = self._df.copy()
            logger.info(f"File processed successfully. Shape: {self._df.shape}")
            
            # Clean up temp file
            file_path.unlink(missing_ok=True)
            
            return self._get_data_info()
            
        except pd.errors.EmptyDataError:
            logger.error("Empty file detected")
            raise ValidationError("File is empty")
        except pd.errors.ParserError as e:
            logger.error(f"Parser error: {str(e)}")
            raise ValidationError(f"Failed to parse file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DataProcessingError(f"Failed to process file: {str(e)}")
    
    def get_profile(self) -> Dict[str, Any]:
        """Get data profile information"""
        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            logger.info("Generating data profile")
            profile = {
                'info': self._get_data_info(),
                'preview': self._df.head().to_dict('records'),
                'missing': self._df.isnull().sum().to_dict(),
                'dtypes': self._df.dtypes.astype(str).to_dict(),
                'numeric_summary': self._get_numeric_summary(),
                'categorical_summary': self._get_categorical_summary()
            }
            logger.info("Profile generated successfully")
            return profile
            
        except Exception as e:
            logger.error(f"Error generating profile: {str(e)}")
            raise DataProcessingError(f"Failed to generate profile: {str(e)}")
    
    def get_plot_data(self, plot_type: str, x: str, y: str = None) -> Dict[str, Any]:
        if self._df is None:
            raise ValidationError("No data loaded")
            
        if plot_type == 'histogram':
            data = {
                'x': self._df[x].tolist(),
                'type': 'histogram'
            }
        elif plot_type == 'scatter':
            data = {
                'x': self._df[x].tolist(),
                'y': self._df[y].tolist(),
                'mode': 'markers',
                'type': 'scatter'
            }
        return {'data': [data]}
    
    def clean_data(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """Clean data based on provided options"""
        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            logger.info(f"Cleaning data with options: {options}")
            if options.get('drop_nulls'):
                self._df = self._df.dropna()
                self._add_transformation('drop_nulls')
                
            if options.get('drop_duplicates'):
                self._df = self._df.drop_duplicates()
                self._add_transformation('drop_duplicates')
                
            logger.info("Data cleaned successfully")
            return self._get_data_info()
            
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            raise DataProcessingError(f"Failed to clean data: {str(e)}")
    
    def reset_data(self) -> Dict[str, Any]:
        """Reset data to original state"""
        if self._original_df is None:
            raise ValidationError("No original data available")
            
        try:
            logger.info("Resetting data to original state")
            self._df = self._original_df.copy()
            self._transformation_history.clear()
            return self._get_data_info()
            
        except Exception as e:
            logger.error(f"Error resetting data: {str(e)}")
            raise DataProcessingError(f"Failed to reset data: {str(e)}")
    
    def _get_data_info(self) -> Dict[str, Any]:
        return {
            'shape': tuple(map(int, self._df.shape)),
            'columns': self._df.columns.tolist(),
            'memory_usage': int(self._df.memory_usage().sum()),
            'dtypes': {k: str(v) for k, v in self._df.dtypes.items()},
            'transformations': self._transformation_history,
            'preview': self._df.head().to_dict('records'),  # Add preview
            'missing': self._df.isnull().sum().to_dict()  # Add missing values info
        }
    
    def _get_numeric_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for numeric columns"""
        numeric_cols = self._df.select_dtypes(include=['int64', 'float64']).columns
        return {
            col: {
                'mean': self._df[col].mean(),
                'std': self._df[col].std(),
                'min': self._df[col].min(),
                'max': self._df[col].max()
            } for col in numeric_cols
        }
    
    def _get_categorical_summary(self) -> Dict[str, Dict[str, int]]:
        """Get summary statistics for categorical columns"""
        categorical_cols = self._df.select_dtypes(include=['object', 'category']).columns
        return {
            col: self._df[col].value_counts().to_dict()
            for col in categorical_cols
        }
    
    def _add_transformation(self, operation: str, **params) -> None:
        """Add transformation to history"""
        self._transformation_history.append({
            'operation': operation,
            'params': params
        })