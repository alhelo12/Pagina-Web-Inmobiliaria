"""
FastAPI Main Application
Sistema Inmobiliario - Backend API
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from typing import Optional

from app.core.config import settings
from app.core.rateLimiter import limiter
from app.core.request_id import RequestIDMiddleware
from app.core.logging import configure_logging
from app.dbConfig.databaseSession import get_pool_status, test_db_connection
from app.services.websocketService import websocket_endpoint

# ==========================================
# IMPORTAR ROUTERS
# ==========================================
from app.controllers.authController import router as auth_router
from app.controllers.userController import router as user_router
from app.controllers.propertyController import router as property_router
from app.controllers.advisorController import router as advisor_router
from app.controllers.appointmentController import router as appointment_router
from app.controllers.favoriteController import router as favorite_router
from app.controllers.notificationController import router as notification_router
from app.controllers.notificationPreferenceController import router as notification_preference_router
from app.controllers.messageController import router as message_router
from app.controllers.postSaleController import router as post_sale_router
from app.controllers.clientAdvisorController import router as client_advisor_router
from app.controllers.activityLogController import router as activity_log_router
from app.controllers.contactController import router as contact_router
from app.controllers.constantsController import router as constants_router

configure_logging(
    level="INFO" if settings.ENVIRONMENT == "production" else "DEBUG",
    json_output=settings.ENVIRONMENT == "production",
    include_request_id=True
)

logger = logging.getLogger(__name__)

# Ejecutar prueba al iniciar
test_db_connection()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para sistema inmobiliario con aprobación de propiedades",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Request ID middleware (debe ir antes de CORS para capturar todos)
app.add_middleware(RequestIDMiddleware)

# Rate Limiting
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Demasiadas peticiones. Por favor intenta más tarde.",
            "retry_after": str(exc.detail)
        }
    )

# Servir archivos estaticos (imagenes de propiedades)
media_dir = Path("media")
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

# ==========================================
# INCLUIR ROUTERS
# ==========================================
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(property_router)
app.include_router(client_advisor_router)
app.include_router(advisor_router)
app.include_router(appointment_router)
app.include_router(favorite_router)
app.include_router(notification_router)
app.include_router(notification_preference_router)
app.include_router(message_router)
app.include_router(post_sale_router)
app.include_router(activity_log_router)
app.include_router(contact_router)
app.include_router(constants_router)

# ==========================================
# WEBSOCKET UNIFICADO
# ==========================================

@app.websocket("/ws")
async def websocket_route(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket unificado para chat y notificaciones en tiempo real.
    Delegado a websocketService para mantener main.py limpio.
    """
    await websocket_endpoint(websocket, token)


# ==========================================
# ENDPOINTS PUBLICOS
# ==========================================

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz — confirma que la API esta corriendo."""
    return {
        "message": "Inmobiliaria API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check basico — para balanceadores y monitoreo."""
    return {"status": "healthy", "service": "inmobiliaria-api"}


@app.get("/health/db", tags=["Health"])
def health_check_database():
    """Health check con verificacion de conexion a PostgreSQL."""
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
    Evento al iniciar la aplicacion
    
    Verifica la conexion a la base de datos.
    """
    print("="*80)
    print("Iniciando Inmobiliaria API...")
    print("="*80)
    
    if test_db_connection():
        print("Conexion a PostgreSQL: OK")
        pool = get_pool_status()
        print(f"Connection Pool: {pool['pool_size']} conexiones disponibles")
    else:
        print("Error: No se pudo conectar a PostgreSQL")
    
    print("="*80)
    print(f"Documentacion disponible en: http://localhost:8000{settings.DOCS_URL}")
    print("="*80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento al cerrar la aplicacion
    """
    print("Cerrando Inmobiliaria API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
