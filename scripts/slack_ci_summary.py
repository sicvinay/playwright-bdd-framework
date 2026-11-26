"""Build and deliver a single Slack card for a UI Automation Tests run."""

import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from jira_regression import RejectRedirects


def section(text):
    return {"type": "section", "text": {"type": "plain_text", "text": text}}


def card(env, results, jobs):
    repo = env["GITHUB_REPOSITORY"]
    run = f'https://github.com/{repo}/actions/runs/{env["GITHUB_RUN_ID"]}'
    attempt = env["GITHUB_RUN_ATTEMPT"]
    run_url = f"{run}/attempts/{attempt}"
    scheduled = env["GITHUB_EVENT_NAME"] == "schedule"
    suite = "Daily QA Regression" if scheduled else "UI Automation Tests"
    expected = int(env["EXPECTED_SHARDS"])
    matrix = env["MATRIX_RESULT"]
    jira = env["JIRA_RESULT"]
    ui_jobs = {job["name"]: job for job in jobs if job["name"].startswith("ui-tests (")}
    failed_job = next((job for job in ui_jobs.values() if job["conclusion"] == "failure"), None)
    jira_job = next((job for job in jobs if job["name"] == "jira-report"), None)
    totals = Counter(case["status"] for row in results for case in row["scenarios"])
    reported = sum(bool(row["scenarios"]) for row in results)
    test_failures = [
        (row, case["name"]) for row in results for case in row["scenarios"]
        if case["status"] == "failed"
    ]
    if matrix in {"cancelled", "skipped"}:
        verdict = f"ℹ️ {matrix.title()}"
    elif test_failures:
        verdict = "❌ Test Failed"
    elif matrix == "failure":
        verdict = "🚨 Infrastructure or Test Execution Failure" if not reported else "⚠️ Test Job Failed"
    elif jira == "failure":
        verdict = "⚠️ Jira Reporting Failed"
    elif reported < expected:
        verdict = "⚠️ Partial Test Results"
    elif any(not row["evidence"] for row in results):
        verdict = "⚠️ Test Evidence Unavailable"
    else:
        verdict = "✅ Passed"

    title = f"{suite} · {verdict}"
    event = "Scheduled 07:00 IST" if scheduled else env["GITHUB_EVENT_NAME"].replace("_", " ")
    context = f'{repo} · {env["GITHUB_REF_NAME"]} · {event} · Run #{env["GITHUB_RUN_NUMBER"]} · {env["TARGET_ENV"]}'
    if attempt != "1":
        context += f" · Attempt {attempt}"
    complete = [job for job in ui_jobs.values() if job.get("started_at") and job.get("completed_at")]
    if complete:
        start = min(datetime.fromisoformat(job["started_at"]) for job in complete)
        end = max(datetime.fromisoformat(job["completed_at"]) for job in complete)
        minutes, seconds = divmod(max(0, int((end - start).total_seconds())), 60)
        context += f" · {minutes}m {seconds:02d}s"

    details = ", ".join(
        f"{browser.title()} {sum(row['browser'] == browser and bool(row['scenarios']) for row in results)} jobs reported"
        for browser in sorted({row["browser"] for row in results})
    )
    counts = " · ".join(f"{totals[name]} {name}" for name in ("passed", "failed", "skipped"))
    if other := sum(value for name, value in totals.items() if name not in {"passed", "failed", "skipped"}):
        counts += f" · {other} broken or unknown"
    coverage = f"{reported} of {expected} jobs reported results"
    if reported < expected:
        coverage = "Partial results · " + coverage
    if not reported:
        counts = "No scenario results were reported."
    if not reported and len(ui_jobs) == expected and all(
        job["conclusion"] == "failure" and not any(
            step["name"] == "Run Behave tests" and step["conclusion"] in {"success", "failure"}
            for step in job.get("steps", [])
        ) for job in ui_jobs.values()
    ):
        counts = "Setup failed in all test jobs. No tests ran."
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": title}},
        {"type": "context", "elements": [{"type": "plain_text", "text": context}]},
        section(f"{counts}\n{coverage}" + (f" · {details}" if details else "")),
    ]
    actions = []
    failed_row = None
    if test_failures:
        failed_row, name = test_failures[0]
        matching_job = ui_jobs.get(f"ui-tests ({failed_row['browser']}, {failed_row['shard']})")
        failed_job = matching_job or failed_job
        reproduced = any(item["scenario"] == name for item in failed_row["confirmed"].values())
        retry = "Failure reproduced" if reproduced else {
            "passed": "Passed on retry",
            "failed": "Reproduction not confirmed for this scenario",
            "error": "Retry did not complete",
        }.get(failed_row["retry"], "Retry not run")
        more = f" (+{len(test_failures) - 1} more)" if len(test_failures) > 1 else ""
        blocks.extend([{"type": "divider"}, section(
            f"Failed scenario · {name[:500]}{more}\n"
            f"{failed_row['browser'].title()} · Job {int(failed_row['shard']) + 1}\nRetry · {retry}"
        )])
    if failed_job:
        actions.append(("Open failed job", failed_job["html_url"]))
    elif jira == "failure" and jira_job:
        actions.append(("Open Jira job logs", jira_job["html_url"]))
    heading_jira = {"success": "Results published", "failure": "Publishing failed",
                    "cancelled": "Publishing cancelled", "skipped": "Publishing skipped"}.get(jira, "Status unavailable")
    bugs = json.loads(env.get("JIRA_BUGS") or "{}")
    if bugs:
        heading_jira += " · " + ", ".join(f"{key} {action}" for key, action in sorted(bugs.items())[:4])
    blocks.append(section(f"Jira · {heading_jira}"))
    if not actions:
        actions.append(("View run summary", run_url))
    evidence_rows = [failed_row] if failed_row else results
    evidence = next((row["evidence"] for row in evidence_rows
                     if row["evidence"].startswith(f"{run}/artifacts/")), None)
    if evidence:
        label = "Download job evidence" if failed_row or len(results) == 1 else "Browse test evidence"
        actions.append((label, evidence if failed_row or len(results) == 1 else run_url))
    site = env.get("JIRA_SITE_URL", "").rstrip("/")
    if re.fullmatch(r"https://[a-z0-9-]+\.atlassian\.net", site):
        key = next(iter(sorted(bugs)), None) or env.get("JIRA_RESULTS_ISSUE", "")
        if jira == "success" and re.fullmatch(r"SCRUM-[1-9][0-9]*", key):
            actions.append(("View Jira Bug" if bugs else "Open Jira report", f"{site}/browse/{key}"))
    if actions[0][1] != run_url:
        actions.append(("View run summary", run_url))
    blocks.append({"type": "actions", "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": label}, "url": url,
         **({"style": "primary"} if index == 0 else {})}
        for index, (label, url) in enumerate(actions)
    ]})
    return {"text": f"{title}\n{counts}\n{coverage}\nJira · {heading_jira}\n{run_url}", "blocks": blocks}


def main():
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("Slack webhook unavailable for this run. Skipping delivery.")
        return
    jobs_path = Path("ci-jobs.json")
    jobs = [job for page in json.loads(jobs_path.read_text()) for job in page["jobs"]] if jobs_path.is_file() else []
    results = [json.loads(path.read_text()) for path in sorted(Path("jira-results").glob("*/jira-result.json"))]
    request = Request(webhook, data=json.dumps(card(os.environ, results, jobs)).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with build_opener(RejectRedirects()).open(request, timeout=20) as response:
            if response.read(128).strip() != b"ok":
                raise SystemExit("Slack returned an unexpected delivery response")
    except HTTPError as exc:
        raise SystemExit(f"Slack rejected the message (HTTP {exc.code})") from None
    except (URLError, TimeoutError):
        raise SystemExit("Slack delivery could not connect or timed out") from None
    print("Slack accepted the run summary")


if __name__ == "__main__":
    main()
