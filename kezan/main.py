from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kezan.routes import profile_routes

app = FastAPI(title="Kezan Protocol API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajusta según tu configuración
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de perfiles
app.include_router(profile_routes.router)

@app.get("/")
async def root():
    return {"message": "Kezan Protocol API"}
