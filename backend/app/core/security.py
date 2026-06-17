"""
Core: Security

Funciones para manejo de JWT (JSON Web Tokens) y seguridad.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from app.core.config import settings
from app.services.authService import verify_password, hash_password as get_password_hash

load_dotenv()

# ==========================================
# CONFIGURACIÓN
# ==========================================

# Usar settings en lugar de leer directamente del .env
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ==========================================
# FUNCIONES JWT
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token JWT
    
    Args:
        data: Datos a codificar en el token (típicamente {"sub": user_id, "role": "admin"})
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        Token JWT codificado
        
    Ejemplo:
        token = create_access_token({"sub": "123", "role": "admin"})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodificar y verificar token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Datos decodificados del token o None si es inválido
        
    Ejemplo:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_token_for_user(user_id: int, email: str, role_name: str) -> str:
    """
    Crear token JWT para un usuario específico
    
    Args:
        user_id: ID del usuario
        email: Email del usuario
        role_name: Nombre del rol (admin, advisor, client)
        
    Returns:
        Token JWT
        
    Ejemplo:
        token = create_token_for_user(123, "user@example.com", "admin")
    """
    token_data = {
        "sub": str(user_id),  # Subject (estándar JWT)
        "email": email,
        "role": role_name
    }
    
    return create_access_token(token_data)


def verify_token(token: str) -> Optional[dict]:
    """
    Alias de decode_access_token para claridad
    
    Args:
        token: Token JWT
        
    Returns:
        Payload decodificado o None
    """
    return decode_access_token(token)


def create_email_token(email: str, purpose: str, expires_minutes: int = 15) -> str:
    """
    Crear token JWT para verificación de email o reseteo de contraseña.
    
    Args:
        email: Email del usuario
        purpose: 'email_verify' o 'password_reset'
        expires_minutes: Minutos hasta expiración (default 15)
        
    Returns:
        Token JWT
    """
    token_data = {
        "sub": email,
        "purpose": purpose
    }
    return create_access_token(token_data, timedelta(minutes=expires_minutes))
