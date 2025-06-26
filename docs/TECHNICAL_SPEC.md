# Technical Specification: Autonomous Telegram-Driven Dev Platform

**Version:** 1.0
**Status:** Core Architecture

## 1. Core Philosophy: A Modular, Extensible Core

The primary goal of this architecture is to create a system that is easy to extend without modifying its core components. We achieve this by adhering to the **Ports & Adapters (Hexagonal) Architecture**.

- **Core Domain (The "Hexagon"):** The business logic, represented by `CrewAI` agents and their interactions, is completely decoupled from the outside world. It knows nothing about Telegram, FastAPI, or specific databases.
- **Adapters:** These are the components that interact with the core. They are divided into two types:
    - **Driving Adapters:** These initiate actions in the core. Examples: `Telegram Bot`, `FastAPI Gateway`. They translate external requests into method calls on the core domain services.
    - **Driven Adapters:** These are used by the core to interact with external systems. Examples: `E2B Sandbox Runner`, `PostgreSQL RAG Store`, `Loki Logger`. The core defines an interface (a "port"), and the adapter implements it.

This design allows us to swap out components easily. We can replace the `Telegram Bot` with a `Discord Bot` or a web interface without touching the agent logic. We can change the sandbox technology without the agents knowing.

---

## 2. System Architecture Overview

| Layer                          | Component / Service                        | Tech‑stack                                                                              | Key duties                                        |
| ------------------------------ | ------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Interface (Driving Adapter)**| **Telegram Bot**                           | `python-telegram-bot` 23.x (async)                                                      | Accept NL jobs, stream progress, send preview URL |
| **API Gateway / Orchestrator** | **FastAPI** + **Redis Streams**            | REST + WebSocket endpoints (`/tasks`, `/tasks/{id}/stream`), auth via Telegram‑id + JWT | Queue & route jobs, expose core to the world      |
| **Multi‑Agent Brain (Core)**   | **CrewAI**                                 | 5 roles (Planner, Coder, Executor, Tester, Reviewer)                                    | Delegates steps, short‑term memory in Redis       |
| **Code Writer (Tool)**         | **Gemini CLI** (Gemini 2.5 Pro)            | Generates / patches code (`git diff`) inside sandbox                                    | An agent tool for code generation                 |
| **Shell Runner (Tool)**        | **Open Interpreter**                       | Produces & executes bash/python cmds in sandbox                                         | An agent tool for shell command execution         |
| **Execution Sandbox (Driven Adapter)** | **E2B Firecracker microVM**        | Isolated VM per step; exposes port 8000 → public HTTPS                                  | Implements the "run environment" port             |
| **Testing / QA (Tool)**        | `pytest` + `ruff`                          | Runs after every diff; must pass before merge                                           | An agent tool for quality assurance               |
| **Knowledge Base (Driven Adapter)** | PostgreSQL 16 + `pgvector`            | Stores dialogs, snippets, infra templates for RAG                                       | Implements the "knowledge" port for agents        |
| **Observability (Adapters)**   | Loki (logs), Prometheus (metrics), Grafana | Collects stdout/stderr, crew logs, queue depth                                          | Implements the "logging" and "metrics" ports      |
| **CI/CD**                      | GitHub Actions + Dagger (Go)               | Mirror sandbox tests, build images, push to GHCR                                        | Infrastructure automation pipeline                |

---

## 3. Data Flow (MVP Example: "Create Hello World")

1.  **User -> Telegram Bot**: User sends a message: `/new_task create Django hello world`.
2.  **Telegram Bot -> API Gateway**: The bot service authenticates the user and sends a structured request to `POST /tasks` on the API Gateway.
3.  **API Gateway -> Redis**: The gateway creates a unique `task_id`, pushes the task into a `tasks_queue` on Redis Streams, and returns the `task_id` to the bot.
4.  **Worker -> Redis**: A worker process is constantly listening to the `tasks_queue`. It picks up the new task.
5.  **Worker -> CrewAI**: The worker initiates a `CrewAI` process, passing the task description to the `Planner` agent.
6.  **CrewAI Agents Interaction**:
    - `Planner` breaks the task down: 1. Create files. 2. Install Django. 3. Run server.
    - `Coder` receives "Create files" sub-task and, using its file-editing tool, generates the necessary `views.py`, `urls.py`, etc.
    - `Executor` receives "Install Django" and "Run server" sub-tasks and uses its shell tool to execute `pip install django` and `python manage.py runserver` inside the **E2B Sandbox**.
    - `Tester` runs checks to ensure the server is up.
7.  **Sandbox -> Worker**: The E2B sandbox exposes the running server's port and returns a public preview URL.
8.  **Worker -> API Gateway**: The worker pushes status updates (and the final URL) to a Redis stream specific to the task (e.g., `task_stream:<task_id>`).
9.  **API Gateway -> Telegram Bot**: The WebSocket connection streams these updates back to the bot, which in turn relays them to the user in the chat. The final message is the preview URL.

---

## 4. Folder Layout & Modularity

This structure is designed for separation of concerns and extensibility.

