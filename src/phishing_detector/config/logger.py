import logging
import json
from datetime import datetime, UTC
import sys
from enum import IntEnum

"""
The hierachy for python logging is: DEBUG, INFO, WARNING, ERROR, CRITICAL
There are also components relevant to logging:
- Logger: What the code actually talks to
- LogRecord: The log structured in a default way
- Handler: Where to write the log to
- Formatter: How the log actually looks
"""

# Defined an enum to map the environment variables to the integer representations of log valuess expected when new Logger is created
class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL



class JsonFormatter(logging.Formatter):
    """
    Create a custom formatter, which inherits from the base logging.Formatter, and override the format method to
    format messages into a custom json format, to make logs easily searchible
    """
    def format(self, record: logging.LogRecord) -> str:
        # We can define a custom structure for the format
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(), #  record.created is the actual UNIX timestamp the log was created, not when it ran
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage()
        }
        # Payload is in Json, we need to return to string
        return json.dumps(payload)



class CustomLogger(logging.Logger):
    """
    Create a CustomLogger object, that inherits from logger. On initialisation, requires a name and log_level to be 
    specified and automatically configures its handler to use the custom formatter. 
    """
    def __init__(self, name: str, level : LogLevel | str = LogLevel.INFO):
        super().__init__(name, level)

        # Initate an instance of the handler
        handler = logging.StreamHandler(sys.stdout)
        # Attach an instance of the formatter to the handler
        handler.setFormatter(JsonFormatter())

        # Attach the handler to the logger
        self.addHandler(handler)


