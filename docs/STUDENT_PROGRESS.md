# Student project progress

This is the status of the local working copy on 12 November 2026. The supplied ZIP is the starter; external account actions and a published deployment have not been performed.

## Implemented locally

- A normal local SQLite settings module, so the app can run on Windows without Docker or PostgreSQL. It is loopback-only by documented run command and refuses the Vercel environment.
- Incident severity choices and a bounded status workflow with reviewed migration.
- Reporter, assigned analyst and application administrator object policies using Django groups.
- Server-owned creation/assignment/actor values, role-checked POST actions, analyst assignment validation and plain-text comments.
- Audit events for incident creation, status change, assignment and comments; audit data does not store comment contents or secrets.
- Access matrix, status transition policy and prioritized threat model.
- Fixed the exercise SQL injection in this student working copy. Source snapshots and verification notes are saved outside the project repository.

## Local verification

- `manage.py test --settings=config.settings.test`: 41 tests found; all 36 applicable tests pass, five security-lab-only tests are skipped under normal settings.
- `manage.py test training.tests.test_hardening --settings=config.settings.security_lab`: 5/5 pass after the fix.
- Replayed the hardening gate temporarily on the saved original query: the two injection tests failed as expected; restored the ORM fix and reran to 5/5 pass.
- `makemigrations --check --dry-run --settings=config.settings.test`: no changes detected.
- Production URL resolution does not expose `/training/search/`.
- ZAP is installed, but the local proxy could not open its socket in the constrained Windows execution environment. No ZAP capture or scan is claimed.
- Added `.github/workflows/security.yml` with the deterministic SQL injection hardening suite plus Semgrep, pip-audit and Gitleaks jobs. The workflow is prepared but cannot be claimed as run until pushed to GitHub Actions. Dependency audit could not be run locally because this environment could not resolve `pypi.org`.

## Still required for the capstone submission

- Create your own local superuser with the documented command; then create a reporter, analyst and application administrator in Django admin and exercise the role matrix. Keep the password private.
- Create/push to your personal GitHub repository and inspect actual Actions runs.
- Push the prepared workflow to GitHub and inspect SAST, dependency and secret scan findings; fix and document real findings. Run an isolated authenticated ZAP scan against only the local training search endpoint. The ZAP scan is still pending because its local proxy could not open a socket here.
- Configure the private hosted PostgreSQL and Vercel project, apply migrations deliberately, smoke-test the actual deployment, and record its real URL and commit.
- Review whether login backoff is required, define the actual failing-check release gate available on the chosen accounts, and document a rollback exercise and residual risks.
