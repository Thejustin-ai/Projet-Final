from django.contrib.auth.models import Group
from django.db.models import Q

ANALYST_GROUP = "Incident Analysts"
ADMIN_GROUP = "Incident Administrators"


def is_app_admin(user):
    return bool(user.is_authenticated and (user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists()))


def is_analyst(user):
    return bool(user.is_authenticated and user.groups.filter(name=ANALYST_GROUP).exists())


def visible_incidents_for(user):
    from .models import Incident

    if is_app_admin(user):
        return Incident.objects.all()
    if is_analyst(user):
        return Incident.objects.filter(Q(created_by=user) | Q(assigned_to=user)).distinct()
    return Incident.objects.filter(created_by=user)


def can_triage(user, incident):
    return is_app_admin(user) or (is_analyst(user) and incident.assigned_to_id == user.pk)


def analyst_users():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.filter(
        is_active=True, groups__name=ANALYST_GROUP,
    ).distinct().order_by("username")


def ensure_role_groups():
    """Create the two application-role groups without granting any access by default."""
    Group.objects.get_or_create(name=ANALYST_GROUP)
    Group.objects.get_or_create(name=ADMIN_GROUP)
