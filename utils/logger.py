import logging
import os


def get_logger():

    log_folder = "reports/logs"

    os.makedirs(
        log_folder,
        exist_ok=True
    )

    log_file = os.path.join(
        log_folder,
        "test_execution.log"
    )

    logger = logging.getLogger(
        "playwright_bdd"
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    if not logger.handlers:

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        file_handler.setFormatter(
            formatter
        )

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

        logger.addHandler(
            console_handler
        )

    return logger