from fastapi import FastAPI

app = FastAPI(title="FeverUp Challenge - Events provider")

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}
