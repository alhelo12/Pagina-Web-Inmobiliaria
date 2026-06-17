import asyncio
from functools import wraps
from app.dbConfig.databaseSession import SessionLocal
from app.services import activityLogService


def log_activity(action: str, entity_type: str = None, entity_id_param: str = None):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                _log(action, entity_type, entity_id_param, kwargs)
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                _log(action, entity_type, entity_id_param, kwargs)
                return result
            return sync_wrapper
    return decorator


def _log(action, entity_type, entity_id_param, kwargs):
    entity_id = None
    if entity_id_param and entity_id_param in kwargs:
        entity_id = kwargs[entity_id_param]
    elif entity_type:
        candidate = f"{entity_type}_id"
        if candidate in kwargs:
            entity_id = kwargs[candidate]

    user = kwargs.get("current_user")
    user_id = user.id if user else None

    db = kwargs.get("db")
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        activityLogService.log_activity(
            db=db, user_id=user_id, action=action,
            entity_type=entity_type, entity_id=entity_id,
        )
    except Exception:
        pass
    finally:
        if own_session:
            db.close()
