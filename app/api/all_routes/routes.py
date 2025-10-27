# app/api/all_routes/routes.py
from fastapi import FastAPI
from . import all_imports

app = FastAPI(title="FunctionLab API")

@app.get("/")
async def root():
    return {"message": "FunctionLab API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

for r in all_imports.routers:
    app.include_router(r)
