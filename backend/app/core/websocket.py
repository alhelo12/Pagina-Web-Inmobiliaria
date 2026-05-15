"""
WebSocket Manager

Gestiona conexiones WebSocket para chat en tiempo real.
"""

from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """
    Gestiona conexiones WebSocket activas.
    
    Mantiene un diccionario de user_id -> set de WebSockets
    para soportar múltiples conexiones por usuario.
    """
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Acepta y registra una nueva conexión WebSocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Elimina una conexión WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """
        Envía un mensaje a un usuario específico.
        
        Args:
            message: Diccionario con datos del mensaje
            user_id: ID del usuario destinatario
        """
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict, exclude_user_id: int = None):
        """
        Envía un mensaje a todos los usuarios conectados.
        
        Args:
            message: Diccionario con datos del mensaje
            exclude_user_id: ID del usuario a excluir (el remitente)
        """
        for user_id, connections in list(self.active_connections.items()):
            if user_id == exclude_user_id:
                continue
            
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            for conn in disconnected:
                self.disconnect(conn, user_id)


manager = ConnectionManager()
