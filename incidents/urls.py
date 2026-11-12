from django.urls import path
from .views import (
    IncidentCreateView, IncidentDetailView, IncidentListView, add_comment,
    assign_incident, change_status,
)
app_name = "incidents"
urlpatterns = [
    path("", IncidentListView.as_view(), name="list"),
    path("incidents/new/", IncidentCreateView.as_view(), name="create"),
    path("incidents/<int:pk>/", IncidentDetailView.as_view(), name="detail"),
    path("incidents/<int:pk>/status/", change_status, name="change-status"),
    path("incidents/<int:pk>/assignment/", assign_incident, name="assign"),
    path("incidents/<int:pk>/comments/", add_comment, name="comment"),
]
