from pathlib import Path
import re
from uuid import uuid4

import allure
from allure_commons.types import AttachmentType

from config.config import DEFAULT_TIMEOUT_MS, PAGE_LOAD_TIMEOUT_MS
from utils.browser_manager import BrowserManager
from utils.logger import get_logger
from utils.screenshot import capture_screenshot

logger = get_logger()


def before_scenario(context, scenario):
    logger.info("Starting Scenario: %s", scenario.name)
    (
        context.playwright,
        context.browser,
        context.browser_context,
        context.page,
    ) = BrowserManager.launch_browser()
    context.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    context.page.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT_MS)


def after_scenario(context, scenario):
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", scenario.name).strip("_") or "scenario"
    unique_id = uuid4().hex[:12]
    trace_dir = Path("reports/traces")
    trace_dir.mkdir(parents=True, exist_ok=True)
    failed = scenario.status.name.lower() == "failed"

    try:
        logger.info("Scenario status: %s", scenario.status.name)
        try:
            screenshot_path = capture_screenshot(context.page, scenario.name)
            if failed:
                allure.attach.file(
                    str(screenshot_path),
                    name="Failure screenshot",
                    attachment_type=AttachmentType.PNG,
                )
        except Exception:
            logger.exception("Unable to capture/attach screenshot")

        try:
            trace_path = trace_dir / f"{safe_name}_{unique_id}.zip"
            context.browser_context.tracing.stop(path=str(trace_path))
            if failed:
                allure.attach.file(
                    str(trace_path),
                    name="Playwright trace",
                    attachment_type=AttachmentType.ZIP,
                )
        except Exception:
            logger.exception("Unable to save/attach Playwright trace")
    finally:
        try:
            # Video files are finalized when the browser context closes.
            video = context.page.video
            context.browser_context.close()
            if failed and video is not None:
                try:
                    video_path = video.path()
                    allure.attach.file(
                        video_path,
                        name="Failure video",
                        attachment_type=AttachmentType.WEBM,
                    )
                except Exception:
                    logger.exception("Unable to attach Playwright video")
        finally:
            try:
                context.browser.close()
            finally:
                context.playwright.stop()
