from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from courses.models import RunUsers


def verify_payment(func):
    """
    Decorator for views that checks whether user is subscribed to the course run and has payed subscription.
    """

    def wrapper(*args, **kwargs):
        request = args[0]

        if "run_slug" in kwargs:
            subscriptions = RunUsers.objects.filter(run__slug=kwargs["run_slug"]).filter(user=request.user)

            if subscriptions.count() == 0 and request.user.is_staff is False:
                raise PermissionDenied(_("You are not subscribed to this course!"))

            for subscription in subscriptions.all():
                if subscription.subscription_level and subscription.price > subscription.payment:
                    messages.error(request, _("You need to finish the payment in order to continue to the course."))
                    return redirect("run_payment_instructions", run_slug=kwargs["run_slug"])

        return func(*args, **kwargs)

    return wrapper
