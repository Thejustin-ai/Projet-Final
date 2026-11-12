from django.contrib import admin
from .models import AuditEvent, Incident, IncidentComment

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "severity", "status", "created_by", "assigned_to", "created_at"]
    list_filter = ["severity", "status"]
    list_select_related = ["created_by", "assigned_to"]
    search_fields = ["title", "created_by__username", "assigned_to__username"]
    readonly_fields = ["title", "description", "created_by", "assigned_to", "severity", "status", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    list_display = ["incident", "author", "created_at"]
    list_select_related = ["incident", "author"]
    search_fields = ["incident__title", "author__username"]
    readonly_fields = ["incident", "author", "body", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["incident", "event_type", "actor", "created_at"]
    list_filter = ["event_type"]
    list_select_related = ["incident", "actor"]
    readonly_fields = ["incident", "actor", "event_type", "metadata", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
