"""Collect Behave shard outcomes and publish trusted regression results to Jira."""

import base64
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def curl_read_status(url, credentials):
    """Compare HTTP clients without putting credentials in logs or arguments."""
    escaped = credentials.replace("\\", "\\\\").replace('"', '\\"')
    result = subprocess.run(
        ["curl", "--disable", "--config", "-", "--basic", "--silent",
         "--output", "/dev/null", "--write-out", "%{http_code}",
         "--max-time", "25", "--header", "Accept: application/json",
         "--header", "Content-Type: application/json", url],
        input=f'user = "{escaped}"\n',
        capture_output=True,
        text=True,
        check=False,
    )
    status = result.stdout.strip()
    if result.returncode == 0 and re.fullmatch(r"[1-5]\d{2}", status):
        print(f"Jira curl read returned HTTP {status}", flush=True)
    else:
        print(f"Jira curl read did not return an HTTP status (curl exit {result.returncode})", flush=True)


def jira(method, path, data=None, missing_ok=False, compare_curl=False):
    cloud_id = os.environ["JIRA_CLOUD_ID"]
    if not re.fullmatch(r"[0-9a-f-]{36}", cloud_id):
        raise ValueError("Invalid Jira Cloud ID")
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_TOKEN", "").strip()
    if not email or not token:
        raise ValueError("Jira CI credentials are missing")
    if not re.fullmatch(r"[^\s:@]+@[^\s:@]+", email):
        raise ValueError("Jira CI email must be a single email address")
    if any(character.isspace() for character in token):
        raise ValueError("Jira CI token contains internal whitespace")
    credentials = f"{email}:{token}"
    auth = base64.b64encode(credentials.encode()).decode()
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3{path}"
    request = Request(
        url,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json",
                 "Accept": "application/json"},
        method=method,
    )
    try:
        with build_opener(RejectRedirects()).open(request, timeout=25) as response:
            body = response.read()
    except HTTPError as exc:
        if missing_ok and exc.code == 404:
            return None
        if compare_curl and exc.code == 401:
            curl_read_status(url, credentials)
        trace_id = exc.headers.get("atl-traceid", "")
        trace = f"; Atlassian trace ID {trace_id}" if re.fullmatch(r"[0-9a-fA-F-]{16,64}", trace_id) else ""
        raise RuntimeError(f"Jira {method} failed (HTTP {exc.code}{trace})") from None
    return json.loads(body) if body else {}


def assertions(filename):
    path = Path("reports", filename)
    failures = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            failure = json.loads(line)
            # Ignore file line numbers in the fingerprint so unrelated edits do
            # not generate a new Bug. Keep the feature and expanded scenario.
            identity = [failure[field] for field in ("feature", "scenario", "step")]
            digest = hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:24]
            failures[digest] = failure
    return failures


