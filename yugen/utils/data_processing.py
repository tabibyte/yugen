import pandas as pd

def load_data(file):
    """Load data from a file into a DataFrame."""
    try:
        # Assuming the uploaded file is a CSV
        return pd.read_csv(file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

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
    
    # Calculate missing values
    missing = dataframe.isnull().sum().to_dict()

    return {
        'describe': description,
        'info': str(info),  # You can modify this to capture the info string better
        'missing': missing
    }