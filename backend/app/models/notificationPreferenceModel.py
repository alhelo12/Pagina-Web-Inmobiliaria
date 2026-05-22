from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_preferences")

    __table_args__ = (
        UniqueConstraint("user_id", "type", name="uq_user_notification_type"),
    )
