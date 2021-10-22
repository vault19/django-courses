from django.forms import ModelForm, Form, CharField, HiddenInput
from courses.models import Submission, Review


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ["title", "description", "data"]


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["title", "description", "accepted"]


class SubscribeForm(Form):
    sender = CharField(label="Sender", widget=HiddenInput())
    run_slug = CharField(label="Run", widget=HiddenInput())
