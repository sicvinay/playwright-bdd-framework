# Playwright BDD Automation Framework

A UI Automation Framework built using **Python, Playwright, Behave (BDD), and Allure Reporting**.

The framework follows the **Page Object Model (POM)** design pattern and supports logging, screenshots, video recording, and test reporting.

---

# Tech Stack

- Python
- Playwright
- Behave (BDD)
- Allure Reporting
- Page Object Model (POM)
- Logging
- Screenshots
- Video Recording
- Trace Viewer
- CI/CD (GitHub Actions)

---

# Project Structure

```text
playwright-bdd-framework
│
├── features
│   ├── login.feature
│   ├── environment.py
│   │
│   └── steps
│       └── login_steps.py
│
├── pages
│   ├── login_page.py
│   └── inventory_page.py
│
├── locators
│   └── login_locators.py
│
├── config
│   ├── config.py
│   └── .env
│
├── test_data
│   └── login_data.json
│
├── utils
│   ├── browser_manager.py
│   ├── logger.py
│   └── screenshot.py
│
├── reports
│   ├── allure-results
│   ├── allure-report
│   └── logs
│
├── screenshots
│
├── videos
│
├── requirements.txt
│
├── .gitignore
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/sicvinay/playwright-bdd-framework.git
```

## Navigate to Project

```bash
cd playwright-bdd-framework
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Virtual Environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Install Playwright Browsers

```bash
playwright install
```

---

# Environment Configuration

Create a `.env` file inside the `config` folder.

Example:

```text
BASE_URL=https://www.saucedemo.com

