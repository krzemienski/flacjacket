import logging
import logging.config
import os
import sys
import structlog
from pythonjsonlogger import jsonlogger
from datetime import datetime
from flask import request, has_request_context

def add_request_context(logger, name, event_dict):
    """Add request context to log entries if available"""
    if has_request_context():
        event_dict["request_id"] = request.headers.get("X-Request-ID")
        event_dict["remote_addr"] = request.remote_addr
        event_dict["path"] = request.path
        event_dict["method"] = request.method
    return event_dict

def add_process_context(logger, name, event_dict):
    """Add process information to log entries"""
    event_dict["pid"] = os.getpid()
    event_dict["process_name"] = sys.argv[0]
    return event_dict

def setup_logging(app):
    """Configure structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            if not log_record.get('timestamp'):
                log_record['timestamp'] = datetime.utcnow().isoformat()
            if log_record.get('level'):
                log_record['level'] = log_record['level'].upper()
            else:
                log_record['level'] = record.levelname
                
    # Configure processors for structlog
    processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_process_context,
        add_request_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ]
    
    # Configure logging
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJsonFormatter,
                'format': '%(timestamp)s %(level)s %(name)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': os.path.join(logs_dir, 'flacjacket.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'download_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': os.path.join(logs_dir, 'downloads.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'analysis_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': os.path.join(logs_dir, 'analysis.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'INFO'
            },
            'flacjacket.download': {
                'handlers': ['console', 'download_file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'flacjacket.analysis': {
                'handlers': ['console', 'analysis_file'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    })
    
    # Configure structlog to use standard library logging
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()
