"""
Service: Authentication

Lógica de negocio para autenticación de usuarios.
Maneja registro, login y validación de credenciales.
"""

from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
import bcrypt as _bcrypt

from app.models import User
from app.schemas import UserCreate, UserLogin
from app.services import userService


# ==========================================
# FUNCIONES DE HASHING
# ==========================================

def hash_password(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en la BD
        
    Returns:
        True si coincide, False si no
    """
    return _bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ==========================================
# REGISTRO
# ==========================================

def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Registrar nuevo usuario
    
    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario a registrar
        
    Returns:
        Usuario creado
        
    Raises:
        HTTPException: Si el email ya existe, el rol no existe,
                      o la contraseña no cumple requisitos
    """
    # Validar contraseña
    validate_password_strength(user_data.password)
    
    # Hash de la contraseña
    password_hash = hash_password(user_data.password)
    
    # Crear usuario usando userService
    user = userService.create_user(db, user_data, password_hash)
    
    return user

# ==========================================
# LOGIN
# ==========================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Autenticar usuario con email y contraseña
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si las credenciales son correctas, None si no
    """
    user = userService.get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def login(db: Session, credentials: UserLogin) -> User:
    """
    Login de usuario
    
    Args:
        db: Sesión de base de datos
        credentials: Credenciales (email y password)
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si las credenciales son incorrectas
                      o el usuario está inactivo
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )
    
    return user


# ==========================================
# VALIDACIONES
# ==========================================

def validate_password_strength(password: str) -> bool:
    """
    Validar que la contraseña cumpla con los requisitos mínimos
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una letra
    - Al menos un número
    
    Args:
        password: Contraseña a validar
        
    Returns:
        True si es válida
        
    Raises:
        HTTPException: Si no cumple los requisitos
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    if not any(char.isalpha() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra"
        )
    
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos un número"
        )
    
    return True


def validate_email_available(db: Session, email: str) -> bool:
    """
    Verificar si un email está disponible para registro
    
    Args:
        db: Sesión de base de datos
        email: Email a verificar
        
    Returns:
        True si está disponible, False si ya existe
    """
    return not userService.user_exists(db, email)


# ==========================================
# CAMBIO DE CONTRASEÑA
# ==========================================

def change_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str
) -> User:
    """
    Cambiar contraseña de usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        current_password: Contraseña actual
        new_password: Nueva contraseña
        
    Returns:
        Usuario actualizado
        
    Raises:
        HTTPException: Si el usuario no existe, la contraseña actual
                      es incorrecta, o la nueva no cumple requisitos
    """
    user = userService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar contraseña actual
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar nueva contraseña
    validate_password_strength(new_password)
    
    # Verificar que la nueva sea diferente
    if verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual"
        )
    
    # Actualizar contraseña
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    
    return user


def reset_password(db: Session, user_id: int, new_password: str) -> User:
    """
    Resetear contraseña (para admin)
    
    ADVERTENCIA: No requiere contraseña actual.
    Solo debe usarse por administradores.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        new_password: Nueva contraseña
        
    Returns:
        Usuario actualizado
        
    Raises:
        HTTPException: Si el usuario no existe o la contraseña no cumple requisitos
    """
    user = userService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar nueva contraseña
    validate_password_strength(new_password)
    
    # Actualizar contraseña
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    
    return user


# ==========================================
# UTILIDADES
# ==========================================

def get_password_hash(password: str) -> str:
    """
    Alias de hash_password para compatibilidad
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return hash_password(password)


# ==========================================
# EMAIL (smtplib - sin dependencias externas)
# ==========================================

def send_email(to: str, subject: str, body: str) -> bool:
    """
    Enviar email usando SMTP configurado en settings.
    Retorna True si se envió, False si SMTP no está configurado.
    """
    from app.core.config import settings
    import smtplib
    from email.mime.text import MIMEText

    if not settings.SMTP_HOST or not settings.SMTP_PORT:
        return False

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL or "noreply@inmobiliaria.com"
    msg["To"] = to

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def send_verification_email(db: Session, user: User, base_url: str = "http://localhost:5173") -> bool:
    """
    Genera token de verificación y envía email al usuario.
    """
    from app.core.security import create_email_token

    token = create_email_token(user.email, "email_verify")
    verify_url = f"{base_url}/verificado?token={token}"

    body = f"""
    <h2>Verifica tu correo electrónico</h2>
    <p>Hola {user.full_name},</p>
    <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>Este enlace expira en 15 minutos.</p>
    """
    return send_email(user.email, "Verifica tu correo - Inmobiliaria", body)


def send_reset_password_email(db: Session, user: User, base_url: str = "http://localhost:5173") -> bool:
    """
    Genera token de reseteo y envía email al usuario.
    """
    from app.core.security import create_email_token

    token = create_email_token(user.email, "password_reset")
    reset_url = f"{base_url}/nueva-contrasena?token={token}"

    body = f"""
    <h2>Restablece tu contraseña</h2>
    <p>Hola {user.full_name},</p>
    <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>Este enlace expira en 15 minutos.</p>
    <p>Si no solicitaste este cambio, ignora este mensaje.</p>
    """
    return send_email(user.email, "Restablece tu contraseña - Inmobiliaria", body)


def verify_email_token(db: Session, token: str) -> User:
    """
    Valida un token de verificación de email y marca al usuario como verificado.
    """
    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if not payload or payload.get("purpose") != "email_verify":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )

    email = payload.get("sub")
    user = userService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    user.is_email_verified = True
    db.commit()
    db.refresh(user)
    return user


def reset_password_with_token(db: Session, token: str, new_password: str) -> User:
    """
    Valida un token de reseteo y actualiza la contraseña.
    """
    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )

    email = payload.get("sub")
    user = userService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    validate_password_strength(new_password)
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
