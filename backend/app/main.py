"""
FastAPI Main Application
Sistema Inmobiliario - Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.dbConfig.databaseSession import get_db, get_pool_status, test_db_connection

# ==========================================
# IMPORTAR ROUTERS
# ==========================================
from app.controllers.authController import router as auth_router
from app.controllers.userController import router as user_router
from app.controllers.propertyController import router as property_router
from app.controllers.advisorController import router as advisor_router
from app.controllers.appointmentController import router as appointment_router
from app.controllers.favoriteController import router as favorite_router

# Ejecutar prueba al iniciar
test_db_connection()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,  # ← USAR settings
    description="API para sistema inmobiliario con aprobación de propiedades",
    version=settings.APP_VERSION,  # ← USAR settings
    docs_url=settings.DOCS_URL,  # ← USAR settings
    redoc_url=settings.REDOC_URL  # ← USAR settings
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ← USAR settings
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,  # ← USAR settings
    allow_methods=settings.CORS_ALLOW_METHODS,  # ← USAR settings
    allow_headers=settings.CORS_ALLOW_HEADERS,  # ← USAR settings
)

# ==========================================
# INCLUIR ROUTERS
# ==========================================
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)
app.include_router(advisor_router)
app.include_router(appointment_router)
app.include_router(favorite_router)

# ==========================================
# ENDPOINTS PÚBLICOS
# ==========================================

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raíz — confirma que la API está corriendo."""
    return {
        "message": "Inmobiliaria API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check básico — para balanceadores y monitoreo."""
    return {"status": "healthy", "service": "inmobiliaria-api"}


@app.get("/health/db", tags=["Health"])
def health_check_database():
    """Health check con verificación de conexión a PostgreSQL."""
    db_connected = test_db_connection()
    pool_stats = get_pool_status() if db_connected else None
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": {"connected": db_connected, "type": "postgresql"},
        "connection_pool": pool_stats
    }


# ==========================================
# EVENT HANDLERS
# ==========================================

@app.on_event("startup")
async def startup_event():
    """
    Evento al iniciar la aplicación
    
    Verifica la conexión a la base de datos.
    """
    print("="*80)
    print("🚀 Iniciando Inmobiliaria API...")
    print("="*80)
    
    if test_db_connection():
        print("✅ Conexión a PostgreSQL: OK")
        pool = get_pool_status()
        print(f"📊 Connection Pool: {pool['pool_size']} conexiones disponibles")
    else:
        print("❌ Error: No se pudo conectar a PostgreSQL")
    
    print("="*80)
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("="*80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento al cerrar la aplicación
    """
    print("👋 Cerrando Inmobiliaria API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    