import pytest
from unittest.mock import patch, MagicMock
from services.worker.main import run_crew

# We need to mock one level deeper to bypass LiteLLM's key validation
LLM_CALL_PATH = "litellm.completion"

@patch(LLM_CALL_PATH)
def test_run_crew_successful_execution(mock_litellm_completion, monkeypatch):
    """
    Tests the full execution of run_crew by mocking the final LLM call.
    """
    # Arrange
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-but-now-it-doesnt-matter")
    # LiteLLM expects a specific dictionary structure, so we mock that.
    # We use a MagicMock that can be instantiated with the expected structure.
    model_response = MagicMock()
    model_response.choices = [MagicMock()]
    model_response.choices[0].message.content = "This is the final mocked research report."
    mock_litellm_completion.return_value = model_response
    
    # Act
    result = run_crew("Analyze the impact of AI on software development.")

    # Assert
    assert mock_litellm_completion.call_count > 0
    assert result.raw == "This is the final mocked research report."

@patch(LLM_CALL_PATH)
def test_run_crew_handles_llm_exception(mock_litellm_completion, monkeypatch):
    """
    Tests that if the LLM call fails, the exception is caught and handled.
    """
    # Arrange
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-but-now-it-doesnt-matter")
    mock_litellm_completion.side_effect = Exception("LiteLLM is down")

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        run_crew("This will fail.")
    
    assert "An error occurred during crew execution" in str(excinfo.value)
    assert "LiteLLM is down" in str(excinfo.value)
