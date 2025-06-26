from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Локальный импорт из нашего воркера
from services.worker.main import run_crew

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Development Platform API",
    description="API for managing and interacting with the AI development team.",
    version="0.1.0",
)

class HealthCheck(BaseModel):
    status: str = "ok"

class Task(BaseModel):
    user_id: int
    text: str
    
class TaskReceipt(BaseModel):
    task_id: str
    status: str = "received"
    message: str

@app.get("/", tags=["Health Check"])
def health_check() -> HealthCheck:
    """
    Проверка работоспособности API.
    Возвращает статус 'ok', если сервис работает.
    """
    logger.info("Health check endpoint was called.")
    return HealthCheck(status="ok")

@app.post("/tasks/", tags=["Tasks"], status_code=202)
def receive_task(task: Task) -> TaskReceipt:
    """
    Принимает задачу от Telegram-бота и передает ее в Worker.
    """
    logger.info(f"Received task from user {task.user_id}: '{task.text}'")
    
    # Прямой вызов воркера (в будущем здесь будет очередь)
    try:
        result = run_crew(task.text)
        logger.info(f"Crew finished with result: {result}")
        # TODO: Отправить результат обратно пользователю в Telegram
        
        return TaskReceipt(
            task_id="crew_task_finished", # Временный ID
            message=f"Crew successfully processed the task. Result: {result}"
        )
    except Exception as e:
        logger.error(f"An error occurred in the worker: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the task in the worker.")

@app.on_event("startup")
async def startup_event():
    logger.info("API Gateway starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API Gateway shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 