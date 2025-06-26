from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

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

@app.get("/", tags=["Health Check"])
def health_check() -> HealthCheck:
    """
    Проверка работоспособности API.
    Возвращает статус 'ok', если сервис работает.
    """
    logger.info("Health check endpoint was called.")
    return HealthCheck(status="ok")

@app.on_event("startup")
async def startup_event():
    logger.info("API Gateway starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API Gateway shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 