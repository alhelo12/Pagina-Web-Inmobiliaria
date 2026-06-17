from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.services import notificationPreferenceService

router = APIRouter(
    prefix="/notifications/preferences",
    tags=["Notification Preferences"]
)


class UpdateBody(BaseModel):
    enabled: bool


@router.get("")
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = notificationPreferenceService.get_preferences(db, current_user.id)
    return {"preferences": prefs}


@router.put("/{notification_type}")
def update_preference(
    notification_type: str,
    body: UpdateBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notificationPreferenceService.set_preference(
        db, current_user.id, notification_type, body.enabled
    )
