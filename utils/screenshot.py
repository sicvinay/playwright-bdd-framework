from datetime import datetime


def capture_screenshot(page):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    page.screenshot(
        path=f"screenshots/{timestamp}.png"
    )