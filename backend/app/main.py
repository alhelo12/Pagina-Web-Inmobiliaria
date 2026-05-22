"""
FastAPI Main Application
Sistema Inmobiliario - Backend API
"""

import logging
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
from app.models import Advisor, User

logger = logging.getLogger(__name__)

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

def _is_participant(conversation, user_id: int, db) -> bool:
    """Verifica que el usuario sea participante de la conversación"""
    if conversation.user_id == user_id:
        return True
    if conversation.advisor:
        return conversation.advisor.user_id == user_id
    return False

def _get_recipient_user_id(conversation, sender_user_id: int) -> Optional[int]:
    """Obtiene el user_id del destinatario (no el advisor_id)"""
    if conversation.user_id == sender_user_id:
        return conversation.advisor.user_id if conversation.advisor else None
    return conversation.user_id

@app.websocket("/ws/messages")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket para chat en tiempo real.
    
    Conexion: ws://localhost:8000/ws/messages?token=JWT_TOKEN
    
    Mensajes enviados:
    - {"type": "message", "data": {...}} — nuevo mensaje recibido
    - {"type": "typing", "user_id": 1} — usuario esta escribiendo
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
        await websocket.close(code=4001, reason="Token invalido")
        return
    
    user_id = int(payload.get("sub", 0))
    if not user_id:
        await websocket.close(code=4001, reason="Token invalido")
        return
    
    await manager.connect(websocket, user_id)
    logger.info(f"WebSocket conectado: user_id={user_id}")
    
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
                    conversation = messageService.get_conversation_by_id(db, conversation_id)
                    if not conversation:
                        logger.warning(f"Conversacion {conversation_id} no encontrada para user {user_id}")
                        continue
                    
                    if not _is_participant(conversation, user_id, db):
                        logger.warning(f"User {user_id} intento enviar mensaje en conversacion {conversation_id} sin acceso")
                        continue
                    
                    message = messageService.send_message(
                        db=db,
                        conversation_id=conversation_id,
                        sender_id=user_id,
                        content=content
                    )
                    
                    db.refresh(conversation)
                    
                    recipient_id = _get_recipient_user_id(conversation, user_id)
                    logger.info(f"WS message: sender={user_id}, conv={conversation_id}, recipient_user_id={recipient_id}, msg_id={message.id}")
                    
                    sender_user = db.query(User).filter(User.id == user_id).first()
                    sender_name = sender_user.full_name if sender_user else payload.get("email", "Usuario")
                    is_client = conversation.user_id == user_id
                    
                    sender_info = {
                        "id": user_id,
                        "name": sender_name,
                        "role": "client" if is_client else "advisor"
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
                        found = recipient_id in manager.active_connections
                        logger.info(f"Enviando a recipient {recipient_id}, conectado={found}")
                        await manager.send_personal_message(message_data, recipient_id)
                    else:
                        logger.warning(f"No se pudo determinar recipient_id para mensaje {message.id}")
                    
                finally:
                    db.close()
            
            elif msg_type == "typing":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    db = SessionLocal()
                    try:
                        conversation = messageService.get_conversation_by_id(db, conversation_id)
                        if conversation and _is_participant(conversation, user_id, db):
                            recipient_id = _get_recipient_user_id(conversation, user_id)
                            if recipient_id:
                                typing_data = {
                                    "type": "typing",
                                    "conversation_id": conversation_id,
                                    "user_id": user_id
                                }
                                await manager.send_personal_message(typing_data, recipient_id)
                    finally:
                        db.close()
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: user_id={user_id}")
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error para user {user_id}: {e}", exc_info=True)
        manager.disconnect(websocket, user_id)


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
