from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from incidents.access import ADMIN_GROUP, ANALYST_GROUP
from incidents.models import AuditEvent, Incident, IncidentComment


class IncidentWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.reporter = User.objects.create_user(username="reporter", password="test-password-only")
        cls.analyst = User.objects.create_user(username="analyst", password="test-password-only")
        cls.other_reporter = User.objects.create_user(username="other", password="test-password-only")
        cls.manager = User.objects.create_user(username="manager", password="test-password-only")
        cls.analyst_group, _ = Group.objects.get_or_create(name=ANALYST_GROUP)
        cls.admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP)
        cls.analyst.groups.add(cls.analyst_group)
        cls.manager.groups.add(cls.admin_group)
        cls.owned = Incident.objects.create(
            title="Reporter owned report", description="Synthetic details for the reporter's issue.",
            created_by=cls.reporter,
        )
        cls.assigned = Incident.objects.create(
            title="Assigned analyst report", description="Synthetic details for analyst review.",
            created_by=cls.other_reporter, assigned_to=cls.analyst,
        )
        cls.unassigned_other = Incident.objects.create(
            title="Unassigned private report", description="Synthetic details not assigned to analyst.",
            created_by=cls.other_reporter,
        )

    def test_reporter_can_choose_severity_but_cannot_forge_owner_status_or_assignment(self):
        self.client.force_login(self.reporter)
        response = self.client.post(reverse("incidents:create"), {
            "title": "New synthetic report", "description": "A sufficiently detailed synthetic incident.",
            "severity": Incident.Severity.HIGH, "status": Incident.Status.CLOSED,
            "created_by": self.other_reporter.pk, "assigned_to": self.analyst.pk,
        })
        self.assertEqual(response.status_code, 302)
        incident = Incident.objects.get(title="New synthetic report")
        self.assertEqual(incident.created_by, self.reporter)
        self.assertEqual(incident.severity, Incident.Severity.HIGH)
        self.assertEqual(incident.status, Incident.Status.OPEN)
        self.assertIsNone(incident.assigned_to)
        self.assertTrue(incident.audit_events.filter(event_type=AuditEvent.EventType.CREATED).exists())

    def test_invalid_severity_is_rejected(self):
        self.client.force_login(self.reporter)
        before = Incident.objects.count()
        response = self.client.post(reverse("incidents:create"), {
            "title": "Invalid severity report", "description": "A sufficiently detailed synthetic incident.",
            "severity": "urgent",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("severity", response.context["form"].errors)
        self.assertEqual(Incident.objects.count(), before)

    def test_analyst_can_view_owned_and_assigned_incidents_only(self):
        self.client.force_login(self.analyst)
        response = self.client.get(reverse("incidents:list"))
        self.assertContains(response, "Assigned analyst report")
        self.assertNotContains(response, "Unassigned private report")
        self.assertNotContains(response, "Reporter owned report")
        self.assertEqual(response.context["paginator"].count, 1)

    def test_application_administrator_can_view_all_incidents(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("incidents:list"))
        self.assertContains(response, "Reporter owned report")
        self.assertContains(response, "Unassigned private report")
        self.assertEqual(response.context["paginator"].count, 3)

    def test_only_assigned_analyst_can_make_an_allowed_status_transition(self):
        self.client.force_login(self.analyst)
        response = self.client.post(reverse("incidents:change-status", args=[self.assigned.pk]), {
            "status": Incident.Status.TRIAGED,
        })
        self.assertEqual(response.status_code, 302)
        self.assigned.refresh_from_db()
        self.assertEqual(self.assigned.status, Incident.Status.TRIAGED)
        event = self.assigned.audit_events.get(event_type=AuditEvent.EventType.STATUS_CHANGED)
        self.assertEqual(event.metadata, {"from": "open", "to": "triaged"})

    def test_invalid_transition_and_unassigned_analyst_are_denied(self):
        self.client.force_login(self.analyst)
        response = self.client.post(reverse("incidents:change-status", args=[self.assigned.pk]), {
            "status": Incident.Status.RESOLVED,
        })
        self.assertEqual(response.status_code, 400)
        self.assigned.refresh_from_db()
        self.assertEqual(self.assigned.status, Incident.Status.OPEN)
        self.assertEqual(self.client.post(reverse("incidents:change-status", args=[self.unassigned_other.pk]), {
            "status": Incident.Status.TRIAGED,
        }).status_code, 404)

    def test_reporter_cannot_change_status(self):
        self.client.force_login(self.reporter)
        response = self.client.post(reverse("incidents:change-status", args=[self.owned.pk]), {
            "status": Incident.Status.TRIAGED,
        })
        self.assertEqual(response.status_code, 403)
        self.owned.refresh_from_db()
        self.assertEqual(self.owned.status, Incident.Status.OPEN)

    def test_only_application_administrator_can_assign_to_an_analyst(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("incidents:assign", args=[self.owned.pk]), {
            "assigned_to": self.analyst.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.owned.refresh_from_db()
        self.assertEqual(self.owned.assigned_to, self.analyst)
        self.assertTrue(self.owned.audit_events.filter(event_type=AuditEvent.EventType.ASSIGNED).exists())

        response = self.client.post(reverse("incidents:assign", args=[self.owned.pk]), {
            "assigned_to": self.other_reporter.pk,
        })
        self.assertEqual(response.status_code, 400)

    def test_reporter_cannot_assign_incident(self):
        self.client.force_login(self.reporter)
        response = self.client.post(reverse("incidents:assign", args=[self.owned.pk]), {
            "assigned_to": self.analyst.pk,
        })
        self.assertEqual(response.status_code, 403)
        self.owned.refresh_from_db()
        self.assertIsNone(self.owned.assigned_to)

    def test_comment_is_plain_text_audited_without_recording_its_body(self):
        self.client.force_login(self.reporter)
        body = "<script>alert('synthetic')</script>"
        response = self.client.post(reverse("incidents:comment", args=[self.owned.pk]), {"body": body})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IncidentComment.objects.get(incident=self.owned).author, self.reporter)
        event = self.owned.audit_events.get(event_type=AuditEvent.EventType.COMMENTED)
        self.assertEqual(event.metadata, {})

        detail = self.client.get(reverse("incidents:detail", args=[self.owned.pk]))
        self.assertNotContains(detail, body)
        self.assertContains(detail, "&lt;script&gt;")

    def test_comment_cannot_be_added_to_another_reporters_incident(self):
        self.client.force_login(self.reporter)
        response = self.client.post(reverse("incidents:comment", args=[self.unassigned_other.pk]), {
            "body": "An unauthorized synthetic comment.",
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(IncidentComment.objects.filter(incident=self.unassigned_other).exists())
