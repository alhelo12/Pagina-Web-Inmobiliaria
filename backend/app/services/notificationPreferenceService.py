from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User
from app.schemas.notificationSchema import NOTIFICATION_TYPES


def get_preferences(db: Session, user_id: int) -> list[dict]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    prefs = user.user_preferences or {"all": True}
    result = []
    for nt in NOTIFICATION_TYPES:
        result.append({
            "id": 0,
            "user_id": user_id,
            "type": nt,
            "enabled": prefs.get(nt, prefs.get("all", True))
        })
    return result


def set_preference(db: Session, user_id: int, notification_type: str, enabled: bool) -> dict:
    if notification_type not in NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de notificación inválido: {notification_type}"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    prefs = dict(user.user_preferences or {})
    prefs[notification_type] = enabled
    user.user_preferences = prefs
    db.commit()
    return {"id": 0, "user_id": user_id, "type": notification_type, "enabled": enabled}


def is_enabled(db: Session, user_id: int, notification_type: str) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return True
    prefs = user.user_preferences or {"all": True}
    return prefs.get(notification_type, prefs.get("all", True))
