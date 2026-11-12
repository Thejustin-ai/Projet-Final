# Incident Desk threat model (student working copy)

## System boundary

Browser → Django application → PostgreSQL. Administrative user provisioning is through Django admin. GitHub Actions builds/tests code, and Vercel serves a released revision. Database credentials and the stable Django signing key are environment configuration. Identify where trust/privileges change, not just machine/container boundaries.

## Assets and evidence

| Asset | Existing control | What remains to verify/extend |
|---|---|---|
| Incident content | Owner-scoped queryset; server-assigned owner | Analyst/admin policy and its negative tests |
| Credentials/sessions | Django hashing/session/CSRF facilities | Backoff, operational monitoring, deployed cookie/session evidence |
| Signing key and DB access | Environment variables; fail-closed production config | Rotation/recovery procedures, least DB privilege, repository/history scan |
| Source/release integrity | Pinned dependency snapshot; baseline tests | SAST/SCA/secrets/DAST, protected release and supply-chain decisions |

Scoring: likelihood and impact use low / medium / high. Impact is high where incident confidentiality or workflow integrity could be materially harmed. The current local demo contains synthetic records; a deployment with real reports would raise the impact of several threats.

## Prioritized threats

| ID / STRIDE | Asset and DFD element | Scenario and assumption | Likelihood | Impact | Control | Verification / status |
|---|---|---|---|---|---|---|
| T1 — Information disclosure / elevation | Incident records; browser → Django | A reporter changes an incident ID or forges an owner/assignee field to read another person's report. | Medium | High | Every list/detail/comment query starts from a role-scoped queryset; owner, assignment and actor are server selected. | Owner, analyst, admin and cross-owner tests pass. Implemented. |
| T2 — Information disclosure / tampering | Search input → database | A crafted title search changes SQL structure or bypasses ownership. | Medium | High | Django ORM binds the query as data and applies `created_by_id` in the same query. | Baseline reproducer confirms the original leak; hardened gate passes 5/5 after remediation. ZAP proxy capture remains unavailable in this environment. |
| T3 — Tampering / code execution in browser | Incident titles, descriptions and comments → templates | A user stores script-shaped text that executes for a later viewer. | Medium | High | Django template auto-escaping; comments are plain text with bounded input. | Existing XSS-shaped incident test and comment-escaping test pass. Implemented. |
| T4 — Tampering / repudiation | Status, assignment, comments; browser → Django | A cross-site request or unauthorized role changes workflow state, reassignment or comments; later attribution is missing. | Medium | High | CSRF middleware and tokens; POST-only actions; per-object role checks; append-only application audit events. Audit payload omits comment bodies and credentials. | Existing CSRF tests plus role-transition/assignment/audit tests pass. Implemented. |
| T5 — Spoofing / elevation | Login and session | Password guessing or a stolen session gains access to reports. | Medium | High | Django password hashing, generic login errors, session rotation/invalidation, short session lifetime, HttpOnly/SameSite cookies. | Session tests pass. Login backoff/rate limiting and deployed cookie review remain open. |
| T6 — Information disclosure / tampering | Repository, CI, deployment config and database | A committed secret, vulnerable dependency, failing security check or misconfigured deployment exposes or changes records. | Medium | High | Required production environment settings, PostgreSQL/TLS validation, pinned dependencies, behavioral CI tests. | Production configuration tests pass. SAST/SCA/secret-scan/DAST and a true release gate are still pending. |

## Data-flow notes

- Reporters submit synthetic incident content; analyst/admin actions mutate status and assignment through authenticated POST routes.
- Django groups grant application roles. Ordinary business administrators do not need Django superuser status; superusers retain the separate Django admin surface.
- Application comments are visible only to users who can see the incident. Audit entries store event type, actor, time and minimal transition/assignee metadata, never the comment body or request credentials.
- Local SQLite data is disposable and ignored by Git. Production requires an isolated hosted PostgreSQL database and private environment configuration.

Update likelihood and impact if the deployment, data sensitivity or user population changes. Preserve accepted/open risks; do not treat a clean scanner result as proof of security.
