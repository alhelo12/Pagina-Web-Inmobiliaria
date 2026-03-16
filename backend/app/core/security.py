"""
Core: Security

Funciones para manejo de JWT (JSON Web Tokens) y seguridad.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONFIGURACIÓN
# ==========================================

SECRET_KEY = os.getenv("SECRET_KEY", "desarrollo_secret_key_temporal_12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================================
# FUNCIONES DE HASHING (ya existen en authService, pero aquí por organización)
# ==========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña coincide con su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en BD
        
    Returns:
        True si coincide, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generar hash de una contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