```
repo-root/
 ├─ .github/workflows/      # CI/CD pipelines (e.g., test, build, deploy)
 ├─ contracts/              # OpenAPI schemas and shared Pydantic models
 ├─ data/                   # Persistent data for local dev (e.g., postgres data)
 ├─ infrastructure/         # IaC (Terraform/Pulumi) and Dagger for CI environments
 │   ├─ k8s/               # Kubernetes manifests and Helm charts
 │   ├─ monitoring/         # Prometheus rules, Grafana dashboards
 │   └─ security/           # AppArmor/SELinux profiles, security policies
 ├─ scripts/                # Helper scripts (e.g., quick_demo.sh, new_service.py)
 ├─ tests/                  # End-to-end and integration tests for the whole system
 │
 ├─ services/               # Each sub-folder is a separate, deployable microservice
 │   ├─ api_gateway/        # FastAPI service - entry point for all requests
 │   ├─ telegram_bot/       # Telegram bot service - user interface
 │   └─ worker/             # Listens to Redis and runs CrewAI tasks
 │
 └─ agents/                 # The "brain" of the system. The core domain logic.
     ├─ crew_graph.py       # Defines the agent crew, their roles, and workflow
     ├─ tools/              # Reusable tools for agents (RAG, Shell, File Edit)
     └─ tests_agent/        # Unit tests specifically for the agents and their tools
```

### How to Extend the System:

*   **To add a new agent:** Create a new agent definition and add it to `agents/crew_graph.py`. No other service needs to be aware of this change.
*   **To add a new tool for agents:** Create a new file in `agents/tools/` and grant it to the relevant agent in `crew_graph.py`.
*   **To add a new interface (e.g., Discord bot):** Create a new microservice in `services/discord_bot/`. This new service will talk to the `api_gateway` just like the `telegram_bot` does. The core `agents` logic remains untouched.
*   **To change the sandbox technology:** Create a new implementation of the shell execution tool in `agents/tools/` that uses the new technology. Update `crew_graph.py` to use the new tool. The `Executor` agent's logic doesn't change.

---

## 5. API Contracts & Data Models

### 5.1 Core Data Models (Pydantic)

```python
# contracts/models/task.py
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    SHELL_COMMAND = "shell_command"
    DEV_PIPELINE = "dev_pipeline"

class Task(BaseModel):
    id: str = Field(..., description="Unique task identifier")
    user_id: str = Field(..., description="Telegram user ID")
    input_text: str = Field(..., description="Original user request")
    task_type: Optional[TaskType] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### 5.2 API Endpoints

```yaml
# contracts/openapi/api_gateway.yaml
openapi: 3.0.0
info:
  title: AI Dev Platform API
  version: 1.0.0

paths:
  /tasks:
    post:
      summary: Create new task
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTaskRequest'
      responses:
        201:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
  
  /tasks/{task_id}:
    get:
      summary: Get task status
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
  
  /tasks/{task_id}/stream:
    get:
      summary: Stream task updates via WebSocket
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
```

### 5.3 Message Queue Schema

```python
# contracts/events/task_events.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class TaskCreatedEvent(BaseModel):
    task_id: str
    user_id: str
    input_text: str
    timestamp: datetime

class TaskRoutedEvent(BaseModel):
    task_id: str
    task_type: TaskType
    confidence: float
    timestamp: datetime

class TaskProgressEvent(BaseModel):
    task_id: str
    agent_name: str
    message: str
    percentage: Optional[int] = None
    timestamp: datetime

class TaskCompletedEvent(BaseModel):
    task_id: str
    result: Dict[str, Any]
    execution_time_ms: int
    timestamp: datetime
```

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **Response time**: < 500ms for intent routing
- **Shell command execution**: < 5s for 95% of commands
- **Dev pipeline**: < 2min for simple tasks
- **Concurrent users**: Support 100 simultaneous users

### 6.2 Security
- **Authentication**: JWT tokens with 24h expiry
- **Rate limiting**: 10 req/min per user, 100 req/min global
- **Sandbox escape**: Zero tolerance, immediate shutdown
- **Secrets rotation**: Every 90 days automated

### 6.3 Reliability
- **Uptime SLA**: 99.5% (excluding planned maintenance)
- **Data durability**: 99.999% for task history
- **Recovery time**: < 5 minutes for critical failures
- **Backup frequency**: Every 6 hours

### 6.4 Scalability
- **Horizontal scaling**: Worker nodes (2-10 instances)
- **Queue depth**: Handle 1000 pending tasks
- **Storage growth**: 1GB/month estimated
- **LLM fallback**: Multiple provider support

---

## 7. Deployment Architecture

### 7.1 Development Environment
```
Single Docker Compose stack:
- All services in one docker-compose.yml
- SQLite for persistence
- Local file mounts for hot-reload
- Mocked LLM responses for testing
```

### 7.2 Production Environment
```
Kubernetes cluster (3 nodes minimum):
- Node 1: Control plane + API Gateway
- Node 2: Worker pods + Redis
- Node 3: PostgreSQL + monitoring stack

Load balancer → Ingress → Services
```

### 7.3 Monitoring Stack
```
- Prometheus: Metrics collection (15s interval)
- Loki: Log aggregation (all containers)
- Grafana: Dashboards and alerts
- Jaeger: Distributed tracing
- AlertManager: PagerDuty integration
``` 