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

USERNAME=standard_user
PASSWORD=secret_sauce
```

The `.env` file should not be committed to GitHub.

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

# Allure Reporting

The framework uses `allure-behave` to generate Allure test results.

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