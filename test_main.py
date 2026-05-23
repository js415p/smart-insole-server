import json
import pytest
from unittest.mock import MagicMock, patch
import sys

# Create mocks for firebase_admin
mock_firebase_admin = MagicMock()
mock_db = MagicMock()
mock_credentials = MagicMock()

# Setup the mock hierarchy
mock_firebase_admin.db = mock_db
mock_firebase_admin.credentials = mock_credentials

# Inject mocks into sys.modules before importing main
sys.modules['firebase_admin'] = mock_firebase_admin
sys.modules['firebase_admin.db'] = mock_db
sys.modules['firebase_admin.credentials'] = mock_credentials

# Now we can import app from main without it triggering real firebase logic
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_update_endpoint():
    # Load dummy data
    with open('dummy_data.json', 'r') as f:
        dummy_data = json.load(f)

    for data in dummy_data:
        # Reset mock for each call
        mock_db.reference.reset_mock()
        
        # Setup mock behavior for balance calculation (db.reference(...).get())
        mock_node = MagicMock()
        mock_node.get.return_value = {"total_pressure": 100} # Mock some existing data
        mock_db.reference.return_value = mock_node

        response = client.post("/update", json=data)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Check if db.reference was called
        # It should be called for:
        # 1. foot data storage: db.reference(f'insole_live/{uid}/{side}').set(foot_data)
        # 2. opposite node retrieval: db.reference(f'insole_live/{uid}/{opposite_side}').get()
        # 3. balance storage: db.reference(f'insole_live/{uid}/balance').set(balance_data)
        assert mock_db.reference.call_count >= 3

def test_logic_validation():
    # Test specific values to verify kPa conversion and balance logic
    # MAX_KPA = 150
    # s1=0.5 -> 75.0, s2=0.4 -> 60.0, s3=0.3 -> 45.0, s4=0.2 -> 30.0
    # total = 210.0
    
    test_input = {
        "name": "LogicTest",
        "side": "left",
        "s1": 0.5,
        "s2": 0.4,
        "s3": 0.3,
        "s4": 0.2
    }
    
    mock_db.reference.reset_mock()
    
    mock_foot_node = MagicMock()
    mock_opposite_node = MagicMock()
    mock_balance_node = MagicMock()
    
    # Setup mock to return different nodes based on path
    def side_effect(path):
        if "left" in path: return mock_foot_node
        if "right" in path: return mock_opposite_node
        if "balance" in path: return mock_balance_node
        return MagicMock()
    
    mock_db.reference.side_effect = side_effect
    mock_opposite_node.get.return_value = {"total_pressure": 210.0} # Same as left for 50/50 balance

    response = client.post("/update", json=test_input)
    
    assert response.status_code == 200
    
    # Verify foot data storage
    mock_foot_node.set.assert_called_once()
    sent_foot_data = mock_foot_node.set.call_args[0][0]
    assert sent_foot_data["total_pressure"] == 210.0
    assert sent_foot_data["sensors"]["s1_kpa"] == 75.0
    
    # Verify balance storage
    mock_balance_node.set.assert_called_once()
    sent_balance_data = mock_balance_node.set.call_args[0][0]
    assert sent_balance_data["left_ratio"] == 50.0
    assert sent_balance_data["right_ratio"] == 50.0
    assert sent_balance_data["imbalance_percent"] == 0.0

if __name__ == "__main__":
    pytest.main([__file__])
