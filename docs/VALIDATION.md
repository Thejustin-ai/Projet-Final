# Validation — 2026-10-25

## Completed

- Installed the exact Django 5.2.18 runtime dependency snapshot in a dedicated virtual environment.
- Applied all Django and incident migrations to the course's local PostgreSQL container.
- **23 tests passed** using isolated SQLite on macOS Python 3.13.2.
- **23 tests passed** using PostgreSQL on macOS Python 3.13.2.
- **23 tests passed** using PostgreSQL in Linux Python 3.12, including the platform-specific psycopg dependency resolution.
- Verified anonymous access denial, owner-only list/detail, forged-owner input, validation limits, escaped script-shaped text, SQL-shaped input as data, missing/invalid-origin CSRF rejection, private-page headers, administrator access denial for normal users, local seeder restrictions, login/session rotation and POST/CSRF logout invalidation.
- Production-settings tests verify required private configuration, PostgreSQL-only storage, secure cookies, explicit hosts and HTTPS origins.
- `makemigrations --check --dry-run` found no missing model migrations.
- `collectstatic` successfully collected the application stylesheet and Django admin assets.
- Production `check --deploy` completed with **two intentionally retained warnings**: security.W005 (no includeSubDomains) and security.W021 (no preload). These reflect a cautious short initial HSTS rollout; no other checks were silenced.
- Browser verified login, private register, creation/detail of a synthetic incident and logout. Saved actual screenshots in docs/images. Local preview used port 8765 because another service occupied 8000.
- Compose/CI YAML, Python syntax and local documentation/image links checked.

The local database uses port 55432; an existing service occupied the originally considered 5433. No unrelated service was stopped. PostgreSQL image is pinned to its tested multi-platform digest.

## Not yet verified externally

- No remote GitHub repository was created, code pushed, or GitHub Actions run triggered. The workflow is supplied and its commands were exercised locally; remote-run success is not claimed.
- No Vercel account/project or hosted PostgreSQL database was created. Native Django entrypoint/static configuration follows official documentation, but a successful Vercel deployment is not claimed until the owner configures their accounts/environment and tests it.
- No SAST/SCA/secrets/DAST pipeline is completed: these are explicit student milestones. Runtime package pins are not evidence of absence of known vulnerabilities.
- Windows setup and browser mobile layouts need classroom verification.

## Distribution

Use scripts/package_starter.py to create a clean ZIP without local .env, .venv, databases, caches or generated staticfiles. The included screenshots show synthetic local records; no real credentials or personal incident information.

## Added local SQL injection challenge

The synthetic baseline reproduced normal owner-only search, quote-triggered SQL error and injected disclosure of Bob's record as Alice. The explicit hardening suite failed in the two intended places. A temporary source copy with the owner-scoped ORM fix passed all five hardening tests; the distributed exercise remains deliberately vulnerable. The normal suite now reports 30 discovered tests: 25 pass and five opt-in challenge tests skip outside security_lab settings. Production/default URL isolation and refusal of insecure settings on Vercel are covered. No authenticated ZAP active scan has been run; scanner detection depends on scope, authentication and installed rules. The student ZIP omits the instructor's exact solution guide and every SQLite fixture file.

## Student working copy — 2026-11-12

The preceding validation describes the supplied starter archive. This working copy now contains the student implementation: severity/status workflow, analyst assignment and application-admin policy, plain-text comments, and audit events. `docs/ACCESS_POLICY.md` records the policy and `docs/THREAT_MODEL.md` records prioritized threats and remaining risks.

- The challenge query in `training/search.py` is fixed with the owner-scoped ORM. Original/fixed source snapshots and a verification report are saved outside the repository in the local task outputs folder.
- Current normal suite: 41 tests found; 36 pass and five security-lab-only tests skip outside `security_lab`.
- Current challenge hardening gate: all five pass. Replaying the gate against the saved original source produced the expected two failures.
- Migration `0002` was applied to the local SQLite development database and creates the role groups. The local app has not been browser-verified because the constrained execution environment could not connect to its loopback server.
- No GitHub repository, remote Actions run, hosted database, Vercel deployment, authenticated ZAP scan, SAST/SCA/secret-scan pipeline, or release/rollback exercise is claimed.

## Student working copy — security workflow preparation

- `.github/workflows/security.yml` now defines the SQL-injection hardening test, Semgrep Community Edition, pip-audit and Gitleaks checks. It has not run on GitHub; review actual findings after the student pushes this repository. Semgrep and Gitleaks currently use version tags; pin image digests before treating the workflow as a frozen release control.
- The dependency audit was not run locally: package index DNS resolution failed in this environment. No clean dependency report is claimed.
- Authenticated ZAP DAST remains a manual, isolated lab step. ZAP active scanning sends attack payloads, so keep the target restricted to the local synthetic `/training/search/` route and verify that the `lab-alice` session remains authenticated. ZAP documentation describes Automation Framework contexts/users and scoped active scans; absence of a scanner alert is not proof of safety. See [ZAP environment configuration](https://www.zaproxy.org/docs/desktop/addons/automation-framework/environment/) and [active scan job](https://www.zaproxy.org/docs/desktop/addons/automation-framework/job-ascan/).
