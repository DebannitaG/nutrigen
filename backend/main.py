from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.database import init_db
from services.ml_service import train_model
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HealthGuard AI",
    description="Scalable, Explainable Nutrition Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting HealthGuard AI...")
    init_db()
    logger.info("Database initialized")
    model_path = os.path.join(os.path.dirname(__file__), "models/rf_model.pkl")
    if not os.path.exists(model_path):
        logger.info("Training ML model...")
        acc = train_model()
        logger.info(f"Model trained with accuracy: {acc:.2f}")
    logger.info("HealthGuard AI is ready!")

@app.get("/")
async def root():
    return {"message": "HealthGuard AI API", "docs": "/docs"}