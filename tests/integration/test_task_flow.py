import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from services.api_gateway.main import app

client = TestClient(app)

@patch('services.api_gateway.main.run_crew')
def test_submit_task_success(mock_run_crew):
    """
    Tests the successful submission of a task.
    Mocks the worker's run_crew function.
    """
    mock_run_crew.return_value = "This is a mock result."
    task_payload = {"user_id": 123, "text": "Analyze this text"}

    response = client.post("/tasks/", json=task_payload)

    assert response.status_code == 202
    mock_run_crew.assert_called_once_with("Analyze this text")
    response_data = response.json()
    assert response_data["task_id"] == "crew_task_finished"
    assert "mock result" in response_data["message"]


@patch('services.api_gateway.main.run_crew')
def test_submit_task_worker_exception(mock_run_crew):
    """
    Tests how the API Gateway handles an exception from the worker.
    """
    mock_run_crew.side_effect = Exception("Worker failed!")
    task_payload = {"user_id": 456, "text": "This one will fail"}

    response = client.post("/tasks/", json=task_payload)

    assert response.status_code == 500
    assert "An error occurred while processing the task in the worker" in response.json()["detail"]
