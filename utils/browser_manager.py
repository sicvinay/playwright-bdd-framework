from playwright.sync_api import sync_playwright


class BrowserManager:

    @staticmethod
    def launch_browser():

        playwright = sync_playwright().start()

        browser = playwright.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            record_video_dir="reports/videos"
        )

        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True
        )

        page = context.new_page()

        return playwright, browser, context, page