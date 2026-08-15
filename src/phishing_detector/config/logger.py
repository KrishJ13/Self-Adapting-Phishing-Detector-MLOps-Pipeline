import logging
import json
from datetime import datetime, UTC
import sys

"""
The hierachy for python logging is: DEBUG, INFO, WARNING, ERROR, CRITICAL
There are also components relevant to logging:
- Logger: What the code actually talks to
- LogRecord: The log structured in a default way
- Handler: Where to write the log to
- Formatter: How the log actually looks
"""

# Set the minimum level of logging
logging.basicConfig(level=logging.INFO)

"""
Create a custom formatter, which inherits from the base logging.Formatter
"""
class JsonFormatter(logging.Formatter):
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


logger = logging.getLogger(name="phishing_detector")


"""
Attach the Formatter to a Handler
"""
handler = logging.StreamHandler(sys.stdout) # Emit logs and let runtime collect them, Will also use docker downstream
handler.setFormatter(fmt=JsonFormatter())

"""
Attach the Handler to the Logger
"""
logger.addHandler(handler)

logger.info("My very new log that should be formatted")



