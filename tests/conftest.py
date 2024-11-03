import pytest
import pandas as pd
from pathlib import Path
from app.services.data_service import DataService

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'num': [1, 2, None, 4, 5],
        'cat': ['A', 'B', 'A', None, 'B'],
        'dup': [1, 1, 2, 2, 3]
    })

@pytest.fixture
def data_service(tmp_path):
    service = DataService()
    df = pd.DataFrame({
        'num': [1, 2, None, 4, 5],
        'cat': ['A', 'B', 'A', None, 'B']
    })
    test_file = tmp_path / "test.csv"
    df.to_csv(test_file, index=False)
    return service, test_file