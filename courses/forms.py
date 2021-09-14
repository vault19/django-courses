from django.forms import ModelForm
from courses.models import Submission


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ["title", "description", "data"]
