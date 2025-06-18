"""
Modern structured logging setup for the chatbot library.

Replaces the custom logkontrol system with industry-standard structured logging.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import json
from datetime import datetime

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class ChatbotLibraryLogger:
    """Centralized logging configuration for the chatbot library."""
    
    _configured = False
    _loggers = {}
    
    @classmethod
    def configure(
        cls,
        level: str = "INFO",
        enable_json: bool = False,
        log_file: Optional[Path] = None,
        enable_structlog: bool = True
    ) -> None:
        """Configure logging for the entire library."""
        if cls._configured:
            return
        
        if enable_structlog and STRUCTLOG_AVAILABLE:
            cls._configure_structlog(level, enable_json, log_file)
        else:
            cls._configure_stdlib_logging(level, enable_json, log_file)
        
        cls._configured = True
    
    @classmethod
    def _configure_structlog(
        cls,
        level: str,
        enable_json: bool,
        log_file: Optional[Path]
    ) -> None:
        """Configure structured logging with structlog."""
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
        ]
        
        if enable_json:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.extend([
                structlog.dev.ConsoleRenderer(colors=True),
            ])
        
        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, level.upper())
            ),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure stdlib logging
        handlers = ['console']
        if log_file:
            handlers.append('file')
        
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'structured': {
                    'format': '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
                },
                'json': {
                    'format': '%(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': level,
                    'formatter': 'structured' if not enable_json else 'json',
                    'stream': sys.stdout
                }
            },
            'root': {
                'level': level,
                'handlers': handlers
            },
            'loggers': {
                'chatbot_library': {
                    'level': level,
                    'handlers': handlers,
                    'propagate': False
                }
            }
        }
        
        if log_file:
            logging_config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': level,
                'formatter': 'structured' if not enable_json else 'json',
                'filename': str(log_file),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        
        logging.config.dictConfig(logging_config)
    
    @classmethod
    def _configure_stdlib_logging(
        cls,
        level: str,
        enable_json: bool,
        log_file: Optional[Path]
    ) -> None:
        """Configure standard library logging as fallback."""
        formatter_class = JSONFormatter if enable_json else logging.Formatter
        
        if enable_json:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10485760, backupCount=5
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> Any:
        """Get a logger instance."""
        if not cls._configured:
            cls.configure()
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        if STRUCTLOG_AVAILABLE:
            logger = structlog.get_logger(f"chatbot_library.{name}")
        else:
            logger = logging.getLogger(f"chatbot_library.{name}")
        
        cls._loggers[name] = logger
        return logger


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Convenience functions that replace logkontrol
def get_logger(name: str) -> Any:
    """Get a logger for a specific module."""
    return ChatbotLibraryLogger.get_logger(name)


def log_function_call(logger: Any, function_name: str, **kwargs) -> None:
    """Log a function call with parameters."""
    if hasattr(logger, 'info'):  # structlog or stdlib
        logger.info("Function called", function=function_name, **kwargs)
    else:
        logger.info(f"Function called: {function_name}", **kwargs)


def log_json_content(logger: Any, content: Dict[str, Any], description: str = "") -> None:
    """Log JSON content in a structured way."""
    if hasattr(logger, 'info'):
        logger.info("JSON content", description=description, content=content)
    else:
        logger.info(f"JSON content: {description}", extra={'content': content})


def log_message(logger: Any, message: str, **context) -> None:
    """Log a message with context."""
    if hasattr(logger, 'info'):
        logger.info(message, **context)
    else:
        logger.info(message, extra=context)


def log_variable(logger: Any, variable_name: str, value: Any, **context) -> None:
    """Log a variable value."""
    if hasattr(logger, 'debug'):
        logger.debug("Variable value", variable=variable_name, value=value, **context)
    else:
        logger.debug(f"Variable {variable_name}", extra={'value': value, **context})


def log_error(logger: Any, error: Exception, context: str = "", **kwargs) -> None:
    """Log an error with context."""
    if hasattr(logger, 'error'):
        logger.error("Error occurred", error=str(error), context=context, **kwargs)
    else:
        logger.error(f"Error in {context}: {error}", extra=kwargs)


def log_api_call(
    logger: Any,
    provider: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    duration: float = 0.0,
    **kwargs
) -> None:
    """Log API calls with metrics."""
    if hasattr(logger, 'info'):
        logger.info(
            "API call completed",
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_seconds=duration,
            **kwargs
        )
    else:
        logger.info(
            f"API call to {provider}/{model}",
            extra={
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'duration_seconds': duration,
                **kwargs
            }
        )


def log_conversation_event(
    logger: Any,
    event_type: str,
    conversation_id: str,
    **kwargs
) -> None:
    """Log conversation-related events."""
    if hasattr(logger, 'info'):
        logger.info(
            "Conversation event",
            event_type=event_type,
            conversation_id=conversation_id,
            **kwargs
        )
    else:
        logger.info(
            f"Conversation {event_type}: {conversation_id}",
            extra=kwargs
        )


def log_tool_execution(
    logger: Any,
    tool_name: str,
    success: bool,
    duration: float = 0.0,
    **kwargs
) -> None:
    """Log tool execution events."""
    if hasattr(logger, 'info'):
        logger.info(
            "Tool execution",
            tool_name=tool_name,
            success=success,
            duration_seconds=duration,
            **kwargs
        )
    else:
        logger.info(
            f"Tool {tool_name} {'succeeded' if success else 'failed'}",
            extra={'duration_seconds': duration, **kwargs}
        )


# Initialize logging on import
ChatbotLibraryLogger.configure()