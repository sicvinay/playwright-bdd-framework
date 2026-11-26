"""Build and deliver a single Slack card for a UI Automation Tests run."""

import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from jira_regression import RejectRedirects


BROWSER_NAMES = {"chromium": "Chromium", "firefox": "Firefox", "webkit": "WebKit"}


def section(text):
    return {"type": "section", "text": {"type": "plain_text", "text": text}}


def elapsed(start, end):
    minutes, seconds = divmod(max(0, int((end - start).total_seconds())), 60)
    return f"{minutes}m {seconds:02d}s"


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.is_file() else default


def baseline_for(env, results):
    expected = int(env["EXPECTED_SHARDS"])
    scope = {(r.get("suite"), r.get("environment"), r["browser"], r["shard"]) for r in results}
    if len(scope) != expected or any(not item[0] for item in scope):
        return None
    repo = env["GITHUB_REPOSITORY"]
    try:
        listed = subprocess.run(
            ["gh", "run", "list", "--repo", repo, "--workflow", "ui-tests.yml", "--status", "success",
             "--branch", env.get("GITHUB_HEAD_REF") or env["GITHUB_REF_NAME"], "--event", env["GITHUB_EVENT_NAME"],
             "--limit", "5", "--json", "databaseId,headSha,number,attempt"],
            capture_output=True, text=True, timeout=12, check=True,
        )
        for prior in json.loads(listed.stdout):
            if str(prior["databaseId"]) == env["GITHUB_RUN_ID"]:
                continue
            with tempfile.TemporaryDirectory() as directory:
                fetched = subprocess.run(
                    ["gh", "run", "download", str(prior["databaseId"]), "--repo", repo,
                     "--pattern", f'jira-result-*-attempt-{prior["attempt"]}', "--dir", directory],
                    capture_output=True, timeout=12, check=False,
                )
                if fetched.returncode:
                    continue
                rows = [read_json(path) for path in Path(directory).rglob("jira-result.json")]
                prior_scope = {(r.get("suite"), r.get("environment"), r["browser"], r["shard"]) for r in rows}
                if prior_scope == scope and all(r["outcome"] == "success" and r["scenarios"] for r in rows):
                    return prior
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return None


def tag_summary(results):
    groups = {}
    for row in results:
        for case in row["scenarios"]:
            for tag in case.get("tags", []):
                groups.setdefault(tag, []).append((row, case))
    lines = []
    for tag, cases in sorted(groups.items()):
        counts = Counter(case["status"] for _, case in cases)
        summary = " · ".join(f"{counts[status]} {status}" for status in ("passed", "failed", "skipped"))
        if other := len(cases) - sum(counts[status] for status in ("passed", "failed", "skipped")):
            summary += f" · {other} broken or unknown"
        durations = [(case["stop"] - case["start"], row, case) for row, case in cases
                     if case["status"] in {"passed", "failed", "broken"}
                     and type(case.get("start")) is int and type(case.get("stop")) is int
                     and case["stop"] >= case["start"]]
        if durations:
            duration, row, case = max(durations, key=lambda item: item[0])
            summary += f" · Slowest: {case['name'][:120]} ({BROWSER_NAMES[row['browser']]}, {duration / 1000:.1f}s)"
        lines.append(f"@{tag} · {summary}")
    return lines


