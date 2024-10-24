import pandas as pd
import tempfile


def load_csv(file):
    """Load data from a file into a DataFrame"""
    try:
        return pd.read_csv(file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def save_dataframe(df):
    """Save the dataframe in temporary .csv"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        return tmp_file.name


def get_data_info(dataframe):
    """Return basic info about the DataFrame."""
    return {
        'rows': dataframe.shape[0],
        'columns': dataframe.shape[1],
        'column_names': dataframe.columns.tolist(),
    }


def profile_data(dataframe):
    """Return profiling information about the DataFrame."""
    description = dataframe.describe(include='all').to_html()
    info = dataframe.info(buf=None)
    
    missing = dataframe.isnull().sum().to_dict()

    return {
        'describe': description,
        'info': str(info),
        'missing': missing
    }
    