def collect():
    first = assertions("ci-assertions.jsonl")
    repeated = assertions("ci-confirmed-assertions.jsonl")
    outcome = os.environ.get("TEST_OUTCOME", "")
    scenarios = {}
    for path in sorted(Path("reports/allure-results").glob("*-result.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        scenarios[entry.get("historyId") or entry.get("fullName") or path.stem] = {
            "name": entry.get("name", "Unnamed scenario"),
            "status": entry.get("status", "unknown"),
            "message": entry.get("statusDetails", {}).get("message", "")[:600]
            if os.environ.get("TEST_SUITE") == "defect_drill" else "",
            "start": entry.get("start"),
            "stop": entry.get("stop"),
        }
    result = {
        "scenarios": list(scenarios.values()),
        "suite": os.environ.get("TEST_SUITE", ""),
        "environment": os.environ.get("TARGET_ENV", ""),
        "retry": os.environ.get("RETRY_OUTCOME", "not run"),
        "browser": os.environ["BROWSER"],
        "shard": os.environ["SHARD_INDEX"],
        "outcome": outcome,
        "evidence": os.environ.get("EVIDENCE_URL", ""),
        "candidates": len(first),
        "confirmed": {key: first[key] for key in first.keys() & repeated.keys()}
        if outcome == "failure" else {},
    }
    Path("jira-result.json").write_text(json.dumps(result), encoding="utf-8")


def paragraph(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def link(label, url):
    return {"type": "paragraph", "content": [
        {"type": "text", "text": label, "marks": [{"type": "link", "attrs": {"href": url}}]}
    ]}


def file_defect(results_issue, candidate, failure, evidence, run_url):
    label = "pw-regression-" + candidate
    property_path = f"/issue/{results_issue}/properties/{label}"
    recorded = jira("GET", property_path, missing_ok=True)
    if recorded is not None:
        value = recorded["value"]
        if "key" not in value:
            raise RuntimeError(f"Resolve pending defect creation for {label} before retrying")
        return value["key"], "reused"
    matches = jira("POST", "/search/jql", {
        "jql": f'project = SCRUM AND labels = "{label}"',
        "fields": ["summary"], "maxResults": 2,
    })["issues"]
    if len(matches) > 1:
        raise RuntimeError(f"Multiple Jira defects already match {label}")
    if matches:
        key = matches[0]["key"]
    else:
        # Reserve before creating. If creation times out or the runner dies,
        # a later run stops on the reservation instead of creating a duplicate.
        jira("PUT", property_path, {"pending_run": run_url})
        content = [
            paragraph("A Then assertion failed on the first run and on the confirmation run."),
            paragraph(f"Feature: {failure['feature']}"),
            paragraph(f"Scenario: {failure['scenario']} (line {failure['line']})"),
            paragraph(f"Assertion step line: {failure['step_line']}"),
            link("GitHub Actions run and job logs", run_url),
        ]
        if os.environ.get("JIRA_DEFECT_DRILL") == "true":
            content.extend([
                paragraph("Controlled integration drill. An intentionally incorrect expectation was used to validate automatic filing."),
                paragraph("Steps: Open SauceDemo and submit the login form with an empty username and the demo password."),
                paragraph("Expected by the drill: Epic sadface: Password is required"),
                paragraph("Observed: Epic sadface: Username is required"),
            ])
        if evidence:
            content.append(link("Evidence archive (Allure HTML, logs, screenshots, video and traces when captured)", evidence))
        created = jira("POST", "/issue", {"fields": {
            "project": {"key": "SCRUM"}, "issuetype": {"name": "Bug"},
            "summary": ("[Playwright regression] " + failure["scenario"])[:240],
            "labels": ["automated-regression", label],
            "description": {"version": 1, "type": "doc", "content": content},
        }})
        key = created["key"]
    jira("PUT", property_path, {"key": key})
    return key, "reused" if matches else "created"


def publish():
    issue = os.environ["JIRA_RESULTS_ISSUE"]
    if not re.fullmatch(r"SCRUM-[1-9][0-9]*", issue):
        raise ValueError("JIRA_RESULTS_ISSUE must identify a SCRUM issue")
    print("Checking GitHub Actions credentials against the Jira reporting issue", flush=True)
    report_issue = jira("GET", f"/issue/{issue}?fields=summary", compare_curl=True)
    if report_issue.get("key") != issue:
        raise RuntimeError("Jira returned an unexpected reporting issue")
    print("Jira reporting issue is readable. Publishing CI results.", flush=True)
    repository = os.environ["GITHUB_REPOSITORY"]
    run = os.environ["GITHUB_RUN_ID"]
    attempt = os.environ["GITHUB_RUN_ATTEMPT"]
    run_url = f"https://github.com/{repository}/actions/runs/{run}/attempts/{attempt}"
    manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(Path("jira-results").glob("*/jira-result.json"))
    ]
    matrix = os.environ["MATRIX_RESULT"]
    expected = int(os.environ["EXPECTED_SHARDS"])
    environment = os.environ["TARGET_ENV"]
    event = os.environ["GITHUB_EVENT_NAME"]
    eligible = (
        (event == "schedule" or (event == "workflow_dispatch" and issue == "SCRUM-59"
         and os.environ.get("JIRA_DEFECT_DRILL") == "true"))
        and environment == "qa" and attempt == "1"
        and os.environ.get("JIRA_DEFECTS_ENABLED") == "true"
    )

    errors = []
    bug_outcomes = {}
    for result in manifests:
        browser = result["browser"]
        shard = result["shard"]
        evidence = result["evidence"]
        if not evidence.startswith(f"https://github.com/{repository}/actions/runs/{run}/artifacts/"):
            evidence = ""
        confirmed = result["confirmed"]
        outcome = result["outcome"]
        if confirmed:
            classification = f"{len(confirmed)} reproduced assertion(s)"
        elif result["candidates"]:
            classification = "assertion failure, reproduction unconfirmed"
        elif outcome == "success":
            classification = "Behave completed"
        else:
            classification = "infrastructure, framework error, or unclassified failure"
        defects = []
        if eligible:
            for fingerprint, failure in sorted(confirmed.items()):
                try:
                    key, action = file_defect(issue, fingerprint, failure, evidence, run_url)
                    defects.append(key)
                    if key not in bug_outcomes or action == "created":
                        bug_outcomes[key] = action
                except RuntimeError as exc:
                    errors.append(str(exc))
        title = f"{browser} shard {shard} | {classification}"
        if defects:
            title += " | " + ", ".join(defects)
        jira("POST", f"/issue/{issue}/remotelink", {
            "globalId": f"github:{repository}:{event}:{environment}:{browser}:{shard}",
            "relationship": "has latest CI evidence",
            "object": {"url": evidence or run_url, "title": title[:240],
                       "summary": "Allure HTML, logs, screenshots, videos and traces where available."
                       if evidence else "Open GitHub Actions for job logs."},
        })
        for defect in set(defects):
            jira("POST", f"/issue/{defect}/remotelink", {
                "globalId": f"github:{repository}:latest-regression",
                "relationship": "last reproduced in",
                "object": {"url": evidence or run_url, "title": f"Run {run} | {browser} shard {shard}"},
            })

    jira("POST", f"/issue/{issue}/remotelink", {
        "globalId": f"github:{repository}:{event}:{environment}:summary",
        "relationship": "has latest CI run",
        "object": {"url": run_url,
                   "title": f"{event} / {environment}: {matrix} ({len(manifests)}/{expected} shard reports)"},
    })
    if report_url := os.environ.get("ALLURE_REPORT_URL"):
        for report_key in {issue, *bug_outcomes}:
            jira("POST", f"/issue/{report_key}/remotelink", {
                "globalId": f"github:{repository}:allure:{run}:{attempt}",
                "relationship": "has Allure report",
                "object": {"url": report_url, "title": f"Open Allure report · Run {run} · Attempt {attempt}"},
            })
    if output := os.environ.get("GITHUB_OUTPUT"):
        owners = {}
        for key in sorted(bug_outcomes)[:4]:
            try:
                details = jira("GET", f"/issue/{key}?fields=assignee")
                assignee = details.get("fields", {}).get("assignee")
                owners[key] = assignee.get("displayName") if assignee else "Unassigned"
            except RuntimeError:
                continue
        with Path(output).open("a", encoding="utf-8") as stream:
            stream.write(f"bugs={json.dumps(bug_outcomes)}\n")
            stream.write(f"owners={json.dumps(owners)}\n")
    if errors:
        raise RuntimeError("; ".join(dict.fromkeys(errors)))


if __name__ == "__main__":
    import sys

    {"collect": collect, "publish": publish}[sys.argv[1]]()
