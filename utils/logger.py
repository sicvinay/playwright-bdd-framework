import logging
import os


def get_logger():

    log_folder = "reports"

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger("playwright_bdd")

    logger.setLevel(logging.INFO)

    if not logger.handlers:

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = logging.FileHandler(
            "reports/test_execution.log"
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger