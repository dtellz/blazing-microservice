from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="FeverUp Challenge - Events provider")

app.include_router(router)
