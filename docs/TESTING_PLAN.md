# Testing Plan

This document outlines the testing strategy for the Autonomous Development Platform.

## 1. Unit Tests

Unit tests are designed to verify the functionality of individual components in isolation.

### 1.1 `api_gateway`
- **`test_health_check`**: Verify that the `/` endpoint returns a `200 OK` status and the expected `{"status": "ok"}` payload.
- **`test_pydantic_models`**: Ensure that `Task` and `TaskReceipt` models correctly validate input data (both valid and invalid cases).

### 1.2 `worker`
- **`test_agent_creation`**: Check if `researcher` and `writer` agents are created with the correct roles, goals, and backstories.
- **`test_task_creation`**: Verify that `create_analysis_task` and `create_report_task` functions return `Task` objects with the correct descriptions and assigned agents.
- **`test_crew_creation`**: Ensure the `create_crew` function assembles a `Crew` with the correct agents and tasks in the specified order.

## 2. Integration Tests

Integration tests are designed to verify that different components of the system work together as expected.

### 2.1 `API Gateway -> Worker`
- **`test_task_submission_flow`**:
  - **Objective**: Verify that a POST request to `/tasks/` on the API Gateway successfully triggers the `run_crew` function in the worker.
  - **Method**:
    - Use `pytest` and `TestClient` from FastAPI.
    - Use `unittest.mock.patch` to mock the `run_crew` function to avoid actual LLM calls.
    - Send a valid payload to the `/tasks/` endpoint.
    - **Assert**:
      - The endpoint returns a `202` status code.
      - The mocked `run_crew` function was called exactly once with the text from the payload.
      - The response body contains the (mocked) result from the crew.
- **`test_task_submission_worker_error`**:
  - **Objective**: Verify that if the worker raises an exception, the API Gateway catches it and returns a `500 Internal Server Error`.
  - **Method**:
    - Mock `run_crew` to raise an exception.
    - Send a valid payload to `/tasks/`.
    - **Assert**:
      - The endpoint returns a `500` status code.
      - The response detail indicates a worker error.

## 3. End-to-End (E2E) Tests (Manual for now)

E2E tests verify the complete workflow from the user's perspective.

- **`test_full_flow_manual`**:
  - **Steps**:
    1. Create a `.env` file with a valid `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY`.
    2. Run `docker-compose up --build`.
    3. Open Telegram and send a message to the bot.
  - **Expected Result**:
    - The bot responds that the task is received.
    - The bot sends a second message with the analysis result from the AI crew.
    - Logs in the `api_gateway` and `telegram_bot` containers show the processing flow without errors. 