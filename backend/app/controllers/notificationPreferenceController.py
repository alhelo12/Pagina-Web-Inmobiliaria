from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.services import notificationPreferenceService
from app.schemas.notificationPreferenceSchema import (
    NotificationPreferenceResponse,
    NotificationPreferencesListResponse,
    NotificationPreferenceUpdate
)

router = APIRouter(
    prefix="/notifications/preferences",
    tags=["Notification Preferences"]
)


@router.get("", response_model=NotificationPreferencesListResponse)
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = notificationPreferenceService.get_preferences(db, current_user.id)
    return NotificationPreferencesListResponse(preferences=prefs)


@router.put("/{notification_type}", response_model=NotificationPreferenceResponse)
def update_preference(
    notification_type: str,
    body: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pref = notificationPreferenceService.set_preference(
        db, current_user.id, notification_type, body.enabled
    )
    return pref
