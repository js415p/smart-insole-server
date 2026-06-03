import json
import pytest
from unittest.mock import MagicMock, patch
import sys
import time

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

# Now we can import app from main
import main
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class MockNode:
    def __init__(self, data=None):
        self.data = data or {}
        self.set = MagicMock()
        self.push = MagicMock()
        
    def get(self):
        # In the real Firebase SDK, if data doesn't exist, it might return None.
        # But for our processing, we want to return the data.
        return self.data

def setup_firebase_mocks():
    # Use patch to ensure main.db.reference is mocked
    storage = {}
    
    def get_reference(path):
        if path not in storage:
            default_data = {}
            if "balance" in path:
                default_data = {"overload_count": 0}
            elif "gait" in path:
                default_data = {"count": 0, "is_stepping_left": False, "is_stepping_right": False}
            elif "left" in path or "right" in path:
                if "diagnosis" not in path:
                    # Default pressure data for the opposite foot
                    default_data = {
                        "total_pressure": 100.0,
                        "sensors": {
                            "s1_kpa": 25.0, "s2_kpa": 25.0, "s3_kpa": 25.0, "s4_kpa": 25.0
                        }
                    }
            storage[path] = MockNode(default_data)
        return storage[path]
    
    # Patch main.db.reference directly
    patcher = patch('main.db.reference', side_effect=get_reference)
    patcher.start()
    return storage, patcher

def test_full_dashboard_logic():
    storage, patcher = setup_firebase_mocks()
    try:
        test_input = {
            "name": "FullTest",
            "side": "left",
            "s1": 1.1, # 165 kPa
            "s2": 0.4,
            "s3": 0.3,
            "s4": 0.2
        }
        
        response = client.post("/update", json=test_input)
        assert response.status_code == 200
        
        # Verify Max Pressure
        balance_path = "insole_live/FullTest/balance"
        sent_balance = storage[balance_path].set.call_args[0][0]
        assert sent_balance["max_pressure"] == 165.0
        assert sent_balance["max_channel"] == "CH3"
    finally:
        patcher.stop()

def test_diagnosis_overpronation():
    storage, patcher = setup_firebase_mocks()
    try:
        over_input = {
            "name": "DiagTest",
            "side": "left",
            "s1": 0.4,
            "s2": 0.5, # 75 kPa
            "s3": 0.2, # 30 kPa
            "s4": 0.3
        }
        response = client.post("/update", json=over_input)
        assert response.status_code == 200
        
        diag_path = "insole_live/DiagTest/diagnosis/left"
        sent_diag = storage[diag_path].set.call_args[0][0]
        assert sent_diag["status"] == "과내전 위험 감지"
        assert "CH1" in sent_diag["issue_zone"]
    finally:
        patcher.stop()

def test_diagnosis_supination():
    storage, patcher = setup_firebase_mocks()
    try:
        sup_input = {
            "name": "DiagTest",
            "side": "right",
            "s1": 0.4,
            "s2": 0.2, # 30 kPa
            "s3": 0.5, # 75 kPa
            "s4": 0.3
        }
        client.post("/update", json=sup_input)
        
        diag_path = "insole_live/DiagTest/diagnosis/right"
        sent_diag = storage[diag_path].set.call_args[0][0]
        assert sent_diag["status"] == "외내전(요족) 위험 감지"
        assert "CH6" in sent_diag["issue_zone"]
    finally:
        patcher.stop()

def test_diagnosis_normal():
    storage, patcher = setup_firebase_mocks()
    try:
        normal_input = {
            "name": "DiagTest",
            "side": "right",
            "s1": 0.4,
            "s2": 0.3, # 45 kPa
            "s3": 0.3, # 45 kPa
            "s4": 0.3
        }
        client.post("/update", json=normal_input)
        
        diag_path = "insole_live/DiagTest/diagnosis/right"
        sent_diag = storage[diag_path].set.call_args[0][0]
        assert sent_diag["status"] == "정상 보행"
    finally:
        patcher.stop()

if __name__ == "__main__":
    pytest.main([__file__])
