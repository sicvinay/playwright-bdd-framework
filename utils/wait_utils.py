import time

from config.config import (
    CUSTOM_WAIT_TIMEOUT_SECONDS,
    POLLING_INTERVAL_SECONDS
)

from utils.logger import get_logger


logger = get_logger()


def wait_until(
    condition,
    timeout=CUSTOM_WAIT_TIMEOUT_SECONDS,
    polling_interval=POLLING_INTERVAL_SECONDS,
    error_message="Condition was not met within the timeout period"
):

    logger.info(
        f"Waiting for condition with timeout: {timeout} seconds"
    )

    start_time = time.time()

    while time.time() - start_time < timeout:

        try:

            result = condition()

            if result:

                logger.info(
                    "Expected condition satisfied"
                )

                return result

        except Exception:
            pass

        time.sleep(
            polling_interval
        )

    logger.error(
        error_message
    )

    raise TimeoutError(
        error_message
    )