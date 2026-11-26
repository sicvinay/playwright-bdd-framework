"""Combine raw Allure results and keep original diagnostics grouped by runner."""

import json
import shutil
from pathlib import Path


def main():
    output = Path("consolidated/allure-results")
    output.mkdir(parents=True, exist_ok=True)
    for artifact in sorted(Path("job-artifacts").glob("ui-automation-test-results-*")):
        job = artifact.name.removeprefix("ui-automation-test-results-").rsplit("-attempt-", 1)[0]
        browser, shard = job.split("-shard-")
        raw = artifact / "allure-results"
        for source in raw.iterdir() if raw.is_dir() else []:
            destination = output / source.name
            if source.name.endswith("-result.json"):
                result = json.loads(source.read_text(encoding="utf-8"))
                labels = result.setdefault("labels", [])
                labels[:] = [label for label in labels if label["name"] not in {"parentSuite", "subSuite"}]
                labels.extend([
                    {"name": "parentSuite", "value": browser},
                    {"name": "subSuite", "value": f"Job {int(shard) + 1}"},
                ])
                if history_id := result.get("historyId"):
                    result["historyId"] = f"{browser}-{history_id}"
                with destination.open("x", encoding="utf-8") as target:
                    json.dump(result, target)
            elif source.name.endswith("-container.json") or "-attachment" in source.name:
                if destination.exists():
                    raise ValueError(f"Conflicting Allure input: {source.name}")
                shutil.copy2(source, destination)
        shutil.copytree(
            artifact, Path("consolidated/job-evidence") / job,
            ignore=shutil.ignore_patterns("allure-results", "allure-report"),
        )


if __name__ == "__main__":
    main()
