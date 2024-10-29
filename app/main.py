"""Main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.security import CORS_CONFIG
from app.db.session import create_tables
from app.exceptions.handler import search_exception_handler

app = FastAPI(title="FeverUp Challenge - Events provider")

# Important to add CORS middleware before routes and exception handlers
app.add_middleware(CORSMiddleware, **CORS_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app.router.lifespan_context = lifespan

app.include_router(router)

app.add_exception_handler(HTTPException, search_exception_handler)
app.add_exception_handler(RequestValidationError, search_exception_handler)
