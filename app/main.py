"""Main application."""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel

from app.api.routes import router
from app.db.session import engine
from app.exceptions.handler import search_exception_handler

app = FastAPI(title="FeverUp Challenge - Events provider")

# Create all tables on startup
SQLModel.metadata.create_all(engine)

app.include_router(router)

app.add_exception_handler(HTTPException, search_exception_handler)
app.add_exception_handler(RequestValidationError, search_exception_handler)
