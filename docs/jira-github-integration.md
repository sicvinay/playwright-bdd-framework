# Jira and GitHub integration

The implementation is tracked under SCRUM-58 in SDET Team. This repository uses the existing GitHub for Jira installation. An Atlassian administrator should confirm that the GitHub account and this repository are connected with synchronization complete before changing any app settings.

## Delivery workflow

1. Create a framework Task, Story, or Bug in SCRUM. Apply `framework-delivery` only to issues that should follow development status. Keep interview preparation issues out of this opt-in.
2. Branch from current `main` with the Jira key, for example `feature/SCRUM-58-jira-regression-integration`. Include the key in commits and the PR title, and keep it in the squash commit if using squash merge.
3. Verify that Jira's Development panel shows the branch, commit and PR for that key. GitHub checks should pass before merging. A draft PR can check CI and linking without triggering a merge.
4. In SCRUM automation, scope each rule to the project and require `framework-delivery` plus an allowed source status. Use PR created to move To Do to In Progress. Use PR merged into the default branch to move to Done only when that PR is the agreed completion gate and the repository requires passing checks. If additional QA approval is required, leave the issue In Progress until sign-off. Validate rules and their audit log using the delivery issue and an unlabelled test issue before applying them broadly.

## CI reporting and defect registration

Existing UI jobs retain their daily 07:00 IST schedule, two feature shards, optional Chromium/Firefox/WebKit runs, evidence upload and Slack notification. A separate Jira job receives small per-shard manifests from trusted runs on `main` and posts the latest links per event/environment/browser/shard to the configured Jira issue. It records the matrix result and missing-shard count. PRs use the normal GitHub checks and keep Jira credentials out of PR workflows.

Suite setup, browser startup, missing credentials, timeouts and unknown failures do not qualify for automatic bug creation. An explicit exception of type `AssertionError` in a Behave Then step is only a candidate. Eligible scheduled QA runs repeat the shard and file a Bug only when the same assertion fails again. A reproduced assertion is evidence for QA triage. Capture and verify the underlying application cause before resolving or escalating it.

The stable fingerprint uses feature path, expanded scenario and assertion step, without browser, shard, run ID or source line number. A Jira issue property on the reporting issue maps each fingerprint to the Bug key, even after the Bug closes. The serialized writer reserves that property before creating a Bug and also checks Jira for an existing exact fingerprint label. If the create result is uncertain, a pending property intentionally blocks automatic retries for that fingerprint. Locate the Bug using its label and original run, then repair the property with the confirmed key. If Jira audit evidence establishes that creation never happened, an administrator can clear that one pending property to allow a later retry. Do not change the reporting issue without migrating its fingerprint properties.

Evidence links target GitHub Actions or the 14-day artifact containing Allure HTML, logs, screenshots, videos and traces. Open the workflow run to see job logs. For the HTML report, download and extract the artifact and serve the `reports/allure-report` directory (or `allure-report` at the archive root) over local HTTP. Keep evidence from confidential environments out of public artifacts. Jira receives links and scenario identifiers with no raw exception traces or credentials.

## Setup and validation

- Create a scoped Jira API token with a dedicated integration identity, using only access needed to browse SCRUM, create Bugs, and update the reporting issue, its remote links and Jira issue properties. Use GitHub Actions secrets `JIRA_CI_EMAIL` and `JIRA_CI_TOKEN`. Store `JIRA_CLOUD_ID` and `JIRA_RESULTS_ISSUE` as repository variables. The token is sent to the Atlassian Cloud API endpoint only.
- After CI and linking have been checked, set `JIRA_REPORTING_ENABLED=true`. Dispatch QA smoke and check both shard links and the run link in Jira. Dispatch QA smoke with `browser=all` and check six shard reports. Review a setup failure and check it appears with no Bug.
- Validate confirmation and deduplication with controlled assertions and an isolated Jira test target before setting `JIRA_DEFECTS_ENABLED=true`. Automatic creation runs only on the first attempt of the daily QA schedule, never on manual dispatches or PRs. Review the first scheduled run and verify the report, Slack delivery where configured, and captured evidence. Disable either integration switch independently if needed.
