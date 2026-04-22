import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Mocking modules before any other imports that might trigger their loading
mock_modules = {
    "brand_brain.synthesis": MagicMock(),
    "brand_brain.engine": MagicMock(),
    "fastapi": MagicMock(),
    "requests": MagicMock(),
}

with patch.dict("sys.modules", mock_modules):
    from brand_brain.orchestrator import MasterOrchestrator

def test_save_vbrain(tmp_path):
    """Verifies that vbrain state is correctly saved to the file system."""
    # Setup: Create a workspace
    workspace = tmp_path / "brand-engine"
    workspace.mkdir()

    # Initialize Orchestrator.
    # Since we named the dir "brand-engine", project_root will be same as workspace.
    orch = MasterOrchestrator(str(workspace))

    # Verify vbrain_path is what we expect
    expected_vbrain_path = workspace / "brand_brain" / "vbrain.json"
    assert orch.vbrain_path == expected_vbrain_path

    # Modify vbrain (actual attribute name in code is 'vbrain')
    test_data = {"test_key": "test_value"}
    orch.vbrain["test_payload"] = test_data

    # Execute
    orch.save_vbrain()

    # Verify file existence
    assert orch.vbrain_path.exists()

    # Verify file content
    with open(orch.vbrain_path, 'r') as f:
        saved_data = json.load(f)

    assert saved_data["test_payload"] == test_data
    # Verify that default structure is also present
    assert "learned_patterns" in saved_data
    assert "inspiration_urls" in saved_data

def test_save_vbrain_updates_existing_file(tmp_path):
    """Verifies that save_vbrain updates an existing vbrain.json file."""
    # Setup: Create a workspace
    workspace = tmp_path / "brand-engine"
    workspace.mkdir()

    # Pre-create vbrain.json
    vbrain_dir = workspace / "brand_brain"
    vbrain_dir.mkdir(parents=True)
    vbrain_file = vbrain_dir / "vbrain.json"
    initial_data = {"initial": "data", "inspiration_urls": []}
    with open(vbrain_file, 'w') as f:
        json.dump(initial_data, f)

    orch = MasterOrchestrator(str(workspace))

    # Verify it loaded the initial data
    assert orch.vbrain["initial"] == "data"

    # Modify and save
    orch.vbrain["new_key"] = "new_value"
    orch.save_vbrain()

    # Verify
    with open(vbrain_file, 'r') as f:
        saved_data = json.load(f)

    assert saved_data["initial"] == "data"
    assert saved_data["new_key"] == "new_value"
