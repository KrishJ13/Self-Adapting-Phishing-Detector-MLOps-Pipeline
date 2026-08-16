
from phishing_detector.config.settings import import_settings
from phishing_detector.config.logger import CustomLogger

def main():
    # Import environment settings
    settings = import_settings()
    # Initialise an instance of custom logger and provide log level from imported settings
    logger = CustomLogger(name="phishing-logger", level=settings.log_level)

    logger.info("This should be a hidden JSON DEBUB log")
    logger.info("This should be a visible JSON INFO log")
    logger.error("This should be a visible JSON ERROR log")

    logger.info(msg="Phishing Detector app started")

if __name__ == "__main__":
    """
    THIS HARMLESS CHANGES IS TO SEE IF GITHUB ACTIONS HAS BEEN SET PROPERLY. EXPECTED TO PASS
    """
    main()