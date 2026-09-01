import os
from datetime import datetime


def capture_screenshot(page, scenario_name):

    os.makedirs(
        "reports/screenshots",
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_name = (
        scenario_name
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    screenshot_path = (
        f"reports/screenshots/"
        f"{safe_name}_{timestamp}.png"
    )

    page.screenshot(
        path=screenshot_path,
        full_page=True
    )