"""Main application."""

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.routes import router
from app.db.session import engine

app = FastAPI(title="FeverUp Challenge - Events provider")

# Create all tables on startup
SQLModel.metadata.create_all(engine)

app.include_router(router)