def card(env, results, jobs, metadata=None, payload=None, baseline=None):
    metadata = metadata or {}
    payload = payload or {}
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
        (row, case) for row in results for case in row["scenarios"]
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
    event = env["GITHUB_EVENT_NAME"]
    actor = (metadata.get("actor") or {}).get("login") or env.get("GITHUB_ACTOR", "")
    rerun = (metadata.get("triggering_actor") or {}).get("login") or env.get("GITHUB_TRIGGERING_ACTOR", "")
    pr = payload.get("pull_request") or {}
    trigger = "Scheduled for 07:00 IST" if scheduled else ("Manual run" if event == "workflow_dispatch" else event.replace("_", " ").title())
    if pr:
        author = (pr.get("user") or {}).get("login", actor)
        trigger = f'Pull request #{pr.get("number", payload.get("number"))} by @{author} · {pr["head"]["ref"]} → {pr["base"]["ref"]}'
    elif not scheduled and actor:
        trigger += f" by @{actor}"
    if attempt != "1" and rerun:
        trigger += f" · Rerun by @{rerun}"
    context = f'{repo} · {env["GITHUB_REF_NAME"]} · Run #{env["GITHUB_RUN_NUMBER"]} · {env["TARGET_ENV"]}'
    if attempt != "1":
        context += f" · Attempt {attempt}"
    tested_sha = env.get("GITHUB_SHA", "")
    source_sha = (pr.get("head") or {}).get("sha") or tested_sha
    tested = f"Tested commit · {tested_sha[:8]}" if tested_sha else "Tested commit unavailable"
    if source_sha and source_sha != tested_sha:
        tested += f" · PR head {source_sha[:8]}"
    if matrix == "failure":
        tested += (f'\nLast comparable pass · Run #{baseline["number"]} · {baseline["headSha"][:8]}'
                   if baseline else "\nLast comparable pass unavailable")
    suite_name = next((r.get("suite") for r in results if r.get("suite")), None)
    suite_name = suite_name or env.get("REQUESTED_SUITE") or ("smoke" if pr else "regression")
    timings = []
    executed = [step for job in ui_jobs.values() for step in job.get("steps", [])
                if step["name"] == "Run Behave tests" and step.get("started_at") and step.get("completed_at")
                and step.get("conclusion") in {"success", "failure"}]
    if executed:
        start = min(datetime.fromisoformat(step["started_at"]) for step in executed)
        end = max(datetime.fromisoformat(step["completed_at"]) for step in executed)
        ist = ZoneInfo("Asia/Kolkata")
        timings.append(f"Tests ran · {start.astimezone(ist):%d %b %H:%M:%S} → {end.astimezone(ist):%d %b %H:%M:%S} IST · {elapsed(start, end)}")
    upstream = [job for job in jobs if job["name"] != "slack-summary" and job.get("completed_at")]
    if upstream and metadata.get("run_started_at"):
        start = datetime.fromisoformat(metadata["run_started_at"])
        end = max(datetime.fromisoformat(job["completed_at"]) for job in upstream)
        timings.append(f"Total CI before Slack · {elapsed(start, end)}")
    durations = [(case["stop"] - case["start"], row, case["name"])
                 for row in results for case in row["scenarios"]
                 if type(case.get("start")) is int and type(case.get("stop")) is int
                 and case["stop"] > case["start"] and case["status"] not in {"skipped", "unknown"}]
    if durations:
        duration, row, name = max(durations, key=lambda item: item[0])
        timings.append(f"Slowest scenario · {name[:240]} · {duration / 1000:.1f}s · {BROWSER_NAMES[row['browser']]} job {int(row['shard']) + 1}")
    browser_lines = []
    browsers = {row["browser"] for row in results}
    if expected == 6:
        browsers.update({"chromium", "firefox", "webkit"})
    for browser in sorted(browsers):
        rows = [row for row in results if row["browser"] == browser]
        tally = Counter(case["status"] for row in rows for case in row["scenarios"])
        quantities = " · ".join(f"{tally[key]} {key}" for key in ("passed", "failed", "skipped"))
        other = sum(tally.values()) - sum(tally[key] for key in ("passed", "failed", "skipped"))
        if other:
            quantities += f" · {other} broken or unknown"
        browser_lines.append(f"{BROWSER_NAMES[browser]} · {quantities} · {sum(bool(row['scenarios']) for row in rows)}/2 jobs reported")
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
    tags = tag_summary(results)
    reported_jobs = {(row["browser"], str(row["shard"])) for row in results if row["scenarios"]}
    missing_failures = [
        job["name"] for job in ui_jobs.values()
        if job["conclusion"] == "failure"
        and (match := re.fullmatch(r"ui-tests \(([^,]+), (\d+)\)", job["name"]))
        and match.groups() not in reported_jobs
    ]
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": title}},
        {"type": "context", "elements": [{"type": "plain_text", "text": context}]},
        section(f"Trigger · {trigger}\n{tested}\nSuite · {suite_name.replace('_', ' ').title()}\n{counts}\n{coverage}"),
        *([section("\n".join(browser_lines))] if browser_lines else []),
        *([section("Results by BDD tag · scenarios can appear under multiple tags\n" + "\n".join(tags))] if tags else []),
        *([section("Failed jobs without scenario results · " + ", ".join(missing_failures))] if missing_failures else []),
        *([section("\n".join(timings))] if timings else []),
    ]
    actions = []
    failed_row = None
    if test_failures:
        failed_row, failed_case = test_failures[0]
        name = failed_case["name"]
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
            f"{BROWSER_NAMES[failed_row['browser']]} · Job {int(failed_row['shard']) + 1}\nRetry · {retry}"
            + (f"\nAssertion · {failed_case['message']}" if failed_case.get("message") else "")
            + "\nNext action · Review the failed step and Playwright evidence."
        )])
    if failed_job:
        actions.append(("Open failed job", failed_job["html_url"]))
    elif jira == "failure" and jira_job:
        actions.append(("Open Jira job logs", jira_job["html_url"]))
    heading_jira = {"success": "Results published", "failure": "Publishing failed",
                    "cancelled": "Publishing cancelled", "skipped": "Publishing skipped"}.get(jira, "Status unavailable")
    bugs = json.loads(env.get("JIRA_BUGS") or "{}")
    if bugs:
        owners = json.loads(env.get("JIRA_OWNERS") or "{}")
        heading_jira += " · " + ", ".join(
            f"{key} {action}" + (f" ({owners[key]})" if owners.get(key) else "")
            for key, action in sorted(bugs.items())[:4]
        )
    blocks.append(section(f"Jira · {heading_jira}"))
    if report_url := env.get("ALLURE_REPORT_URL"):
        actions.append(("Open Allure report", report_url))
    full_report = env.get("FULL_ALLURE_URL", "")
    if full_report.startswith(f"{run}/artifacts/"):
        actions.append(("Download full evidence", full_report))
    if not actions:
        actions.append(("View run summary", run_url))
    evidence_rows = [failed_row] if failed_row else results if len(results) == 1 else []
    evidence = next((row["evidence"] for row in evidence_rows
                     if row["evidence"].startswith(f"{run}/artifacts/")), None)
    if evidence:
        actions.append(("Download job evidence", evidence))
    site = env.get("JIRA_SITE_URL", "").rstrip("/")
    if re.fullmatch(r"https://[a-z0-9-]+\.atlassian\.net", site):
        key = next(iter(sorted(bugs)), None) or env.get("JIRA_RESULTS_ISSUE", "")
        if jira == "success" and re.fullmatch(r"SCRUM-[1-9][0-9]*", key):
            actions.append(("View Jira Bug" if bugs else "Open Jira report", f"{site}/browse/{key}"))
    if pr.get("html_url"):
        actions.append(("View PR", pr["html_url"]))
    if (baseline and re.fullmatch(r"[a-f0-9]{40}", baseline["headSha"])
        and re.fullmatch(r"[a-f0-9]{40}", source_sha) and baseline["headSha"] != source_sha):
        actions.append(("Compare changes", f"https://github.com/{repo}/compare/{baseline['headSha']}...{source_sha}"))
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
    metadata = read_json(Path("ci-run.json")) or {}
    payload = read_json(Path(os.environ["GITHUB_EVENT_PATH"])) or {}
    baseline = baseline_for(os.environ, results) if os.environ["MATRIX_RESULT"] == "failure" else None
    request = Request(webhook, data=json.dumps(card(os.environ, results, jobs, metadata, payload, baseline)).encode(),
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

