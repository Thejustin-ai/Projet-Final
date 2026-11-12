from django import forms
from .access import analyst_users
from .models import Incident, IncidentComment

class IncidentForm(forms.ModelForm):
    severity = forms.ChoiceField(
        choices=Incident.Severity.choices, required=False,
        initial=Incident.Severity.MEDIUM,
    )

    class Meta:
        model = Incident
        # Ownership is never accepted from the browser.
        fields = ["title", "description", "severity"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "A short, descriptive title", "autofocus": True}),
            "description": forms.Textarea(attrs={"rows": 8, "placeholder": "What happened? Include synthetic details only."}),
        }
        help_texts = {
            "title": "3–150 characters.",
            "description": "10–5,000 characters. Use plain text; do not enter passwords or personal data.",
            "severity": "Choose the impact level that best matches the reported incident.",
        }

    def clean_severity(self):
        return self.cleaned_data.get("severity") or Incident.Severity.MEDIUM


class StatusTransitionForm(forms.Form):
    status = forms.ChoiceField(label="Move to status")

    def __init__(self, *args, incident, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = Incident.ALLOWED_STATUS_TRANSITIONS[incident.status]
        self.fields["status"].choices = [(value, Incident.Status(value).label) for value in allowed]


class AssignmentForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=analyst_users(), required=False, empty_label="Unassigned",
        label="Assign to analyst",
    )


class IncidentCommentForm(forms.ModelForm):
    class Meta:
        model = IncidentComment
        fields = ["body"]
        labels = {"body": "Comment"}
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "maxlength": 2000, "placeholder": "Add a plain-text update."}),
        }
