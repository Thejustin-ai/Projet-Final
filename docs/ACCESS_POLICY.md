# Incident access policy

## Roles

| Role | Read | Create | Comment | Assign | Change status |
|---|---|---|---|---|---|
| Reporter (default) | Incidents they created | Yes | On visible incidents | No | No |
| Incident Analyst group | Their own and incidents assigned to them | Yes | On visible incidents | No | Assigned incidents only |
| Incident Administrator group | All incidents | Yes | On all incidents | Assign/unassign to an active analyst | All incidents |
| Django superuser | All incidents and Django admin | Yes | On all incidents | Assign/unassign to an active analyst | All incidents |

Application groups are created by migration `0002`. Add memberships through Django admin. A normal business administrator should receive the **Incident Administrators** group, not Django superuser status. The Django admin remains a separate superuser-only account-management and read-only incident inspection surface.

Incident creation always sets `created_by` on the server. Initial status is `Open`; an accepted severity is selected from Low, Medium, High, or Critical, defaulting to Medium if omitted. Assignment only accepts active accounts in the analyst group. Comment authors are set from the authenticated session. No form accepts owner, status, assignee, actor, or audit metadata fields.

## Status transitions

| Current status | Allowed next statuses |
|---|---|
| Open | Triaged, Closed |
| Triaged | In progress, Closed |
| In progress | Resolved |
| Resolved | In progress, Closed |
| Closed | None |

Only the assigned analyst or an application administrator can use the transition endpoint. The endpoint checks both object visibility and the transition table on every POST; controls hidden in the template are not an authorization boundary.

## Comments and audit trail

Comments are plain text with a 2,000-character bound and rely on Django template auto-escaping. They cannot be edited or deleted through the application. Audit events record incident creation, status changes, assignment changes, and comment creation. Event metadata is limited to transition values and assignee IDs; comment text, passwords, tokens, IP addresses, and request headers are not copied into the audit table. Django admin exposes comments and events read-only.

## Verification

`incidents/tests/test_workflow.py` covers server-owned fields, severity validation, reporter/analyst/administrator object scope, assigned-only state changes, invalid transitions, assignment validation, comment escaping, audit metadata, and cross-owner denial.
