from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import BadRequest

from courses.forms import SubscribeForm
from courses.models import Run, SubscriptionLevel
from courses.utils import send_templated_email


@login_required
def run_subscription_levels(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    subscribed = run.is_subscribed(request.user)

    subscription_levels = SubscriptionLevel.objects.filter(run=run)
    if subscription_levels.count() == 0:
        subscription_levels = SubscriptionLevel.objects.filter(course=run.course)

    if subscription_levels.count() == 0:
        raise BadRequest(_("Missing Course Levels!"))

    elif subscribed:
        total_subscription = 0

        for level in run.get_subscription_level(request.user):
            total_subscription += level[1].price

        if run.user_payment(request.user) >= total_subscription:
            return redirect("course_run_detail", run_slug=run_slug)
        else:
            messages.warning(request, _("You are already subscribed to course: %(run)s.") % {"run": run})
            messages.error(request, _("You need to finish the payment in order to continue to the course."))
            return redirect("run_payment_instructions", run_slug=run_slug)

    form = SubscribeForm(
        initial={"sender": request.user.username, "run_slug": run_slug},
        subscription_levels=subscription_levels.values_list("id", "title"),
    )

    context = {
        "run": run,
        "subscription_levels": subscription_levels.all(),
        "subscribed": subscribed,
        "form": form,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "url": reverse("course_detail", args=(run.course.slug,)),
                "title": run.course.title,
            },
            {
                "title": run.title.upper(),
            },
            {
                "title": _("Subscription levels"),
            },
        ],
        "page_tab_title": run.course.title,
    }

    return render(request, "courses/run_subscription_levels.html", context)


@login_required
def run_payment_instructions(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    run_subscription_levels = run.get_subscription_level(request.user)
    payment = run.user_payment(request.user)
    total_subscription = 0

    for level in run_subscription_levels:
        total_subscription += level[1].price

    if payment >= total_subscription:
        messages.success(
            request,
            _(
                "We have received %(payment)s of %(price)s EUR. Enjoy your course."
                % {"price": total_subscription, "payment": payment}
            ),
        )
        return redirect("course_run_detail", run_slug=run_slug)

    context = {
        "run": run,
        "subscribed": run.is_subscribed(request.user),
        "subscribed_levels": run_subscription_levels,
        "total_paid": payment,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "url": reverse("course_detail", args=(run.course.slug,)),
                "title": run.course.title,
            },
            {
                "title": run.title.upper(),
            },
            {
                "title": _("Payment instructions"),
            },
        ],
    }

    return render(request, "courses/run_payment_instructions.html", context)


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
            form = SubscribeForm(data=request.POST, subscription_levels=subscription_levels.values_list("id", "title"))

            if not form.is_valid():
                messages.error(request, _("Please correct errors in your subscription form.") + form.errors)

            defaults = {"payment": 0}

            if "subscription_level" in form.cleaned_data:
                defaults["subscription_level_id"] = form.cleaned_data["subscription_level"]

            # in M2M add will store to DB!
            run.users.add(
                request.user,
                through_defaults=defaults,
            )

            # run.save()  # No need to save run
            messages.success(request, _("You have been subscribed to course: %(run)s.") % {"run": run})

            mail_template = run.course.mail_subscription

            # If the mail_template is specified, send a subscription email
            if mail_template:
                send_templated_email(
                    request.user,
                    mail_subject=mail_template.mail_subject,
                    mail_body_html=mail_template.mail_body_html,
                    template_variables={
                        "user": request.user,
                        "course_run": run,
                        "subscribed_levels": run.get_subscription_level(request.user),
                    },
                )
            # If the mail_template is not specified, notify the Course creator
            else:
                send_templated_email(
                    run.course.creator,
                    mail_subject="Course mail_subscription not specified!",
                    mail_body_html="The mail_subscription template is missing for {{ course|safe }}!\n\n"
                                   "The user {{ user|safe }} did not receive an email.",
                    template_variables={
                        "user": request.user,
                        "course": run.course,
                    },
                )
    else:
        messages.warning(request, _("You need to submit subscription form in order to subscribe!"))

    if run.get_subscription_level(request.user):
        return redirect("run_payment_instructions", run_slug=run_slug)

    return redirect("all_subscribed_runs")


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
