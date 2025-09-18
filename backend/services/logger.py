import logging
import os

# Create a logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure the logger
LOG_FILE = os.path.join(LOG_DIR, "backend.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create a logger instance
logger = logging.getLogger("backend_logger")

# Example usage
if __name__ == "__main__":
    logger.info("Logger is set up and ready to use.")
