from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.models import NotificationPreference, User
from app.schemas.notificationSchema import NOTIFICATION_TYPES


def get_preferences(db: Session, user_id: int) -> List[NotificationPreference]:
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).all()
    
    existing_types = {p.type for p in prefs}
    for nt in NOTIFICATION_TYPES:
        if nt not in existing_types:
            pref = NotificationPreference(user_id=user_id, type=nt, enabled=True)
            db.add(pref)
            prefs.append(pref)
    
    if existing_types != set(NOTIFICATION_TYPES.keys()):
        db.commit()
        for p in prefs:
            db.refresh(p)
    
    return prefs


def set_preference(
    db: Session,
    user_id: int,
    notification_type: str,
    enabled: bool
) -> NotificationPreference:
    if notification_type not in NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de notificación inválido: {notification_type}"
        )
    
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.type == notification_type
    ).first()
    
    if pref:
        pref.enabled = enabled
    else:
        pref = NotificationPreference(
            user_id=user_id,
            type=notification_type,
            enabled=enabled
        )
        db.add(pref)
    
    db.commit()
    db.refresh(pref)
    return pref


def is_enabled(db: Session, user_id: int, notification_type: str) -> bool:
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.type == notification_type
    ).first()
    
    if pref is None:
        return True
    return pref.enabled
