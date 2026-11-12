from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView
from .access import can_triage, is_app_admin, visible_incidents_for
from .forms import AssignmentForm, IncidentCommentForm, IncidentForm, StatusTransitionForm
from .models import AuditEvent, Incident

class OwnedIncidentsMixin(LoginRequiredMixin):
    def get_queryset(self):
        return visible_incidents_for(self.request.user)

class IncidentListView(OwnedIncidentsMixin, ListView):
    model = Incident
    template_name = "incidents/list.html"
    context_object_name = "incidents"
    paginate_by = 10

class IncidentDetailView(OwnedIncidentsMixin, DetailView):
    model = Incident
    template_name = "incidents/detail.html"
    context_object_name = "incident"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident = self.object
        context["comment_form"] = IncidentCommentForm()
        context["can_triage"] = can_triage(self.request.user, incident)
        context["can_assign"] = is_app_admin(self.request.user)
        if context["can_triage"]:
            context["status_form"] = StatusTransitionForm(incident=incident)
        if context["can_assign"]:
            context["assignment_form"] = AssignmentForm(initial={"assigned_to": incident.assigned_to_id})
        return context

class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        with transaction.atomic():
            response = super().form_valid(form)
            AuditEvent.objects.create(
                incident=self.object, actor=self.request.user,
                event_type=AuditEvent.EventType.CREATED,
            )
        messages.success(self.request, "Your incident has been recorded.")
        return response

    def get_success_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.object.pk})


@login_required
@require_POST
def change_status(request, pk):
    with transaction.atomic():
        incident = get_object_or_404(visible_incidents_for(request.user).select_for_update(), pk=pk)
        if not can_triage(request.user, incident):
            return HttpResponseForbidden("Only an assigned analyst or application administrator can change status.")
        form = StatusTransitionForm(request.POST, incident=incident)
        if not form.is_valid():
            return HttpResponseBadRequest("Invalid status transition.")
        old_status = incident.status
        new_status = form.cleaned_data["status"]
        if new_status == old_status:
            return HttpResponseBadRequest("Choose a different status.")
        incident.status = new_status
        incident.save(update_fields=["status"])
        AuditEvent.objects.create(
            incident=incident, actor=request.user,
            event_type=AuditEvent.EventType.STATUS_CHANGED,
            metadata={"from": old_status, "to": new_status},
        )
    messages.success(request, "Incident status updated.")
    return redirect("incidents:detail", pk=incident.pk)


@login_required
@require_POST
def assign_incident(request, pk):
    with transaction.atomic():
        incident = get_object_or_404(visible_incidents_for(request.user).select_for_update(), pk=pk)
        if not is_app_admin(request.user):
            return HttpResponseForbidden("Only an application administrator can assign incidents.")
        form = AssignmentForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest("Choose an active user in the analyst group.")
        old_assignee_id = incident.assigned_to_id
        assignee = form.cleaned_data["assigned_to"]
        if old_assignee_id == (assignee.pk if assignee else None):
            messages.info(request, "Assignment did not change.")
        else:
            incident.assigned_to = assignee
            incident.save(update_fields=["assigned_to"])
            AuditEvent.objects.create(
                incident=incident, actor=request.user,
                event_type=AuditEvent.EventType.ASSIGNED,
                metadata={"from_user_id": old_assignee_id, "to_user_id": assignee.pk if assignee else None},
            )
            messages.success(request, "Incident assignment updated.")
    return redirect("incidents:detail", pk=incident.pk)


@login_required
@require_POST
def add_comment(request, pk):
    incident = get_object_or_404(visible_incidents_for(request.user), pk=pk)
    form = IncidentCommentForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Write a comment of at most 2,000 characters.")
        return redirect("incidents:detail", pk=incident.pk)
    with transaction.atomic():
        comment = form.save(commit=False)
        comment.incident = incident
        comment.author = request.user
        comment.save()
        AuditEvent.objects.create(
            incident=incident, actor=request.user,
            event_type=AuditEvent.EventType.COMMENTED,
        )
    messages.success(request, "Comment added.")
    return redirect("incidents:detail", pk=incident.pk)
