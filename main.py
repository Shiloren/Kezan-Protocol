from fastapi import FastAPI
from kezan.api import router as kezan_router

app = FastAPI(title="Kezan Protocol")

app.include_router(kezan_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a Kezan Protocol: Inteligencia de Mercado para WoW"}
