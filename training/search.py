"""Owner-scoped incident search for the local synthetic exercise."""
from incidents.models import Incident

def search_incidents(user_id, query):
    return list(
        Incident.objects.filter(created_by_id=user_id, title__icontains=query)
        .order_by("-created_at")
        .values("id", "title", "description")[:20]
    )
