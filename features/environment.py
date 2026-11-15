from pathlib import Path
import re

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
    trace_dir = Path("reports/traces")
    trace_dir.mkdir(parents=True, exist_ok=True)
    try:
        logger.info("Scenario status: %s", scenario.status.name)
        try:
            capture_screenshot(context.page, scenario.name)
        except Exception:
            logger.exception("Unable to capture screenshot")
        try:
            context.browser_context.tracing.stop(path=str(trace_dir / f"{safe_name}.zip"))
        except Exception:
            logger.exception("Unable to save Playwright trace")
    finally:
        try:
            context.browser_context.close()  # Flush recorded video files.
        finally:
            try:
                context.browser.close()
            finally:
                context.playwright.stop()
