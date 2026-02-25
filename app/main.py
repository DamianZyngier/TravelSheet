from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys

# Konfiguracja logowania do stdout dla GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("uvicorn")

from .database import engine
from . import models
from .api.api import api_router

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Cheatsheet API",
    description="Polish travel information aggregator",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Travel Cheatsheet API",
        "version": "1.0.0",
        "endpoints": {
            "countries": "/api/countries",
            "country": "/api/countries/{iso_code}",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
