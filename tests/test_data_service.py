import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.data_service import DataService
from app.utils.exceptions import DataProcessingError, ValidationError

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
    # Create test data
    df = pd.DataFrame({
        'num': [1, 2, None, 4, 5],
        'cat': ['A', 'B', 'A', None, 'B']
    })
    test_file = tmp_path / "test.csv"
    df.to_csv(test_file, index=False)
    return service, test_file

def test_process_file(data_service):
    service, file_path = data_service
    result = service.process_file(file_path)
    
    assert result['shape'] == (5, 2)
    assert 'num' in result['columns']
    assert 'cat' in result['columns']

def test_clean_data(data_service):
    service, file_path = data_service
    service.process_file(file_path)
    
    result = service.clean_data({
        'drop_nulls': True,
        'drop_duplicates': False
    })
    
    assert result['shape'] == (3, 2)

def test_get_profile(data_service):
    service, file_path = data_service
    service.process_file(file_path)
    
    profile = service.get_profile()
    
    assert 'info' in profile
    assert 'preview' in profile
    assert 'numeric_summary' in profile
    assert 'categorical_summary' in profile

def test_invalid_file_type(data_service):
    service, _ = data_service
    invalid_path = Path('test.txt')
    
    with pytest.raises(ValidationError):
        service.process_file(invalid_path)

def test_no_data_loaded():
    service = DataService()
    
    with pytest.raises(ValidationError):
        service.get_profile()

def test_reset_data(data_service):
    service, file_path = data_service
    service.process_file(file_path)
    
    service.clean_data({'drop_nulls': True})
    result = service.reset_data()
    
    assert result['shape'] == (5, 2)