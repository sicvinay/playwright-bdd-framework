import re
from pathlib import Path
from uuid import uuid4


def capture_screenshot(page, scenario_name):
    screenshot_dir = Path("reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", scenario_name).strip("_") or "scenario"
    screenshot_path = screenshot_dir / f"{safe_name}_{uuid4().hex[:12]}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    return screenshot_path
