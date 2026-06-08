# Playwright BDD Automation Framework

A production-ready UI Automation Framework built using Python, Playwright, and Behave (BDD).

---

## Tech Stack

* Python
* Playwright
* Behave (BDD)
* Page Object Model (POM)
* Logging
* Screenshots
* Video Recording
* Trace Viewer
* CI/CD (GitHub Actions)

---

## Project Structure

```text
playwright-bdd-framework
│
├── features
│   ├── login.feature
│   ├── environment.py
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

## Installation

### Clone Repository

```bash
git clone <repository-url>
```

### Navigate to Project

```bash
cd playwright-bdd-framework
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright Browsers

```bash
playwright install
```

---

## Execute Tests

Run all tests:

```bash
behave
```

Run a specific feature:

```bash
behave features/login.feature
```

---

## Framework Features

### BDD Automation

* Gherkin Feature Files
* Given / When / Then implementation
* Readable business scenarios

### Playwright Automation

* Chromium Browser Support
* Auto Wait Mechanism
* Fast Execution

### Page Object Model

* Separation of Locators
* Reusable Page Classes
* Easy Maintenance

### Logging

* Scenario Start and End Logs
* Action-Level Logging
* File and Console Logging

### Screenshot Capture

* Failure Screenshots
* Timestamped Files

### Video Recording

* Playwright Video Capture
* Stored for Failed Executions

### Reporting

* HTML Reports
* Allure Reports (Future Enhancement)

### CI/CD Ready

* GitHub Actions Integration
* Automated Test Execution

---

## Test Application

SauceDemo

https://www.saucedemo.com

---

## Future Enhancements

* Data Driven Testing
* Cross Browser Execution
* Parallel Execution
* Allure Reporting
* GitHub Actions Pipeline
* Jenkins Integration
* Docker Support

---

## Author

Vinay B S
QA Automation Engineer
Python | Playwright | API Testing | BDD
