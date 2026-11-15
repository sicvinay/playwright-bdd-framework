# SDET Portfolio Roadmap

This document separates functionality visible in the repository from planned improvements. It is not a claim that the framework has passed CI or that all integrations are operational.

## Current repository components

- Python + Playwright + Behave (BDD) with Gherkin login scenarios.
- Page Object Model with separate page and locator modules.
- Scenario lifecycle hooks and screenshot/trace handling in `features/environment.py`.
- Logging utilities and Allure dependencies.
- GitHub Actions workflow in `.github/workflows/ui-tests.yml`.

## Verify before claiming production readiness

- Run the suite locally and in GitHub Actions; record passing and failing results.
- Check whether CI secrets `SAUCE_USERNAME` and `SAUCE_PASSWORD` are set. The sample Gherkin scenarios contain SauceDemo demo credentials, but CI uses GitHub secrets.
- Check whether `SLACK_WEBHOOK_URL` is configured: the current workflow attempts a notification after every run.
- Confirm artifact folders exist before trace saving and that screenshot/trace/video attachments are actually present in Allure.
- Ensure generated logs and reports are ignored and remove previously committed artifacts from tracking if appropriate.
- Validate documented environment-variable names against `config/config.py` (which reads `USERNAME` and `PASSWORD`).
- Review README claims and remove placeholder markup.

## Suggested implementation milestones

1. **Reliability:** reproducible setup, smoke tests passing in CI, safe artifact paths, correct cleanup.
2. **Test coverage:** inventory sorting, product details, cart operations, checkout happy/negative paths, logout.
3. **Diagnostics:** Allure screenshots, Playwright trace/video capture and artifact upload.
4. **Quality gates:** linting, formatting, dependency checks and clear PR checks.
5. **Advanced:** cross-browser matrix, parallel execution with isolated test data, API tests, environment-based configuration.

## Portfolio presentation

- Keep README installation and run instructions accurate and tested.
- Add a short architecture diagram and a representative sample Allure report screenshot once verified.
- Link this project from the [GitHub profile](https://github.com/sicvinay).
- Do not publish real credentials, tokens, production datasets or private employer code.

> Roadmap only; no tests or CI jobs were run as part of writing this document.
