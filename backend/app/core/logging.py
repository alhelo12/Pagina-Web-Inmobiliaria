"""
Structured Logging Configuration

Configura logging estructurado con request IDs para trazabilidad.
Compatible con structlog si está disponible, fallback a stdlib.
"""

import logging
import sys
from importlib.util import find_spec

HAS_STRUCTLOG = find_spec("structlog") is not None


def configure_logging(
    level: str = "INFO",
    json_output: bool = False,
    include_request_id: bool = True
) -> None:
    """
    Configura logging estructurado para la aplicación.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        json_output: Si True, salida en JSON para agregadores
        include_request_id: Si True, incluye request_id en logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar handler base
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    if json_output and HAS_STRUCTLOG:
        # Usar structlog para JSON estructurado
        configure_structlog(handler, include_request_id)
    else:
        # Formatter estándar con request_id
        formatter = RequestIDFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            include_request_id=include_request_id
        )
        handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]
    
    # Silenciar loggers ruidosos de terceros
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("slowapi").setLevel(logging.WARNING)


class RequestIDFormatter(logging.Formatter):
    """Formatter que inyecta request_id del contexto"""
    
    def __init__(self, fmt: str, datefmt: str, include_request_id: bool = True):
        super().__init__(fmt, datefmt)
        self.include_request_id = include_request_id
    
    def format(self, record: logging.LogRecord) -> str:
        from app.core.request_id import get_request_id
        
        if self.include_request_id:
            request_id = get_request_id()
            if request_id:
                record.request_id = request_id
            else:
                record.request_id = "-"
        
        return super().format(record)


def configure_structlog(handler: logging.Handler, include_request_id: bool) -> None:
    """Configura structlog para salida JSON"""
    
    import structlog
    
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if include_request_id:
        shared_processors.append(add_request_id)
    
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer()
        ],
    )
    handler.setFormatter(formatter)


def add_request_id(logger, method_name, event_dict):
    """Processor para agregar request_id a structlog"""
    from app.core.request_id import get_request_id
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict
