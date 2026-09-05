import os
import allure

from utils.logger import get_logger

logger = get_logger()


def attach_screenshot(file_path, name="Screenshot"):
    """
    Attach a screenshot file to the Allure report.
    """

    if not file_path:
        logger.warning("Screenshot path is empty. Skipping Allure attachment.")
        return

    if not os.path.exists(file_path):
        logger.warning(
            f"Screenshot file not found: {file_path}. "
            "Skipping Allure attachment."
        )
        return

    allure.attach.file(
        file_path,
        name=name,
        attachment_type=allure.attachment_type.PNG
    )

    logger.info(f"Screenshot attached to Allure: {file_path}")


def attach_video(file_path, name="Video"):
    """
    Attach a Playwright video file to the Allure report.
    """

    if not file_path:
        logger.warning("Video path is empty. Skipping Allure attachment.")
        return

    if not os.path.exists(file_path):
        logger.warning(
            f"Video file not found: {file_path}. "
            "Skipping Allure attachment."
        )
        return

    allure.attach.file(
        file_path,
        name=name,
        attachment_type=allure.attachment_type.WEBM
    )

    logger.info(f"Video attached to Allure: {file_path}")


def attach_trace(file_path, name="Trace"):
    """
    Attach a Playwright trace ZIP file to the Allure report.
    """

    if not file_path:
        logger.warning("Trace path is empty. Skipping Allure attachment.")
        return

    if not os.path.exists(file_path):
        logger.warning(
            f"Trace file not found: {file_path}. "
            "Skipping Allure attachment."
        )
        return

    allure.attach.file(
        file_path,
        name=name,
        attachment_type=allure.attachment_type.ZIP
    )

    logger.info(f"Trace attached to Allure: {file_path}")