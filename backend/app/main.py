from fastapi import FastAPI
from dotenv import load_dotenv
import os

# 1. Cargar variables de entorno al inicio
load_dotenv()

# 2. Configuración básica de la App
app = FastAPI(
    title=os.getenv("PROJECT_NAME", "Inmobiliaria API"),
    version=os.getenv("VERSION", "1.0.0"),
    description="API Híbrida para gestión inmobiliaria"
)

# 3. Ruta de prueba (Health Check)
@app.get("/", tags=["General"])
def read_root():
    return {"message": "Bienvenido a la API Inmobiliaria", "status": "OK"}

# 4. Ruta para verificar versión (siguiendo tu estructura /api/v1)
@app.get("/api/v1/health", tags=["General"])
def health_check():
    return {"status": "active", "version": "v1"}
