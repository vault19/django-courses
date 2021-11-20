from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from courses.forms import SubscribeForm
from courses.models import Run, SubscriptionLevel


@login_required
def subscribe_to_run(request, run_slug):
    if request.method == "POST":
        run = get_object_or_404(Run, slug=run_slug)

        if run.is_full:
            messages.error(request, _("Subscribed user's limit has been reached."))
        elif not run.get_setting("COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE") and run.start <= timezone.now().date():
            messages.error(request, _("You are not allowed to subscribe to course that has already started."))
        elif run.end < timezone.now().date():
            messages.error(request, _("You are not allowed to subscribe to course that has already finished."))
        elif run.is_subscribed(request.user):
            messages.warning(request, _("You are already subscribed to course: %(run)s.") % {"run": run})
        elif run.is_subscribed_in_different_active_run(request.user):
            messages.error(request, _("You are already subscribed in different course run."))
        else:
            subscription_levels = SubscriptionLevel.objects.filter(run=run)
            form = SubscribeForm(data=request.POST, subscription_levels=subscription_levels.values_list('id', 'title'))

            if not form.is_valid():
                messages.error(request, _("Please correct errors in your subscription form.") + form.errors)

            # in M2M add will store to DB!
            run.users.add(request.user, through_defaults={'subscription_level_id': form.cleaned_data['subscription_level'], "payment": 0})

            # run.save()  # No need to save run
            messages.success(request, _("You have been subscribed to course: %(run)s.") % {"run": run})

            ctx_dict = {
                "user": request.user,
                "course_run": run,
                "subscription_levels": subscription_levels.all(),
                "selected_level": int(form.cleaned_data['subscription_level']),
            }
            subject = run.get_setting("COURSES_EMAIL_SUBJECT_PREFIX") + render_to_string(
                run.get_setting("COURSES_SUBSCRIBED_EMAIL_SUBJECT"), ctx_dict, request=request
            )
            # Email subject *must not* contain newlines
            subject = "".join(subject.splitlines())
            message = render_to_string(run.get_setting("COURSES_SUBSCRIBED_EMAIL_BODY"), ctx_dict, request=request)

            email_message = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            if run.get_setting("COURSES_SUBSCRIBED_EMAIL_HTML"):
                try:
                    message_html = render_to_string(
                        run.get_setting("COURSES_SUBSCRIBED_EMAIL_HTML"), ctx_dict, request=request
                    )
                except TemplateDoesNotExist:
                    pass
                else:
                    email_message.attach_alternative(message_html, "text/html")

            email_message.send()
    else:
        messages.warning(request, _("You need to submit subscription form in order to subscribe!"))

    return redirect("course_run_detail", run_slug=run_slug)


@login_required
def unsubscribe_from_run(request, run_slug):
    if request.method == "POST":
        run = get_object_or_404(Run, slug=run_slug)

        if not run.get_setting("COURSES_ALLOW_USER_UNSUBSCRIBE"):
            messages.warning(request, _("You are not allowed to unsubscribe from the course: %(run)s.") % {"run": run})
        elif run.is_subscribed(request.user):
            run.users.remove(request.user)  # in M2M remove will store to DB!
            # run.save()  # No need to save run
            messages.success(request, _("You have been unsubscribed from course: %(run)s.") % {"run": run})
        else:
            messages.warning(request, _("You are not subscribed to the course: %(run)s.") % {"run": run})
    else:
        messages.warning(request, _("You need to submit subscription form in order to unsubscribe!"))

    return redirect("course_run_detail", run_slug=run_slug)
