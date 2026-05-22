from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class NotificationPreferenceBase(BaseModel):
    type: str = Field(..., description="Tipo de notificación")
    enabled: bool = Field(True, description="Activa o desactiva este tipo")


class NotificationPreferenceUpdate(BaseModel):
    enabled: bool = Field(..., description="Activa o desactiva este tipo")


class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferencesListResponse(BaseModel):
    preferences: list[NotificationPreferenceResponse]
