from django.forms import ModelForm, Form, CharField, HiddenInput, ModelChoiceField, ChoiceField, RadioSelect
from courses.models import Submission, Review
from django.contrib.auth import get_user_model


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ["title", "description", "data"]


User = get_user_model()


class AuthorChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class SubmissionChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class ReviewForm(ModelForm):
    author = AuthorChoiceField(queryset=User.objects.none())
    submission = SubmissionChoiceField(queryset=Submission.objects.none())

    class Meta:
        model = Review
        fields = ["submission", "author", "title", "description", "accepted"]

    def __init__(self, run=None, lecture=None, submission_id=None, author=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if submission_id:
            self.fields["submission"].queryset = Submission.objects.filter(id=submission_id).all()

        elif run and lecture:
            self.fields["submission"].queryset = Submission.objects.filter(lecture=lecture).filter(run=run).all()

        if author:
            self.fields["author"].queryset = User.objects.filter(id=author).all()


class SubscribeForm(Form):
    CHOICES = []

    sender = CharField(label="Sender", widget=HiddenInput())
    run_slug = CharField(label="Run", widget=HiddenInput())
    subscription_level = ChoiceField(choices=CHOICES, widget=RadioSelect, required=False)

    def __init__(self, subscription_levels=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if subscription_levels:
            self.fields["subscription_level"] = ChoiceField(
                choices=subscription_levels, widget=RadioSelect, required=True
            )
        else:
            del self.fields["subscription_level"]
