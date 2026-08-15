import logging

"""
The hierachy for python logging is: DEBUG, INFO, WARNING, ERROR, CRITICAL
There are also components relevant to logging:
- Logger: What the code actually talks to
- LogRecord: The log structured in a default way
- Handler: Where to write the log to
- Formatter: How the log actually looks
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(name="phishing_detector")
logger.info("Application started")

