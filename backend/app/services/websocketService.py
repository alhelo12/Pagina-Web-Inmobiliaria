"""
WebSocket Service - Lógica de negocio para WebSocket unificado

Maneja conexión, autenticación, rate limiting, mensajes y typing indicators.
"""

import json
import time
from collections import defaultdict
from typing import Optional

from fastapi import Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.websocket import manager
from app.core.security import decode_access_token
from app.dbConfig.databaseSession import SessionLocal
from app.services import messageService
from app.models import User


# Configuración
MAX_MESSAGES_PER_MINUTE = 30
MAX_MESSAGE_LENGTH = 5000


def _get_recipient_user_id(conversation, sender_user_id: int) -> Optional[int]:
    if conversation.user_id == sender_user_id:
        return conversation.advisor.user_id if conversation.advisor else None
    return conversation.user_id


def _is_participant(conversation, user_id: int, db: Session) -> bool:
    return conversation.user_id == user_id or (conversation.advisor and conversation.advisor.user_id == user_id)


async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket unificado para chat y notificaciones en tiempo real.

    Conexion: ws://localhost:8000/ws?token=JWT_TOKEN

    Mensajes recibidos:
    - {"type": "ping"}
    - {"type": "message", "conversation_id": 1, "content": "..."}
    - {"type": "typing", "conversation_id": 1}

    Mensajes enviados:
    - {"type": "pong"}
    - {"type": "message", "data": {...}}
    - {"type": "typing", "conversation_id": 1, "user_id": 1}
    - {"type": "notification", "data": {...}}
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

    # Verificar que el usuario existe y está activo
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            await websocket.close(code=4003, reason="Usuario inactivo o no encontrado")
            return
    finally:
        db.close()

    await manager.connect(websocket, user_id)

    # Rate limiting simple por conexión
    message_timestamps = defaultdict(list)

    try:
        while True:
            data = await websocket.receive_json()

            # Validar tamaño del mensaje
            if len(json.dumps(data)) > MAX_MESSAGE_LENGTH:
                await websocket.send_json({"type": "error", "message": "Mensaje demasiado largo"})
                continue

            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "message":
                conversation_id = data.get("conversation_id")
                content = data.get("content", "").strip()

                if not conversation_id or not content:
                    continue

                # Rate limiting
                now = time.time()
                message_timestamps[user_id] = [ts for ts in message_timestamps[user_id] if now - ts < 60]
                if len(message_timestamps[user_id]) >= MAX_MESSAGES_PER_MINUTE:
                    await websocket.send_json({"type": "error", "message": "Demasiados mensajes. Espere un momento."})
                    continue
                message_timestamps[user_id].append(now)

                db = SessionLocal()
                try:
                    conversation = messageService.get_conversation_by_id(db, conversation_id)
                    if not conversation:
                        continue

                    if not _is_participant(conversation, user_id, db):
                        continue

                    message = messageService.send_message(
                        db=db, conversation_id=conversation_id, sender_id=user_id, content=content
                    )

                    db.refresh(conversation)

                    recipient_id = _get_recipient_user_id(conversation, user_id)

                    sender_user = db.query(User).filter(User.id == user_id).first()
                    sender_name = sender_user.full_name if sender_user else payload.get("email", "Usuario")
                    is_client = conversation.user_id == user_id

                    message_data = {
                        "type": "message",
                        "data": {
                            "id": message.id,
                            "conversation_id": message.conversation_id,
                            "sender_id": message.sender_id,
                            "content": message.content,
                            "is_read": message.is_read,
                            "created_at": message.created_at.isoformat() if message.created_at else None,
                            "sender": {"id": user_id, "name": sender_name, "role": "client" if is_client else "advisor"}
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
                        if conversation and _is_participant(conversation, user_id, db):
                            recipient_id = _get_recipient_user_id(conversation, user_id)
                            if recipient_id:
                                await manager.send_personal_message(
                                    {"type": "typing", "conversation_id": conversation_id, "user_id": user_id},
                                    recipient_id
                                )
                    finally:
                        db.close()

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)
        raise
