from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import logging
from app.utils.exceptions import DataProcessingError, ValidationError

logger = logging.getLogger('yugen')

class DataService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._original_df: Optional[pd.DataFrame] = None
        self._transformation_history: List[Dict[str, Any]] = []
        self._file_path = None
        
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process uploaded file and return data info"""
        logger.info(f"Processing file: {file_path}")
        
        try:
            self._file_path = file_path
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                raise ValidationError(f"File not found: {file_path}")

            if file_path.suffix == '.csv':
                logger.info("Reading CSV file")
                self._df = pd.read_csv(
                    file_path, 
                    encoding='utf-8',
                    na_values=['', 'NULL', 'null', 'None', 'N/A', 'n/a', '#N/A']
                )
            elif file_path.suffix in ['.xlsx', '.xls']:
                logger.info("Reading Excel file")
                self._df = pd.read_excel(
                    file_path,
                    na_values=['', 'NULL', 'null', 'None', 'N/A', 'n/a', '#N/A']
                )
            else:
                logger.error(f"Unsupported file type: {file_path.suffix}")
                raise ValidationError(f"Unsupported file type: {file_path.suffix}")
            
            # Validate DataFrame
            if self._df.empty:
                raise ValidationError("The uploaded file is empty")
                
            if len(self._df.columns) == 0:
                raise ValidationError("No columns found in the file")
                
            self._original_df = self._df.copy()
            logger.info(f"File processed successfully. Shape: {self._df.shape}")
            logger.info(f"Total null values: {self._df.isnull().sum().sum()}")
            
            return self._get_data_info()
            
        except pd.errors.EmptyDataError:
            logger.error("Empty file detected")
            raise ValidationError("File is empty")
        except pd.errors.ParserError as e:
            logger.error(f"Parser error: {str(e)}")
            raise ValidationError(f"Failed to parse file: {str(e)}")
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error: {str(e)}")
            raise ValidationError("Failed to read file. Please check the file encoding.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DataProcessingError(f"Failed to process file: {str(e)}")
    
    def _safe_convert_value(self, value):
        """Convert pandas values to JSON-safe values"""
        if pd.isna(value):
            return None
        elif isinstance(value, np.integer):
            return int(value)
        elif isinstance(value, np.floating):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        else:
            return value

    def profiling(self) -> Dict[str, Any]:
        """Generate data profile with proper NaN handling"""
        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            numeric_cols = self._df.select_dtypes(include=[np.number]).columns
            categorical_cols = self._df.select_dtypes(include=['object', 'category']).columns
            
            # Handle correlation matrix with NaN values
            correlation = {}
            if len(numeric_cols) > 1:
                corr_matrix = self._df[numeric_cols].corr()
                correlation = {}
                for col in corr_matrix.columns:
                    correlation[col] = {}
                    for other_col in corr_matrix.columns:
                        val = corr_matrix.loc[col, other_col]
                        if pd.isna(val):
                            correlation[col][other_col] = None
                        elif isinstance(val, (int, float, np.integer, np.floating)):
                            correlation[col][other_col] = float(val)
                        else:
                            correlation[col][other_col] = None
            
            return {
                'dtypes': {
                    'numeric': len(numeric_cols),
                    'categorical': len(categorical_cols),
                    'details': {k: str(v) for k, v in self._df.dtypes.items()}
                },
                'missing': {
                    'total': int(self._df.isnull().sum().sum()),
                    'by_column': {col: int(count) for col, count in self._df.isnull().sum().items()},
                    'percentage': {
                        col: round(float(count / len(self._df) * 100), 2) if len(self._df) > 0 else 0
                        for col, count in self._df.isnull().sum().items()
                    }
                },
                'numeric_summary': self._get_numeric_summary(),
                'categorical_summary': self._get_categorical_summary(),
                'correlation': correlation
            }
        except Exception as e:
            logger.error(f"Error generating profile: {str(e)}")
            raise DataProcessingError(f"Failed to generate profile: {str(e)}")

        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            numeric_cols = self._df.select_dtypes(include=['int64', 'float64']).columns
            categorical_cols = self._df.select_dtypes(include=['object', 'category']).columns
            
            return {
                'dtypes': {
                    'numeric': len(numeric_cols),
                    'categorical': len(categorical_cols),
                    'details': self._df.dtypes.astype(str).to_dict()
                },
                'missing': {
                    'total': int(self._df.isnull().sum().sum()),
                    'by_column': self._df.isnull().sum().to_dict(),
                    'percentage': (self._df.isnull().sum() / len(self._df) * 100).round(2).to_dict()
                },
                'numeric_summary': self._get_numeric_summary(),
                'categorical_summary': self._get_categorical_summary(),
                'correlation': self._df[numeric_cols].corr().to_dict() if len(numeric_cols) > 0 else {}
            }
        except Exception as e:
            raise DataProcessingError(f"Failed to generate profile: {str(e)}")
    
    def get_plot_data(self, plot_type: str, x: str, y: Optional[str] = None) -> Dict[str, Any]:
        """Get plot data with NaN handling"""
        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            if plot_type == 'histogram':
                # Remove NaN values for plotting
                x_data = self._df[x].dropna().tolist()
                data = {
                    'x': x_data,
                    'type': 'histogram'
                }
            elif plot_type == 'scatter':
                # Remove rows where either x or y is NaN
                clean_df = self._df[[x, y]].dropna()
                data = {
                    'x': clean_df[x].tolist(),
                    'y': clean_df[y].tolist(),
                    'mode': 'markers',
                    'type': 'scatter'
                }
            else:
                raise ValidationError(f"Unsupported plot type: {plot_type}")
            return {'data': [data]}
        except Exception as e:
            logger.error(f"Error generating plot data: {str(e)}")
            raise DataProcessingError(f"Failed to generate plot data: {str(e)}")
    
    def clean_data(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """Clean data based on provided options"""
        if self._df is None:
            raise ValidationError("No data loaded")
            
        try:
            logger.info(f"Cleaning data with options: {options}")
            
            if options.get('drop_nulls'):
                original_shape = self._df.shape
                self._df = self._df.dropna()
                logger.info(f"Dropped nulls: {original_shape} -> {self._df.shape}")
                self._add_transformation('drop_nulls')
                
            if options.get('drop_duplicates'):
                original_shape = self._df.shape
                self._df = self._df.drop_duplicates()
                logger.info(f"Dropped duplicates: {original_shape} -> {self._df.shape}")
                self._add_transformation('drop_duplicates')
                
            logger.info("Data cleaned successfully")
            
            # Return cleaned data info with the cleaned DataFrame
            result = self._get_data_info()
            result['data'] = self._df  # Add the cleaned DataFrame
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            raise DataProcessingError(f"Failed to clean data: {str(e)}")
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
        """Get data information with proper NaN handling"""
        if self._df is None:
            raise ValidationError("No data loaded")
        
        # Handle preview data with NaN values
        preview_df = self._df.head(10).copy()
        preview_records = []
        
        for _, row in preview_df.iterrows():
            record = {}
            for col in preview_df.columns:
                record[col] = self._safe_convert_value(row[col])
            preview_records.append(record)
        
        # Handle missing data counts
        missing_counts = {}
        for col in self._df.columns:
            count = int(self._df[col].isnull().sum())
            missing_counts[col] = count
            
        return {
            'shape': tuple(map(int, self._df.shape)),
            'columns': self._df.columns.tolist(),
            'memory_usage': int(self._df.memory_usage(deep=True).sum()),
            'dtypes': {k: str(v) for k, v in self._df.dtypes.items()},
            'transformations': self._transformation_history.copy(),
            'preview': preview_records,
            'missing': missing_counts
        }
    
    def _get_numeric_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for numeric columns with NaN handling"""
        if self._df is None:
            return {}
            
        numeric_cols = self._df.select_dtypes(include=[np.number]).columns
        summary = {}
        
        for col in numeric_cols:
            stats = self._df[col].describe()
            summary[col] = {
                'count': int(stats['count']) if not pd.isna(stats['count']) else 0,
                'mean': float(stats['mean']) if not pd.isna(stats['mean']) else None,
                'std': float(stats['std']) if not pd.isna(stats['std']) else None,
                'min': float(stats['min']) if not pd.isna(stats['min']) else None,
                'max': float(stats['max']) if not pd.isna(stats['max']) else None,
                '25%': float(stats['25%']) if not pd.isna(stats['25%']) else None,
                '50%': float(stats['50%']) if not pd.isna(stats['50%']) else None,
                '75%': float(stats['75%']) if not pd.isna(stats['75%']) else None
            }
        
        return summary
    
    def _get_categorical_summary(self) -> Dict[str, Dict[str, int]]:
        """Get summary statistics for categorical columns with NaN handling"""
        if self._df is None:
            return {}
            
        categorical_cols = self._df.select_dtypes(include=['object', 'category']).columns
        summary = {}
        
        for col in categorical_cols:
            value_counts = self._df[col].value_counts(dropna=False)
            summary[col] = {
                str(k) if k is not None and not (isinstance(k, float) and pd.isna(k)) else 'null': int(v) 
                for k, v in value_counts.items()
            }
        
        return summary

        """Get summary statistics for categorical columns"""
        if self._df is None:
            return {}
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
        
    def get_file_path(self):
        return self._file_path