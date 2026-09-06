import json
import sys
from pathlib import Path
from xml.etree import ElementTree


def format_duration(seconds):
    seconds = float(seconds)

    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes, remaining_seconds = divmod(int(seconds), 60)

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {remaining_seconds}s"


def generate_summary(junit_directory):
    junit_directory = Path(junit_directory)

    xml_files = list(junit_directory.glob("*.xml"))

    if not xml_files:
        raise FileNotFoundError(
            f"No JUnit XML files found in: {junit_directory}"
        )

    total = 0
    passed = 0
    failed = 0
    skipped = 0
    duration = 0.0
    failed_scenarios = []

    for xml_file in xml_files:
        root = ElementTree.parse(xml_file).getroot()

        for testcase in root.iter("testcase"):
            total += 1

            duration += float(testcase.attrib.get("time", 0))

            if testcase.find("skipped") is not None:
                skipped += 1

            elif (
                testcase.find("failure") is not None
                or testcase.find("error") is not None
            ):
                failed += 1
                failed_scenarios.append(
                    testcase.attrib.get("name", "Unknown scenario").strip()
                )

            else:
                passed += 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration_seconds": round(duration, 2),
        "duration": format_duration(duration),
        "failed_scenarios": failed_scenarios,
    }


def main():
    junit_directory = (
        sys.argv[1] if len(sys.argv) > 1 else "reports/junit"
    )

    summary = generate_summary(junit_directory)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()