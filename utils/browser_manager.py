from pathlib import Path

from config.config import BROWSER

from playwright.sync_api import sync_playwright


class BrowserManager:
    @staticmethod
    def launch_browser():
        Path("reports/videos").mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        try:
            browser = getattr(playwright, BROWSER).launch(headless=True)
            context = browser.new_context(record_video_dir="reports/videos")
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()
            return playwright, browser, context, page
        except Exception:
            playwright.stop()
            raise
