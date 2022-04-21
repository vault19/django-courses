from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.forms import ModelForm, Form, CharField, HiddenInput, ModelChoiceField, ChoiceField, RadioSelect, Textarea
from django.utils.translation import gettext_lazy as _

from courses.models import Submission, Review


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ["title", "description", "video_link", "image", "data"]


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

    sender = CharField(label=_("Sender"), widget=HiddenInput())
    run_slug = CharField(label=_("Run"), widget=HiddenInput())
    subscription_level = ChoiceField(choices=CHOICES, widget=RadioSelect, required=False)

    def __init__(self, subscription_levels=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if subscription_levels:
            self.fields["subscription_level"] = ChoiceField(
                choices=subscription_levels, widget=RadioSelect, required=True
            )
        else:
            del self.fields["subscription_level"]


class MailForm(Form):
    recipient = CharField(label=_("Recipient"), validators=[EmailValidator()])
    subject = CharField(label=_("Subject"), min_length=3, max_length=256)
    body = CharField(label=_("Body"), widget=Textarea(attrs={"rows": 5, "cols": 20}))
