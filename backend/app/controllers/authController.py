"""
Controller: Authentication

Endpoints para registro, login, verificación de email y reseteo de contraseña.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.dbConfig.databaseSession import get_db
from app.services import authService, userService
from app.core.security import create_token_for_user
from app.core.dependencies import get_current_user
from app.core.rateLimiter import limiter
from app.core.config import is_production
from app.schemas import (
    UserCreate,
    ClientRegister,
    UserResponse,
    Token,
    PasswordChange
)
from app.models import User


class EmailCheckRequest(BaseModel):
    email: EmailStr


class PasswordValidateRequest(BaseModel):
    password: str


class SendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTRO
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3 per hour")
def register(
    request: Request,
    client_data: ClientRegister,
    db: Session = Depends(get_db)
):
    from app.models import Role
    client_role = db.query(Role).filter(Role.name == 'client').first()
    if not client_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: rol 'client' no existe"
        )

    user_create_data = UserCreate(
        full_name=client_data.full_name,
        email=client_data.email,
        password=client_data.password,
        phone=client_data.phone,
        role_id=client_role.id
    )
    user = authService.register_user(db, user_create_data)
    return user


@router.post("/register/client", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3 per hour")
def register_client(
    request: Request,
    client_data: ClientRegister,
    db: Session = Depends(get_db)
):
    from app.models import Role
    client_role = db.query(Role).filter(Role.name == 'client').first()
    if not client_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: rol 'client' no existe"
        )

    user_create_data = UserCreate(
        full_name=client_data.full_name,
        email=client_data.email,
        password=client_data.password,
        phone=client_data.phone,
        role_id=client_role.id
    )
    user = authService.register_user(db, user_create_data)

    return user


# ==========================================
# LOGIN
# ==========================================

@router.post("/login", response_model=Token)
@limiter.limit("5 per minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )

    access_token = create_token_for_user(
        user_id=user.id,
        email=user.email,
        role_name=user.role.name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================
# VERIFICACIÓN DE EMAIL
# ==========================================

@router.post("/send-verification")
def send_verification(
    body: SendVerificationRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Envía email de verificación al usuario.
    Si SMTP no está configurado, devuelve el token en la respuesta (desarrollo).
    """
    user = userService.get_user_by_email(db, body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if user.is_email_verified:
        return {"message": "El email ya está verificado"}

    from app.core.security import create_email_token

    sent = authService.send_verification_email(db, user)
    if sent:
        return {"message": "Email de verificación enviado"}

    # Solo devolver token en desarrollo, nunca en producción
    if not is_production():
        from app.core.security import create_email_token
        token = create_email_token(user.email, "email_verify")
        return {
            "message": "SMTP no configurado. Token de verificación (solo desarrollo):",
            "token": token
        }

    return {"message": "Email de verificación enviado"}


@router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verifica el email del usuario usando un token JWT.
    """
    user = authService.verify_email_token(db, token)
    return {
        "message": "Email verificado correctamente",
        "email": user.email
    }


# ==========================================
# RECUPERACIÓN DE CONTRASEÑA
# ==========================================

@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Envía email con token para restablecer la contraseña.
    Si SMTP no está configurado, devuelve el token en la respuesta (desarrollo).
    """
    user = userService.get_user_by_email(db, body.email)
    if not user:
        # No revelar si el email existe o no
        return {"message": "Si el email existe, recibirás un enlace para restablecer tu contraseña"}

    from app.core.security import create_email_token

    sent = authService.send_reset_password_email(db, user)
    if sent:
        return {"message": "Si el email existe, recibirás un enlace para restablecer tu contraseña"}

    # Solo devolver token en desarrollo, nunca en producción
    if not is_production():
        from app.core.security import create_email_token
        token = create_email_token(user.email, "password_reset")
        return {
            "message": "SMTP no configurado. Token de reseteo (solo desarrollo):",
            "token": token
        }

    return {"message": "Si el email existe, recibirás un enlace para restablecer tu contraseña"}


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Restablece la contraseña usando un token JWT.
    """
    user = authService.reset_password_with_token(db, body.token, body.new_password)
    return {
        "message": "Contraseña actualizada correctamente",
        "email": user.email
    }


# ==========================================
# OBTENER USUARIO ACTUAL
# ==========================================

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


# ==========================================
# CAMBIO DE CONTRASEÑA (autenticado)
# ==========================================

@router.post("/change-password", response_model=UserResponse)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = authService.change_password(
        db,
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    return user


# ==========================================
# VALIDACIONES
# ==========================================

@router.post("/check-email")
def check_email_available(
    body: EmailCheckRequest,
    db: Session = Depends(get_db)
):
    available = authService.validate_email_available(db, body.email)
    return {
        "email": body.email,
        "available": available
    }


@router.post("/validate-password")
def validate_password(body: PasswordValidateRequest):
    try:
        authService.validate_password_strength(body.password)
        return {"valid": True, "errors": []}
    except HTTPException as e:
        return {"valid": False, "errors": [e.detail]}
