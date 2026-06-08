from playwright.sync_api import sync_playwright


class BrowserManager:

    @staticmethod
    def launch_browser():

        playwright = sync_playwright().start()

        browser = playwright.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        return playwright, browser, page