TARGET_ENV=qa
APP_USERNAME=standard_user
APP_PASSWORD=secret_sauce
BROWSER=chromium
```

The `.env` file should not be committed to GitHub. `TARGET_ENV` supports `qa`, `dev`, and `staging`. QA defaults to SauceDemo; DEV and STAGING require a real `BASE_URL` for the deployed application. `APP_USERNAME` and `APP_PASSWORD` are preferred; legacy `USERNAME` and `PASSWORD` remain supported for local compatibility.

For GitHub Actions, configure repository secrets `SAUCE_USERNAME` and `SAUCE_PASSWORD` under **Settings → Secrets and variables → Actions**. Configure repository variables `DEV_BASE_URL` and `STAGING_BASE_URL` only after real deployments exist. For DEV, configure `DEV_APP_USERNAME` and `DEV_APP_PASSWORD` as Actions secrets; for STAGING, configure `STAGING_APP_USERNAME` and `STAGING_APP_PASSWORD`. The workflow selects credentials by `TARGET_ENV` and fails early if the selected environment lacks either secret. QA continues to use `SAUCE_USERNAME` and `SAUCE_PASSWORD`. Never commit credentials or put them in the URL. Workflow reports include environment and base URL metadata but never passwords.

---

# Test Execution

## Run All Tests

```bash
behave
```

## Run a Specific Feature

```bash
behave features/login.feature
```

## Run Tests Using Tags

Run smoke tests:

```bash
behave --tags=@smoke
```

Run negative tests:

```bash
behave --tags=@negative
```

Run login tests:

```bash
behave --tags=@login
```

---

# Parallel Behave Execution in CI

GitHub Actions distributes the top-level `.feature` files across **two parallel shards** using a deterministic sorted round-robin assignment. Each shard runs in a separate runner and produces its own Allure report, screenshots, videos, traces, and logs. Existing cross-browser `browser=all` expands to **six jobs** (3 browser engines × 2 shards). Daily 07:00 IST QA runs all three engines with two shards per engine.

This is **feature-file-level parallelism**, not scenario-level parallelism: scenarios inside one feature still run sequentially. Shard durations can differ if feature files have unequal numbers of scenarios. The current two-feature suite gives one feature to each shard. The workflow avoids simultaneous writes to shared report directories by using isolated runners and unique artifact names. The workflow also combines the shard results into one Allure report for the run. No additional Python parallel-runner package is required.

---

# Cross-Browser Testing

The framework supports `BROWSER=chromium` (default), `BROWSER=firefox`, and `BROWSER=webkit`. Install all engines locally using `python -m playwright install chromium firefox webkit`. In PowerShell, select an engine with `$env:BROWSER="firefox"; behave --tags=@smoke` (replace firefox with chromium or webkit).

For GitHub Actions, choose **Actions → UI Automation Tests → Run workflow**, select `browser=all` to run three separate browser jobs, and select the desired suite/environment. Each job publishes its own browser- and shard-specific evidence artifact. Pull requests and pushes default to Chromium. WebKit is Playwright's Safari engine, not the Safari desktop browser.

---

# Scheduled Regression Runs

GitHub Actions runs all regular QA scenarios automatically every day at **07:00 IST (01:30 UTC)** against the QA SauceDemo environment. The workflow uses `cron: '30 1 * * *'`, so the schedule is UTC-based and does not shift for daylight saving time in India. Scheduled workflows run from the default branch and GitHub may delay their start during periods of high load.

You can still run tests manually via **Actions → UI Automation Tests → Run workflow**. Pull requests continue to run smoke tests; normal pushes continue to run regression tests. The workflow serializes overlapping scheduled runs, generates Allure reports and uploads test artifacts. Slack notifications require a configured `SLACK_WEBHOOK_URL` secret.

---

# Allure Reporting

The framework uses `allure-behave` to generate Allure test results.

Each workflow attempt produces one Slack card with run totals and a breakdown by BDD tag. Scenarios with several tags appear under each tag and count once per browser in the run total. Scheduled runs execute the regular QA suite across all browsers and exclude `@wip` and `@defect_drill`. Manual runs can select one suite or `all`.

For eligible QA runs, **Open Allure report** opens a hosted overview with outcomes and timing grouped by browser and job. Public reports use approved scenario titles and suite tags. **Download full evidence** links to a GitHub Actions artifact retained for 14 days. It includes a single-file Allure report with the raw test details and attachment data, plus the individual jobs' diagnostic files where captured. Jira receives the available links. If a job fails before producing results, use the job logs for setup diagnostics. A failed-jobs-only retry can show partial results because reports are scoped to the current attempt.

## Generate Allure Results

```bash
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
```

## Open Allure Report

```bash
allure serve reports/allure-results
```

## Generate a Permanent Allure HTML Report

```bash
allure generate reports/allure-results -o reports/allure-report --clean
```

## Open Generated Report

```bash
allure open reports/allure-report
```

> Note: The Allure Commandline must be installed separately and available in the system PATH.

---

# Framework Features

## BDD Automation

- Gherkin Feature Files
- Given / When / Then implementation
- Scenario Outlines
- Examples for data-driven testing
- Tags for test categorization
- Readable business scenarios

---

## Playwright Automation

- Chromium browser automation
- Playwright auto-wait mechanism
- Dynamic waits
- Browser context isolation
- Fast execution

---

## Page Object Model

- Separation of page logic
- Reusable page classes
- Centralized locators
- Improved maintainability

---

## Logging

The framework supports:

- Scenario start logging
- Scenario completion logging
- Action-level logging
- Console logging
- File logging

Execution logs are stored under:

```text
reports/logs/
```

---

## Screenshots

The framework is being configured to capture screenshots for:

- Passed scenarios
- Failed scenarios

Screenshots will be attached to the Allure report.

---

## Video Recording

The framework is being configured to record Playwright execution videos for:

- Passed scenarios
- Failed scenarios

Videos will be attached to the Allure report.

---

## Allure Report Artifacts

The target Allure report will contain:

```text
Scenario
│
├── Execution Status
│
├── Test Steps
│
├── Execution Logs
│
├── Screenshot
│
├── Video Recording
│
└── Failure Details
```

---

# Test Application

The current framework uses SauceDemo as the practice application.

SauceDemo

:contentReference[oaicite:0]{index=0}

---

# Future Enhancements

- Cross-browser execution
- Parallel execution
- Playwright Trace Viewer integration
- GitHub Actions pipeline
- Jenkins integration
- Docker support
- Test data management
- API automation integration
- Database validation
- Retry mechanism for flaky tests
- Environment configuration for DEV / QA / PROD

---

# Author

Vinay B S

QA Automation Engineer

**Python | Playwright | Behave | API Testing | BDD | Test Automation**
