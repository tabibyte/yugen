import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import pandas as pd

class VisualizationService:
    def __init__(self):
        self._df = None
    
    def set_data(self, df: pd.DataFrame):
        self._df = df
    
    def get_histogram(self, column: str) -> Dict[str, Any]:
        if self._df is None:
            raise ValueError("No data loaded")
        fig = px.histogram(self._df, x=column)
        return fig.to_json()
    
    def get_scatter(self, x: str, y: str) -> Dict[str, Any]:
        if self._df is None:
            raise ValueError("No data loaded")
        fig = px.scatter(self._df, x=x, y=y)
        return fig.to_json()