from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

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
                if subscription.subscription_level and (subscription.subscription_level.price >= subscription.payment):
                    raise PermissionDenied(_("Subscription has not been payed yet!"))

        return func(*args, **kwargs)

    return wrapper
