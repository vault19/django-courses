import base64
import requests
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import BadRequest

from courses.forms import SubscribeForm
from courses.models import Run, SubscriptionLevel, RunUsers
from courses.utils import send_templated_email
from courses.decorators import paypal_enabled
from courses.settings import PAYPAL_BASE_URL, PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_CURRENCY, BANK_TRANSFER, \
    BANK_NAME, BANK_ACCOUNT_NAME, BANK_IBAN, BANK_SWIFT, BANK_CURRENCY

logger = logging.getLogger(__name__)


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
    run_user = get_object_or_404(RunUsers, run=run, user=request.user)
    run_subscription_levels = run.get_subscription_level(request.user)  # Potentially delete
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
        return redirect("course_run_overview", run_slug=run_slug)

    context = {
        "request": request,
        "run": run,
        "subscribed": run.is_subscribed(request.user),
        "subscribed_levels": run_subscription_levels,
        "run_user": run_user,
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

    if PAYPAL_CLIENT_ID:
        context["paypal_client_id"] = PAYPAL_CLIENT_ID
        context["paypal_client_currency"] = PAYPAL_CURRENCY

    if BANK_TRANSFER:
        context["bank_name"] = BANK_NAME
        context["bank_account_name"] = BANK_ACCOUNT_NAME
        context["bank_iban"] = BANK_IBAN
        context["bank_swift"] = BANK_SWIFT
        context["bank_currency"] = BANK_CURRENCY

    return render(request, "courses/run_payment_instructions.html", context)


@login_required
@paypal_enabled
def verify_paypal_order(request, order_id):
    consumer_key_secret = f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}"
    consumer_key_secret_enc = base64.b64encode(consumer_key_secret.encode()).decode()

    headersAuth = {
        "Authorization": 'Basic ' + str(consumer_key_secret_enc),
    }

    data = {
        "grant_type": "client_credentials",
    }

    ## Authentication request
    response = requests.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", headers=headersAuth, data=data, verify=True)
    j = response.json()

    if "access_token" not in j:
        raise BadRequest(_("PayPal Access Token missing. Please contact support with ORDER ID: %s" % order_id))

    headersAPI = {
        "accept": "application/json",
        "Authorization": f"Bearer {j['access_token']}",
    }

    response = requests.get(f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}", headers=headersAPI, verify=True)
    order = response.json()

    if 'purchase_units' not in order:
        raise BadRequest(_("Something went wrong with the order. Please contact support with ORDER ID: %s" % order_id))
    else:
        if 'reference_id' not in order['purchase_units'][0]:
            raise BadRequest(_("Missing reference_id, can not pair with payment. Please contact support with "
                               "ORDER ID: %s" % order_id))
        # RunUsers.id == reference_id
        if order['status'] != 'COMPLETED':
            raise BadRequest(_("Order is not COMPLETED. If you have finished the payment please contact support with "
                               "ORDER ID: %s" % order_id))

        subscription = RunUsers.objects.get(id=order['purchase_units'][0]['reference_id'])
        subscription.payment = order['purchase_units'][0]['amount']['value']
        subscription.save()

        logger.info("PayPal Order %s was matched with RunUser ID %s and updated with payment of %s %s", order_id,
                    subscription.id, subscription.payment, order['purchase_units'][0]['amount']['currency_code'])
        messages.success(request, _("Thank you for your payment."))

    return redirect("course_run_overview", run_slug=subscription.run.slug)


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

            defaults = {
                "payment": 0,
                "price": 0,
            }

            if "subscription_level" in form.cleaned_data:
                subscribed_level = SubscriptionLevel.objects.get(id=form.cleaned_data["subscription_level"])
                defaults["subscription_level_id"] = form.cleaned_data["subscription_level"]
                defaults["price"] = subscribed_level.price

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
