"""Project CI manifests into a minimal, attachment-free public Allure dataset."""

import json
import os
import re
from pathlib import Path
from uuid import uuid4


def main():
    feature_titles = {
        match.group(1).strip()
        for feature in Path("features").glob("*.feature")
        for match in re.finditer(
            r"^\s*Scenario(?: Outline)?:\s*([^\r\n]+)",
            feature.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    }
    output = Path("public-allure-results")
    output.mkdir(exist_ok=True)
    count = 0
    reported = 0
    for manifest in sorted(Path("jira-results").glob("*/jira-result.json")):
        row = json.loads(manifest.read_text(encoding="utf-8"))
        browser = row["browser"]
        if browser not in {"chromium", "firefox", "webkit"}:
            continue
        shard = str(row["shard"])
        if shard not in {"0", "1"}:
            continue
        reported += bool(row["scenarios"])
        for case in row["scenarios"]:
            count += 1
            # Only publish names from the public feature files. Discard
            # expanded example parameters and any other runner-supplied text.
            candidate = re.sub(r"\s+--\s+@\d+\.\d+.*$", "", case["name"]).strip()
            name = candidate if candidate in feature_titles else f"Scenario {count}"
            status = case["status"]
            result = {
                "uuid": uuid4().hex,
                "name": name,
                "status": status if status in {"passed", "failed", "broken", "skipped"} else "unknown",
                "labels": [
                    {"name": "suite", "value": browser},
                    {"name": "subSuite", "value": f"Job {int(shard) + 1}"},
                    *({"name": "tag", "value": tag} for tag in case.get("tags", [])
                      if tag in {"smoke", "sanity", "regression", "negative", "defect_drill"}),
                ],
                "stage": "finished",
            }
            if all(type(case.get(field)) is int for field in ("start", "stop")):
                result.update(start=case["start"], stop=case["stop"])
            (output / f"{result['uuid']}-result.json").write_text(
                json.dumps(result), encoding="utf-8"
            )
    if not count:
        raise SystemExit("No scenario results available to publish")
    expected = int(os.environ.get("EXPECTED_SHARDS", reported))
    (output / "environment.properties").write_text(
        f"Jobs with scenario results={reported}/{expected}\n", encoding="utf-8"
    )
    (output / "executor.json").write_text(json.dumps({
        "name": "GitHub Actions",
        "buildName": f"Run #{int(os.environ['GITHUB_RUN_NUMBER'])}",
        "buildUrl": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{int(os.environ['GITHUB_RUN_ID'])}",
    }), encoding="utf-8")
    print(f"Prepared {count} public Allure scenario results")


if __name__ == "__main__":
    main()

