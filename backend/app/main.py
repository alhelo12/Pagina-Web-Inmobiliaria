"""
FastAPI Main Application
Sistema Inmobiliario - Backend API
"""

from pathlib import Path
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from typing import Optional

from app.core.config import settings
from app.core.rateLimiter import limiter
from app.core.activityLogger import ActivityLoggerMiddleware
from app.core.websocket import manager
from app.dbConfig.databaseSession import get_db, get_pool_status, test_db_connection, SessionLocal
from app.core.security import decode_access_token
from app.services import messageService
from app.models import Advisor

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
from app.controllers.messageController import router as message_router
from app.controllers.postSaleController import router as post_sale_router
from app.controllers.clientAdvisorController import router as client_advisor_router
from app.controllers.activityLogController import router as activity_log_router

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

# Activity Logger Middleware
app.add_middleware(ActivityLoggerMiddleware)

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
app.include_router(advisor_router)
app.include_router(appointment_router)
app.include_router(favorite_router)
app.include_router(notification_router)
app.include_router(message_router)
app.include_router(post_sale_router)
app.include_router(client_advisor_router)
app.include_router(activity_log_router)

# ==========================================
# WEBSOCKET — Chat en tiempo real
# ==========================================

@app.websocket("/ws/messages")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket para chat en tiempo real.
    
    Conexión: ws://localhost:8000/ws/messages?token=JWT_TOKEN
    
    Mensajes enviados:
    - {"type": "message", "data": {...}} — nuevo mensaje recibido
    - {"type": "typing", "user_id": 1} — usuario está escribiendo
    - {"type": "pong"} — respuesta a ping
    
    Mensajes recibidos:
    - {"type": "message", "conversation_id": 1, "content": "..."}
    - {"type": "typing", "conversation_id": 1}
    - {"type": "ping"}
    """
    if not token:
        await websocket.close(code=4001, reason="Token requerido")
        return
    
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    user_id = payload.get("user_id")
    if not user_id:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "message":
                conversation_id = data.get("conversation_id")
                content = data.get("content", "").strip()
                
                if not conversation_id or not content:
                    continue
                
                db = SessionLocal()
                try:
                    message = messageService.send_message(
                        db=db,
                        conversation_id=conversation_id,
                        sender_id=user_id,
                        content=content
                    )
                    
                    conversation = messageService.get_conversation_by_id(db, conversation_id)
                    
                    recipient_id = None
                    if conversation:
                        if conversation.user_id == user_id:
                            recipient_id = conversation.advisor_id
                            sender_info = {
                                "id": user_id,
                                "name": payload.get("email", "Usuario"),
                                "role": "client"
                            }
                        else:
                            recipient_id = conversation.user_id
                            sender_info = {
                                "id": user_id,
                                "name": conversation.advisor.user.full_name if conversation.advisor else "Asesor",
                                "role": "advisor"
                            }
                    
                    message_data = {
                        "type": "message",
                        "data": {
                            "id": message.id,
                            "conversation_id": message.conversation_id,
                            "sender_id": message.sender_id,
                            "content": message.content,
                            "is_read": message.is_read,
                            "created_at": message.created_at.isoformat() if message.created_at else None,
                            "sender": sender_info
                        }
                    }
                    
                    await manager.send_personal_message(message_data, user_id)
                    
                    if recipient_id:
                        await manager.send_personal_message(message_data, recipient_id)
                    
                finally:
                    db.close()
            
            elif msg_type == "typing":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    db = SessionLocal()
                    try:
                        conversation = messageService.get_conversation_by_id(db, conversation_id)
                        if conversation:
                            recipient_id = conversation.user_id if conversation.advisor_id == user_id else conversation.advisor_id
                            typing_data = {
                                "type": "typing",
                                "conversation_id": conversation_id,
                                "user_id": user_id
                            }
                            if recipient_id:
                                await manager.send_personal_message(typing_data, recipient_id)
                    finally:
                        db.close()
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)


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
    
